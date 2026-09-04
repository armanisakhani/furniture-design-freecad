"""
Single source of truth for every design parameter used by the bed /
drawer-box model. No geometry logic lives here — only named values,
grouped by subject.

Units: millimeters everywhere, unless a name says otherwise.

Anything not yet measured/decided is marked "# TBD" with a placeholder
value that keeps the rest of the model runnable. Update the value here,
never inline in geometry code, once the real number is known.
"""

import os

# --- Style presets ----------------------------------------------------
# Bundles the handful of parameters that vary together for a design
# variant, so switching variants is one env var instead of hand-editing
# several unrelated lines in sync. Select with the STYLE env var, e.g.
# `STYLE=2 make test-bed` or `STYLE=2 ./tools/view_bed.sh --rebuild` —
# default is style 1 (today's baseline). Add a new entry here for a new
# variant. (Env var, not a `--style` CLI flag: freecadcmd's own argument
# parser rejects unrecognized flags unpredictably, but env vars pass
# through untouched to every entry point — freecadcmd, the Makefile,
# view_bed.sh's GUI-launch path — with no extra plumbing.)
# Either knob can still be overridden on top of the selected style with
# its own same-named env var (wins over the style's value):
# `DRAWER_OVERLAY_STYLE=rail_above_drawer`, `MATTRESS_TO_FRAME_GAP_WIDTH=50`.
STYLES = {
    1: dict(drawer_overlay_style="box_over_drawer", mattress_gap_width=0),
    2: dict(drawer_overlay_style="rail_above_drawer", mattress_gap_width=100),
}


def _resolve_style():
    style_id = int(os.environ.get("STYLE") or 1)
    if style_id not in STYLES:
        raise ValueError(f"Unknown STYLE={style_id}; known styles: {sorted(STYLES)}")
    values = dict(STYLES[style_id])
    if os.environ.get("DRAWER_OVERLAY_STYLE"):
        values["drawer_overlay_style"] = os.environ["DRAWER_OVERLAY_STYLE"]
    if os.environ.get("MATTRESS_TO_FRAME_GAP_WIDTH"):
        values["mattress_gap_width"] = int(os.environ["MATTRESS_TO_FRAME_GAP_WIDTH"])
    return values


_style = _resolve_style()

# --- Mattress -----------------------------------------------------------
# LENGTH = head-to-toe direction. WIDTH = side-by-side direction.
MATTRESS_LENGTH = 2000
MATTRESS_WIDTH = 1800

# Visual placeholder in the full-bed assembly (bed.py) only — not a real
# fabrication dimension, the mattress isn't something we build.
MATTRESS_THICKNESS = 300  # confirmed: 30cm

# Offset between the mattress edge and the box frame's outer edge. Kept
# as 2 separate params since the axes aren't symmetric: along LENGTH the
# frame only extends past the mattress at the foot end (head end sits
# flush); along WIDTH the gap is the same on both sides.
MATTRESS_TO_FRAME_GAP_LENGTH = 100  # confirmed: 10cm, foot end only
MATTRESS_TO_FRAME_GAP_WIDTH = _style["mattress_gap_width"]  # confirmed: 10cm, both sides — set per style, see STYLES above

# The mattress-stop strip (bed.py) fills exactly this foot-end gap, lying
# on top of the top panel's surface — its width IS
# MATTRESS_TO_FRAME_GAP_LENGTH, not a separate number.

# --- Frame / box ----------------------------------------------------------
# The bed is BOX_COUNT identical boxes placed side by side along LENGTH.
BOX_COUNT = 3

# Derived: total external footprint of the boxes.
FRAME_LENGTH = MATTRESS_LENGTH + MATTRESS_TO_FRAME_GAP_LENGTH
FRAME_WIDTH = MATTRESS_WIDTH + 2 * MATTRESS_TO_FRAME_GAP_WIDTH

# Clear/interior height of one box: cut height of the 2 long side walls
# and the internal transverse walls (both trapped between top and bottom
# — see box.py). Confirmed against the reference spreadsheet's "کناره"
# and "دیواره عرضی داخلی" rows, which independently agree on this figure.
BOX_INTERIOR_HEIGHT = 250

# MDF board's own thickness (core only, face-to-face), confirmed by the
# user. Drives all box/drawer fitting geometry.
MDF_THICKNESS = 16

# One box's footprint along LENGTH (Y). Not simply FRAME_LENGTH split
# evenly: 1 MDF_THICKNESS is subtracted from the total before splitting,
# shrinking every box equally, so the last box's far wall stops exactly
# 1 MDF_THICKNESS short of FRAME_LENGTH — leaving room for EndFaceFoot
# (bed.py) to sit flush inside that gap without poking out past it.
BOX_LENGTH = (FRAME_LENGTH - MDF_THICKNESS) / BOX_COUNT

