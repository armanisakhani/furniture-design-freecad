"""
Single source of truth for every design parameter of the TV table
(میز تلویزیون): a low trapezoidal corner unit (wide front, narrow
back against the wall): ONE drawer whose Face spans the whole front, an
MDF trapezoid Top over it, and a second MDF trapezoid shelf on metal legs.
Mirrors furniture/dresser/params.py's shape. Dimensions below are from the
user's own brief (photo tv-table.jpg + sizes, 2026-10-03): trapezoid
parallel sides 1670 / 860, trapezoid height (depth) 400, drawer Face
1670 x 220.

Units: millimeters. Axes: X = left-right, Y = front-back (Y=0 is the
front edge of the trapezoid, the drawer opens toward -Y), Z = height.
"""

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

# Each slanted edge of the trapezoid runs inward from its front corner by this much.
SIDE_INSET = (FRONT_WIDTH - BACK_WIDTH) / 2

INTERIOR_HEIGHT = HEIGHT - MDF_THICKNESS  # drawer's own room: floor to the Top panel's underside

# --- Upper shelf ----------------------------------------------------------
# The photo's 2nd tier: a second MDF trapezoid (same size as the Top) on
# metal legs above the cabinet. Leg sizes/positions are estimates from
# tv-table.jpg (TBD — not given by the user).
HAS_SHELF = os.environ.get("HAS_SHELF", "1") not in ("0", "false", "False")
SHELF_THICKNESS = MDF_THICKNESS
SHELF_LEG_HEIGHT = int(os.environ.get("SHELF_LEG_HEIGHT") or 80)  # TBD: gap between the cabinet Top and the shelf
SHELF_LEG_SIZE = 25  # TBD: square metal post standing in for the round chrome leg
SHELF_LEG_SETBACK = 50  # TBD: leg center's distance from the front/back edge
SHELF_LEG_SIDE_FRACTION = 0.12  # TBD: side legs sit this fraction of the width in from each slanted edge
LEG_COLOR = colors.swatch_rgb("metal")

# --- Drawer ------------------------------------------------------------
# The whole body is just the drawer + the Top trapezoid above it (no
# floor, sides or back, per the user). The Face covers the whole front
# (full overlay, flush against Y=0 and protruding toward -Y by its own
# thickness); the drawer box itself is as wide as the trapezoid's short
# side, so it stays under the Top all the way back.
FACE_WIDTH = FRONT_WIDTH
FACE_HEIGHT = HEIGHT
FACE_THICKNESS = MDF_THICKNESS

DRAWER_BOTTOM_THICKNESS = 3  # fiber board, same as furniture/dresser
RAIL_CLEARANCE = 13  # per side, slide hardware
RAIL_BACK_CLEARANCE = 20
DRAWER_TOP_REVEAL_GAP = 6
DRAWER_WIDTH = BACK_WIDTH
DRAWER_DEPTH = DEPTH - RAIL_BACK_CLEARANCE
DRAWER_CARCASS_HEIGHT = INTERIOR_HEIGHT - DRAWER_BOTTOM_THICKNESS - DRAWER_TOP_REVEAL_GAP
