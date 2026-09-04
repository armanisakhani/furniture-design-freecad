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
"""

import os

import colors

# --- Style presets ----------------------------------------------------
# Mirrors furniture/bed/params.py's STYLES pattern: select with the STYLE
# env var, e.g. `STYLE=2 make view-dresser`. Style 1 is today's default
# (body brown, drawer fronts misty); style 2 swaps the 2 roles (body
# misty, drawer fronts brown) — same idea as furniture/bed's
# MIDDLE_BOX_REVERSE_COLOR toggle, just picked by a style number here
# since the dresser has no other structural variant yet to hang it off of.
# REVERSE_COLORS can still be overridden on top of the selected style with
# its own same-named env var, same as STYLE's own per-knob overrides.
STYLES = {
    1: dict(reverse_colors=False),
    2: dict(reverse_colors=True),
}


def _resolve_style():
    style_id = int(os.environ.get("STYLE") or 1)
    if style_id not in STYLES:
        raise ValueError(f"Unknown STYLE={style_id}; known styles: {sorted(STYLES)}")
    values = dict(STYLES[style_id])
    if os.environ.get("REVERSE_COLORS"):
        values["reverse_colors"] = os.environ["REVERSE_COLORS"] not in ("0", "false", "False")
    return values


_style = _resolve_style()
REVERSE_COLORS = _style["reverse_colors"]

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
# panel.
DRAWER_DEPTH = DEPTH - 2 * MDF_THICKNESS - RAIL_BACK_CLEARANCE

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

# --- Derived: overall interior / exterior height -------------------------
# Height the Left/Right/Back panels actually span (trapped between the
# Bottom and Top panels) — DRAWER_COUNT bands stacked with no gap between
# them.
INTERIOR_HEIGHT = DRAWER_COUNT * DRAWER_FACE_HEIGHT

# Exterior height, floor to the Top panel's own top edge.
HEIGHT = TOE_KICK_HEIGHT + 2 * MDF_THICKNESS + INTERIOR_HEIGHT

# --- Material / appearance -----------------------------------------------
# Same visible/stock_source convention as furniture/bed (see
# docs/CONTEXT.md): panels visible in the finished piece are new stock,
# hidden ones are reclaimed. Per the user's brief: body (carcass) brown,
# drawer fronts (درها) misty (STYLE=1); every drawer's own hidden carcass
# is reclaimed MDF with a separate (fiber) bottom board; every visible
# Face is always new stock regardless of what's reclaimed elsewhere.
RECLAIMED_MDF_COLOR = colors.swatch_rgb("white")
if REVERSE_COLORS:
    BODY_COLOR = colors.DRAWER_FRONT_COLOR
    DRAWER_FRONT_COLOR = colors.BODY_COLOR
else:
    BODY_COLOR = colors.BODY_COLOR
    DRAWER_FRONT_COLOR = colors.DRAWER_FRONT_COLOR

# Whether each drawer's own Face alternates between DRAWER_FRONT_COLOR and
# BODY_COLOR instead of every Face sharing DRAWER_FRONT_COLOR uniformly:
# the topmost drawer gets DRAWER_FRONT_COLOR (the usual accent, "reverse
# of body"), the one right below it gets BODY_COLOR instead, then keeps
# alternating down the stack. Independent of REVERSE_COLORS/STYLE above —
# combines with either. See dresser.py's _add_drawer.
ALTERNATE_DRAWER_COLORS = os.environ.get("ALTERNATE_DRAWER_COLORS", "") not in ("", "0", "false", "False")
