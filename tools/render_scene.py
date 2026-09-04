"""
Renders a scene.json (tools/dump_scene.py) to a PNG using matplotlib's
software (Agg) rasterizer — no FreeCAD, no OpenGL/GPU needed, so it works
in headless environments where FreeCAD's own GUI screenshot path
(view.saveImage(), which needs a working OpenGL context) doesn't. Not a
substitute for actually opening the model in FreeCAD (tools/view_*.sh) —
just a quick, dependency-light visual for reviewing a design remotely.

Draws each panel as an axis-aligned box (see dump_scene.py's docstring
for why the bounding box alone is exact here) with its own PanelColor.
Only ONLY_VISIBLE panels are drawn by default — the point is to preview
the finished piece's actual appearance, not its hidden internal carcass.

Usage:
    .venv/bin/python tools/render_scene.py <scene.json> <output.png> \\
        [--elev 20] [--azim -60] [--all]   # --all includes hidden panels
"""

import argparse
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


def box_faces(bbox):
    x0, x1 = bbox["xmin"], bbox["xmax"]
    y0, y1 = bbox["ymin"], bbox["ymax"]
    z0, z1 = bbox["zmin"], bbox["zmax"]
    corners = {
        (0, 0, 0): (x0, y0, z0), (1, 0, 0): (x1, y0, z0),
        (1, 1, 0): (x1, y1, z0), (0, 1, 0): (x0, y1, z0),
        (0, 0, 1): (x0, y0, z1), (1, 0, 1): (x1, y0, z1),
        (1, 1, 1): (x1, y1, z1), (0, 1, 1): (x0, y1, z1),
    }
    c = corners
    return [
        [c[(0, 0, 0)], c[(1, 0, 0)], c[(1, 1, 0)], c[(0, 1, 0)]],  # bottom
        [c[(0, 0, 1)], c[(1, 0, 1)], c[(1, 1, 1)], c[(0, 1, 1)]],  # top
        [c[(0, 0, 0)], c[(1, 0, 0)], c[(1, 0, 1)], c[(0, 0, 1)]],  # front (y min)
        [c[(0, 1, 0)], c[(1, 1, 0)], c[(1, 1, 1)], c[(0, 1, 1)]],  # back (y max)
        [c[(0, 0, 0)], c[(0, 1, 0)], c[(0, 1, 1)], c[(0, 0, 1)]],  # left (x min)
        [c[(1, 0, 0)], c[(1, 1, 0)], c[(1, 1, 1)], c[(1, 0, 1)]],  # right (x max)
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scene_json")
    ap.add_argument("output_png")
    ap.add_argument("--elev", type=float, default=18)
    ap.add_argument("--azim", type=float, default=-60)
    ap.add_argument("--all", action="store_true", help="include hidden/reclaimed panels too")
    ap.add_argument("--width", type=float, default=12)
    ap.add_argument("--height", type=float, default=9)
    args = ap.parse_args()

    with open(args.scene_json) as f:
        panels = json.load(f)

    if not args.all:
        panels = [p for p in panels if p["visible"]]

    fig = plt.figure(figsize=(args.width, args.height))
    ax = fig.add_subplot(111, projection="3d")

    xs, ys, zs = [], [], []
    for p in panels:
        b = p["bbox"]
        xs += [b["xmin"], b["xmax"]]
        ys += [b["ymin"], b["ymax"]]
        zs += [b["zmin"], b["zmax"]]

        faces = box_faces(b)
        color = tuple(p["color"])
        poly = Poly3DCollection(
            faces, facecolor=color, edgecolor=(0, 0, 0, 0.35), linewidths=0.4,
        )
        ax.add_collection3d(poly)

    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    zmin, zmax = min(zs), max(zs)
    span = max(xmax - xmin, ymax - ymin, zmax - zmin) / 2
    cx, cy, cz = (xmin + xmax) / 2, (ymin + ymax) / 2, (zmin + zmax) / 2
    ax.set_xlim(cx - span, cx + span)
    ax.set_ylim(cy - span, cy + span)
    ax.set_zlim(cz - span, cz + span)
    ax.set_box_aspect((1, 1, 1))

    ax.view_init(elev=args.elev, azim=args.azim)
    ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(args.output_png, dpi=150, facecolor="white")
    print(f"Rendered {len(panels)} panels to {args.output_png}")


main()
