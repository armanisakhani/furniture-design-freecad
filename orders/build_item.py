"""
Builds ONE order entry (one furniture type, with its own STYLE/LAYOUT/etc.
overrides already set as environment variables by run_order.py) and saves
both its .FCStd (for combine_order.py) and its panels.json (for
cutlist.py) under output/items/ (see registry.py's item_paths). One entry
per process — see registry.py's own docstring for why.

Usage: FURNITURE=dresser INSTANCE_KEY=dresser-1 STYLE=2 freecadcmd orders/build_item.py
"""

import importlib
import json
import os
import sys

_ORDERS_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_ORDERS_DIR)
for _p in (_ROOT, _ORDERS_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from registry import FURNITURE, item_paths

import FreeCAD as App

NAME = os.environ.get("FURNITURE")
INSTANCE_KEY = os.environ.get("INSTANCE_KEY")
if NAME not in FURNITURE or not INSTANCE_KEY:
    raise SystemExit(f"Set FURNITURE to one of {sorted(FURNITURE)} and INSTANCE_KEY")

INFO = FURNITURE[NAME]
if INFO["dir"] not in sys.path:
    sys.path.insert(0, INFO["dir"])

_module = importlib.import_module(NAME)  # furniture/<name>/<name>.py
_create = getattr(_module, f"create_{NAME}")


def main():
    doc = App.newDocument("OrderItem")
    result = _create(doc)
    panels = result[0] if isinstance(result, tuple) else result  # bed returns (panels, mattress)
    doc.recompute()

    paths = item_paths(INSTANCE_KEY)
    os.makedirs(os.path.dirname(paths["fcstd"]), exist_ok=True)
    doc.saveAs(paths["fcstd"])

    data = [
        dict(
            name=p.Name, label=p.Label,
            length=p.Length.Value, width=p.Width.Value, thickness=p.Thickness.Value,
            material=p.Material, stock_source=p.StockSource, color=list(p.PanelColor)[:3],
        )
        for p in panels
    ]
    with open(paths["panels_json"], "w") as f:
        json.dump(data, f, indent=2)

    print(f"Built {INSTANCE_KEY} ({NAME}): {len(data)} panels -> {paths['fcstd']}")


main()
