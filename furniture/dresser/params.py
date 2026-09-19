"""
Single source of truth for every design parameter used by the dresser
(دراور) model. No geometry logic lives here — only named values, grouped
by subject. Mirrors furniture/bed/params.py's shape; see that file and
docs/CONTEXT.md for the shared visible/stock_source convention this
follows.

Units: millimeters everywhere, unless a name says otherwise.

First-draft numbers below (from the user's initial brief, 2026-09-05):
WIDTH/DEPTH/DRAWER_FACE_HEIGHT are given exactly, everything else is a
reasonable placeholder ("# TBD") to be confirmed once the user reacts to
the first build — this whole module is a "build it so I can see it, then
I'll comment" first draft, styled after references/reference-page8.png
(look only, not its hardware/connection details — this design's own
fastening is screws, per the user).

Revised 2026-09-05: drawer Faces are Inset, not Full Overlay — they sit
BETWEEN the 2 side panels (DRAWER_FACE_WIDTH) and land flush with the
shell's own front face, instead of protruding past it and covering the
sides' own front edge. The Top panel is likewise inset between the sides
(TOP_PANEL_WIDTH) rather than resting on top of them. Both changes are in
service of the same visual goal, straight from the user's own brief: the
2 side panels must stay visible as a continuous vertical strip on the
left and right in a front view (2-tone body/drawer-front look), and the
Top panel's own front edge stays flush/open — only its left and right
ends get a small lip, SIDE_TOP_LIP, above the Top panel's own surface
(the 2 side panels simply run a bit taller than the Top panel — no
separate frame or tray piece).

Also revised 2026-09-05: the topmost drawer's own Face rises all the way
up to be flush with the Left/Right/Back panels' own top edge (see
TOP_DRAWER_FACE_EXTRA_HEIGHT), instead of stopping at the Top panel's
underside like every other drawer — the Top panel's own front edge
retreats a little (TOP_PANEL_Y_MIN) to make room. Per-drawer Face color
now comes from DRAWER_COLOR_PATTERN, a string with one '0'/'1' digit per
drawer (top to bottom) — replaces the old ALTERNATE_DRAWER_COLORS
boolean, per the user's own suggested config format.

Also revised 2026-09-05: dropped the recessed toe-kick board — the
user's own reference (references/reference-base-example.jpeg) shows no board at all,
just small corner glide feet screwed directly into the underside of the
Left/Right panels at each corner (front and back), same idea as
furniture/bed's unmodeled drawer-slide hardware: real, but not worth
modeling as geometry. See FOOT_HEIGHT below — the Left/Right/Back panels
now run straight down to just above the floor instead of stopping
TOE_KICK_HEIGHT short of it for a board to fill.
"""

import os

import yaml

import colors

# --- Style presets ----------------------------------------------------
# Mirrors furniture/bed/params.py's pattern: named presets loaded from
# furniture/dresser/styles.yaml, selected with the STYLE env var, e.g.
# `STYLE=standard make view-dresser` (an order item's own `style:` key,
# see orders/specs/<name>.yaml, becomes this same STYLE env var). Color is
# NOT one of these knobs (same as furniture/bed) — it's fully independent
# of geometry STYLE, driven entirely by colors.py's own MAIN_COLOR/
# SECOND_COLOR/REUSED_MDF_COLOR + PART_ROLES, plus DRAWER_COLOR_PATTERN
# below (still a STYLES knob, since which drawer gets which of the 2
# colors IS a geometry-adjacent layout choice). drawer_color_pattern can
# still be overridden on top of the selected style with its own
# same-named env var (DRAWER_COLOR_PATTERN), same as STYLE's own
# per-knob overrides.
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "styles.yaml")) as _f:
    STYLES = yaml.safe_load(_f)

DEFAULT_STYLE = "standard"


def _resolve_style():
    style_name = os.environ.get("STYLE") or DEFAULT_STYLE
    if style_name not in STYLES:
        raise ValueError(f"Unknown STYLE={style_name!r}; known styles: {sorted(STYLES)}")
    values = dict(STYLES[style_name])
    if os.environ.get("DRAWER_COLOR_PATTERN"):
        values["drawer_color_pattern"] = os.environ["DRAWER_COLOR_PATTERN"]
    return values


_style = _resolve_style()

