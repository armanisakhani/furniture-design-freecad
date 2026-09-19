"""
Turns furniture/bed/output/panels.json (see tools/dump_panels.py) into a
sheet-buying plan: how many 1830x3660 / 1830x2440 sheets of each new-stock
color are needed, plus a plain list of the reclaimed-stock panels (no fixed
sheet size for those — cut from leftover scrap, see CONTEXT.md's
visible/stock_source concept).

Only "new" StockSource panels get nested onto sheets; "reclaimed" ones are
grouped and counted only (matched against scrap by hand at cut time).

Plain Python (project's own .venv, not freecadcmd) — nesting uses rectpack
(see requirements.txt), a pure rectangle bin-packing library. Not FreeCAD:
FreeCAD itself has no built-in cutlist/nesting tool (only third-party,
GUI-oriented addons), and this is a plain 2D rectangle bin-packing problem
with all dimensions already known as plain Python data, so a small script
against a dedicated library is simpler than fighting FreeCAD's addon layer.

Always reports 2 scenarios side by side, since BOX_SHELL_ALL_NEW (params.py)
is a real cost/logistics choice the user wants compared every time, not a
one-off setting: whether the Box shell's Bottom + 2 side walls are cut from
new stock (like Top, which is always new) or from reclaimed scrap.

Usage (see `make cutlist-bed`, which does exactly this):
    BOX_SHELL_ALL_NEW=0 PANELS_OUTPUT=furniture/bed/output/panels_top_only.json tools/dump_panels.sh
    BOX_SHELL_ALL_NEW=1 PANELS_OUTPUT=furniture/bed/output/panels_full_shell.json tools/dump_panels.sh
    .venv/bin/python tools/cutlist.py
"""

import json
import os
import sys
from collections import defaultdict

from rectpack import newPacker, SORT_AREA, MaxRectsBssf

_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BED_DIR = os.path.join(_ROOT_DIR, "furniture", "bed")
_OUTPUT_DIR = os.path.join(_BED_DIR, "output")

# MAIN_COLOR resolves identically (same env var, same swatch names) in
# every furniture/<name>/colors.py — importing bed's is just a convenient,
# already-on-disk way to read it here without duplicating the swatch table.
if _BED_DIR not in sys.path:
    sys.path.insert(0, _BED_DIR)
import colors as _bed_colors

# Always compared side by side (see module docstring) — not just the
# current PANELS_OUTPUT single-file default, kept only as an escape hatch
# for ad-hoc single-scenario runs (e.g. tests).
SCENARIOS = [
    ("فقط بالای باکس نو — Top-only", os.path.join(_OUTPUT_DIR, "panels_top_only.json")),
    ("کل بدنه‌ی باکس نو — Full shell", os.path.join(_OUTPUT_DIR, "panels_full_shell.json")),
]

# Confirmed by the user: both in-stock new colors are 16mm, plain color (no
# grain/pattern direction) — free rotation during nesting.
SHEET_SIZES = {
    "large (1830x3660)": (1830, 3660),
    "small (1830x2440)": (1830, 2440),
}

# MAIN_COLOR (colors.py's "main" role, e.g. misty) is only actually stocked
# as large (1830x3660) sheets at the workshop — small (1830x2440) isn't a
# real purchasing option for it, confirmed by the user, so it's never
# offered as a candidate for that one color specifically (every other
# new-stock color still compares both sizes normally). Rounded the same
# way group_new_stock's own dict keys are, so a direct dict lookup matches.
MAIN_COLOR_RGB = tuple(round(c, 2) for c in _bed_colors.MAIN_COLOR)

# Not measured yet (workshop unknown) — reasonable defaults per the user's
# own call ("خودت یک چیز منطقی بذار"). Revisit once the actual saw/workshop
# is known.
KERF = 3        # mm, saw blade width consumed per cut
TRIM_MARGIN = 10  # mm, unusable strip left at each sheet edge

# Reclaimed/white stock (hidden structural panels) — TBD, configurable:
# the user's own assumed default size for the white sheets these are cut
# from, so the reclaimed section can report a sheet count too instead of
# "no fixed size, from scrap."
WHITE_SHEET_SIZE = (1800, 850)

COLOR_NAMES = {
    (0.31, 0.44, 0.5): "میستی (Misty)",
    (0.43, 0.35, 0.28): "قهوه‌ای (Brown)",
    (0.78, 0.83, 0.85): "شیشه‌ی آینه (Mirror Glass)",
    (1.0, 1.0, 1.0): "سفید (White)",
    (0.59, 0.52, 0.48): "کاپوچینو (Cuppuccino)",
    (0.97, 0.97, 0.96): "مروارید (Pearl)",
    (0.79, 0.78, 0.79): "خاکستری سنگی (Shale Gray)",
}


def round_color(c):
    return tuple(round(v, 2) for v in c)


