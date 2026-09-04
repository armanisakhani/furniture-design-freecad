"""
Single entrypoint for the whole order pipeline: parses ORDER (see
registry.py), builds each entry via its own freecadcmd subprocess
(build_item.py — one entry per process, since 2 differently configured
designs can't share one Python process, see registry.py), combines them
into one viewable .FCStd (combine_order.py), and prints the combined cut
list (order_cutlist.py).

Usage (run with the project's own .venv, for order_cutlist.py's rectpack):
    ORDER="bed:1,dresser:1,wardrobe:1" .venv/bin/python orders/run_order.py
    ORDER="dresser:1:STYLE=2,wardrobe:1:LAYOUT=two_piece" .venv/bin/python orders/run_order.py

Or just: tools/order.sh (same thing, with a default ORDER + opens the
result in FreeCAD).
"""

import os
import subprocess
import sys

_ORDERS_DIR = os.path.dirname(os.path.abspath(__file__))
if _ORDERS_DIR not in sys.path:
    sys.path.insert(0, _ORDERS_DIR)

from registry import parse_order

FREECADCMD = "/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd"


def main():
    order_spec = os.environ.get("ORDER", "bed:5,dresser:1,wardrobe:1")
    entries = parse_order(order_spec)

    for entry in entries:
        print(
            f"Building {entry['instance_key']} ({entry['name']}, qty={entry['qty']}, "
            f"overrides={entry['overrides']})...", flush=True,
        )
        env = dict(os.environ, FURNITURE=entry["name"], INSTANCE_KEY=entry["instance_key"], **entry["overrides"])
        subprocess.run([FREECADCMD, os.path.join(_ORDERS_DIR, "build_item.py")], env=env, check=True)

    print("Combining into one order...", flush=True)
    subprocess.run(
        [FREECADCMD, os.path.join(_ORDERS_DIR, "combine_order.py")],
        env=dict(os.environ, ORDER=order_spec), check=True,
    )

    print(flush=True)
    subprocess.run(
        [sys.executable, os.path.join(_ORDERS_DIR, "order_cutlist.py")],
        env=dict(os.environ, ORDER=order_spec), check=True,
    )


if __name__ == "__main__":
    main()