# Per-drawer Face color, top to bottom, one digit per drawer: '1' = main
# (colors.MAIN_COLOR, same as the body), '0' = second (colors.SECOND_COLOR,
# the accent) — e.g. "1000" means the topmost drawer matches the body, the
# other 3 don't. Per the user's own suggested config format, preserved
# unchanged by the main/second/reused refactor — this is a distinct,
# per-instance color pick layered on top of colors.py's PART_ROLES, not
# replaced by it. Length must match DRAWER_COUNT (checked below, once
# DRAWER_COUNT is known). See dresser.py's _add_drawer.
DRAWER_COLOR_PATTERN = _style["drawer_color_pattern"]

# --- Overall footprint ---------------------------------------------------
# X = WIDTH (left-right), Y = DEPTH (front-back). Every drawer opens from
# the Y=0 face. Z = height, floor at Z=0.
WIDTH = 900  # confirmed
DEPTH = 550  # confirmed: matches furniture/wardrobe's own DEPTH

# --- Material --------------------------------------------------------
MDF_THICKNESS = 16  # confirmed: same board as furniture/bed

# 3mm fiber board, not structural MDF — same convention as
# furniture/bed/params.py's DRAWER_BOTTOM_THICKNESS ("زیرش از جنس ورق
# دیگه‌ای هست").
DRAWER_BOTTOM_THICKNESS = 3

# --- Drawers ---------------------------------------------------------
DRAWER_COUNT = 4  # TBD: matches references/reference-page8.png's 4-drawer layout

if len(DRAWER_COLOR_PATTERN) != DRAWER_COUNT or any(c not in "01" for c in DRAWER_COLOR_PATTERN):
    raise ValueError(
        f"DRAWER_COLOR_PATTERN={DRAWER_COLOR_PATTERN!r} must be a string of "
        f"{DRAWER_COUNT} '0'/'1' characters (one per drawer, top to bottom) "
        f"— got length {len(DRAWER_COLOR_PATTERN)}"
    )

# Exterior face height, per drawer (نمای بیرونی هر کشو). Drawers stack
# with no gap between their bands — DRAWER_FACE_GAP_Z below is a reveal
# carved out of each band, not extra space between bands.
DRAWER_FACE_HEIGHT = 200  # confirmed: ~20cm per the user's brief

# Reveal gap between 2 vertically-stacked Face panels (and between the
# bottom Face and the Bottom panel it sits just above), so they don't
# rub. Mirrors furniture/bed's DRAWER_FACE_GAP, just along Z here instead
# of Y.
DRAWER_FACE_GAP_Z = 3  # TBD: placeholder reveal, no real number chosen yet

# The Drawer's front is 2 separate panels: a structural front (part of the
# carcass, hidden) plus a separate Face panel (نما) screwed onto it — the
# one actually visible. The Face always mounts flush against the
# structural front and protrudes outward (toward the viewer) by its own
# thickness — that thickness IS the overlay amount. Same convention as
# furniture/bed's DRAWER_FRONT_OVERLAY_AMOUNT.
DRAWER_FRONT_OVERLAY_AMOUNT = MDF_THICKNESS

# Inset, not Full Overlay (see module docstring): the structural front —
# and with it the whole carcass behind it (bottom, sides, back) — sits
# back from the shell's own open-face plane (Y=0) by exactly the Face's
# own thickness, so the Face's protrusion (above) lands flush with the
# shell instead of past it, and doesn't cover the 2 side panels' own
# front edge. Same idea as furniture/bed's DRAWER_FRONT_SETBACK for its
# "inset" DRAWER_STYLE.
DRAWER_FRONT_SETBACK = DRAWER_FRONT_OVERLAY_AMOUNT

# Reveal gap between the Face and the 2 side panels it sits between (X),
# so it doesn't rub — the Inset counterpart of DRAWER_FACE_GAP_Z above.
DRAWER_FACE_SIDE_GAP = 3  # TBD: placeholder reveal, no real number chosen yet

# Derived: the Face's own width — fits entirely BETWEEN the 2 side
# panels (WIDTH minus both MDF_THICKNESS side panels, minus the reveal),
# never spanning past them. The whole point of Inset over Full Overlay:
# this is what keeps the side panels' own front edge visible.
DRAWER_FACE_WIDTH = WIDTH - 2 * MDF_THICKNESS - DRAWER_FACE_SIDE_GAP

