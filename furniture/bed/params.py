"""
Single source of truth for every design parameter used by the bed / drawer-box
model. No geometry logic lives here — only named values, grouped by subject.
(فایل پارامترها. فقط اعداد و تنظیمات؛ منطق هندسی اینجا نیست.)

Units: millimeters everywhere, unless a name says otherwise.
(واحد همه‌جا میلی‌متره، مگر اسم پارامتر چیز دیگه‌ای بگه.)

Anything not yet measured/decided is marked "# TBD" with a placeholder value
that keeps the rest of the model runnable. Update the value here, never
inline in geometry code, once the real number is known.
(هر چی هنوز اندازه‌گیری/تصمیم نهایی نشده با "# TBD" علامت خورده؛ وقتی عدد
واقعی معلوم شد همینجا عوضش کن، نه توی کد هندسه.)
"""

# --- Mattress -----------------------------------------------------------
# (تشک)
# LENGTH = head-to-toe direction. WIDTH = side-by-side direction.
# (LENGTH = جهت سر تا پا. WIDTH = جهت پهلو به پهلو.)
MATTRESS_LENGTH = 2000
MATTRESS_WIDTH = 1800

# Just for a visual placeholder in the full-bed assembly (bed.py) — not a
# real fabrication dimension, the mattress isn't something we build.
# (فقط برای جای‌گیر بصری توی مونتاژ کامل تخت (bed.py) — بعد فابریکیشن واقعی
# نیست، تشک چیزی نیست که ما بسازیمش.)
MATTRESS_THICKNESS = 300  # confirmed: 30cm

# Offset between the mattress edge and the outer edge of the box frame
# beneath it. Kept as two separate parameters because the two axes are not
# symmetric: along LENGTH the frame only extends past the mattress at the
# foot end (the head end sits flush, no overhang there), while along WIDTH
# the frame is centered under the mattress with the same gap on both sides.
# (فاصله‌ی لبه‌ی تشک تا لبه‌ی بیرونی باکس زیرش. دو پارامتر جداست چون قرینه
# نیست: در جهت LENGTH فقط سمت پایین تخت این فاصله هست، سمت سر تخت صاف
# می‌شینه؛ در جهت WIDTH این فاصله دو طرف یکسانه.)
MATTRESS_TO_FRAME_GAP_LENGTH = 100  # confirmed: 10cm — foot end only / فقط سمت پایین تخت
MATTRESS_TO_FRAME_GAP_WIDTH = 0  # confirmed: 10cm — applied on both sides / هر دو طرف — experiment: was 0

# The mattress-stop strip (bed.py) is a flat MDF cap that fills exactly
# this same foot-end gap, lying on top of the top panel's surface (not a
# raised wall) — its own width IS MATTRESS_TO_FRAME_GAP_LENGTH, not a
# separate number. See bed.py for placement; MDF_THICKNESS is its Z
# thickness, stacked additionally on top of the top panel.
# (نوار جلوگیری از تشک (bed.py) یه کلاهک صاف ام‌دی‌افه که دقیقاً همین
# فاصله‌ی سمت پایین تخت رو پر می‌کنه، روی سطح صفحه‌ی بالایی می‌شینه (نه
# یه دیواره‌ی بلندشده) — عرض خودش همون MATTRESS_TO_FRAME_GAP_LENGTH هست،
# نه یه عدد جدا. برای جای‌گیریش bed.py رو نگاه کن؛ MDF_THICKNESS هم
# ضخامت Z شه، اضافه روی صفحه‌ی بالایی.)

# --- Frame / box ----------------------------------------------------------
# (فریم / باکس)
# The bed is BOX_COUNT identical boxes placed side by side along the length.
# (تخت از BOX_COUNT تا باکس یکسان تشکیل شده که کنار هم در جهت LENGTH چیده شدن.)
BOX_COUNT = 3

# Derived, not measured: total external footprint of the boxes.
# (محاسبه‌شده، نه اندازه‌گیری‌شده: کل ابعاد بیرونی مجموع باکس‌ها.)
FRAME_LENGTH = MATTRESS_LENGTH + MATTRESS_TO_FRAME_GAP_LENGTH
FRAME_WIDTH = MATTRESS_WIDTH + 2 * MATTRESS_TO_FRAME_GAP_WIDTH

