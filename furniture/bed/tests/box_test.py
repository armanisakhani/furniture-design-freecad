"""
Phase 3 test.

Purpose: generate one full Box (shell + 2 Drawer_box carcasses) via box.py
and confirm the panel count and rough dimensions are sane, and that nothing
overlaps outside its expected bounds. Open the saved .FCStd in the FreeCAD
GUI to visually confirm the shell + 2 drawers look like a real box.

Note: freecadcmd runs a script with __name__ set to the script's filename,
not "__main__" — call main() unconditionally (see smoke_test.py).
"""

import os
import sys

# freecadcmd doesn't know this project's own package layout — put this
# furniture module's own directory (for params/box/bed) and the repo root
# (for core/) on sys.path before any project-local import.
_BED_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ROOT_DIR = os.path.dirname(os.path.dirname(_BED_DIR))
for _p in (_ROOT_DIR, _BED_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import FreeCAD as App

import params
from box import create_box
from core.verify import verify_footprint

OUTPUT_DIR = os.path.join(_BED_DIR, "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "box_test.FCStd")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    doc = App.newDocument("Phase3BoxTest")

    panels = create_box(doc, box_index=0)
    doc.recompute()
    doc.saveAs(OUTPUT_FILE)

    print(f"Created {OUTPUT_FILE}")
    print(f"Panel count: {len(panels)} (expected 6 shell + 2x6 drawer = 18)")

    for p in panels:
        bbox = p.Shape.BoundBox
        print(
            f"  {p.Label:35s} X[{bbox.XMin:7.1f},{bbox.XMax:7.1f}] "
            f"Y[{bbox.YMin:7.1f},{bbox.YMax:7.1f}] "
            f"Z[{bbox.ZMin:7.1f},{bbox.ZMax:7.1f}]  Material={p.Material}"
        )

    # Z runs SKIRT_HEIGHT below 0 (the Face panels' drawer-side skirt
    # reach) and stops at BOX_HEIGHT.
    verify_footprint(
        "box_test", panels,
        expected=dict(
            xmin=0, xmax=params.FRAME_WIDTH,
            ymin=0, ymax=params.BOX_LENGTH,
            zmin=-params.SKIRT_HEIGHT, zmax=params.BOX_HEIGHT,
        ),
    )


main()