# External height of one box (top of top panel to bottom of bottom
# panel): BOX_INTERIOR_HEIGHT plus the top/bottom panels' own thickness,
# since those 2 panels cap over the (shorter) side walls. Derived — set
# BOX_INTERIOR_HEIGHT instead, never this directly.
BOX_HEIGHT = BOX_INTERIOR_HEIGHT + 2 * MDF_THICKNESS

# PVC edge-banding tape thickness, glued onto exposed cut edges. Wraps
# the edge only — does not add to MDF_THICKNESS or affect fitting
# geometry. Reconciles the reference photos' ~20mm apparent wall
# thickness: MDF_THICKNESS (16) + 2 * PVC_THICKNESS (2 + 2) = 20.
PVC_THICKNESS = 2

# --- Drawer -----------------------------------------------------------
DRAWERS_PER_BOX = 2

DRAWER_BOTTOM_THICKNESS = 3  # 3mm fiber board, not structural MDF

# "inset": drawer front flush inside the box opening. "overlay": drawer
# front proud of the box. Building overlay first; inset stays supported
# through this same parameter, just built second.
DRAWER_FRONT_MODE = "overlay"

# The Drawer_box's front is 2 separate panels: a structural front (flush
# with the box opening, part of the carcass, hidden once assembled) plus
# a separate Face panel (نما) attached to it — the one actually visible
# and overlaying. DRAWER_FRONT_OVERLAY_AMOUNT is the Face's own board
# thickness: mounted flush against the structural front, it protrudes by
# its full thickness, so that thickness IS the overlay amount.
DRAWER_FRONT_OVERLAY_AMOUNT = MDF_THICKNESS  # TBD

# Reveal gap between the Face panels of 2 adjacent boxes (Y), so they
# don't rub. Split evenly: each Face is centered in its own box's
# Y-footprint, inset by half this gap on each side.
DRAWER_FACE_GAP = 3  # TBD: placeholder reveal, no real number chosen yet

# In "overlay" mode, 2 physical ways the drawer meets the box, picked via
# DRAWER_OVERLAY_STYLE:
#   "box_over_drawer" (default) — the box's own Top panel extends to
#     FRAME_WIDTH and caps the drawer's Face from above; no separate
#     rail-mount frame consumes height. Matches the user's explicit
#     request that the Top panel itself do this job.
#   "rail_above_drawer" — an unmodeled rail-mount frame sits on top of
#     the drawer and reaches out to meet the Face instead; the Top panel
#     stays flush with the rest of the shell (BOX_WIDTH) and the drawer
#     carcass loses one MDF_THICKNESS of height for that frame.
# In both styles the box shell itself (Bottom, 2 side walls, drawer
# carcasses) is inset from FRAME_WIDTH by MDF_THICKNESS on each X side —
# BOX_WIDTH, below. The Face's own overlay is what reaches back out to
# exactly FRAME_WIDTH.
DRAWER_OVERLAY_STYLE = _style["drawer_overlay_style"]  # or "rail_above_drawer" — set per style, see STYLES above

# Box shell's own X footprint — always inset from FRAME_WIDTH by
# MDF_THICKNESS on each side, regardless of DRAWER_OVERLAY_STYLE. The
# Face panel's overlay closes this gap back up to FRAME_WIDTH (box.py).
BOX_WIDTH = FRAME_WIDTH - 2 * MDF_THICKNESS

# Box shell's X=0 edge, relative to FRAME_WIDTH's own X=0 origin — always
# MDF_THICKNESS in from it.
BOX_SHELL_X_MIN = MDF_THICKNESS

# Vertical gap between the underside of the overhanging top panel and the
# drawer front's top edge, so the drawer can slide without rubbing.
# Ball-bearing side-mount slides (what RAIL_THICKNESS below assumes) need
# only ~6.35mm total vertical clearance, ~3mm above/below — since the
# drawer bottom already sits flush on the box bottom (no "below" gap
# modeled), the full allowance is put here, above.
DRAWER_TOP_REVEAL_GAP = 6  # TBD: matches ball-bearing side-mount convention, confirm w/ datasheet

# Everything that varies by DRAWER_OVERLAY_STYLE, computed together here
# — one seam, one branch per style — instead of re-branching on the style
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
RAIL_LENGTH = 650  # TBD: confirm rail model

# Per-side horizontal clearance between the drawer carcass and the box
# opening, for the slide hardware itself. Side-mount ball-bearing slide
# research (docs/roadmap.md Phase 3) confirms ~13mm/side is the right
# ballpark (commonly cited as ~1/2"-17/32", i.e. 12.7-13.5mm).
RAIL_CLEARANCE = 13  # TBD: per-side clearance from rail datasheet (mm)