# Clear/interior height of one box: the actual cut height of the 2 long
# side walls AND the internal transverse walls (both trapped between top
# and bottom — see box.py), confirmed against the reference spreadsheet's
# "کناره" (side) and "دیواره عرضی داخلی" (internal transverse wall) rows,
# which both independently give this same 25cm figure.
# (ارتفاع خالص/داخلی یک باکس: قد واقعی برش‌خورده‌ی دیواره‌های جانبی بلند
# باکس و دیواره‌های عرضی داخلی (که هر دو بین رو و پایین گیر افتادن — نگاه
# کن به box.py). با ردیف‌های «کناره» و «دیواره عرضی داخلی» توی شیت مرجع چک
# شد — هر دو مستقل از هم همین عدد ۲۵ سانت رو نشون دادن.)
BOX_INTERIOR_HEIGHT = 250

# Actual thickness of the MDF board itself (core only, face-to-face),
# confirmed by the user. This is the number that drives all box/drawer
# fitting geometry. Placed here, above BOX_LENGTH, since BOX_LENGTH's own
# formula now depends on it.
# (ضخامت واقعی خود ورق ام‌دی‌اف، از سطح صاف تا سطح صاف — همین عدد پایه‌ی
# محاسبه‌ی جفت‌شدن باکس‌ها و کشوهاست. اینجا، قبل از BOX_LENGTH، چون فرمول
# خود BOX_LENGTH الان بهش وابسته‌ست.)
MDF_THICKNESS = 16

# Footprint of one box along LENGTH (Y): boxes sit side by side along Y.
# NOT simply FRAME_LENGTH split evenly — corrected this session: the last
# box's own far wall needs to stop 1 MDF_THICKNESS short of FRAME_LENGTH,
# leaving exactly enough room for EndFaceFoot (bed.py) to sit flush inside
# that gap without poking out past FRAME_LENGTH (same "shell inset, Face
# pokes back out to the true boundary" pattern used for BOX_WIDTH above —
# before this fix, EndFaceFoot's own thickness stuck out past FRAME_LENGTH,
# which is what forced MattressStopFoot to be inflated by an extra
# MDF_THICKNESS to still cap over it; now it doesn't need to be). Since all
# BOX_COUNT boxes are identical and placed by a plain box_index * BOX_LENGTH
# offset (see box.py/bed.py — no per-box special-casing), the 1
# MDF_THICKNESS is subtracted from the total before splitting evenly,
# shrinking every box by the same small amount, rather than only the last
# one. Derived, not measured.
# (طول یک باکس در جهت LENGTH (محور Y): باکس‌ها کنار هم در جهت Y می‌شینن. نه
# صرفاً FRAME_LENGTH تقسیم مساوی — این جلسه اصلاح شد: دیواره‌ی دور آخرین
# باکس باید یک MDF_THICKNESS قبل از FRAME_LENGTH تموم بشه، تا دقیقاً جا برای
# EndFaceFoot (bed.py) باز بمونه که توی همون فاصله بشینه بدون این‌که از
# FRAME_LENGTH رد بشه (همون الگوی «بدنه تو رفته، نما دوباره تا مرز واقعی
# بیرون می‌زنه» که برای BOX_WIDTH بالا استفاده شد — قبل این فیکس، ضخامت خود
# EndFaceFoot از FRAME_LENGTH رد می‌شد، که باعث می‌شد MattressStopFoot یک
# MDF_THICKNESS اضافه بزرگ بشه تا هنوز روش رو بپوشونه؛ الان دیگه لازم نیست).
# چون همه‌ی BOX_COUNT باکس یکسانن و با یه آفست ساده‌ی box_index * BOX_LENGTH
# جا می‌گیرن (box.py/bed.py — بدون حالت خاص برای هیچ باکسی)، همون یک
# MDF_THICKNESS از کل قبل از تقسیم مساوی کم می‌شه، یعنی هر باکس یه‌ذره کوچیک
# می‌شه، نه فقط آخری. محاسبه‌شده.)
BOX_LENGTH = (FRAME_LENGTH - MDF_THICKNESS) / BOX_COUNT

