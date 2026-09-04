"""
Combined sheet-buying plan for a whole ORDER (e.g. "bed:1,dresser:1,
wardrobe:1") — same nesting logic as tools/cutlist.py (which reports one
furniture design alone), fed one merged panel list across every ordered
item instead. Sourced from each entry's own build_item.py output (see
registry.py), repeated per its own quantity. Metal hardware (handles, the
wardrobe's rod) is excluded — it's bought, not cut from a sheet.

Plain Python (project's own .venv, not freecadcmd) — see tools/cutlist.py's
own docstring for why this half of the pipeline doesn't need FreeCAD.

Usage (see tools/order.sh, which does exactly this via run_order.py):
    ORDER="bed:1,dresser:2:STYLE=2" .venv/bin/python orders/run_order.py
"""

import json
import os
import sys

_ORDERS_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_ORDERS_DIR)
for _p in (_ROOT, os.path.join(_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from registry import FURNITURE, parse_order, item_paths
import cutlist as shared  # tools/cutlist.py's own nesting helpers


def load_order_panels(entries):
    """Returns one combined panel list — each entry's own dumped panels
    repeated `qty` times, labels tagged with an instance number so the
    report can tell them apart, Metal hardware dropped (not sheet stock)."""
    combined = []
    for entry in entries:
        with open(item_paths(entry["instance_key"])["panels_json"]) as f:
            panels = [p for p in json.load(f) if p["material"] != "Metal"]
        label = FURNITURE[entry["name"]]["label"]
        for instance in range(1, entry["qty"] + 1):
            suffix = f" [{label} #{instance}]" if entry["qty"] > 1 else f" [{label}]"
            for p in panels:
                combined.append({**p, "label": p["label"] + suffix})
    return combined


def main():
    entries = parse_order(os.environ.get("ORDER", ""))
    panels = load_order_panels(entries)

    summary = ", ".join(f"{e['name']} x{e['qty']}" for e in entries)
    print(f"Order: {summary} — {len(panels)} sheet panels total\n")

    new_groups = shared.group_new_stock(panels)
    reclaimed = shared.group_reclaimed(panels)

    print("=" * 70)
    print("NEW STOCK — نستینگ روی ورق‌های نو (کل سفارش)")
    print("=" * 70)
    for color, rows in new_groups.items():
        name = shared.COLOR_NAMES.get(color, str(color))
        total_qty = sum(r["qty"] for r in rows.values())
        print(f"\n--- {name} ({total_qty} panel) ---")
        for (length, width, thickness), row in sorted(rows.items()):
            print(f"  {length:>7.1f} x {width:>7.1f} x {thickness:>2.0f}mm  qty={row['qty']:<3} "
                  f"({row['labels'][0]}{' ...' if row['qty'] > 1 else ''})")
        print(f"  kerf={shared.KERF}mm, edge trim={shared.TRIM_MARGIN}mm/side, free rotation (solid color)")
        for sheet_name, (sw, sh) in shared.SHEET_SIZES.items():
            n, _ = shared.pack_onto(rows, sw, sh)
            util = shared.utilization(rows, n, sw, sh)
            print(f"    if buying ONLY {sheet_name}: {n} sheet(s)  (~{util:.0f}% material used)")

    print("\n" + "=" * 70)
    print("RECLAIMED / WHITE — بدون سایز ثابت، از اسکرپ موجود")
    print("=" * 70)
    total_reclaimed = sum(r["qty"] for r in reclaimed.values())
    print(f"({total_reclaimed} panel total)\n")
    for (length, width, thickness, material), row in sorted(reclaimed.items(), key=lambda kv: -kv[1]["qty"]):
        print(f"  {length:>7.1f} x {width:>7.1f} x {thickness:>2.0f}mm  {material:<6} qty={row['qty']:<3} "
              f"({row['labels'][0]}{' ...' if row['qty'] > 1 else ''})")


if __name__ == "__main__":
    main()
