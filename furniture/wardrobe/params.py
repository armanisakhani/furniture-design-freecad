"""
Single source of truth for every design parameter used by the wardrobe
(کمد لباس) model. No geometry logic lives here — only named values, grouped
by subject. Mirrors furniture/dresser/params.py's shape.

Units: millimeters everywhere, unless a name says otherwise.

The drawer section reuses furniture/dresser's own design unchanged (inset
Face, metal bar handle, DRAWER_COUNT=4). The hanging compartment (rod + 2
doors) is new. Doors and the drawer Face are always Inset (fit BETWEEN the
Left/Right side panels, which stay visible), never Full Overlay.

LAYOUT (set per-STYLE below, or directly via its own env var) picks one of
2 physical arrangements:
  "one_piece" (default): one continuous carcass — the same Left/Right/Back
    panels span both the drawer section and the hanging compartment.
  "two_piece": 2 separate freestanding units stacked — a dresser-like unit
    and the hanging unit (each own Bottom/Left/Right/Back/Top) simply
    resting on top of it, not fastened together.

Every Top panel (the outermost ceiling, both layouts) is Full Overlay —
a full WIDTH x DEPTH slab resting ON TOP of the Left/Right/Back panels,
never inset between them like furniture/dresser's own Top. The internal
Divider (one_piece) and the bottom unit's own Top (two_piece) stay as
they were.

All dimensions below are "# TBD" placeholders — first draft, for visual
review.
"""

import os

import colors

# --- Style presets ----------------------------------------------------
# Select with the STYLE env var. main_color names which of colors.COLOR_PAIR
# is the body color; the other becomes the drawer/door accent automatically.
# color_pattern is "<door digit>_<drawer pattern>", e.g. "1_1000": the
# digit before "_" picks the doors' color (same '1'=body/'0'=accent
# convention as the drawer pattern after it, one digit per drawer top to
# bottom). layout is one of LAYOUT's own 2 values (see below).
STYLES = {
    1: dict(main_color="misty", color_pattern="0_1111", layout="two_piece"),
    2: dict(main_color="misty", color_pattern="0_1111", layout="one_piece"),
}


def _resolve_style():
    style_id = int(os.environ.get("STYLE") or 1)
    if style_id not in STYLES:
        raise ValueError(f"Unknown STYLE={style_id}; known styles: {sorted(STYLES)}")
    values = dict(STYLES[style_id])
    if os.environ.get("MAIN_COLOR"):
        values["main_color"] = os.environ["MAIN_COLOR"]
    if os.environ.get("COLOR_PATTERN"):
        values["color_pattern"] = os.environ["COLOR_PATTERN"]
    if os.environ.get("LAYOUT"):
        values["layout"] = os.environ["LAYOUT"]
    return values


_style = _resolve_style()

MAIN_COLOR = _style["main_color"]
if MAIN_COLOR not in colors.COLOR_PAIR:
    raise ValueError(f"Unknown MAIN_COLOR={MAIN_COLOR!r}; must be one of {colors.COLOR_PAIR}")
ALTERNATE_COLOR = next(c for c in colors.COLOR_PAIR if c != MAIN_COLOR)

_door_digit, DRAWER_COLOR_PATTERN = _style["color_pattern"].split("_")
if _door_digit not in "01":
    raise ValueError(f"color_pattern's door digit must be '0' or '1', got {_door_digit!r}")
DOOR_COLOR_DIGIT = _door_digit

# --- Layout -------------------------------------------------------------
LAYOUT = _style["layout"]
if LAYOUT not in ("one_piece", "two_piece"):
    raise ValueError(f"Unknown LAYOUT={LAYOUT!r}; must be 'one_piece' or 'two_piece'")

# --- Overall footprint ---------------------------------------------------
WIDTH = 800  # TBD
DEPTH = 550  # confirmed: matches furniture/dresser's own DEPTH
MDF_THICKNESS = 16  # confirmed: same board as furniture/bed and furniture/dresser
DRAWER_BOTTOM_THICKNESS = 3