# External height of one box (top of top panel to bottom of bottom panel):
# BOX_INTERIOR_HEIGHT plus the top and bottom panels' own thickness, since
# those 2 panels cap over the (shorter) side walls rather than sitting
# flush within their height. Derived, not measured directly — do not set
# this literally, change BOX_INTERIOR_HEIGHT instead.
# (ارتفاع بیرونی یک باکس، از روی صفحه‌ی بالا تا زیر صفحه‌ی پایین:
# BOX_INTERIOR_HEIGHT به‌علاوه‌ی ضخامت خود صفحه‌ی رو و پایین، چون این دو
# صفحه روی دیواره‌های (کوتاه‌تر) جانبی رو می‌پوشونن، نه این‌که هم‌تراز
# داخل ارتفاعشون بشینن. محاسبه‌شده، مستقیم عوضش نکن — BOX_INTERIOR_HEIGHT
# رو عوض کن.)
BOX_HEIGHT = BOX_INTERIOR_HEIGHT + 2 * MDF_THICKNESS

# Thickness of the PVC edge-banding tape glued onto exposed cut edges to
# hide the raw MDF core. This wraps the edge — it does NOT add to
# MDF_THICKNESS or affect box/drawer fitting geometry, only the visible
# edge profile and later the cut list.
# Reconciles the earlier "~20mm effective wall" observation from the
# reference photos: MDF_THICKNESS (16) + 2 * PVC_THICKNESS (2 + 2) = 20 —
# an edge band wrapping both visible faces of a cut edge, not a face
# laminate as originally guessed.
# (ضخامت نوار پی‌وی‌سی لبه، که فقط دور لبه‌ی برش‌خورده می‌پیچه تا هسته‌ی
# خام دیده نشه. این به MDF_THICKNESS اضافه نمی‌شه و روی هندسه‌ی جفت‌شدن
# باکس/کشو اثر نداره، فقط روی ظاهر لبه و بعداً کات‌لیست. همین عدد توضیح
# می‌ده چرا توی عکس‌های مرجع لبه ~۲۰ میل به‌نظر می‌رسید: ۱۶ + ۲ + ۲ = ۲۰.)
PVC_THICKNESS = 2

# --- Drawer -----------------------------------------------------------
# (کشو)
DRAWERS_PER_BOX = 2

# Drawer bottom is 3mm fiber board, not structural MDF.
# (کف کشو از فیبر ۳ میل هست، نه ام‌دی‌اف ساختاری.)
DRAWER_BOTTOM_THICKNESS = 3

# "inset": drawer front sits flush inside the box opening.
# "overlay": drawer front sits proud of the box, extending past its face.
# Decided: build overlay first. Both modes must stay supported through this
# same parameter — inset is not being dropped, just built second.
# ("inset": روی کشو هم‌سطح بدنه‌ست. "overlay": روی کشو از بدنه جلوتره.
# تصمیم: اول overlay می‌سازیم؛ inset کنار گذاشته نشده، فقط بعداً ساخته می‌شه.)
DRAWER_FRONT_MODE = "overlay"

# The Drawer_box's "front" is 2 separate panels, confirmed this session
# (not one panel doing both jobs, an earlier simplification this session
# that was corrected): a structural front (flush/inset with the box
# opening, part of the drawer carcass, hidden once assembled) plus a
# separate "Face" panel (نما) attached to it, which is what's actually
# visible and actually overlays. DRAWER_FRONT_OVERLAY_AMOUNT is the Face
# panel's own board thickness — since it's mounted directly against the
# structural front's outer face and extends outward by its full thickness,
# that thickness IS how far it protrudes past the box.
# (جلوی Drawer_box در واقع ۲ پنل جداست، این جلسه تأیید شد (نه یه پنل با دو
# نقش، که ساده‌سازی اشتباه همین جلسه بود): یه جلوی ساختاری (هم‌سطح با
# بازشوی باکس، جزو بدنه‌ی کشو، بعد از مونتاژ دیده نمی‌شه) به‌علاوه‌ی یه پنل
# جدا به اسم «نما» که بهش وصل می‌شه و همونیه که واقعاً دیده می‌شه و واقعاً
# overlay داره. DRAWER_FRONT_OVERLAY_AMOUNT ضخامت خود تخته‌ی نماست — چون
# مستقیم به سطح بیرونی جلوی ساختاری چسبیده و به اندازه‌ی کل ضخامت خودش
# بیرون می‌زنه، همون ضخامت میزان جلوزدگیشه.)
DRAWER_FRONT_OVERLAY_AMOUNT = MDF_THICKNESS  # TBD

