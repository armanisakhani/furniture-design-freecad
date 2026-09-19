"""
Single entrypoint for the whole order pipeline: loads a named order
(orders/specs/<name>.yaml, see registry.load_order), builds each entry via
its own freecadcmd subprocess (build_item.py — one entry per process, since
2 differently configured designs can't share one Python process, see
registry.py), combines them into one viewable .FCStd (combine_order.py),
and prints the combined cut list (order_cutlist.py). Every output lands
under orders/output/<name>/, so 2 named orders never collide.

Usage (run with the project's own .venv, for order_cutlist.py's rectpack):
    .venv/bin/python orders/run_order.py default
    .venv/bin/python orders/run_order.py winter-bedroom

Or just: tools/order.sh <name> (same thing, with a default name + opens the
result in FreeCAD).
"""

import os
import subprocess
import sys

_ORDERS_DIR = os.path.dirname(os.path.abspath(__file__))
if _ORDERS_DIR not in sys.path:
    sys.path.insert(0, _ORDERS_DIR)

from registry import load_order, require_item_built

FREECADCMD = "/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd"


def main():
    if len(sys.argv) != 2:
        raise SystemExit(f"Usage: {sys.argv[0]} <order name>  (a file under orders/specs/)")
    order_name = sys.argv[1]
    order = load_order(order_name)

    for entry in order["entries"]:
        print(
            f"Building {entry['instance_key']} ({entry['name']}, qty={entry['qty']}, "
            f"overrides={entry['overrides']})...", flush=True,
        )
        env = dict(
            os.environ, **order["env"],
            FURNITURE=entry["name"], INSTANCE_KEY=entry["instance_key"], ORDER_NAME=order_name,
            **entry["overrides"],
        )
        subprocess.run([FREECADCMD, os.path.join(_ORDERS_DIR, "build_item.py")], env=env, check=True)
        require_item_built(order_name, entry)

    print("Combining into one order...", flush=True)
    subprocess.run(
        [FREECADCMD, os.path.join(_ORDERS_DIR, "combine_order.py")],
        env=dict(os.environ, ORDER_NAME=order_name), check=True,
    )

    print(flush=True)
    subprocess.run(
        [sys.executable, os.path.join(_ORDERS_DIR, "order_cutlist.py")],
        env=dict(os.environ, ORDER_NAME=order_name), check=True,
    )


if __name__ == "__main__":
    main()
