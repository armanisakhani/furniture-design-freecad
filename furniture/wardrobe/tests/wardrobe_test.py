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

    # two_piece only: 3 side shelves (params.SIDE_SHELF_COUNT), each 1
    # shelf board + 2 brackets (front/back) x 2 legs = 5 panels/shelf,
    # plus 1 spare of the side panel they're screwed into.
    side_shelf_panels = params.SIDE_SHELF_COUNT * 5 + 1 if params.LAYOUT == "two_piece" else 0
    non_drawer_panels = (15 if params.LAYOUT == "one_piece" else 19) + side_shelf_panels
    height = params.ONE_PIECE_HEIGHT if params.LAYOUT == "one_piece" else params.TWO_PIECE_HEIGHT

    print(f"Created {OUTPUT_FILE} (LAYOUT={params.LAYOUT!r})")
    print(
        f"Total panels: {len(panels)} "
        f"(expected {non_drawer_panels} shell/rod/top/doors/door-handles/side-shelves + "
        f"{params.DRAWER_COUNT} x 9 drawer)"
    )

    # X: 0..WIDTH, except two_piece's side shelves reach SIDE_SHELF_PROJECTION
    # further out past whichever side (params.SIDE_SHELF_SIDE) they're on.
    # Y: each drawer's metal handle is the furthest-forward feature,
    # protruding to -(HANDLE_STANDOFF + HANDLE_BAR_SIZE); DEPTH is the
    # furthest back. Z: floor (0, no raised base) to the top surface.
    xmin, xmax = 0, params.WIDTH
    if params.LAYOUT == "two_piece":
        if params.SIDE_SHELF_SIDE == "right":
            xmax += params.SIDE_SHELF_PROJECTION
        else:
            xmin -= params.SIDE_SHELF_PROJECTION
    verify_footprint(
        "wardrobe_test", panels,
        expected=dict(
            xmin=xmin, xmax=xmax,
            ymin=-(params.HANDLE_STANDOFF + params.HANDLE_BAR_SIZE), ymax=params.DEPTH,
            zmin=0, zmax=height,
        ),
    )


main()
