"""
Combines every order entry's already-built .FCStd (build_item.py, one per
entry) into one "Order" document, laid out side by side along X with a
gap. Reads the entry list from the ORDER_NAME named order (orders/specs/
<name>.yaml, see registry.load_order) to know each entry's own
instance_key/qty/flip.

Usage: ORDER_NAME=default freecadcmd orders/combine_order.py
"""

import os
import sys

_ORDERS_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_ORDERS_DIR)
for _p in (_ROOT, _ORDERS_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import FreeCAD as App

from registry import FURNITURE, load_order, order_paths, item_paths
from core.verify import combined_bbox

GAP = 300  # mm between items, TBD — default; an entry's own "gap_after"
           # key (see registry.load_order) replaces this for the space
           # added after that entry's own copies, e.g. a dresser item with
           # gap_after: 0 butts the next item flush against it (touching).
FLIP_ROTATION = App.Rotation(App.Vector(0, 0, 1), 180)


def main():
    order_name = os.environ.get("ORDER_NAME")
    if not order_name:
        raise SystemExit("Set ORDER_NAME to a name under orders/specs/ (e.g. ORDER_NAME=default)")
    order = load_order(order_name)
    entries = order["entries"]
    output_file = order_paths(order_name)["fcstd"]

    combined_doc = App.newDocument("Order")
    x_offset = 0.0

    for entry in entries:
        paths = item_paths(order_name, entry["instance_key"])
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
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    combined_doc.saveAs(output_file)
    print(f"Created {output_file}: {len(combined_doc.Objects)} objects")


main()
