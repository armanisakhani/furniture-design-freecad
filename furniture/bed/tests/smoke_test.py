"""
Phase 0 smoke test.

Purpose: confirm the toolchain works end to end — running this script with
FreeCAD's own Python (via freecadcmd) creates a FreeCAD document with one box,
saves it as a .FCStd file, and that file should open correctly in the FreeCAD
GUI with the expected dimensions.

This is NOT part of the real furniture model. It uses round placeholder
numbers, not project parameters (params.py doesn't exist yet — that's Phase 1).

Coordinate convention (see plan.md): X = width, Y = depth/length, Z = height.

Note: freecadcmd runs a script with __name__ set to the script's filename,
not "__main__" — so we call main() unconditionally rather than relying on
the usual `if __name__ == "__main__":` guard.
"""

import os

import FreeCAD as App
import Part

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "smoke_test.FCStd")

# Round placeholder dimensions, just to make X vs Y vs Z visually obvious.
BOX_WIDTH = 400.0   # X
BOX_DEPTH = 300.0   # Y
BOX_HEIGHT = 18.0   # Z


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    doc = App.newDocument("Phase0SmokeTest")

    box = doc.addObject("Part::Box", "SmokeTestBox")
    box.Length = BOX_WIDTH   # FreeCAD Part::Box: Length along X
    box.Width = BOX_DEPTH    # Width along Y
    box.Height = BOX_HEIGHT  # Height along Z

    doc.recompute()
    doc.saveAs(OUTPUT_FILE)

    print(f"Created {OUTPUT_FILE}")
    print(f"Box dimensions (X, Y, Z) = ({box.Length.Value}, {box.Width.Value}, {box.Height.Value})")


main()