# Small reveal gap between the Face panels of 2 adjacent boxes (in Y), so
# they don't rub against each other. Split evenly: each Face is centered
# in its own box's Y-footprint, inset by half this gap on each side.
# (فاصله‌ی کوچیک بین نمای دو باکس کناری (در جهت Y)، تا به هم سایش نکنن.
# مساوی تقسیم می‌شه: هر نما وسط باکس خودش می‌شینه، هر طرف نصف این فاصله
# تو رفته.)
DRAWER_FACE_GAP = 3  # TBD: placeholder reveal, no real number chosen yet

# CONFIRMED direction (this session): in "overlay" mode there are 2 distinct
# physical ways the drawer meets the box, picked via DRAWER_OVERLAY_STYLE:
#   "box_over_drawer" — the box's own Top panel extends all the way out to
#     FRAME_WIDTH and caps over the drawer's Face from above (no separate
#     rail-mount frame consumes extra height). Default — matches the
#     user's explicit request that the Top panel itself do this job, not an
#     applied trim strip, even though reference photos show a separate
#     piece doing it.
#   "rail_above_drawer" — a slide-mounting frame (unmodeled hardware, like
#     RAIL_* below) sits on top of the drawer and is what pokes out to meet
#     the Face, so the Top panel itself stays flush with the rest of the
#     shell (BOX_WIDTH, not FRAME_WIDTH) and the drawer carcass loses one
#     MDF_THICKNESS of height to make room for that frame (see
#     drawer_side_height in box.py).
# In BOTH styles, the box shell itself (Bottom, the 2 side walls, and the
# drawer carcasses) is inset from FRAME_WIDTH by MDF_THICKNESS on each X
# side — this is what BOX_WIDTH is, below. The Face panel's own overlay
# (DRAWER_FRONT_OVERLAY_AMOUNT) is what reaches back out to exactly
# FRAME_WIDTH; before this session the shell sat flush at FRAME_WIDTH
# already, so the assembled box+Face actually overshot FRAME_WIDTH by 2 *
# MDF_THICKNESS — this insetting is what fixes that.
# (تأییدشده (این جلسه): توی حالت "overlay" دو راه فیزیکی متفاوت هست که کشو
# به باکس می‌رسه، با DRAWER_OVERLAY_STYLE انتخاب می‌شه:
#   "box_over_drawer" — خود صفحه‌ی بالای باکس تا FRAME_WIDTH جلو میاد و از
#     بالا روی نمای کشو رو می‌پوشونه (فریم نصب جدایی ارتفاع اضافه مصرف
#     نمی‌کنه). پیش‌فرض — چون کاربر صریح خواسته خود صفحه‌ی بالایی این نقش
#     رو بازی کنه.
#   "rail_above_drawer" — یه فریم نگه‌دارنده‌ی ریل (سخت‌افزار مدل‌نشده، مثل
#     RAIL_* پایین) روی کشو می‌شینه و اونیه که بیرون می‌زنه، پس خود صفحه‌ی
#     بالایی هم‌تراز بقیه‌ی بدنه می‌مونه (BOX_WIDTH نه FRAME_WIDTH) و بدنه‌ی
#     کشو یه MDF_THICKNESS از ارتفاعش رو برای جا باز کردن اون فریم از دست
#     می‌ده (نگاه کن drawer_side_height توی box.py).
# توی هر دو حالت، خود بدنه‌ی باکس (کف، دو دیواره‌ی کناری، بدنه‌ی کشوها) از
# FRAME_WIDTH هر طرف به اندازه‌ی MDF_THICKNESS تو رفته — این همون BOX_WIDTH
# پایینه. جلوزدگی خود پنل نما (DRAWER_FRONT_OVERLAY_AMOUNT) اونیه که دوباره
# تا دقیقاً FRAME_WIDTH بیرون میاد؛ قبل این جلسه بدنه صاف روی FRAME_WIDTH
# می‌شست، یعنی مجموعه‌ی باکس+نما واقعاً ۲ برابر MDF_THICKNESS از FRAME_WIDTH
# رد می‌شد — این تو رفتگی همون رو درست می‌کنه.)
DRAWER_OVERLAY_STYLE = "box_over_drawer"  # or "rail_above_drawer"