# The compartment a slide sits in should run a few mm deeper than the
# slide's own nominal length, so the drawer doesn't jam when fully
# closed. Research (docs/roadmap.md Phase 3) cites ~3-5mm; used here as
# the gap behind each drawer before the internal transverse wall.
RAIL_BACK_CLEARANCE = 5  # TBD: confirm against chosen rail's datasheet

# Metal channel thickness of a standard side-mount ball-bearing slide
# (typically ~12mm/side, slightly less than RAIL_CLEARANCE which also
# includes a small extra running gap). Confirm against the chosen rail's
# datasheet once picked.
RAIL_THICKNESS = 12  # TBD: confirm rail model

# Height from the box's internal bottom face up to the rail's mounting
# line. Standard side-mount slides run just above the drawer bottom
# panel, so this is set just past DRAWER_BOTTOM_THICKNESS to clear it.
RAIL_POSITION_Z = 15  # TBD: confirm against chosen rail + drawer construction

# --- Skirt / apron -----------------------------------------------------
# Thin decorative MDF trim hanging from the underside of the box, near
# the floor — unrelated to drawer position (the drawer lives up near the
# top of the box; see DRAWER_TOP_REVEAL_GAP, a separate parameter).

# Skirt on the two long (drawer-carrying) faces of a box. Always on —
# this is the bed's most visible face. Only covers part of
# LEG_FRAME_HEIGHT; the rest stays open below it for hand clearance
# under the drawer front.
HAS_DRAWER_SIDE_SKIRT = True

# Skirt on the two short (head/foot) end faces, which have no drawer.
# Togglable — purely for visual continuity around the base, not
# functional.
HAS_END_SKIRT = True

# Height of the skirt board itself. The remaining gap below it, down to
# the floor (LEG_FRAME_HEIGHT - SKIRT_HEIGHT), stays open as the
# hand-clearance space for reaching under the handle-less drawer front.
SKIRT_HEIGHT = 20  # confirmed: 2cm

# Independent from MDF_THICKNESS — the skirt is a separate decorative
# board, not a structural box wall, so it may end up a different
# thickness.
SKIRT_THICKNESS = 16  # TBD

# --- Support frame (Model A only: handle-less drawers, opened by hand
# from underneath, so the bed needs to be raised for finger clearance) ----
LEG_FRAME_HEIGHT = 100  # TBD: driven by hand-clearance requirement

# --- Headboard (تاج) -----------------------------------------------------
# A single MDF panel standing at the head end (Y=0 — the end that butts
# against the room's wall), attached to the outer face of the first
# box's SideWallNear, same overlay/attachment pattern as EndFaceFoot but
# mirrored to the other end of the bed (see create_headboard in bed.py).
# Height is measured from the actual floor (Z = -LEG_FRAME_HEIGHT, where
# the leg/support frame ends) up to the panel's own top edge — NOT from
# the box's own bottom (Z=0), which is why this is a separate param
# rather than derived from BOX_HEIGHT/SKIRT_HEIGHT.
HEADBOARD_HEIGHT = 1100  # confirmed: 1.1m total, floor to top edge

# --- Material / appearance -----------------------------------------------
# Color is driven by StockSource first, then role. Any panel with
# StockSource == "reclaimed" (see docs/CONTEXT.md's visible/stock_source
# concept) always gets RECLAIMED_MDF_COLOR, regardless of its role —
# these are hidden panels cut from leftover stock, so their finish only
# matters for being visually distinct in the model. New-stock, visible
# panels get a role-specific color instead:
#   * BODY_COLOR: new-stock Box body panels (currently just the Top panel)
#   * DRAWER_FRONT_COLOR: the Drawer_box's Face (نما) panel only
# A Face never carries the body color, and no other panel carries the
# Face's color.
RECLAIMED_MDF_COLOR = (1.0, 1.0, 1.0)  # confirmed: white

# Estimated by eye from references/colors/1128-misty.jpg ("Misty", code
# 1128) — no exact hex/RAL code given yet, refine if one becomes available.
BODY_COLOR = (0.31, 0.44, 0.50)  # TBD: "Misty" 1128, estimated from swatch

# Estimated by eye from references/colors/1126-brown.jpg ("Brown", code
# 1126) — same caveat as BODY_COLOR above.
DRAWER_FRONT_COLOR = (0.43, 0.35, 0.28)  # TBD: "Brown" 1126, estimated from swatch

WOOD_COLOR = (0.76, 0.60, 0.42)  # decorative wood-toned panels, if used
RAIL_COLOR = (0.5, 0.5, 0.5)   # metal rails / hardware
