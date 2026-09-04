"""
Early, partial Phase 6 test.

Purpose: assemble all BOX_COUNT boxes side by side plus a placeholder
mattress (bed.py) and confirm the overall footprint looks right — no skirt
or leg frame yet, see bed.py's docstring and roadmap.md.

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
from bed import create_bed
from core.verify import verify_footprint

OUTPUT_DIR = os.path.join(_BED_DIR, "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "bed_test.FCStd")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    doc = App.newDocument("Phase6BedTest")

    panels, mattress = create_bed(doc)
    doc.recompute()
    doc.saveAs(OUTPUT_FILE)

    print(f"Created {OUTPUT_FILE}")
    print(f"Total panels: {len(panels)} (expected {params.BOX_COUNT} x 18)")

    # Y runs MDF_THICKNESS below 0 (the headboard's own reach past the head
    # end) and Z runs from FLOOR_Z (the actual floor — -LEG_FRAME_HEIGHT
    # normally, or 0 itself with HAS_LEG_FRAME=False) up to the headboard's
    # top edge (HEADBOARD_HEIGHT above the floor) — the tallest thing in
    # the assembly, above the mattress placeholder's own top.
    verify_footprint(
        "bed_test", panels + [mattress],
        expected=dict(
            xmin=0, xmax=params.FRAME_WIDTH,
            ymin=-params.MDF_THICKNESS, ymax=params.FRAME_LENGTH,
            zmin=params.FLOOR_Z,
            zmax=params.FLOOR_Z + params.HEADBOARD_HEIGHT,
        ),
    )


main()
