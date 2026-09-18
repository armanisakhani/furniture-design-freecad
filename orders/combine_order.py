"""
Combines every order entry's already-built .FCStd (build_item.py, one per
entry) into one "Order" document, laid out side by side along X with a
gap. Reads the entry list from ORDER (same spec as registry.parse_order)
to know each entry's own instance_key/qty/flip.

Usage: ORDER="bed:1,dresser:2:STYLE=2" freecadcmd orders/combine_order.py
"""

import os
import sys

_ORDERS_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_ORDERS_DIR)
for _p in (_ROOT, _ORDERS_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import FreeCAD as App

from registry import FURNITURE, parse_order, item_paths
from core.verify import combined_bbox

OUTPUT_FILE = os.path.join(_ORDERS_DIR, "output", "order.FCStd")
GAP = 300  # mm between items, TBD — default; an entry's own "GAP" override
           # (see registry.parse_order) replaces this for the space added
           # after that entry's own copies, e.g. "dresser:1:GAP=0,wardrobe:1"
           # butts the wardrobe flush against the dresser (0mm, touching).
FLIP_ROTATION = App.Rotation(App.Vector(0, 0, 1), 180)


def main():
    entries = parse_order(os.environ.get("ORDER", "bed:1,dresser:1,wardrobe:1"))

    combined_doc = App.newDocument("Order")
    x_offset = 0.0

    for entry in entries:
        paths = item_paths(entry["instance_key"])
        if not os.path.exists(paths["fcstd"]):
            raise SystemExit(f"{paths['fcstd']} doesn't exist yet — run orders/run_order.py first.")

        source_doc = App.openDocument(paths["fcstd"])
        source_doc.recompute()
        source_objs = [o for o in source_doc.Objects if hasattr(o, "Shape")]

        rotation = FLIP_ROTATION if FURNITURE[entry["name"]]["flip"] else App.Rotation()

        for _ in range(entry["qty"]):
            copies = combined_doc.copyObject(source_objs, True)
            # Apply the flip (if any) about the world origin first, then
            # re-measure the bbox — a plain rotation changes which local
            # coordinates end up where, so the old (pre-rotation) bbox
            # can't be reused for the shift below.
            for obj in copies:
                obj.Placement = App.Placement(App.Vector(0, 0, 0), rotation).multiply(obj.Placement)
            # Accessories meant to overhang past the item's own body (e.g.
            # the wardrobe's side shelves, which float above a neighboring
            # item on purpose) don't count toward alignment/spacing — only
            # the item's own footprint does, or "touching" would leave a
            # real gap the width of the overhang.
            footprint_copies = [o for o in copies if "Side Shelf" not in (o.Label or "")]
            bbox = combined_bbox(footprint_copies or copies)
            # Y=0 is the shared "wall": every item's own BACK (its own
            # bbox.YMax — the Back panel for dresser/wardrobe, the
            # headboard for a flipped bed) lands there, with its front
            # protruding toward -Y by its own depth. Aligns backs against
            # one wall, like real furniture, instead of aligning fronts
            # (which left the bed's headboard sticking out past everyone
            # else's own back).
            shift = App.Vector(x_offset - bbox.XMin, -bbox.YMax, 0)
            for obj in copies:
                obj.Placement = App.Placement(obj.Placement.Base + shift, obj.Placement.Rotation)
            gap = GAP if entry["gap_after"] is None else entry["gap_after"]
            x_offset += bbox.XLength + gap

        App.closeDocument(source_doc.Name)

    combined_doc.recompute()
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    combined_doc.saveAs(OUTPUT_FILE)
    print(f"Created {OUTPUT_FILE}: {len(combined_doc.Objects)} objects")


main()