def applicable_sheet_sizes(color):
    """Every SHEET_SIZES candidate normally compared for a new-stock color
    group, except MAIN_COLOR (see MAIN_COLOR_RGB above), which only ever
    gets the large size — the workshop doesn't actually stock it as
    small sheets, so offering that as a candidate would recommend
    something not really purchasable."""
    if round_color(color) == MAIN_COLOR_RGB:
        return {name: size for name, size in SHEET_SIZES.items() if name.startswith("large")}
    return SHEET_SIZES


def load_panels(path):
    with open(path) as f:
        return json.load(f)


def group_new_stock(panels):
    """{color_tuple: [{length, width, thickness, qty, labels}]} — panels
    with identical (length, width, thickness) collapse into one row with a
    quantity, since that's what a workshop actually needs (a cut list, not
    57 separate lines). PVC edge-banding panels are skipped here — bought
    as a roll of tape, not nested onto sheets like MDF/Fiber board."""
    groups = defaultdict(lambda: defaultdict(lambda: dict(qty=0, labels=[])))
    for p in panels:
        if p["stock_source"] != "new" or p.get("material") == "PVC":
            continue
        color = round_color(p["color"])
        key = (round(p["length"], 1), round(p["width"], 1), p["thickness"])
        row = groups[color][key]
        row["qty"] += 1
        row["labels"].append(p["label"])
    return groups


def group_reclaimed(panels):
    """{material: {(length, width, thickness): {qty, labels}}} — same shape
    as group_new_stock (grouped by material instead of color), so the same
    pack_onto/utilization nesting can run per material group; different
    materials (MDF vs Fiber) don't share a sheet."""
    groups = defaultdict(lambda: defaultdict(lambda: dict(qty=0, labels=[])))
    for p in panels:
        if p["stock_source"] != "reclaimed":
            continue
        key = (round(p["length"], 1), round(p["width"], 1), p["thickness"])
        row = groups[p["material"]][key]
        row["qty"] += 1
        row["labels"].append(p["label"])
    return groups


def pack_onto(rows, sheet_w, sheet_h, kerf=KERF, margin=TRIM_MARGIN):
    """rows: {(length, width, thickness): {"qty": n, "labels": [...]}}.
    Returns (sheets_used, placements) where placements is [(sheet_index,
    x, y, w, h, rid, length, width, label)], coordinates already shifted
    back to un-inflated, margin-relative sheet space."""
    usable_w = sheet_w - 2 * margin
    usable_h = sheet_h - 2 * margin

    total_area = sum(l * w * row["qty"] for (l, w, t), row in rows.items())
    max_bins = max(4, int(total_area / (usable_w * usable_h)) + 4)

    packer = newPacker(pack_algo=MaxRectsBssf, sort_algo=SORT_AREA, rotation=True)
    packer.add_bin(usable_w, usable_h, count=max_bins)

    rid_map = {}
    next_rid = 0
    for (length, width, thickness), row in rows.items():
        # row["labels"][0]: one representative FreeCAD label for every
        # panel this row groups together (same size+color, possibly
        # different instances) — carried through so a cutting diagram can
        # show a real descriptive name per placed piece, not just its size.
        rid_map[next_rid] = (length, width, thickness, row["labels"][0])
        for _ in range(row["qty"]):
            packer.add_rect(length + kerf, width + kerf, rid=next_rid)
        next_rid += 1

    packer.pack()

    n_placed = sum(len(b) for b in packer)
    n_expected = sum(row["qty"] for row in rows.values())
    if n_placed != n_expected:
        raise RuntimeError(
            f"Only placed {n_placed}/{n_expected} rects on {sheet_w}x{sheet_h} "
            "sheets — a panel doesn't fit even a single sheet."
        )

    placements = []
    for bin_index, abin in enumerate(packer):
        for rect in abin:
            length, width, thickness, label = rid_map[rect.rid]
            placements.append((bin_index, rect.x, rect.y, rect.width - kerf, rect.height - kerf, rect.rid, length, width, label))

    return len(packer), placements


def utilization(rows, sheets_used, sheet_w, sheet_h):
    used_area = sum(l * w * row["qty"] for (l, w, t), row in rows.items())
    return used_area / (sheets_used * sheet_w * sheet_h) * 100


def split_by_fit(rows, sheet_w, sheet_h, kerf=KERF, margin=TRIM_MARGIN):
    """Splits rows into (fitting, oversized) — a panel that doesn't fit
    sheet_w x sheet_h in either orientation, even alone, would otherwise
    crash pack_onto; oversized ones are reported separately instead."""
    usable_w = sheet_w - 2 * margin
    usable_h = sheet_h - 2 * margin
    fitting, oversized = {}, {}
    for key, row in rows.items():
        length, width, thickness = key
        fits = (length + kerf <= usable_w and width + kerf <= usable_h) or (
            width + kerf <= usable_w and length + kerf <= usable_h
        )
        (fitting if fits else oversized)[key] = row
    return fitting, oversized


