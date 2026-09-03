"""
Early, partial Phase 6 test.

Purpose: assemble all BOX_COUNT boxes side by side plus a placeholder
mattress (bed.py) and confirm the overall footprint looks right — no skirt
or leg frame yet, see bed.py's docstring and roadmap.md.

Note: freecadcmd runs a script with __name__ set to the script's filename,
not "__main__" — call main() unconditionally (see phase0_smoke_test.py).
"""

import os

import FreeCAD as App

import params
from bed import create_bed

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "phase6_bed_test.FCStd")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    doc = App.newDocument("Phase6BedTest")

    panels, mattress = create_bed(doc)
    doc.recompute()
    doc.saveAs(OUTPUT_FILE)

    print(f"Created {OUTPUT_FILE}")
    print(f"Total panels: {len(panels)} (expected {params.BOX_COUNT} x 18)")

    overall_bbox = App.BoundBox(panels[0].Shape.BoundBox)
    for p in panels[1:]:
        overall_bbox.add(p.Shape.BoundBox)
    overall_bbox.add(mattress.Shape.BoundBox)

    print(
        f"Overall bounding box: X[{overall_bbox.XMin:.1f},{overall_bbox.XMax:.1f}] "
        f"Y[{overall_bbox.YMin:.1f},{overall_bbox.YMax:.1f}] "
        f"Z[{overall_bbox.ZMin:.1f},{overall_bbox.ZMax:.1f}]"
    )
    print(
        f"Expected boxes footprint: X[0,{params.FRAME_WIDTH}] "
        f"Y[0,{params.FRAME_LENGTH}] Z[0,{params.BOX_HEIGHT}]"
    )
    print(
        f"Expected mattress top: Z={params.BOX_HEIGHT + params.MATTRESS_THICKNESS}"
    )


main()