# Span between the Left/Right panels' own inner faces — anything inset
# (Top/Divider/Bottom panels of the hanging unit, doors) fits within this.
INTERIOR_WIDTH = WIDTH - 2 * MDF_THICKNESS

# --- Drawers (furniture/dresser's own design, reused unchanged) ---------
DRAWER_COUNT = 4  # confirmed: same as furniture/dresser

if len(DRAWER_COLOR_PATTERN) != DRAWER_COUNT or any(c not in "01" for c in DRAWER_COLOR_PATTERN):
    raise ValueError(
        f"color_pattern's drawer part {DRAWER_COLOR_PATTERN!r} must be a "
        f"string of {DRAWER_COUNT} '0'/'1' characters (one per drawer, top "
        f"to bottom) — got length {len(DRAWER_COLOR_PATTERN)}"
    )

DRAWER_FACE_HEIGHT = 200  # TBD
DRAWER_FACE_GAP_Z = 3  # TBD: reveal between stacked Face panels
DRAWER_FRONT_OVERLAY_AMOUNT = MDF_THICKNESS
DRAWER_FRONT_SETBACK = DRAWER_FRONT_OVERLAY_AMOUNT
DRAWER_FACE_SIDE_GAP = 3  # TBD: reveal between the Face and the 2 side panels
DRAWER_FACE_WIDTH = INTERIOR_WIDTH - DRAWER_FACE_SIDE_GAP

HANDLE_WIDTH = 232  # confirmed: Shahre Yaragh/Meloni handle, 192mm screw-center size
HANDLE_BAR_SIZE = 10  # TBD: bar cross-section (mm)
HANDLE_STANDOFF = 25  # TBD: projection from the Face (mm)
HANDLE_COLOR = colors.swatch_rgb("metal")

RAIL_CLEARANCE = 13  # TBD: per-side clearance from rail datasheet (mm)
RAIL_BACK_CLEARANCE = 20  # TBD
DRAWER_TOP_REVEAL_GAP = 6  # TBD

DRAWER_CARCASS_HEIGHT = (
    DRAWER_FACE_HEIGHT - DRAWER_BOTTOM_THICKNESS - DRAWER_TOP_REVEAL_GAP
)
DRAWER_DEPTH = DEPTH - 2 * MDF_THICKNESS - RAIL_BACK_CLEARANCE - DRAWER_FRONT_SETBACK
DRAWER_WIDTH = WIDTH - 2 * MDF_THICKNESS - 2 * RAIL_CLEARANCE

# Total height the DRAWER_COUNT stacked drawers occupy.
DRAWER_SECTION_HEIGHT = DRAWER_COUNT * DRAWER_FACE_HEIGHT

# --- Hanging compartment --------------------------------------------------
# Sized (with DRAWER_SECTION_HEIGHT below) so the assembled wardrobe's
# total height lands around 1800mm.
HANGING_INTERIOR_HEIGHT = 936  # TBD

# Hanging rod (میله آویز): a square metal bar standing in for a round rod
# (box-only Panel primitive, like the drawer handle's own bar). No
# mounting brackets modeled (real hardware, not worth modeling).
ROD_THICKNESS = 20  # TBD
ROD_DROP = 70  # TBD: gap from the compartment's own ceiling to the rod's top face
ROD_LENGTH = INTERIOR_WIDTH
ROD_COLOR = colors.swatch_rgb("metal")

# --- Doors (Inset, not Full Overlay) -------------------------------------
# 2 doors fit BETWEEN the Left/Right side panels (like the drawer Face),
# hinged on their outer edges (hinges/pulls unmodeled — real hardware, not
# worth modeling yet).
DOOR_GAP = 3  # TBD: reveal between the 2 doors
DOOR_SIDE_GAP = 3  # TBD: reveal between each door and the side panel next to it
DOOR_GAP_Z = 3  # TBD: reveal above/below each door
DOOR_THICKNESS = MDF_THICKNESS

