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
    print(f"Total panels: {len(panels)} (expected 6 shell + {params.DRAWER_COUNT} x 6 drawer)")

    # X: 0..WIDTH. Y: the Face panels' own protrusion is the furthest-
    # forward point (negative), DEPTH the furthest back. Z: floor (0) ..
    # top of the Top panel (HEIGHT).
    verify_footprint(
        "dresser_test", panels,
        expected=dict(
            xmin=0, xmax=params.WIDTH,
            ymin=-params.DRAWER_FRONT_OVERLAY_AMOUNT, ymax=params.DEPTH,
            zmin=0, zmax=params.HEIGHT,
        ),
    )


main()
