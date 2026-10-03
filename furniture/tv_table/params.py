"""
Single source of truth for every design parameter of the TV table
(میز تلویزیون): a low, trapezoidal corner cabinet (wide front, narrow
back against the wall) with ONE drawer whose Face spans the whole front.
Mirrors furniture/dresser/params.py's shape. Dimensions below are from the
user's own brief (photo tv-table.jpg + sizes, 2026-10-03): trapezoid
parallel sides 1670 / 860, trapezoid height (depth) 400, drawer Face
1670 x 220. The glass shelf on legs visible in the photo is not modeled.

Units: millimeters. Axes: X = left-right, Y = front-back (Y=0 is the
front edge of the trapezoid, the drawer opens toward -Y), Z = height.
"""

import math
import os

import colors

MDF_THICKNESS = 16

# --- Trapezoid footprint (plan view) -----------------------------------
FRONT_WIDTH = int(os.environ.get("FRONT_WIDTH") or 1670)  # long parallel side, at the viewer
BACK_WIDTH = int(os.environ.get("BACK_WIDTH") or 860)  # short parallel side, against the wall
DEPTH = int(os.environ.get("DEPTH") or 400)  # trapezoid height
HEIGHT = int(os.environ.get("HEIGHT") or 220)  # whole body, == drawer Face height

if BACK_WIDTH >= FRONT_WIDTH:
    raise ValueError(f"BACK_WIDTH={BACK_WIDTH} must be smaller than FRONT_WIDTH={FRONT_WIDTH}")

# Each slanted side runs from the front corner inward by this much.
SIDE_INSET = (FRONT_WIDTH - BACK_WIDTH) / 2
# Length of a slanted side's outer edge, and how far one board thickness
# shifts it horizontally (t / sin(angle)) / along Y (t * SIDE_INSET / L).
SIDE_SLANT_LENGTH = math.hypot(SIDE_INSET, DEPTH)
SIDE_HORIZONTAL_THICKNESS = MDF_THICKNESS * SIDE_SLANT_LENGTH / DEPTH

INTERIOR_HEIGHT = HEIGHT - 2 * MDF_THICKNESS

# --- Drawer ------------------------------------------------------------
# The Face covers the whole front (full overlay, flush against Y=0 and
# protruding toward -Y by its own thickness); the drawer box itself is as
# wide as the trapezoid's short side, so it still clears the slanted sides
# all the way back.
FACE_WIDTH = FRONT_WIDTH
FACE_HEIGHT = HEIGHT
FACE_THICKNESS = MDF_THICKNESS

DRAWER_BOTTOM_THICKNESS = 3  # fiber board, same as furniture/dresser
RAIL_CLEARANCE = 13  # per side, slide hardware
RAIL_BACK_CLEARANCE = 20
DRAWER_TOP_REVEAL_GAP = 6
DRAWER_WIDTH = BACK_WIDTH
DRAWER_DEPTH = DEPTH - MDF_THICKNESS - RAIL_BACK_CLEARANCE
DRAWER_CARCASS_HEIGHT = INTERIOR_HEIGHT - DRAWER_BOTTOM_THICKNESS - DRAWER_TOP_REVEAL_GAP


def interior_width_at(y):
    """Clear width between the slanted sides' inner faces at depth y."""
    return FRONT_WIDTH - 2 * (y * SIDE_INSET / DEPTH + SIDE_HORIZONTAL_THICKNESS)


if interior_width_at(DRAWER_DEPTH) < DRAWER_WIDTH + 2 * RAIL_CLEARANCE:
    raise ValueError(
        f"Drawer ({DRAWER_WIDTH} wide, {DRAWER_DEPTH} deep) doesn't clear the slanted "
        f"sides: only {interior_width_at(DRAWER_DEPTH):.0f}mm free at its back"
    )
