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
    expected = 7 + (5 if params.HAS_SHELF else 0)  # Top + 6 drawer pieces, + shelf + 4 legs
    print(f"Created {OUTPUT_FILE}: {len(panels)} panels (expected {expected})")
    assert len(panels) == expected

    zmax = params.HEIGHT
    if params.HAS_SHELF:
        zmax += params.SHELF_LEG_HEIGHT + params.SHELF_THICKNESS
    verify_footprint(
        "tv_table_test", panels,
        dict(
            xmin=0, xmax=params.FRONT_WIDTH,
            ymin=-params.FACE_THICKNESS, ymax=params.DEPTH,
            zmin=0, zmax=zmax,
        ),
    )

    by_name = {p.Name: p for p in panels}
    top = by_name["Top"]
    drawer = [n for n in by_name if n.startswith("Drawer_")]
    names = ["Top"] + drawer + [n for n in by_name if n.startswith("Shelf")]
    pairs = [(a, b) for i, a in enumerate(names) for b in names[i + 1:]]
    for a, b in pairs:
        volume = by_name[a].Shape.common(by_name[b].Shape).Volume
        ok = volume < 1.0
        print(f"  [{'PASS' if ok else 'FAIL'}] {a} x {b} overlap volume {volume:.1f} mm^3")
        assert ok, f"{a} overlaps {b} by {volume:.1f} mm^3"

    # The drawer box must stay under the Top's own footprint (it's as wide
    # as the trapezoid's short side), and below its underside.
    dbb = combined = by_name["Drawer_Bottom"].Shape.BoundBox
    for n in drawer:
        if n != "Drawer_Face":
            bb = by_name[n].Shape.BoundBox
            assert bb.ZMax <= top.Shape.BoundBox.ZMin + 1e-3, f"{n} pokes into the Top"
            for cx in (bb.XMin, bb.XMax):
                for cy in (bb.YMin, bb.YMax):
                    assert top.Shape.isInside(App.Vector(cx, cy, top.Shape.BoundBox.ZMax - 1), 1e-6, True), f"{n} sticks out from under the Top"

    if params.HAS_SHELF:
        shelf = by_name["Shelf"]
        legs = [n for n in by_name if n.startswith("ShelfLeg")]
        assert len(legs) == 4
        for leg in legs:
            lb = by_name[leg].Shape.BoundBox
            assert abs(lb.ZMin - top.Shape.BoundBox.ZMax) < 1e-3, f"{leg} not resting on Top"
            assert abs(lb.ZMax - shelf.Shape.BoundBox.ZMin) < 1e-3, f"{leg} doesn't reach the shelf"
            for cx in (lb.XMin, lb.XMax):
                for cy in (lb.YMin, lb.YMax):
                    assert top.Shape.isInside(App.Vector(cx, cy, top.Shape.BoundBox.ZMax - 1), 1e-6, True), f"{leg} hangs off the Top"
    print("tv_table_test: all checks passed")


main()
