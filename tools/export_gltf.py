"""
Exports the currently-open document to a self-contained glTF binary
(.glb), for sharing outside FreeCAD (e.g. an interactive <model-viewer>
web page). Run via the GUI binary, not freecadcmd — needs a live
ViewObject to read PanelColor from (see tools/export_bed_gltf.sh; the
GUI binary works fine with QT_QPA_PLATFORM=offscreen, no visible window
needed since nothing is actually rendered to a screen here).

Output path: EXPORT_PATH env var (default /tmp/export.glb) — an env var,
not a CLI flag, for the same reason params.py's STYLE is: freecadcmd's
own argument parser rejects unrecognized flags unpredictably.

Import.export()'s own glTF writer (OpenCascade's RWGltf_CafWriter)
doesn't read ViewObject.ShapeColor at all — every mesh comes out with no
material. This patches the material array into the .glb's JSON chunk
afterward: one material per distinct PanelColor (object order into
Import.export == node child order in the output, so node N+1
corresponds to objs[N]), falling back to a neutral gray for non-Panel
objects (e.g. the mattress placeholder).
"""

import json
import os
import struct

import FreeCAD as App
import Import

OUT_PATH = os.environ.get("EXPORT_PATH", "/tmp/export.glb")
DEFAULT_COLOR = (0.7, 0.7, 0.7)

doc = App.ActiveDocument

for obj in doc.Objects:
    if hasattr(obj, "PanelColor") and obj.ViewObject is not None:
        obj.ViewObject.ShapeColor = obj.PanelColor
doc.recompute()

objs = [obj for obj in doc.Objects if hasattr(obj, "Shape")]
for obj in objs:
    obj.Shape.tessellate(1.0)

Import.export(objs, OUT_PATH)

with open(OUT_PATH, "rb") as f:
    data = f.read()

magic, version, _total_length = struct.unpack("<4sII", data[:12])
json_len, _json_type = struct.unpack("<I4s", data[12:20])
json_bytes = data[20:20 + json_len]
rest = data[20 + json_len:]  # BIN chunk header + data, unchanged

gltf = json.loads(json_bytes)

materials = []
color_to_material = {}


def material_index_for(color):
    key = tuple(round(c, 4) for c in color)
    if key not in color_to_material:
        color_to_material[key] = len(materials)
        materials.append({
            "pbrMetallicRoughness": {
                "baseColorFactor": [key[0], key[1], key[2], 1.0],
                "metallicFactor": 0.0,
                "roughnessFactor": 0.8,
            }
        })
    return color_to_material[key]


assert len(gltf["nodes"]) - 1 == len(objs), (
    f"node/object count mismatch: {len(gltf['nodes']) - 1} nodes vs "
    f"{len(objs)} objects — a shape probably failed tessellation"
)

for obj, node in zip(objs, gltf["nodes"][1:]):
    color = getattr(obj, "PanelColor", DEFAULT_COLOR)
    mat_idx = material_index_for(color)
    for prim in gltf["meshes"][node["mesh"]]["primitives"]:
        prim["material"] = mat_idx

gltf["materials"] = materials

new_json_bytes = json.dumps(gltf).encode("utf-8")
pad = (4 - len(new_json_bytes) % 4) % 4
new_json_bytes += b" " * pad  # glTF spec: JSON chunk padded with spaces

new_total_length = 12 + 8 + len(new_json_bytes) + len(rest)
with open(OUT_PATH, "wb") as f:
    f.write(struct.pack("<4sII", magic, version, new_total_length))
    f.write(struct.pack("<I4s", len(new_json_bytes), b"JSON"))
    f.write(new_json_bytes)
    f.write(rest)

print(f"Exported {OUT_PATH} ({len(objs)} objects, {len(materials)} materials)")
os._exit(0)  # skip Qt/Coin3D teardown, which segfaults under offscreen platform
