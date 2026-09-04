"""
First-draft build/verify script for the dresser (دراور) — a single
front-opening carcass with DRAWER_COUNT stacked drawers. See
furniture/bed/tests/bed_test.py for the pattern this follows.

Note: freecadcmd runs a script with __name__ set to the script's
filename, not "__main__" — call main() unconditionally.
"""

import os
import sys

# freecadcmd doesn't know this project's own package layout — put this
# furniture module's own directory (for params/dresser) and the repo root
# (for core/) on sys.path before any project-local import.
_DRESSER_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ROOT_DIR = os.path.dirname(os.path.dirname(_DRESSER_DIR))
for _p in (_ROOT_DIR, _DRESSER_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import FreeCAD as App

import params
from dresser import create_dresser
from core.verify import verify_footprint

OUTPUT_DIR = os.path.join(_DRESSER_DIR, "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "dresser_test.FCStd")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    doc = App.newDocument("DresserTest")

    panels = create_dresser(doc)
    doc.recompute()
    doc.saveAs(OUTPUT_FILE)

    print(f"Created {OUTPUT_FILE}")
    print(f"Total panels: {len(panels)} (expected 5 shell + {params.DRAWER_COUNT} x 9 drawer)")

    # X: 0..WIDTH. Y: Inset Face panels land flush at Y=0 (the shell's own
    # open-face plane) — the furthest-forward point of the carcass itself
    # — but each drawer's metal handle protrudes further out still, to
    # -(HANDLE_STANDOFF + HANDLE_BAR_SIZE); DEPTH is the furthest back. Z:
    # floor (0, no raised base — see params.py's Base/feet section) to the
    # top of the Left/Right side panels (HEIGHT), the tallest feature
    # (SIDE_TOP_LIP above the Top panel's own surface).
    verify_footprint(
        "dresser_test", panels,
        expected=dict(
            xmin=0, xmax=params.WIDTH,
            ymin=-(params.HANDLE_STANDOFF + params.HANDLE_BAR_SIZE), ymax=params.DEPTH,
            zmin=0, zmax=params.HEIGHT,
        ),
    )


main()