# Derived: each door's own width and X position, split from INTERIOR_WIDTH.
DOOR_WIDTH = (INTERIOR_WIDTH - DOOR_SIDE_GAP - DOOR_GAP) / 2
DOOR_LEFT_X_MIN = MDF_THICKNESS + DOOR_SIDE_GAP / 2
DOOR_RIGHT_X_MIN = DOOR_LEFT_X_MIN + DOOR_WIDTH + DOOR_GAP

# Each door gets a vertical bar handle near its own inner edge (by the
# center gap, away from the hinge) — same "bridge pull" hardware as the
# drawer handles (HANDLE_BAR_SIZE/HANDLE_STANDOFF/HANDLE_COLOR), just
# oriented vertically.
DOOR_HANDLE_HEIGHT = 160  # TBD: vertical handle length
DOOR_HANDLE_EDGE_GAP = 40  # TBD: door's inner edge to the handle's own center line

# --- Derived: one_piece heights ------------------------------------------
# One continuous carcass: Bottom -> DRAWER_COUNT drawers -> Divider (inset,
# closes the drawer section / floors the hanging compartment) -> hanging
# compartment -> Top (on top, full width — see module docstring). The
# sides stop where the hanging compartment does; the Top panel then adds
# its own thickness on top of that.
ONE_PIECE_SIDE_HEIGHT = DRAWER_SECTION_HEIGHT + MDF_THICKNESS + HANGING_INTERIOR_HEIGHT
ONE_PIECE_HEIGHT = MDF_THICKNESS + ONE_PIECE_SIDE_HEIGHT + MDF_THICKNESS
ONE_PIECE_DIVIDER_Z_MIN = MDF_THICKNESS + DRAWER_SECTION_HEIGHT
ONE_PIECE_TOP_PANEL_Z_MIN = MDF_THICKNESS + ONE_PIECE_SIDE_HEIGHT

# --- Derived: two_piece heights -------------------------------------------
# Bottom unit: furniture/dresser's own shape with TOP_PANEL_MODE="on_top".
BOTTOM_UNIT_SIDE_HEIGHT = DRAWER_SECTION_HEIGHT
BOTTOM_UNIT_HEIGHT = MDF_THICKNESS + BOTTOM_UNIT_SIDE_HEIGHT + MDF_THICKNESS
BOTTOM_UNIT_TOP_PANEL_Z_MIN = MDF_THICKNESS + BOTTOM_UNIT_SIDE_HEIGHT

# Hanging unit: a standalone box, Bottom (full) below + Top (on top, full
# width) above, just with a rod instead of drawers. Z values below are
# relative to this unit's own floor (Z=0); wardrobe.py offsets them by
# BOTTOM_UNIT_HEIGHT when placing it.
HANGING_UNIT_SIDE_HEIGHT = HANGING_INTERIOR_HEIGHT
HANGING_UNIT_HEIGHT = MDF_THICKNESS + HANGING_UNIT_SIDE_HEIGHT + MDF_THICKNESS
HANGING_UNIT_TOP_PANEL_Z_MIN = MDF_THICKNESS + HANGING_UNIT_SIDE_HEIGHT

# Combined height of the 2 stacked units.
TWO_PIECE_HEIGHT = BOTTOM_UNIT_HEIGHT + HANGING_UNIT_HEIGHT

# --- Material / appearance -----------------------------------------------
RECLAIMED_MDF_COLOR = colors.swatch_rgb("white")
BODY_COLOR = colors.swatch_rgb(MAIN_COLOR)
DRAWER_FRONT_COLOR = colors.swatch_rgb(ALTERNATE_COLOR)
DOOR_COLOR = BODY_COLOR if DOOR_COLOR_DIGIT == "1" else DRAWER_FRONT_COLOR