# Box shell's own X footprint (Bottom, 2 side walls, drawer carcasses) —
# always inset from FRAME_WIDTH by MDF_THICKNESS on each side, regardless
# of DRAWER_OVERLAY_STYLE. The Face panel's overlay closes this gap back up
# to FRAME_WIDTH (see box.py).
# (فوت‌پرینت X خود بدنه‌ی باکس (کف، دو دیواره، بدنه‌ی کشوها) — همیشه از
# FRAME_WIDTH هر طرف به اندازه‌ی MDF_THICKNESS تو رفته، فارغ از
# DRAWER_OVERLAY_STYLE. جلوزدگی پنل نما دوباره این فاصله رو تا FRAME_WIDTH
# می‌بنده (نگاه کن box.py).)
BOX_WIDTH = FRAME_WIDTH - 2 * MDF_THICKNESS

# Where the box shell's X=0 edge sits relative to FRAME_WIDTH's own X=0
# origin — MDF_THICKNESS in from it, always.
# (لبه‌ی X=۰ بدنه‌ی باکس نسبت به مبدأ X=۰ خود FRAME_WIDTH کجاست — همیشه به
# اندازه‌ی MDF_THICKNESS تو رفته.)
BOX_SHELL_X_MIN = MDF_THICKNESS

# Vertical gap between the underside of that overhanging top panel and the
# top edge of the drawer front, so the drawer can slide in/out without
# rubbing against the panel above it.
# Corrected after follow-up research specifically on ball-bearing side-mount
# slides (what RAIL_THICKNESS below already assumes) rather than a generic
# "drawer slides" guide: these need only ~1/4" (6.35mm) TOTAL vertical
# clearance, typically split ~1/8" (3mm) above and ~1/8" (3mm) below — much
# less than the ~12mm a more generic/mixed source first suggested (that
# figure was closer to what undermount or epoxy Euro slides need, ~1/2"-3/4"
# total). Our drawer bottom already sits flush on the box's own bottom panel
# (no modeled "below" gap), so the full ~6mm allowance is put here, above.
# A bigger gap than this both looks sloppy and lets the drawer sit loose in
# the opening — confirm against the actual chosen rail's datasheet.
# (فاصله‌ی عمودی بین زیر همون لبه‌ی جلوزده و روی کشو، تا کشو موقع باز/بسته
# شدن به صفحه‌ی بالایی سایش پیدا نکنه. بعد از تحقیق دقیق‌تر مخصوص ریل‌های
# ساید-مونت بلبرینگی (همونی که RAIL_THICKNESS پایین فرض کرده) اصلاح شد: این
# ریل‌ها فقط ~۶.۳۵ میل کلیرنس عمودی کل لازم دارن (تقریباً ۳ میل بالا و ۳
# میل پایین) — خیلی کمتر از ۱۲ میلی که یه منبع عمومی‌تر اول پیشنهاد داده
# بود (اون عدد بیشتر مال ریل‌های زیرکار یا اپوکسی یوروئه). چون کف کشو همینجا
# صاف روی کف باکس می‌شینه (فاصله‌ای «پایین» مدل نشده)، کل اون ~۶ میل رو
# همینجا، بالا، گذاشتیم. فاصله‌ی بیشتر از این هم بد به‌نظر می‌رسه هم کشو
# توی دهنه‌ی باکس شل می‌شینه — با دیتاشیت ریل واقعی چک بشه.)
DRAWER_TOP_REVEAL_GAP = 6  # TBD: matches ball-bearing side-mount convention, confirm w/ datasheet

