"""
One-command, automated cutlist report for an ORDER: builds every entry
fresh (same steps as tools/order.sh), renders it, and writes a single
self-contained HTML report — full parts-list tables plus a real cutting-
diagram SVG for EVERY sheet, both new-stock (colored) and reclaimed/white.

Reports exactly the ONE build that ORDER describes (its own
BOX_SHELL_ALL_NEW/STYLE/LAYOUT/etc. are already baked into each item's own
panels.json) — no side-by-side "what if" scenario comparison, so the
report always matches the render/photo of that same build. Registering a
different configuration is a different ORDER run, producing its own
report.html to compare by eye.

Plain Python (project's own .venv) — only the FreeCAD build/combine/scene-
dump steps need freecadcmd; those run as subprocesses, same split as
run_order.py.

Usage:
    ORDER="dresser:1,wardrobe:1:LAYOUT=two_piece" \\
        .venv/bin/python orders/generate_report.py
    -> orders/output/report.html (+ orders/output/order_render.png)
"""

import base64
import datetime
import os
import subprocess
import sys

_ORDERS_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_ORDERS_DIR)
for _p in (_ROOT, os.path.join(_ROOT, "tools"), _ORDERS_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from registry import FURNITURE, parse_order
from order_cutlist import load_order_panels
from report_labels import translate, FA_LABELS
from svg_cutting import sheet_svg
import cutlist as shared

FREECADCMD = "/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd"
OUTPUT_DIR = os.path.join(_ORDERS_DIR, "output")
SCENE_JSON = os.path.join(OUTPUT_DIR, "order_scene.json")
RENDER_PNG = os.path.join(OUTPUT_DIR, "order_render.png")
REPORT_HTML = os.path.join(OUTPUT_DIR, "report.html")

# Always brown/misty (see the project's fixed color palette) — an
# unrecognized color (e.g. mirror glass) still renders fine, just with
# the generic "reclaimed" swatch instead of breaking report generation.
COLOR_STYLE = {
    (0.31, 0.44, 0.5): dict(css="misty", fill="var(--misty-soft)", stroke="var(--misty)"),
    (0.43, 0.35, 0.28): dict(css="brown", fill="var(--brown-soft)", stroke="var(--brown)"),
    (0.78, 0.83, 0.85): dict(css="glass", fill="var(--glass-soft)", stroke="var(--glass)"),
}
DEFAULT_STYLE = dict(css="reclaimed", fill="var(--reclaimed-soft)", stroke="var(--reclaimed)")
RECLAIMED_STYLE = dict(css="reclaimed", fill="var(--reclaimed-soft)", stroke="var(--reclaimed)")


def build_order(order_spec, entries):
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


def render_order():
    print("Rendering...", flush=True)
    subprocess.run([FREECADCMD, os.path.join(_ORDERS_DIR, "dump_order_scene.py")], check=True)
    subprocess.run(
        [sys.executable, os.path.join(_ROOT, "tools", "render_scene.py"), SCENE_JSON, RENDER_PNG],
        check=True,
    )
    with open(RENDER_PNG, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def rank_sheet_sizes(rows):
    """Every candidate size in SHEET_SIZES, ranked by utilization (least
    wasted material first) — the project's own standing rule for which
    sheet size to recommend, applied generically instead of hardcoding
    which size goes with which color."""
    candidates = []
    for sheet_name, (sw, sh) in shared.SHEET_SIZES.items():
        n, placements = shared.pack_onto(rows, sw, sh)
        util = shared.utilization(rows, n, sw, sh)
        candidates.append(dict(sheet_name=sheet_name, sw=sw, sh=sh, n=n, util=util, placements=placements))
    candidates.sort(key=lambda c: -c["util"])
    return candidates


# Panels whose (length, width) or color fell back to a generic label/style
# this run — report_labels.FA_LABELS and generate_report.COLOR_STYLE are
# both static lookup tables keyed by exact numbers seen when they were
# written, not something that auto-refreshes; a size/color tweak in some
# furniture's params.py silently drops a panel out of them instead of
# erroring, so main() prints this list as a visible warning rather than
# letting the report quietly show worse labels/colors than before.
STALE_LOOKUPS = []


def table_rows_html(rows):
    trs = []
    for (length, width, thickness), row in sorted(rows.items()):
        label = translate(length, width)
        if (round(length, 1), round(width, 1)) not in FA_LABELS:
            STALE_LOOKUPS.append(f"label ({length:.1f}×{width:.1f}): {row['labels'][0]!r} -> {label!r} (generic fallback)")
        trs.append(
            f'<tr><td class="dim mono">{length:.1f} × {width:.1f} × {thickness:.0f}</td>'
            f'<td class="qty">{row["qty"]}</td><td class="label">{label}</td></tr>'
        )
    return "\n".join(trs)


def table_html(rows, css_class):
    return (
        f'<div class="table-wrap"><table><thead class="{css_class}">'
        f'<tr><th class="dim">ابعاد (mm)</th><th>تعداد</th><th>قطعه</th></tr></thead>'
        f'<tbody>{table_rows_html(rows)}</tbody></table></div>'
    )


def diagrams_html(placements, n_sheets, sw, sh, style, group_label):
    blocks = []
    for i in range(n_sheets):
        aria = f"نقشه برش {group_label} - شیت {i + 1} از {n_sheets}"
        svg = sheet_svg(i, placements, sw, sh, style["fill"], style["stroke"], aria)
        blocks.append(
            f'<h3 class="sheet-title"><span class="swatch" style="background:{style["stroke"]};"></span>'
            f'{group_label} — ورق {i + 1} از {n_sheets} ({sw}×{sh}mm)</h3>'
            f'<div class="diagram-wrap">{svg}</div>'
        )
    return "\n".join(blocks)


def new_stock_section(new_groups):
    tiles, tables, diagrams = [], [], []
    for color, rows in new_groups.items():
        style = COLOR_STYLE.get(color, DEFAULT_STYLE)
        name = shared.COLOR_NAMES.get(color, str(color))
        if color not in COLOR_STYLE:
            STALE_LOOKUPS.append(f"color {color}: no COLOR_STYLE/COLOR_NAMES match -> generic style, shown as {name!r}")
        total_qty = sum(r["qty"] for r in rows.values())
        ranked = rank_sheet_sizes(rows)
        best = ranked[0]

        alt_lines = [
            f'<span class="mono">{c["n"]}× {c["sw"]}×{c["sh"]}</span> (~{c["util"]:.0f}%)'
            for c in ranked[1:]
        ]
        alt_html = f'<div class="tile-alt">سایر گزینه‌ها: {"، ".join(alt_lines)}</div>' if alt_lines else ""
        tiles.append(
            f'<div class="tile {style["css"]}">'
            f'<div class="tile-role"><span class="swatch"></span>{name} — {total_qty} قطعه</div>'
            f'<div class="tile-count"><span class="num">{best["n"]}</span><span class="unit">ورق</span></div>'
            f'<div class="tile-size mono">{best["sw"]} × {best["sh"]} mm · ~{best["util"]:.0f}% مصرف (کمترین دورریز)</div>'
            f'{alt_html}</div>'
        )
        tables.append(f'<h3 class="sheet-title"><span class="swatch" style="background:{style["stroke"]};"></span>{name} — {total_qty} قطعه</h3>' + table_html(rows, style["css"]))
        diagrams.append(diagrams_html(best["placements"], best["n"], best["sw"], best["sh"], style, name))

    return "\n".join(tiles), "\n".join(tables), "\n".join(diagrams)


def reclaimed_section(reclaimed):
    sw, sh = shared.WHITE_SHEET_SIZE
    tiles, tables, diagrams, oversized_html = [], [], [], []
    for material, rows in reclaimed.items():
        total_qty = sum(r["qty"] for r in rows.values())
        fitting, oversized = shared.split_by_fit(rows, sw, sh)

        tables.append(
            f'<h3 class="sheet-title"><span class="swatch" style="background:{RECLAIMED_STYLE["stroke"]};"></span>{material} — {total_qty} قطعه</h3>'
            + table_html(rows, RECLAIMED_STYLE["css"])
        )

        if fitting:
            n, placements = shared.pack_onto(fitting, sw, sh)
            util = shared.utilization(fitting, n, sw, sh)
            fit_qty = sum(r["qty"] for r in fitting.values())
            tiles.append(
                f'<div class="tile reclaimed">'
                f'<div class="tile-role"><span class="swatch"></span>{material} — {fit_qty} قطعه روی ورق سفید</div>'
                f'<div class="tile-count"><span class="num">{n}</span><span class="unit">ورق</span></div>'
                f'<div class="tile-size mono">{sw} × {sh} mm · ~{util:.0f}% مصرف</div></div>'
            )
            diagrams.append(diagrams_html(placements, n, sw, sh, RECLAIMED_STYLE, material))

        if oversized:
            rows_html = []
            for (length, width, thickness), row in sorted(oversized.items()):
                reason = shared.oversized_reason(length, width, sw, sh)
                rows_html.append(
                    f'<div class="oversize-row"><div class="oversize-dim mono">{length:.1f} × {width:.1f} × {thickness:.0f}mm '
                    f'<span class="qty">× {row["qty"]}</span></div>'
                    f'<div class="oversize-reason">{reason}</div></div>'
                )
            oversized_html.append(
                f'<div class="oversize-block"><h3 class="sheet-title">{material} — جا نمی‌شود روی ورق سفید {sw}×{sh}mm</h3>'
                + "\n".join(rows_html) + "</div>"
            )

    return "\n".join(tiles), "\n".join(tables), "\n".join(diagrams), "\n".join(oversized_html)


PAGE_CSS = """
:root{color-scheme:light}
body{margin:0;padding:0;font:14px -apple-system,BlinkMacSystemFont,sans-serif;background:#faf9f5;color:#141413}
img{max-width:100%}
:root {
  --bg: #f3ede1; --surface: #fffdf8; --ink: #241f18; --ink-soft: #6b6255;
  --line: #ded3bf; --line-strong: #c9bca3;
  --misty: #3f5c6c; --misty-soft: #e6edef;
  --brown: #6d5642; --brown-soft: #efe6dc;
  --reclaimed: #a89c85; --reclaimed-soft: #eee8dc;
  --glass: #6b8f9e; --glass-soft: #e9f1f3;
  --sheet-bg: #fbf8f1; --sheet-waste: #eee7d6;
  --warn: #a3542f; --warn-soft: #f5e4d7;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #16140f; --surface: #211d16; --ink: #f1ebdc; --ink-soft: #b4a894;
    --line: #3c3527; --line-strong: #4f4531;
    --misty: #8fb2c3; --misty-soft: #232d32;
    --brown: #c9a583; --brown-soft: #362c22;
    --reclaimed: #b9ac8f; --reclaimed-soft: #2c2718;
    --glass: #9fc4d3; --glass-soft: #202b2e;
    --sheet-bg: #221e16; --sheet-waste: #2a2519;
    --warn: #d38e64; --warn-soft: #362317;
  }
}
:root[data-theme="dark"] {
  --bg: #16140f; --surface: #211d16; --ink: #f1ebdc; --ink-soft: #b4a894;
  --line: #3c3527; --line-strong: #4f4531;
  --misty: #8fb2c3; --misty-soft: #232d32;
  --brown: #c9a583; --brown-soft: #362c22;
  --reclaimed: #b9ac8f; --reclaimed-soft: #2c2718;
  --glass: #9fc4d3; --glass-soft: #202b2e;
  --sheet-bg: #221e16; --sheet-waste: #2a2519;
  --warn: #d38e64; --warn-soft: #362317;
}
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--ink); font-family: "Vazirmatn", "Tahoma", sans-serif; direction: rtl; padding: 48px 20px 80px; }
.page { max-width: 960px; margin: 0 auto; display: flex; flex-direction: column; gap: 40px; }
.mono { font-family: "JetBrains Mono", ui-monospace, monospace; font-variant-numeric: tabular-nums; direction: ltr; unicode-bidi: isolate; }
header { display: flex; flex-direction: column; gap: 10px; border-bottom: 2px solid var(--line-strong); padding-bottom: 28px; }
.eyebrow { font-family: "JetBrains Mono", monospace; font-size: 12.5px; letter-spacing: 0.06em; color: var(--ink-soft); direction: ltr; text-align: right; }
h1 { margin: 0; font-size: clamp(28px, 4vw, 38px); font-weight: 800; text-wrap: balance; line-height: 1.25; }
.lede { margin: 0; max-width: 66ch; color: var(--ink-soft); font-size: 16px; line-height: 1.9; }
.lede b { color: var(--ink); font-weight: 600; }
.render-wrap { background: var(--surface); border: 1px solid var(--line); border-radius: 4px; padding: 20px; display: flex; flex-direction: column; align-items: center; gap: 12px; }
.render-wrap img { width: 100%; max-width: 720px; }
.render-caption { font-size: 13px; color: var(--ink-soft); text-align: center; }
.summary { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 620px) { .summary { grid-template-columns: 1fr; } }
.tile { background: var(--surface); border: 1px solid var(--line); border-radius: 4px; padding: 22px 24px; display: flex; flex-direction: column; gap: 10px; position: relative; overflow: hidden; }
.tile::before { content: ""; position: absolute; inset-inline-start: 0; top: 0; bottom: 0; width: 5px; background: var(--accent); }
.tile.misty { --accent: var(--misty); } .tile.brown { --accent: var(--brown); } .tile.reclaimed { --accent: var(--reclaimed); } .tile.glass { --accent: var(--glass); }
.tile-role { font-size: 13.5px; color: var(--ink-soft); }
.swatch { display: inline-block; width: 11px; height: 11px; border-radius: 2px; background: var(--accent); margin-inline-end: 6px; vertical-align: -1px; }
.tile-count { display: flex; align-items: baseline; gap: 8px; }
.tile-count .num { font-family: "JetBrains Mono", monospace; font-size: 40px; font-weight: 700; color: var(--accent); line-height: 1; }
.tile-count .unit { font-size: 15px; color: var(--ink-soft); }
.tile-size { font-size: 14px; text-align: right; color: var(--ink); }
.tile-alt { font-size: 12.5px; color: var(--ink-soft); border-top: 1px dashed var(--line); padding-top: 8px; line-height: 1.7; }
section h2 { font-size: 20px; font-weight: 700; margin: 0 0 4px; }
section .section-note { margin: 0 0 18px; color: var(--ink-soft); font-size: 14.5px; line-height: 1.8; max-width: 68ch; }
.legend { display: flex; flex-wrap: wrap; gap: 8px 20px; font-size: 13px; color: var(--ink-soft); background: var(--surface); border: 1px solid var(--line); border-radius: 4px; padding: 12px 16px; margin-bottom: 20px; }
.diagram-wrap { background: var(--surface); border: 1px solid var(--line); border-radius: 4px; padding: 20px; overflow-x: auto; }
.diagram-wrap svg { display: block; margin: 0 auto; width: 1500px; max-width: none; height: 750px; }
h3.sheet-title { font-size: 15px; font-weight: 600; margin: 32px 0 10px; display: flex; align-items: center; gap: 8px; }
h3.sheet-title:first-of-type { margin-top: 0; }
.table-wrap { overflow-x: auto; background: var(--surface); border: 1px solid var(--line); border-radius: 4px; }
table { width: 100%; border-collapse: collapse; font-size: 14.5px; min-width: 560px; }
thead th { text-align: start; font-weight: 600; font-size: 12.5px; letter-spacing: 0.02em; color: var(--ink-soft); padding: 12px 16px; border-bottom: 1px solid var(--line-strong); }
thead.misty th { background: var(--misty-soft); } thead.brown th { background: var(--brown-soft); } thead.reclaimed th { background: var(--reclaimed-soft); } thead.glass th { background: var(--glass-soft); }
tbody td { padding: 12px 16px; border-bottom: 1px solid var(--line); }
tbody tr:last-child td { border-bottom: none; }
td.dim, th.dim { direction: ltr; text-align: right; }
td.qty { font-family: "JetBrains Mono", monospace; font-weight: 600; }
td.label { color: var(--ink-soft); font-size: 13.5px; }
.oversize-block { background: var(--warn-soft); border: 1px solid var(--warn); border-radius: 4px; padding: 16px 20px; margin-top: 14px; }
.oversize-row { padding: 10px 0; border-bottom: 1px dashed var(--line); }
.oversize-row:last-child { border-bottom: none; }
.oversize-dim { font-weight: 700; color: var(--warn); }
.oversize-dim .qty { font-weight: 600; color: var(--ink-soft); margin-inline-start: 8px; }
.oversize-reason { font-size: 13px; color: var(--ink-soft); line-height: 1.8; margin-top: 4px; }
footer { border-top: 1px solid var(--line); padding-top: 20px; font-size: 13px; color: var(--ink-soft); line-height: 2; }
footer code { font-family: "JetBrains Mono", monospace; background: var(--reclaimed-soft); padding: 1px 6px; border-radius: 3px; font-size: 12px; direction: ltr; unicode-bidi: isolate; }
"""


def render_html(order_spec, entries, panels, render_b64, new_groups, reclaimed):
    item_summary = "، ".join(f'{FURNITURE[e["name"]]["label"]} × {e["qty"]}' for e in entries)
    new_tiles, new_tables, new_diagrams = new_stock_section(new_groups)
    rec_tiles, rec_tables, rec_diagrams, rec_oversized = reclaimed_section(reclaimed)
    total_new = sum(r["qty"] for rows in new_groups.values() for r in rows.values())
    total_reclaimed = sum(r["qty"] for rows in reclaimed.values() for r in rows.values())
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    return f"""<!doctype html><html><head><meta charset=utf8><meta name=viewport content="width=device-width,initial-scale=1">
<title>گزارش برش — {item_summary}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{PAGE_CSS}</style></head><body>
<div class="page">
  <header>
    <div class="eyebrow">ORDER · {order_spec}</div>
    <h1>گزارش برش و لیست قطعات — {item_summary}</h1>
    <p class="lede">
      {len(panels)} قطعه‌ی روی ورق ({total_new} از ورق نو، {total_reclaimed} از اسکرپ/ورق سفید بازیافتی) —
      دقیقاً همین سفارش، همین‌طور که ثبت و ساخته شده؛ بدون مقایسه‌ی حالت‌های دیگر.
      برای پیکربندی دیگر، همین سفارش را با تنظیمات دیگر دوباره ثبت و اجرا کنید.
    </p>
  </header>

  <div class="render-wrap">
    <img src="data:image/png;base64,{render_b64}" alt="رندر مستقیم از مدل واقعی FreeCAD همین سفارش" />
    <p class="render-caption">رندر مستقیم از <code class="mono">orders/output/order.FCStd</code> همین سفارش — نه یک طرح دستی.</p>
  </div>

  <section>
    <h2>خلاصه‌ی خرید ورق نو</h2>
    <p class="section-note">اندازه‌ی پیشنهادی هر رنگ، اندازه‌ای‌ست با کمترین دورریز (نه لزوماً کمترین تعداد ورق).</p>
    <div class="summary">{new_tiles}</div>
  </section>

  <section>
    <h2>خلاصه‌ی ورق سفید / بازیافتی ({shared.WHITE_SHEET_SIZE[0]}×{shared.WHITE_SHEET_SIZE[1]}mm)</h2>
    <p class="section-note">قطعات پنهان بدنه — کف، دیواره‌ی داخلی کشو، پشت‌ها؛ به تفکیک جنس (چون دو جنس روی یک ورق نمی‌شینند).</p>
    <div class="summary">{rec_tiles}</div>
    {rec_oversized}
  </section>

  <section>
    <h2>لیست قطعات — ورق نو</h2>
    {new_tables}
  </section>

  <section>
    <h2>لیست قطعات — ورق سفید / بازیافتی</h2>
    {rec_tables}
  </section>

  <section>
    <h2>نقشه‌ی برش — ورق نو</h2>
    <div class="legend">
      <span class="mono">کِرف اره: {shared.KERF}mm</span>
      <span><span class="mono">حاشیه لبه: {shared.TRIM_MARGIN}mm</span> هر طرف</span>
      <span>چرخش قطعه: آزاد (رنگ یک‌دست)</span>
    </div>
    {new_diagrams}
  </section>

  <section>
    <h2>نقشه‌ی برش — ورق سفید / بازیافتی</h2>
    <div class="legend">
      <span class="mono">کِرف اره: {shared.KERF}mm</span>
      <span><span class="mono">حاشیه لبه: {shared.TRIM_MARGIN}mm</span> هر طرف</span>
      <span>چرخش قطعه: آزاد</span>
    </div>
    {rec_diagrams}
  </section>

  <footer>
    سفارش: <code>{order_spec}</code> · تولید خودکار در {now} ·
    <code>orders/generate_report.py</code>
  </footer>
</div>
</body></html>
"""


def main():
    order_spec = os.environ.get("ORDER", "bed:1,dresser:1,wardrobe:1")
    entries = parse_order(order_spec)

    build_order(order_spec, entries)
    render_b64 = render_order()

    panels = load_order_panels(entries)
    new_groups = shared.group_new_stock(panels)
    reclaimed = shared.group_reclaimed(panels)

    html = render_html(order_spec, entries, panels, render_b64, new_groups, reclaimed)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(REPORT_HTML, "w") as f:
        f.write(html)
    print(f"\nWrote {REPORT_HTML} ({len(panels)} panels)")

    if STALE_LOOKUPS:
        print(
            f"\nWARNING: {len(STALE_LOOKUPS)} panel(s) fell back to a generic label/style "
            "(report_labels.FA_LABELS / generate_report.COLOR_STYLE didn't recognize their "
            "exact size/color — likely a param changed since those tables were last updated):"
        )
        for line in STALE_LOOKUPS:
            print(f"  - {line}")


if __name__ == "__main__":
    main()
