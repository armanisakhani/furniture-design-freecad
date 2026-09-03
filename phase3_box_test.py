"""
Phase 3 test.

Purpose: generate one full Box (shell + 2 Drawer_box carcasses) via box.py
and confirm the panel count and rough dimensions are sane, and that nothing
overlaps outside its expected bounds. Open the saved .FCStd in the FreeCAD
GUI to visually confirm the shell + 2 drawers look like a real box.

Note: freecadcmd runs a script with __name__ set to the script's filename,
not "__main__" — call main() unconditionally (see phase0_smoke_test.py).
"""

import os

import FreeCAD as App

import params
from box import create_box

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "phase3_box_test.FCStd")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    doc = App.newDocument("Phase3BoxTest")

    panels = create_box(doc, box_index=0)
    doc.recompute()
    doc.saveAs(OUTPUT_FILE)

    print(f"Created {OUTPUT_FILE}")
    print(f"Panel count: {len(panels)} (expected 6 shell + 2x6 drawer = 18)")

    overall_bbox = None
    for p in panels:
        bbox = p.Shape.BoundBox
        if overall_bbox is None:
            overall_bbox = App.BoundBox(bbox)
        else:
            overall_bbox.add(bbox)
        print(
            f"  {p.Label:35s} X[{bbox.XMin:7.1f},{bbox.XMax:7.1f}] "
            f"Y[{bbox.YMin:7.1f},{bbox.YMax:7.1f}] "
            f"Z[{bbox.ZMin:7.1f},{bbox.ZMax:7.1f}]  Material={p.Material}"
        )

    print(
        f"Overall bounding box: X[{overall_bbox.XMin:.1f},{overall_bbox.XMax:.1f}] "
        f"Y[{overall_bbox.YMin:.1f},{overall_bbox.YMax:.1f}] "
        f"Z[{overall_bbox.ZMin:.1f},{overall_bbox.ZMax:.1f}]"
    )
    print(
        f"Expected external footprint: X[0,{params.FRAME_WIDTH}] "
        f"Y[0,{params.BOX_LENGTH}] Z[0,{params.BOX_HEIGHT}]"
    )


main()