# Everything that varies by DRAWER_OVERLAY_STYLE, computed together here —
# one seam, one branch per style — instead of re-branching on the style
# string at each dependent call site (box.py used to carry 2 of its own
# copies of this check). See box.py's module docstring for the physical
# reasoning behind each style.
def _drawer_overlay_geometry(style):
    if style == "box_over_drawer":
        return dict(
            top_panel_width=FRAME_WIDTH,
            top_x_min=0,
            drawer_height_reduction=0,
            face_top_ref_z=BOX_HEIGHT - MDF_THICKNESS,
        )
    elif style == "rail_above_drawer":
        return dict(
            top_panel_width=BOX_WIDTH,
            top_x_min=BOX_SHELL_X_MIN,
            drawer_height_reduction=MDF_THICKNESS,
            face_top_ref_z=BOX_HEIGHT,
        )
    raise ValueError(f"Unknown DRAWER_OVERLAY_STYLE: {style!r}")


_overlay_geometry = _drawer_overlay_geometry(DRAWER_OVERLAY_STYLE)
# Top panel's X footprint/start: flush with FRAME_WIDTH (caps the drawer
# from above) in "box_over_drawer", or matching the shell inset in
# "rail_above_drawer" (unmodeled rail frame reaches out instead).
BOX_TOP_PANEL_WIDTH = _overlay_geometry["top_panel_width"]
BOX_TOP_X_MIN = _overlay_geometry["top_x_min"]
# Height the drawer carcass gives up for the unmodeled rail-mount frame in
# "rail_above_drawer" (0 in "box_over_drawer"). Used by box.py.
DRAWER_HEIGHT_REDUCTION = _overlay_geometry["drawer_height_reduction"]
# Z reference the Face's top edge measures DRAWER_TOP_REVEAL_GAP down from.
# Used by box.py.
DRAWER_FACE_TOP_REF_Z = _overlay_geometry["face_top_ref_z"]

# Drawer slide rail. Reference notes a 600 or 650mm nominal rail; exact
# model/brand and its datasheet clearance are not chosen yet.
# (ریل کشو. مرجع ۶۰۰ یا ۶۵۰ میل رو نشون می‌ده؛ مدل دقیق و کلیرنس دیتاشیت
# هنوز انتخاب نشده.)
RAIL_LENGTH = 650  # TBD: confirm rail model

# Per-side horizontal clearance between the drawer carcass and the box
# opening, for the slide hardware itself. Research on side-mount ball-
# bearing slides (see roadmap.md Phase 3 entry for sources) confirms ~13mm
# per side is the right ballpark (commonly cited as ~1/2" to 17/32", i.e.
# 12.7-13.5mm) — this placeholder already matched before confirming it.
# (کلیرنس افقی هر طرف بین بدنه‌ی کشو و بازشوی باکس، برای خود سخت‌افزار ریل.
# تحقیق روی ریل‌های ساید-مونت (منابع توی roadmap.md فاز ۳) تأیید کرد که
# ~۱۳ میل هر طرف عدد درستیه — این جاگذار از قبل هم همین‌جا بود.)
RAIL_CLEARANCE = 13  # TBD: per-side clearance from rail datasheet (mm)

# General rule for side-mount slides: the box/compartment the slide sits in
# should be a few mm deeper than the slide's own nominal length, so the
# drawer doesn't jam against whatever's behind it when fully closed.
# Research (see roadmap.md Phase 3 entry) cites ~3-5mm; used here as the gap
# behind each drawer before the internal transverse wall.
# (قاعده‌ی کلی ریل‌های ساید-مونت: فضایی که ریل توش می‌شینه باید چند میلی‌متر
# از طول اسمی خود ریل عمیق‌تر باشه، تا کشو موقع کاملاً بسته‌شدن به هرچی
# پشتشه گیر نکنه. تحقیق ~۳-۵ میل رو تأیید کرد؛ اینجا فاصله‌ی پشت هر کشو تا
# دیواره عرضی داخلی همینه.)
RAIL_BACK_CLEARANCE = 5  # TBD: confirm against chosen rail's datasheet

# Metal channel thickness of a standard side-mount ball-bearing slide
# (typically ~12mm on each side, slightly less than RAIL_CLEARANCE which
# also includes a small extra running gap). Confirm against the chosen
# rail's datasheet once picked.
# (ضخامت ریل فلزی ساید-مونت معمولی، تقریباً ۱۲ میل هر طرف — کمی کمتر از
# RAIL_CLEARANCE که یه فاصله‌ی اضافه هم داره. با دیتاشیت ریل واقعی چک بشه.)
RAIL_THICKNESS = 12  # TBD: confirm rail model