# --- Handle (دستگیره) ------------------------------------------------------
# Every drawer gets a metal bar handle centered on its own Face — unlike
# drawer-slide/glide-foot hardware, this one the user asked to actually
# model. Shape: a "bridge" pull — the bar itself, plus 2 short mounting
# posts connecting it back to the Face — built from the same box-only
# Panel primitive as everything else (core/panel.py), just with
# Material="Metal" and HANDLE_COLOR.
#
# Matches the user's own chosen hardware: Shahre Yaragh / Meloni brushed
# stainless steel cabinet handle, the 192mm screw-center size (232mm
# overall length) — see HANDLE_COLOR's "metal" swatch for the brushed-
# steel finish. This model doesn't drill screw holes, so HANDLE_WIDTH is
# the visible bar's overall length (232mm) rather than the 192mm
# hole-to-hole spacing; the posts simply sit at the bar's own two ends.
HANDLE_WIDTH = 232  # confirmed: Shahre Yaragh/Meloni handle, 192mm screw-center size
HANDLE_BAR_SIZE = 10  # TBD: bar cross-section (mm) — not listed on the product page
HANDLE_STANDOFF = 25  # TBD: projection from the Face (mm) — not listed on the product page
HANDLE_COLOR = colors.swatch_rgb("metal")

# --- Top panel support brackets (نبشی) --------------------------------
# The Top panel is Inset (see TOP_PANEL_MODE above), so unlike the Bottom
# panel (which rests on the floor) or the Back panel (which faces the
# wall), it has no naturally hidden side to screw from — its own edges
# only butt against the Left/Right/Back panels' own INNER faces, inside
# the cavity. Per the user's own construction brief: 3 L-shaped metal
# corner brackets (one against each of Left/Right/Back's own inner face,
# see _add_top_brackets in dresser.py) hold it up — one leg screwed to
# the panel's inner face, the other screwed to the Top panel's own
# underside, both hidden inside the cavity. Modeled the same box-only
# way as the drawer handle (2 thin Panel plates forming an L, per
# bracket) since the user asked for these to actually show in the model.
BRACKET_LEG = 30  # TBD: how far each leg reaches (mm) — no datasheet yet
BRACKET_WIDTH = 25  # TBD: bracket width along its mounted edge (mm)
BRACKET_THICKNESS = 2  # TBD: steel plate thickness (mm)
BRACKET_COLOR = colors.swatch_rgb("metal")

# Per-side horizontal clearance (X) between the drawer carcass and the
# dresser's own opening, for slide hardware. Same ballpark as
# furniture/bed's RAIL_CLEARANCE — not the focus of this first draft (the
# user only specified screws as the fastening method), just enough to
# keep the drawer carcasses from overlapping the shell visually.
RAIL_CLEARANCE = 13  # TBD: per-side clearance from rail datasheet (mm)

# Gap behind the drawer's back before it hits the dresser's own Back
# panel, so the drawer doesn't jam when fully closed. Same idea as
# furniture/bed's RAIL_BACK_CLEARANCE.
RAIL_BACK_CLEARANCE = 20  # TBD: confirm against chosen rail's datasheet

# Vertical gap above the drawer carcass (below whatever sits above it —
# the next drawer's own bottom, or the underside of the Top panel for the
# topmost drawer) so it can slide without rubbing. Same idea as
# furniture/bed's DRAWER_TOP_REVEAL_GAP.
DRAWER_TOP_REVEAL_GAP = 6  # TBD: matches ball-bearing side-mount convention, confirm w/ datasheet

# Derived: how much of a DRAWER_FACE_HEIGHT band the drawer carcass itself
# (hidden, behind the Face) actually occupies.
DRAWER_CARCASS_HEIGHT = (
    DRAWER_FACE_HEIGHT - DRAWER_BOTTOM_THICKNESS - DRAWER_TOP_REVEAL_GAP
)

# Derived: drawer depth, filling most of DEPTH — front-to-back, from just
# behind the structural front to RAIL_BACK_CLEARANCE short of the Back
# panel. Shrinks by DRAWER_FRONT_SETBACK compared to a flush (non-inset)
# front, since the whole carcass recedes into the dresser by that much
# (RAIL_BACK_CLEARANCE itself stays measured against the Back panel,
# which doesn't move).
DRAWER_DEPTH = DEPTH - 2 * MDF_THICKNESS - RAIL_BACK_CLEARANCE - DRAWER_FRONT_SETBACK