def oversized_reason(length, width, sheet_w, sheet_h, kerf=KERF, margin=TRIM_MARGIN):
    """Persian, math-backed explanation of why split_by_fit put this panel
    in its oversized bucket — the usable-area subtraction (margin on each
    edge) and, for both orientations, which dimension(s) still don't fit
    even after that. Used by report generation so "doesn't fit" isn't just
    a bare claim."""
    usable_w = sheet_w - 2 * margin
    usable_h = sheet_h - 2 * margin

    def orientation(a, b, usable_a, usable_b):
        need_a, need_b = a + kerf, b + kerf
        over = []
        if need_a > usable_a:
            over.append(f"طولش با کرف {need_a:.0f}mm > فضای {usable_a:.0f}mm")
        if need_b > usable_b:
            over.append(f"عرضش با کرف {need_b:.0f}mm > فضای {usable_b:.0f}mm")
        return over

    normal = orientation(length, width, usable_w, usable_h)
    rotated = orientation(width, length, usable_w, usable_h)

    return (
        f"فضای قابل‌برش ورق {sheet_w:.0f}×{sheet_h:.0f}mm پس از {margin:.0f}mm حاشیه هر لبه: "
        f"{usable_w:.0f}×{usable_h:.0f}mm. قطعه {length:.0f}×{width:.0f}mm — "
        f"بدون چرخش: {'؛ '.join(normal) if normal else 'جا می‌شود'}؛ "
        f"با چرخش ۹۰°: {'؛ '.join(rotated) if rotated else 'جا می‌شود'}."
    )


def report_scenario(scenario_name, path):
    panels = load_panels(path)
    new_groups = group_new_stock(panels)
    reclaimed = group_reclaimed(panels)

    print("#" * 70)
    print(f"# SCENARIO: {scenario_name}")
    print("#" * 70)

    print("\n" + "=" * 70)
    print("NEW STOCK — نستینگ روی ورق‌های نو")
    print("=" * 70)
    for color, rows in new_groups.items():
        name = COLOR_NAMES.get(color, str(color))
        total_qty = sum(r["qty"] for r in rows.values())
        print(f"\n--- {name} ({total_qty} panel) ---")
        for (length, width, thickness), row in sorted(rows.items()):
            print(f"  {length:>7.1f} x {width:>7.1f} x {thickness:>2.0f}mm  qty={row['qty']:<3} "
                  f"({row['labels'][0]}{' ...' if row['qty'] > 1 else ''})")

        print(f"  kerf={KERF}mm, edge trim={TRIM_MARGIN}mm/side, free rotation (solid color)")
        for sheet_name, (sw, sh) in applicable_sheet_sizes(color).items():
            n, _ = pack_onto(rows, sw, sh)
            util = utilization(rows, n, sw, sh)
            print(f"    if buying ONLY {sheet_name}: {n} sheet(s)  (~{util:.0f}% material used)")

    print("\n" + "=" * 70)
    print(f"RECLAIMED / WHITE — نستینگ روی ورق سفید {WHITE_SHEET_SIZE[0]}x{WHITE_SHEET_SIZE[1]}mm")
    print("=" * 70)
    total_reclaimed = sum(r["qty"] for rows in reclaimed.values() for r in rows.values())
    print(f"({total_reclaimed} panel total)\n")
    for material, rows in reclaimed.items():
        total_qty = sum(r["qty"] for r in rows.values())
        print(f"\n--- {material} ({total_qty} panel) ---")
        for (length, width, thickness), row in sorted(rows.items()):
            print(f"  {length:>7.1f} x {width:>7.1f} x {thickness:>2.0f}mm  qty={row['qty']:<3} "
                  f"({row['labels'][0]}{' ...' if row['qty'] > 1 else ''})")
        sw, sh = WHITE_SHEET_SIZE
        fitting, oversized = split_by_fit(rows, sw, sh)
        print(f"  kerf={KERF}mm, edge trim={TRIM_MARGIN}mm/side, free rotation")
        if fitting:
            n, _ = pack_onto(fitting, sw, sh)
            util = utilization(fitting, n, sw, sh)
            print(f"    sheets needed: {n}  (~{util:.0f}% material used)")
        if oversized:
            print(f"    doesn't fit a single {sw}x{sh}mm sheet even alone — needs bigger stock:")
            for (length, width, thickness), row in sorted(oversized.items()):
                print(f"      {length:>7.1f} x {width:>7.1f} x {thickness:>2.0f}mm  qty={row['qty']}")
    print()


def main():
    for scenario_name, path in SCENARIOS:
        report_scenario(scenario_name, path)


if __name__ == "__main__":
    main()
