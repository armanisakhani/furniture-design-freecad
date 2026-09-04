"""
First-draft build/verify script for the wardrobe (کمد لباس) — a hanging
compartment (2 doors, 1 rod) over a DRAWER_COUNT-drawer section. See
furniture/dresser/tests/dresser_test.py for the pattern this follows.

Note: freecadcmd runs a script with __name__ set to the script's
filename, not "__main__" — call main() unconditionally.
"""

import os
import sys

# freecadcmd doesn't know this project's own package layout — put this
# furniture module's own directory (for params/wardrobe) and the repo root
# (for core/) on sys.path before any project-local import.
_WARDROBE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ROOT_DIR = os.path.dirname(os.path.dirname(_WARDROBE_DIR))
for _p in (_ROOT_DIR, _WARDROBE_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import FreeCAD as App

import params
from wardrobe import create_wardrobe
from core.verify import verify_footprint

OUTPUT_DIR = os.path.join(_WARDROBE_DIR, "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "wardrobe_test.FCStd")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    doc = App.newDocument("WardrobeTest")

    panels = create_wardrobe(doc)
    doc.recompute()
    doc.saveAs(OUTPUT_FILE)

    non_drawer_panels = 15 if params.LAYOUT == "one_piece" else 19
    height = params.ONE_PIECE_HEIGHT if params.LAYOUT == "one_piece" else params.TWO_PIECE_HEIGHT

    print(f"Created {OUTPUT_FILE} (LAYOUT={params.LAYOUT!r})")
    print(
        f"Total panels: {len(panels)} "
        f"(expected {non_drawer_panels} shell/rod/top/doors/door-handles + {params.DRAWER_COUNT} x 9 drawer)"
    )

    # X: 0..WIDTH. Y: each drawer's metal handle is the furthest-forward
    # feature, protruding to -(HANDLE_STANDOFF + HANDLE_BAR_SIZE); DEPTH is
    # the furthest back. Z: floor (0, no raised base) to the top surface.
    verify_footprint(
        "wardrobe_test", panels,
        expected=dict(
            xmin=0, xmax=params.WIDTH,
            ymin=-(params.HANDLE_STANDOFF + params.HANDLE_BAR_SIZE), ymax=params.DEPTH,
            zmin=0, zmax=height,
        ),
    )


main()