# Derived: drawer width, inset from WIDTH by MDF_THICKNESS on each side
# (the carcass's own Left/Right walls) plus RAIL_CLEARANCE on each side
# (slide hardware).
DRAWER_WIDTH = WIDTH - 2 * MDF_THICKNESS - 2 * RAIL_CLEARANCE

# --- Base / feet -----------------------------------------------------------
# No raised base/plinth at all (per references/reference-base-example.jpeg — there's
# no toe-kick board or leg frame in that reference, just small plastic
# glide feet screwed straight into the Left/Right panels' own bottom
# edge). Those glides are a few mm at most: not worth a floor-offset
# parameter, since they don't change this model's own dimensions or
# look — the Left/Right/Back panels' own bottom edge (Z=0) IS the floor,
# same idea as furniture/bed's HAS_LEG_FRAME=False case.

# --- Top panel / side lip -------------------------------------------------
# The Bottom panel always spans the full WIDTH x DEPTH footprint, with the
# Left/Right panels resting on top of its 2 edges — never inset.
#
# The Top panel has 2 modes (TOP_PANEL_MODE):
#   "inset" (default, standalone dresser): sits BETWEEN the 2 side
#     panels, which then run SIDE_TOP_LIP (one MDF_THICKNESS) taller than
#     it, forming a small open lip on each end (no separate frame/tray
#     piece) — the topmost drawer's own Face rises to fill it, reaching
#     flush with the sides' top edge. Needed for the 2-tone
#     body/drawer-front look — the side panels stay visible as a
#     continuous vertical strip.
#   "on_top" (furniture/wardrobe's bottom unit): a full WIDTH x DEPTH
#     panel resting ON TOP of the side panels, flush, mirroring the
#     Bottom panel's own relationship to them (just flipped) — no lip
#     concept applies here, since nothing is inset. Used for a
#     standalone unit that needs a flat, unbroken top surface for
#     something else to rest on (see furniture/wardrobe's two-piece
#     layout) — that's also why its own drawer heights must stay
#     uniform (no TOP_DRAWER_FACE_EXTRA_HEIGHT) rather than matching the
#     "inset" dresser's own lip: the wardrobe's Bottom Unit and Hanging
#     Unit are 2 separate freestanding boxes, not one dresser-shaped
#     piece, so there's no equivalent "recessed top" to fill.
TOP_PANEL_MODE = os.environ.get("TOP_PANEL_MODE", "inset")
if TOP_PANEL_MODE not in ("inset", "on_top"):
    raise ValueError(f"Unknown TOP_PANEL_MODE={TOP_PANEL_MODE!r}; must be 'inset' or 'on_top'")

# Derived: height the space available for drawers actually spans — DRAWER_COUNT
# bands stacked with no gap between them.
INTERIOR_HEIGHT = DRAWER_COUNT * DRAWER_FACE_HEIGHT

if TOP_PANEL_MODE == "inset":
    TOP_PANEL_WIDTH = WIDTH - 2 * MDF_THICKNESS
    TOP_PANEL_X_MIN = MDF_THICKNESS
    TOP_PANEL_Y_MIN = DRAWER_FRONT_SETBACK
    TOP_PANEL_DEPTH = DEPTH - TOP_PANEL_Y_MIN
    # The Top panel sits one MDF_THICKNESS below the sides' own top edge
    # (per the user's brief) — the sides simply run SIDE_TOP_LIP taller,
    # forming a small open lip on each end (no separate frame/tray
    # piece). The topmost drawer's own Face rises to fill that lip too,
    # reaching flush with the sides' top edge (TOP_DRAWER_FACE_EXTRA_HEIGHT
    # below) instead of stopping at the Top panel's own underside like
    # every other drawer.
    SIDE_TOP_LIP = MDF_THICKNESS
    SIDE_HEIGHT = INTERIOR_HEIGHT + MDF_THICKNESS + SIDE_TOP_LIP
    HEIGHT = MDF_THICKNESS + SIDE_HEIGHT
    TOP_PANEL_Z_MIN = MDF_THICKNESS + INTERIOR_HEIGHT
    TOP_DRAWER_FACE_EXTRA_HEIGHT = MDF_THICKNESS + SIDE_TOP_LIP
