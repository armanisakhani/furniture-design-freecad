"""
Dumps every Panel object of a furniture assembly to a plain JSON "scene"
file — label, world-space bounding box (xmin/xmax/ymin/ymax/zmin/zmax),
color, visible, material, stock_source. No FreeCAD-specific data in the
output, so tools/render_scene.py (a separate, plain-Python script, no
FreeCAD needed) can turn it into a PNG for a quick visual check without
needing FreeCAD's own (OpenGL-dependent) screenshot path.

The world-space bounding box is enough to reconstruct each panel's exact
box, not an approximation: every Panel placement in this project only
ever rotates by 90-degree multiples (see core/placement.py's
IDENTITY/ROT_X90/ROT_Y90), so each panel's world-space shape is itself
axis-aligned — its BoundBox already IS its exact extent, nothing lost by
dropping the rotation and keeping only the box.

Run with freecadcmd, given a furniture module name and its create-
function name (the module's own directory must already be a valid
furniture/<name>/ path):

    MODULE=dresser CREATE_FN=create_dresser tools/dump_scene.sh
    MODULE=bed CREATE_FN=create_bed tools/dump_scene.sh
"""

import importlib
import json
import os
import sys

MODULE = os.environ["MODULE"]
CREATE_FN = os.environ.get("CREATE_FN", f"create_{MODULE}")

_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MODULE_DIR = os.path.join(_ROOT_DIR, "furniture", MODULE)
for _p in (_ROOT_DIR, _MODULE_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import FreeCAD as App

OUTPUT_PATH = os.environ.get(
    "SCENE_OUTPUT", os.path.join(_MODULE_DIR, "output", "scene.json")
)


def main():
    doc = App.newDocument("SceneDump")
    mod = importlib.import_module(MODULE)
    create_fn = getattr(mod, CREATE_FN)
    result = create_fn(doc)
    # Some create_* functions (e.g. bed.create_bed) return a
    # (panels, extra_obj) tuple instead of just the panel list.
    panels = result[0] if isinstance(result, tuple) else result
    doc.recompute()

    data = []
    for p in panels:
        if not hasattr(p, "Shape"):
            continue
        bbox = p.Shape.BoundBox
        data.append(dict(
            name=p.Name,
            label=p.Label,
            bbox=dict(
                xmin=bbox.XMin, xmax=bbox.XMax,
                ymin=bbox.YMin, ymax=bbox.YMax,
                zmin=bbox.ZMin, zmax=bbox.ZMax,
            ),
            color=list(p.PanelColor)[:3] if hasattr(p, "PanelColor") else [0.7, 0.7, 0.7],
            visible=bool(p.PanelVisible) if hasattr(p, "PanelVisible") else True,
            material=getattr(p, "Material", None),
            stock_source=getattr(p, "StockSource", None),
        ))

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Wrote {len(data)} panels to {OUTPUT_PATH}")


main()
