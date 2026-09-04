"""
Dumps every Panel object of the current bed assembly (params.py's
STYLE/COLOR_SCHEME env vars select the variant, same as test-bed/view-bed)
to a plain JSON file — Label, Length/Width/Thickness (mm), Material,
StockSource, PanelColor. No FreeCAD-specific data in the output, so
tools/cutlist.py (a separate, plain-Python script) can consume it without
needing freecadcmd/FreeCAD itself.

Run with freecadcmd (see tools/dump_panels.sh):
    STYLE=5 COLOR_SCHEME=charcoal_front tools/dump_panels.sh
"""

import json
import os
import sys

_BED_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "furniture", "bed")
_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_ROOT_DIR, _BED_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import FreeCAD as App

from bed import create_bed

OUTPUT_PATH = os.environ.get(
    "PANELS_OUTPUT", os.path.join(_BED_DIR, "output", "panels.json")
)


def main():
    doc = App.newDocument("CutlistDump")
    panels, _mattress = create_bed(doc)
    doc.recompute()

    data = []
    for p in panels:
        data.append(dict(
            name=p.Name,
            label=p.Label,
            length=p.Length.Value,
            width=p.Width.Value,
            thickness=p.Thickness.Value,
            material=p.Material,
            stock_source=p.StockSource,
            color=list(p.PanelColor)[:3],
        ))

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Wrote {len(data)} panels to {OUTPUT_PATH}")


main()
