"""
Build/verify script for the TV table (میز تلویزیون). Same pattern as
furniture/dresser/tests/dresser_test.py: freecadcmd runs this with
__name__ set to the filename, so main() is called unconditionally.
"""

import os
import sys

_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ROOT_DIR = os.path.dirname(os.path.dirname(_DIR))
for _p in (_ROOT_DIR, _DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import FreeCAD as App

import params
from tv_table import create_tv_table
from core.verify import verify_footprint

OUTPUT_DIR = os.path.join(_DIR, "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "tv_table_test.FCStd")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    doc = App.newDocument("TvTableTest")
    panels = create_tv_table(doc)
    doc.recompute()
    doc.saveAs(OUTPUT_FILE)
    print(f"Created {OUTPUT_FILE}: {len(panels)} panels (expected 2 + 2 + 1 + 5 drawer pieces + 1 face = 11 incl. face)")
    assert len(panels) == 11

    verify_footprint(
        "tv_table_test", panels,
        dict(
            xmin=0, xmax=params.FRONT_WIDTH,
            ymin=-params.FACE_THICKNESS, ymax=params.DEPTH,
            zmin=0, zmax=params.HEIGHT,
        ),
    )

    by_name = {p.Name: p for p in panels}
    # Nothing structural may overlap: the 2 slanted sides vs each other
    # parts they touch, and the drawer box vs the sides/back.
    shell = ["Bottom", "Top", "Left", "Right", "Back"]
    drawer = [n for n in by_name if n.startswith("Drawer_") and n != "Drawer_Face"]
    pairs = [(a, b) for i, a in enumerate(shell) for b in shell[i + 1:]]
    pairs += [(d, s) for d in drawer for s in shell]
    pairs += [("Drawer_Face", s) for s in shell]
    for a, b in pairs:
        volume = by_name[a].Shape.common(by_name[b].Shape).Volume
        ok = volume < 1.0
        print(f"  [{'PASS' if ok else 'FAIL'}] {a} x {b} overlap volume {volume:.1f} mm^3")
        assert ok, f"{a} overlaps {b} by {volume:.1f} mm^3"

    for name in ("Left", "Right"):
        bb = by_name[name].Shape.BoundBox
        print(f"  {name}: Y[{bb.YMin:.1f},{bb.YMax:.1f}] X[{bb.XMin:.1f},{bb.XMax:.1f}]")
        assert abs(bb.YMin) < 1e-3 and abs(bb.YMax - params.DEPTH) < 1e-3
    print("tv_table_test: all checks passed")


main()
