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
"""

import os

import colors

# --- Style presets ----------------------------------------------------
# Mirrors furniture/bed/params.py's STYLES pattern: select with the STYLE
# env var, e.g. `STYLE=2 make view-dresser`. main_color names which of
# colors.COLOR_PAIR is the body color — the other one becomes the drawer
# accent color automatically (see MAIN_COLOR/ALTERNATE_COLOR below).
# Style 1 is today's default (body brown, drawer fronts misty); style 2
# swaps the 2 roles (body misty, drawer fronts brown). Style 3 also
# alternates each drawer's own Face between the 2 colors instead of every
# Face sharing one (see DRAWER_COLOR_PATTERN below). Both main_color and
# drawer_color_pattern can still be overridden on top of the selected
# style with their own same-named env var (MAIN_COLOR /
# DRAWER_COLOR_PATTERN), same as STYLE's own per-knob overrides.
STYLES = {
    1: dict(main_color="brown", drawer_color_pattern="0000"),
    2: dict(main_color="misty", drawer_color_pattern="0000"),
    3: dict(main_color="misty", drawer_color_pattern="0101"),
    4: dict(main_color="misty", drawer_color_pattern="1000"),
}


def _resolve_style():
    style_id = int(os.environ.get("STYLE") or 1)
    if style_id not in STYLES:
        raise ValueError(f"Unknown STYLE={style_id}; known styles: {sorted(STYLES)}")
    values = dict(STYLES[style_id])
    if os.environ.get("MAIN_COLOR"):
        values["main_color"] = os.environ["MAIN_COLOR"]
    if os.environ.get("DRAWER_COLOR_PATTERN"):
        values["drawer_color_pattern"] = os.environ["DRAWER_COLOR_PATTERN"]
    return values


_style = _resolve_style()

# The body color, named directly (e.g. "brown" or "misty") instead of a
# reverse-from-default boolean — per the user's own suggestion. Whichever
# of colors.COLOR_PAIR isn't MAIN_COLOR becomes ALTERNATE_COLOR (the
# drawer accent) automatically.
MAIN_COLOR = _style["main_color"]
if MAIN_COLOR not in colors.COLOR_PAIR:
    raise ValueError(f"Unknown MAIN_COLOR={MAIN_COLOR!r}; must be one of {colors.COLOR_PAIR}")
ALTERNATE_COLOR = next(c for c in colors.COLOR_PAIR if c != MAIN_COLOR)

# Per-drawer Face color, top to bottom, one digit per drawer: '1' = same
# as BODY_COLOR (MAIN_COLOR), '0' = the opposite (DRAWER_FRONT_COLOR /
# ALTERNATE_COLOR) — e.g. "1000" means the topmost drawer matches the
# body, the other 3 don't. Per the user's own suggested config format.
# Length must match DRAWER_COUNT (checked below, once DRAWER_COUNT is
# known). See dresser.py's _add_drawer.
DRAWER_COLOR_PATTERN = _style["drawer_color_pattern"]

# --- Overall footprint ---------------------------------------------------
# X = WIDTH (left-right), Y = DEPTH (front-back). Every drawer opens from
# the Y=0 face. Z = height, floor at Z=0.
WIDTH = 900  # confirmed
DEPTH = 450  # confirmed

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
# top/bottom Face and whatever caps it — the Top panel / toe-kick board),
# so they don't rub. Mirrors furniture/bed's DRAWER_FACE_GAP, just along Z
# here instead of Y.
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

# --- Toe-kick ------------------------------------------------------------
# The whole carcass is raised off the floor by TOE_KICK_HEIGHT (small
# feet, unmodeled — a fabrication/hardware detail, out of scope for this
# first draft per the user), and a thin decorative board fills that gap
# at the front, recessed by TOE_KICK_SETBACK for toe clearance. Same idea
# as furniture/bed's Skirt, just filling the whole raised height instead
# of leaving part of it open (no drawer here needs hand clearance
# underneath, unlike bed's handle-less Model A).
TOE_KICK_HEIGHT = 60  # TBD
TOE_KICK_SETBACK = 20  # TBD: how far back from the front face the toe-kick board sits
TOE_KICK_THICKNESS = 16  # TBD

# --- Top panel / side lip -------------------------------------------------
# The Top panel sits INSET between the 2 side panels (see module
# docstring) instead of resting on top of them.
TOP_PANEL_WIDTH = WIDTH - 2 * MDF_THICKNESS
TOP_PANEL_X_MIN = MDF_THICKNESS

# The Top panel's own front edge also retreats a little (Y), just enough
# to clear the topmost drawer's Face — which rises all the way up to be
# flush with the Left/Right/Back panels' own top edge instead of stopping
# at the Top panel's underside (per the user's brief) — while the rest of
# that drawer's carcass stays the normal DRAWER_CARCASS_HEIGHT, tucked
# below the Top panel same as every other drawer. DRAWER_FRONT_SETBACK is
# exactly the Face's own thickness, i.e. where the Face ends and the
# (normal-height) structural front begins — the Top panel is free to
# start right there with no collision.
TOP_PANEL_Y_MIN = DRAWER_FRONT_SETBACK
TOP_PANEL_DEPTH = DEPTH - TOP_PANEL_Y_MIN

# How far the 2 side panels rise above the Top panel's own finished (top)
# surface — the whole lip is just the side panels themselves running
# taller, no separate frame or tray piece (see module docstring). Front
# and back stay open; only the left/right ends get this lip.
SIDE_TOP_LIP = 10  # confirmed: per the user's brief

# --- Derived: overall interior / exterior height -------------------------
# Height the space available for drawers actually spans (from the top of
# the Bottom panel to the underside of the Top panel) — DRAWER_COUNT
# bands stacked with no gap between them.
INTERIOR_HEIGHT = DRAWER_COUNT * DRAWER_FACE_HEIGHT

# Derived: how tall the 2 side panels (and the Back panel, which spans
# the same Z range) actually are — trapped between the Bottom panel and
# SIDE_TOP_LIP above the Top panel's own finished surface. Taller than
# INTERIOR_HEIGHT by MDF_THICKNESS (the Top panel's own thickness, now
# nested within the sides' height instead of capping them from above) +
# SIDE_TOP_LIP.
SIDE_HEIGHT = INTERIOR_HEIGHT + MDF_THICKNESS + SIDE_TOP_LIP

# Exterior height, floor to the 2 side panels' own top edge (the tallest
# feature — see SIDE_TOP_LIP above).
HEIGHT = TOE_KICK_HEIGHT + MDF_THICKNESS + SIDE_HEIGHT

# How much taller the topmost drawer's own Face is than every other
# drawer's — enough to reach from its normal top edge all the way up to
# the Left/Right/Back panels' own top edge (SIDE_HEIGHT), past where the
# Top panel's own thickness and SIDE_TOP_LIP used to cap it. See
# dresser.py's _add_drawer and TOP_PANEL_Y_MIN above.
TOP_DRAWER_FACE_EXTRA_HEIGHT = MDF_THICKNESS + SIDE_TOP_LIP

# --- Material / appearance -----------------------------------------------
# Same visible/stock_source convention as furniture/bed (see
# docs/CONTEXT.md): panels visible in the finished piece are new stock,
# hidden ones are reclaimed. Per the user's brief: body (carcass) brown,
# drawer fronts (درها) misty (STYLE=1); every drawer's own hidden carcass
# is reclaimed MDF with a separate (fiber) bottom board; every visible
# Face is always new stock regardless of what's reclaimed elsewhere.
RECLAIMED_MDF_COLOR = colors.swatch_rgb("white")
BODY_COLOR = colors.swatch_rgb(MAIN_COLOR)
DRAWER_FRONT_COLOR = colors.swatch_rgb(ALTERNATE_COLOR)
