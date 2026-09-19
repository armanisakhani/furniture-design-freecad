"""
Persian display names for cutlist report panels, keyed by the panel's own
descriptive FreeCAD label (e.g. "Drawer 2 - Face", "Box1 - Top Panel") —
NOT by its size. A label survives any dimension change (a STYLE, a WIDTH
override, a different BOX_COUNT, ...); a fixed (length, width) pair the
old version of this table used doesn't, so a knob like WIDTH that this
project explicitly supports overriding would silently break every panel's
label the moment someone actually used it.

Matching normalizes 2 things away first: any digit run in the label's own
"core" part (Box1/Drawer 2/Side Shelf 3/... all become BoxN/Drawer N/Side
Shelf N — the physical part is the same kind of thing whichever instance
it is), and the "#N" instance suffix inside a multi-quantity order's own
furniture tag (see orders/order_cutlist.py's load_order_panels — "[دراور
#2]" becomes just "دراور"). The furniture tag itself (تخت/دراور/کمد لباس)
is kept as a second, separate key, since several furniture/ modules reuse
the exact same part names (e.g. both dresser and wardrobe have their own
"Bottom Panel").

Best-effort: a label that isn't in this table still renders fine, just
with its own raw name + size as a generic fallback instead of a
translated phrase — so a new furniture feature never breaks report
generation, it just reads a bit rougher until someone adds its
translation here (generate_report.py's STALE_LOOKUPS flags exactly this).
"""

import re

