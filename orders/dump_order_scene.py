"""
Same as tools/dump_scene.py, but for an already-combined order (see
combine_order.py) instead of a single freshly-built furniture module —
opens the saved orders/output/order.FCStd directly rather than calling a
create_<name>() function, since a combined order isn't one furniture
module's own doc. Feeds tools/render_scene.py for generate_report.py's
render image.

Run with freecadcmd, after combine_order.py has produced order.FCStd:
    freecadcmd orders/dump_order_scene.py
"""

import json
import os

import FreeCAD as App

_ORDERS_DIR = os.path.dirname(os.path.abspath(__file__))
FCSTD_PATH = os.path.join(_ORDERS_DIR, "output", "order.FCStd")
OUTPUT_PATH = os.path.join(_ORDERS_DIR, "output", "order_scene.json")


def main():
    doc = App.openDocument(FCSTD_PATH)
    doc.recompute()

    data = []
    for p in doc.Objects:
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

    with open(OUTPUT_PATH, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Wrote {len(data)} panels to {OUTPUT_PATH}")


main()
