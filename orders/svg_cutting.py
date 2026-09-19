"""
Renders one rectpack sheet (tools/cutlist.py's pack_onto placements) as a
real-scale SVG cutting diagram — the same visual style used across this
project's cutlist reports. Always displays the sheet long-side horizontal
(landscape), regardless of which raw axis pack_onto used, since a
narrow/long sheet reads better that way.
"""

from report_labels import translate


def _font_for(w, h):
    m = min(w, h)
    if m >= 500:
        return 40
    if m >= 300:
        return 32
    if m >= 150:
        return 23
    return 14


def sheet_svg(bin_index, placements, sheet_w, sheet_h, fill_var, stroke_var, aria_label):
    """placements: pack_onto's own return value (list of (bin_index, x, y,
    w, h, rid, length, width, label)) — draws only the ones on bin_index."""
    transpose = sheet_w < sheet_h
    disp_w, disp_h = (sheet_h, sheet_w) if transpose else (sheet_w, sheet_h)
    parts = [
        f'<svg viewBox="0 0 {disp_w} {disp_h}" width="1500" '
        f'height="{round(1500 * disp_h / disp_w)}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="{aria_label}">',
        f'<rect x="0" y="0" width="{disp_w}" height="{disp_h}" fill="var(--sheet-waste)" />',
        f'<rect x="10" y="10" width="{disp_w - 20}" height="{disp_h - 20}" '
        f'fill="var(--sheet-bg)" stroke="var(--line-strong)" stroke-width="4" stroke-dasharray="14 10" />',
    ]
    for (bi, x, y, w, h, rid, length, width, raw_label) in placements:
        if bi != bin_index:
            continue
        dx, dy, dw, dh = (y, x, h, w) if transpose else (x, y, w, h)
        label = translate(raw_label, length, width)
        cx, cy = dx + dw / 2, dy + dh / 2
        fs = _font_for(dw, dh)
        rotate = dw < dh
        tf = f' transform="rotate(-90 {cx:.1f} {cy:.1f})"' if rotate else ""
        parts.append(
            f'<g>\n  <rect x="{dx:.1f}" y="{dy:.1f}" width="{dw:.1f}" height="{dh:.1f}" '
            f'fill="{fill_var}" stroke="{stroke_var}" stroke-width="4" />\n'
            f'  <text x="{cx:.1f}" y="{cy - fs * 0.3:.1f}" text-anchor="middle"{tf} '
            f'font-family="Vazirmatn" font-size="{fs}" font-weight="700" fill="var(--ink)">{label}</text>\n'
            f'  <text x="{cx:.1f}" y="{cy + fs * 0.55:.1f}" text-anchor="middle"{tf} '
            f'font-family="JetBrains Mono" font-size="{int(fs * 0.72)}" '
            f'fill="var(--ink-soft)">{length:.1f} × {width:.1f}</text>\n</g>'
        )
    parts.append("</svg>")
    return "\n".join(parts)