# (normalized core label, furniture tag) -> Persian display name.
FA_LABELS = {
    # --- تخت (bed) ---------------------------------------------------
    ("BoxN - Bottom Panel", "تخت"): "کف جعبه (تخت)",
    ("BoxN - Top Panel", "تخت"): "پنل بالایی جعبه (تخت)",
    ("BoxN - Side Wall (Y near)", "تخت"): "دیواره‌ی کناری جعبه، نزدیک (تخت)",
    ("BoxN - Side Wall (Y far)", "تخت"): "دیواره‌ی کناری جعبه، دور (تخت)",
    ("BoxN - Drawer N - Bottom", "تخت"): "کف کشو (تخت)",
    ("BoxN - Drawer N - Side (Y near)", "تخت"): "کنار کشو، نزدیک (تخت)",
    ("BoxN - Drawer N - Side (Y far)", "تخت"): "کنار کشو، دور (تخت)",
    ("BoxN - Drawer N - Structural Front", "تخت"): "جلوی ساختاری کشو (تخت)",
    ("BoxN - Drawer N - Back", "تخت"): "پشت کشو (تخت)",
    ("BoxN - Drawer N - Face", "تخت"): "نمای کشو (تخت)",
    ("BoxN - Internal Wall (behind Drawer N)", "تخت"): "دیواره‌ی داخلی (تخت)",
    ("Mattress Stop (Foot)", "تخت"): "توقف‌گاه تشک، انتها (تخت)",
    ("Mattress Stop (Side Near)", "تخت"): "توقف‌گاه تشک، کنار نزدیک (تخت)",
    ("Mattress Stop (Side Far)", "تخت"): "توقف‌گاه تشک، کنار دور (تخت)",
    ("End Face (Foot)", "تخت"): "دیواره‌ی انتها (تخت)",
    ("Headboard (Crown)", "تخت"): "هدتخت (تخت)",

    # --- دراور (dresser) -----------------------------------------------
    ("Bottom Panel", "دراور"): "کف (دراور)",
    ("Top Panel", "دراور"): "سقف (دراور)",
    ("Left Side Panel", "دراور"): "کناره‌ی چپ (دراور)",
    ("Right Side Panel", "دراور"): "کناره‌ی راست (دراور)",
    ("Back Panel", "دراور"): "پشت (دراور)",
    ("Left - Bracket (vertical leg)", "دراور"): "نبشی چپ - پایه‌ی عمودی (دراور)",
    ("Left - Bracket (horizontal leg)", "دراور"): "نبشی چپ - پایه‌ی افقی (دراور)",
    ("Right - Bracket (vertical leg)", "دراور"): "نبشی راست - پایه‌ی عمودی (دراور)",
    ("Right - Bracket (horizontal leg)", "دراور"): "نبشی راست - پایه‌ی افقی (دراور)",
    ("Back - Bracket (vertical leg)", "دراور"): "نبشی پشت - پایه‌ی عمودی (دراور)",
    ("Back - Bracket (horizontal leg)", "دراور"): "نبشی پشت - پایه‌ی افقی (دراور)",
    ("Drawer N - Bottom", "دراور"): "کف کشو (دراور)",
    ("Drawer N - Side (left)", "دراور"): "کنار کشو، چپ (دراور)",
    ("Drawer N - Side (right)", "دراور"): "کنار کشو، راست (دراور)",
    ("Drawer N - Structural Front", "دراور"): "جلوی ساختاری کشو (دراور)",
    ("Drawer N - Back", "دراور"): "پشت کشو (دراور)",
    ("Drawer N - Face", "دراور"): "نمای کشو (دراور)",
    ("Drawer N - Handle Bar", "دراور"): "میله‌ی دستگیره‌ی کشو (دراور)",
    ("Drawer N - Handle Post (left)", "دراور"): "پایه‌ی دستگیره‌ی کشو، چپ (دراور)",
    ("Drawer N - Handle Post (right)", "دراور"): "پایه‌ی دستگیره‌ی کشو، راست (دراور)",
    ("Mirror - Top Rail", "دراور"): "قاب بالای آینه (دراور)",
    ("Mirror - Bottom Rail", "دراور"): "قاب پایین آینه (دراور)",
    ("Mirror - Left Stile", "دراور"): "قاب چپ آینه (دراور)",
    ("Mirror - Right Stile", "دراور"): "قاب راست آینه (دراور)",
    ("Mirror Pane", "دراور"): "شیشه‌ی آینه (دراور)",

    # --- کمد لباس (wardrobe) — one_piece + shared with two_piece --------
    ("Bottom Panel", "کمد لباس"): "کف (کمد لباس)",
    ("Top Panel", "کمد لباس"): "سقف (کمد لباس)",
    ("Left Side Panel", "کمد لباس"): "کناره‌ی چپ (کمد لباس)",
    ("Right Side Panel", "کمد لباس"): "کناره‌ی راست (کمد لباس)",
    ("Back Panel", "کمد لباس"): "پشت (کمد لباس)",
    ("Divider Panel", "کمد لباس"): "میان‌قاب (کمد لباس)",
    ("Door (left)", "کمد لباس"): "در چپ (کمد لباس)",
    ("Door (right)", "کمد لباس"): "در راست (کمد لباس)",
    ("Door (left) Handle Bar", "کمد لباس"): "میله‌ی دستگیره‌ی در چپ (کمد لباس)",
    ("Door (right) Handle Bar", "کمد لباس"): "میله‌ی دستگیره‌ی در راست (کمد لباس)",
    ("Door (left) Handle Post (top)", "کمد لباس"): "پایه‌ی دستگیره‌ی در چپ، بالا (کمد لباس)",
    ("Door (left) Handle Post (bottom)", "کمد لباس"): "پایه‌ی دستگیره‌ی در چپ، پایین (کمد لباس)",
    ("Door (right) Handle Post (top)", "کمد لباس"): "پایه‌ی دستگیره‌ی در راست، بالا (کمد لباس)",
    ("Door (right) Handle Post (bottom)", "کمد لباس"): "پایه‌ی دستگیره‌ی در راست، پایین (کمد لباس)",
    ("Hanging Rod", "کمد لباس"): "میله‌ی آویز (کمد لباس)",
    ("Drawer N - Bottom", "کمد لباس"): "کف کشو (کمد لباس)",
    ("Drawer N - Side (left)", "کمد لباس"): "کنار کشو، چپ (کمد لباس)",
    ("Drawer N - Side (right)", "کمد لباس"): "کنار کشو، راست (کمد لباس)",
    ("Drawer N - Structural Front", "کمد لباس"): "جلوی ساختاری کشو (کمد لباس)",
    ("Drawer N - Back", "کمد لباس"): "پشت کشو (کمد لباس)",
    ("Drawer N - Face", "کمد لباس"): "نمای کشو (کمد لباس)",
    ("Drawer N - Handle Bar", "کمد لباس"): "میله‌ی دستگیره‌ی کشو (کمد لباس)",
    ("Drawer N - Handle Post (left)", "کمد لباس"): "پایه‌ی دستگیره‌ی کشو، چپ (کمد لباس)",
    ("Drawer N - Handle Post (right)", "کمد لباس"): "پایه‌ی دستگیره‌ی کشو، راست (کمد لباس)",

    # --- کمد لباس (wardrobe) — two_piece only ---------------------------
    ("Bottom Unit - Left Side", "کمد لباس"): "کناره‌ی واحد پایین، چپ (کمد لباس)",
    ("Bottom Unit - Right Side", "کمد لباس"): "کناره‌ی واحد پایین، راست (کمد لباس)",
    ("Bottom Unit - Back", "کمد لباس"): "پشت واحد پایین (کمد لباس)",
    ("Bottom Unit - Top Panel", "کمد لباس"): "سقف واحد پایین (کمد لباس)",
    ("Hanging Unit - Left Side", "کمد لباس"): "کناره‌ی واحد آویز، چپ (کمد لباس)",
    ("Hanging Unit - Right Side", "کمد لباس"): "کناره‌ی واحد آویز، راست (کمد لباس)",
    ("Hanging Unit - Left Side (Spare)", "کمد لباس"): "کناره‌ی واحد آویز، چپ - یدک (کمد لباس)",
    ("Hanging Unit - Right Side (Spare)", "کمد لباس"): "کناره‌ی واحد آویز، راست - یدک (کمد لباس)",
    ("Hanging Unit - Back", "کمد لباس"): "پشت واحد آویز (کمد لباس)",
    ("Hanging Unit - Bottom", "کمد لباس"): "کف واحد آویز (کمد لباس)",
    ("Hanging Unit - Top Panel", "کمد لباس"): "سقف واحد آویز (کمد لباس)",
    ("Side Shelf N", "کمد لباس"): "طبقه‌ی کناری (کمد لباس)",
    ("Side Shelf N - Bracket (front, vertical leg)", "کمد لباس"): "نبشی طبقه، جلو - پایه‌ی عمودی (کمد لباس)",
    ("Side Shelf N - Bracket (front, horizontal leg)", "کمد لباس"): "نبشی طبقه، جلو - پایه‌ی افقی (کمد لباس)",
    ("Side Shelf N - Bracket (back, vertical leg)", "کمد لباس"): "نبشی طبقه، پشت - پایه‌ی عمودی (کمد لباس)",
    ("Side Shelf N - Bracket (back, horizontal leg)", "کمد لباس"): "نبشی طبقه، پشت - پایه‌ی افقی (کمد لباس)",
}

_TAG_RE = re.compile(r"^(?P<core>.*?)(?:\s*\[(?P<furniture>[^\]#]+?)(?:\s*#\d+)?\])?$")


def normalize_key(label):
    """label -> (core_pattern, furniture_tag): strips the order-level
    "[دراور]"/"[دراور #2]" furniture tag into its own field, and replaces
    every digit run in the remaining core part name with "N" (Box1/Drawer
    2/... all collapse to the same pattern regardless of instance)."""
    m = _TAG_RE.match(label)
    core = re.sub(r"\d+", "N", m.group("core")).strip()
    return core, m.group("furniture")


def translate(label, length, width):
    """The Persian display name for a panel's own FreeCAD label, or a
    generic (but still descriptive — core name + size) fallback if it
    isn't in FA_LABELS yet."""
    key = normalize_key(label)
    if key in FA_LABELS:
        return FA_LABELS[key]
    core, furniture = key
    suffix = f" ({furniture})" if furniture else ""
    return f"{core} — {length:.0f}×{width:.0f}{suffix}"