else:  # "on_top"
    TOP_PANEL_WIDTH = WIDTH
    TOP_PANEL_X_MIN = 0
    TOP_PANEL_Y_MIN = 0
    TOP_PANEL_DEPTH = DEPTH
    SIDE_TOP_LIP = 0
    SIDE_HEIGHT = INTERIOR_HEIGHT
    TOP_PANEL_Z_MIN = MDF_THICKNESS + SIDE_HEIGHT
    HEIGHT = TOP_PANEL_Z_MIN + MDF_THICKNESS
    TOP_DRAWER_FACE_EXTRA_HEIGHT = 0

# --- Material / appearance -----------------------------------------------
# Same visible/stock_source convention as furniture/bed (see
# docs/CONTEXT.md): panels visible in the finished piece are new stock,
# hidden ones are reclaimed. Color itself is NOT re-exposed here —
# dresser.py imports colors directly and reads colors.MAIN_COLOR/
# colors.SECOND_COLOR/colors.REUSED_COLOR/colors.part_rgb("body") (see
# colors.py's PART_ROLES for which part uses which role).

# --- Mirror (آینه, optional) -----------------------------------------------
# Wall-mounted, built as part of this same dresser (not a separate
# furniture/ module — orders/combine_order.py only lays items out side
# by side on the floor, with no way to float one above another, so a
# piece meant to hang above the dresser has to be part of the dresser's
# own build instead). HAS_MIRROR off by default — every existing
# STYLE/test/cutlist keeps working unchanged; set HAS_MIRROR=1 to add it.
#
# A plain 4-piece MDF frame (2 rails spanning the full outer width, 2
# stiles fitting between them — butt joints, no miters, buildable with
# just a handsaw and square) around a glued-in mirror pane, centered
# above the dresser's own Top panel by MIRROR_HANG_GAP, flush against
# the same wall plane as the Back panel (Y=DEPTH). The pane sits at the
# frame's own back (against the wall), recessed behind its front face —
# a shallow "shadow box" reveal, the simplest option without a routed
# rabbet; real mounting (mirror mastic/corner clips) isn't modeled, same
# "not worth modeling" convention as the drawer-slide hardware.
#
# Mirror width picked as 2/3 of this dresser's own WIDTH (900mm) — the
# standard 2/3-3/4 proportion for a mirror over a dresser, so it reads
# proportional rather than stranded or top-heavy. Height is a standard
# portrait mirror proportion, not derived from the dresser. Frame border
# narrower than the ~50-75mm standard range, per the user's own request
# (looked too heavy stacked visually right above the dresser).
HAS_MIRROR = bool(int(os.environ.get("HAS_MIRROR", "0")))
# Horizontal position over the dresser's own Top: "center" (default),
# "left" (flush with the dresser's own left side), or "right" (flush with
# the right side) — e.g. useful to shift the mirror away from a
# neighboring item in a combined order.
MIRROR_ALIGN = os.environ.get("MIRROR_ALIGN", "center")
if MIRROR_ALIGN not in ("left", "right", "center"):
    raise ValueError(f"MIRROR_ALIGN must be left/right/center, got {MIRROR_ALIGN!r}")
MIRROR_WIDTH = 600  # TBD: confirm against 2/3-3/4 of WIDTH (900mm)
# Sized so the frame's own top edge lands flush with the wardrobe's own
# ceiling (furniture/wardrobe/params.py's TWO_PIECE_HEIGHT=1800mm) when
# mounted above this dresser in a combined order — not a standard
# portrait-mirror proportion; if HEIGHT/MIRROR_HANG_GAP/
# MIRROR_FRAME_BORDER_WIDTH or the wardrobe's own height changes, this
# needs re-deriving: MIRROR_HEIGHT = 1800 - HEIGHT - MIRROR_HANG_GAP -
# 2 * MIRROR_FRAME_BORDER_WIDTH.
MIRROR_HEIGHT = 722
MIRROR_THICKNESS = 4  # TBD: typical mirror glass (mm)
MIRROR_COLOR = colors.swatch_rgb("glass")
MIRROR_FRAME_BORDER_WIDTH = 40  # TBD: user asked for slimmer than the ~50-75mm standard range
MIRROR_FRAME_THICKNESS = MDF_THICKNESS
MIRROR_HANG_GAP = 150  # TBD: within the 100-200mm standard "above the dresser" range
MIRROR_OUTER_WIDTH = MIRROR_WIDTH + 2 * MIRROR_FRAME_BORDER_WIDTH
MIRROR_OUTER_HEIGHT = MIRROR_HEIGHT + 2 * MIRROR_FRAME_BORDER_WIDTH