# Height from the box's internal bottom face up to the rail's mounting
# line. Standard side-mount slides run just above the drawer bottom panel,
# so this is set just past DRAWER_BOTTOM_THICKNESS to clear it.
# (ارتفاع از کف داخلی باکس تا خط نصب ریل. ریل‌های ساید-مونت معمولاً درست
# بالای کف کشو نصب می‌شن، پس این عدد کمی بیشتر از DRAWER_BOTTOM_THICKNESS ست.)
RAIL_POSITION_Z = 15  # TBD: confirm against chosen rail + drawer construction

# --- Skirt / apron -----------------------------------------------------
# (اسکرت / تِرین پایه)
# Thin decorative MDF trim visible around the base of the bed, hanging down
# from the underside of the box. Has nothing to do with drawer position —
# it's a separate board below the box (near the floor), not an extension
# of the drawer front (which lives up near the top of the box — see
# DRAWER_TOP_REVEAL_GAP above, a different and unrelated parameter).
# (تِرین تزئینی نازک دور پایه‌ی تخت، از زیر باکس آویزون می‌شه، نزدیک زمین.
# هیچ ربطی به موقعیت کشو نداره — کشو بالای باکسه (نگاه کن به
# DRAWER_TOP_REVEAL_GAP، یه پارامتر کاملاً جدا)، اسکرت پایین باکسه.)

# Skirt on the two long (drawer-carrying) faces of a box. Always on — this
# is the bed's most visible face. Only covers part of LEG_FRAME_HEIGHT;
# the rest stays open below it for hand clearance under the drawer front.
# (اسکرت روی دو وجه بلند باکس (همونایی که کشو دارن). همیشه روشنه — چون
# مهم‌ترین وجه دیدنی تخته. فقط بخشی از LEG_FRAME_HEIGHT رو می‌پوشونه؛ بقیه
# برای رد شدن دست زیر کشو باز می‌مونه.)
HAS_DRAWER_SIDE_SKIRT = True

# Skirt on the two short (head/foot) end faces, which have no drawer.
# Togglable — purely for visual continuity around the base, not functional.
# (اسکرت روی دو وجه کوتاه سر و پای تخت، که کشو ندارن. اختیاریه — فقط برای
# هماهنگی ظاهری دور پایه، نه یه ضرورت عملکردی.)
HAS_END_SKIRT = True

# Height of the skirt board itself. The remaining gap below it, down to the
# floor (LEG_FRAME_HEIGHT - SKIRT_HEIGHT), stays open as the hand-clearance
# space for reaching under the handle-less drawer front.
# (ارتفاع خود تخته‌ی اسکرت. باقی‌مونده‌ی فاصله زیرش تا کف زمین
# (LEG_FRAME_HEIGHT - SKIRT_HEIGHT) بازه، برای رد شدن دست زیر کشوی
# بی‌دستگیره.)
SKIRT_HEIGHT = 20  # confirmed: 2cm

# Independent from MDF_THICKNESS — the skirt is a separate decorative board,
# not a structural box wall, so it may end up a different thickness.
# (مستقل از MDF_THICKNESS — اسکرت یه تخته‌ی تزئینی جداست، نه دیواره‌ی
# ساختاری باکس، پس ممکنه ضخامتش فرق کنه.)
SKIRT_THICKNESS = 16  # TBD

# --- Support frame (Model A only: handle-less drawers, opened by hand from
# underneath, so the bed needs to be raised for finger clearance) -----------
# (فریم پایه — فقط مدل A: کشوی بی‌دستگیره که با دست از زیر باز می‌شه، پس
# تخت باید بلند بشه تا جای دست باشه.)
LEG_FRAME_HEIGHT = 100  # TBD: driven by hand-clearance requirement

# --- Headboard (تاج) -----------------------------------------------------
# A single MDF panel standing at the head end (Y=0 — the end that butts
# against the room's wall), attached to the outer face of the first box's
# SideWallNear, same overlay/attachment pattern as EndFaceFoot but mirrored
# to the other end of the bed (see create_headboard in bed.py).
# Confirmed with the user: 1.4m TOTAL height, measured from the actual
# floor (Z = -LEG_FRAME_HEIGHT in this model, where the leg/support frame
# ends) up to the panel's own top edge — NOT from the box's own bottom
# (Z=0), which is why this is a separate param from BOX_HEIGHT/SKIRT_HEIGHT
# rather than derived from them.
# (یه پنل ام‌دی‌اف تک که سر تخت (Y=۰ — همون سمتی که به دیوار اتاق می‌چسبه)
# می‌ایسته، چسبیده به بیرون دیواره‌ی سر باکس اول، همون الگوی وصل‌شدن
# EndFaceFoot اما برعکس، طرف دیگه‌ی تخت. تأییدشده: ارتفاع کل ۱.۴ متر، از کف
# واقعی زمین (Z = -LEG_FRAME_HEIGHT توی این مدل، همون‌جا که فریم پایه تموم
# می‌شه) تا لبه‌ی بالای خود پنل — نه از کف باکس (Z=۰)، برای همین یه پارامتر
# جداست، نه از BOX_HEIGHT/SKIRT_HEIGHT محاسبه‌شده.)
HEADBOARD_HEIGHT = 1400  # confirmed: 1.4m total, floor to top edge

# --- Material / appearance -----------------------------------------------
# (متریال / ظاهر)
# Color is driven by StockSource first, then role. Any panel with
# StockSource == "reclaimed" (see CONTEXT.md's visible/stock_source
# concept) always gets RECLAIMED_MDF_COLOR, regardless of its role — these
# are hidden panels cut from leftover stock, so their finish doesn't
# matter for appearance, only for being visually distinct in the model.
# New-stock, visible panels get a role-specific color instead:
#   * BODY_COLOR: new-stock Box body panels (currently just the Top panel)
#   * DRAWER_FRONT_COLOR: the Drawer_box's Face (نما) panel only
# A Face never carries the body color, and no other panel carries the
# Face's color.
# (رنگ اول از StockSource میاد، بعد از نقش پنل. هر پنلی که StockSource ش
# "reclaimed" باشه (نگاه کن به مفهوم visible/stock_source توی CONTEXT.md)
# همیشه RECLAIMED_MDF_COLOR می‌گیره، فارغ از نقشش — این‌ها پنل‌های مخفی از
# جنس باقی‌مونده‌ی انبارن، ظاهرشون مهم نیست، فقط برای تشخیص بصری توی مدله.
# پنل‌های new-stock و دیده‌شده رنگ مخصوص نقش خودشون رو می‌گیرن:
#   * BODY_COLOR: پنل‌های بدنه‌ی باکس با new-stock (فعلاً فقط صفحه‌ی بالایی)
#   * DRAWER_FRONT_COLOR: فقط پنل نمای (نما) Drawer_box.
# نما هیچ‌وقت رنگ بدنه رو نداره و هیچ پنل دیگه‌ای رنگ نما رو.)
RECLAIMED_MDF_COLOR = (1.0, 1.0, 1.0)  # confirmed: white

# Estimated by eye from colors/1128-misty.jpg ("Misty", code 1128) — no
# exact hex/RAL code given yet, refine if one becomes available.
# (تخمین چشمی از colors/1128-misty.jpg ("Misty"، کد ۱۱۲۸) — کد هگز/RAL
# دقیق هنوز داده نشده، اگه بعداً بود دقیق‌ترش کن.)
BODY_COLOR = (0.31, 0.44, 0.50)  # TBD: "Misty" 1128, estimated from swatch

# Estimated by eye from colors/1126-brown.jpg ("Brown", code 1126) — same
# caveat as BODY_COLOR above.
# (تخمین چشمی از colors/1126-brown.jpg ("Brown"، کد ۱۱۲۶) — همون ملاحظه‌ی
# BODY_COLOR بالا.)
DRAWER_FRONT_COLOR = (0.43, 0.35, 0.28)  # TBD: "Brown" 1126, estimated from swatch

WOOD_COLOR = (0.76, 0.60, 0.42)  # decorative wood-toned panels, if used
RAIL_COLOR = (0.5, 0.5, 0.5)   # metal rails / hardware
