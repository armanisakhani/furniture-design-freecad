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

import colors

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
# Any knob can still be overridden on top of the selected style with its
# own same-named env var (wins over the style's value):
# `DRAWER_STYLE=inset`, `MATTRESS_TO_FRAME_GAP_WIDTH=50`, `HAS_LEG_FRAME=0`.
STYLES = {
    1: dict(drawer_style="inset", mattress_gap_width=0, has_leg_frame=False, box_color_by_position=False),
    5: dict(drawer_style="overlay_over_box", mattress_gap_width=0, has_leg_frame=True, box_color_by_position=False),
    2: dict(drawer_style="overlay_under_box", mattress_gap_width=100, has_leg_frame=True, box_color_by_position=False),
    3: dict(drawer_style="inset", mattress_gap_width=100, has_leg_frame=True, box_color_by_position=False),
    4: dict(drawer_style="inset", mattress_gap_width=0, has_leg_frame=True, box_color_by_position=False),
    6: dict(drawer_style="inset", mattress_gap_width=0, has_leg_frame=False, box_color_by_position=True),
}


def _resolve_style():
    style_id = int(os.environ.get("STYLE") or 1)
    if style_id not in STYLES:
        raise ValueError(f"Unknown STYLE={style_id}; known styles: {sorted(STYLES)}")
    values = dict(STYLES[style_id])
    if os.environ.get("DRAWER_STYLE"):
        values["drawer_style"] = os.environ["DRAWER_STYLE"]
    if os.environ.get("MATTRESS_TO_FRAME_GAP_WIDTH"):
        values["mattress_gap_width"] = int(os.environ["MATTRESS_TO_FRAME_GAP_WIDTH"])
    if os.environ.get("HAS_LEG_FRAME"):
        values["has_leg_frame"] = os.environ["HAS_LEG_FRAME"] not in ("0", "false", "False")
    if os.environ.get("BOX_COLOR_BY_POSITION"):
        values["box_color_by_position"] = os.environ["BOX_COLOR_BY_POSITION"] not in ("0", "false", "False")
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

# Whether the Box shell's Bottom + 2 long side walls are cut from new stock
# too (same as the Top panel, which is always new — it bears the mattress)
# instead of reclaimed scrap. A pure cost/logistics choice, independent of
# DRAWER_STYLE/STYLE — off by default (only Top is new; Bottom/side walls
# are reclaimed to save cost, see box.py's create_box). Env var only (not
# part of STYLES) since it's a "how much do I want to spend" toggle
# orthogonal to the style presets: `BOX_SHELL_ALL_NEW=1 make cutlist-bed`.
BOX_SHELL_ALL_NEW = os.environ.get("BOX_SHELL_ALL_NEW", "") not in ("", "0", "false", "False")

# Give every box a single solid color instead of a 2-tone body/
# drawer-front, that color depending on the box's position: the single
# middle box (box_index == BOX_COUNT // 2, only when BOX_COUNT is odd —
# with an even count there's no single middle box, so this has no effect)
# gets colors.MIDDLE_BOX_COLOR, the other (side) boxes get
# colors.SIDE_BOX_COLOR — e.g. a misty middle box between 2 solid-brown
# side boxes. Set per style (STYLE=6 turns it on, see STYLES above); still
# overridable on top of any style with its own env var, same as
# HAS_LEG_FRAME etc: `BOX_COLOR_BY_POSITION=1 make view-bed`. See
# box.py's create_box.
BOX_COLOR_BY_POSITION = _style["box_color_by_position"]

# --- Drawer -----------------------------------------------------------
DRAWERS_PER_BOX = 2

DRAWER_BOTTOM_THICKNESS = 3  # 3mm fiber board, not structural MDF

# How the drawer meets the box — one parameter covering everything that
# used to be 2 separate, independently-settable knobs (DRAWER_OVERLAY_STYLE
# + DRAWER_FRONT_MODE), collapsed once it became clear only 3 of their 2x2
# combinations are real design intents (the 4th, a flush inset front capped
# by an overhanging Top panel, was never used and doesn't correspond to
# anything worth building):
#   "overlay_over_box" (Model A): front (its Face) protrudes past the shell
#     to FRAME_WIDTH — no handle, opened by hand from underneath. The box's
#     own Top panel also reaches out to FRAME_WIDTH and caps the drawer's
#     Face from above; no separate rail-mount frame consumes height.
#   "overlay_under_box": front also protrudes to FRAME_WIDTH, but the Top
#     panel instead stays inset with the rest of the shell (BOX_WIDTH) — an
#     unmodeled rail-mount frame sits above the drawer and reaches out to
#     meet the Face instead ("under": the drawer sits under the box's own
#     top plane, not capped by it), so the drawer carcass loses one
#     MDF_THICKNESS of height to make room for that frame.
#   "inset" (Model B, push-to-open): front doesn't protrude at all — it
#     lands flush with the shell's own open face instead, sized to fill the
#     box's actual interior opening (its only job is covering the hole in
#     the box's face, unrelated to how wide the mechanism behind it happens
#     to be). No handle: opened by pushing the front. Always pairs with the
#     Top panel staying inset, same reasoning as "overlay_under_box" —
#     nothing reaches past the shell here either.
# Set per style, see STYLES above.
DRAWER_STYLE = _style["drawer_style"]  # "overlay_over_box" / "overlay_under_box" / "inset" — set per style, see STYLES above

# The Drawer_box's front is 2 separate panels: a structural front (part of
# the carcass, hidden once assembled) plus a separate Face panel (نما)
# attached to it — the one actually visible. DRAWER_FRONT_OVERLAY_AMOUNT is
# the Face's own board thickness: mounted flush against the structural
# front, it protrudes by its full thickness in the 2 "overlay_*" styles —
# that thickness IS the overlay amount.
DRAWER_FRONT_OVERLAY_AMOUNT = MDF_THICKNESS  # TBD

# Reveal gap between the Face panels of 2 adjacent boxes (Y), so they
# don't rub. Split evenly: each Face is centered in its own box's
# Y-footprint, inset by half this gap on each side. The 2 "overlay_*"
# styles only — see box.py's add_drawer for why "inset" doesn't need it.
DRAWER_FACE_GAP = 3  # TBD: placeholder reveal, no real number chosen yet

# "inset" style only: reveal gap between the Face and the box's own
# opening edges — top/bottom (against Top/Bottom) and each side (against
# the 2 side walls) — so the Face nearly fills the box's actual interior
# opening (BOX_INTERIOR_HEIGHT tall, box_length - 2*MDF_THICKNESS wide)
# with only a minimal clearance to avoid rubbing during push-to-open
# operation, rather than the (much narrower) drawer carcass's own
# footprint. Distinct from DRAWER_FACE_GAP above (that one's the reveal
# BETWEEN 2 adjacent boxes' Faces, along Y only) — this one is WITHIN one
# box's own opening, both axes.
DRAWER_FACE_OPENING_GAP = 3  # TBD: placeholder reveal, no real number chosen yet

# Box shell's own X footprint — always inset from FRAME_WIDTH by
# MDF_THICKNESS on each side, regardless of DRAWER_STYLE. The Face panel's
# overlay closes this gap back up to FRAME_WIDTH in the 2 "overlay_*"
# styles (box.py).
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

# Everything that varies by DRAWER_STYLE, computed together here — one
# seam, one branch per style — instead of re-branching on the style string
# at each dependent call site. See box.py's module docstring for the
# physical reasoning behind each style.
def _drawer_style_geometry(style):
    if style == "overlay_over_box":
        return dict(
            top_panel_width=FRAME_WIDTH,
            top_x_min=0,
            drawer_height_reduction=0,
            face_top_ref_z=BOX_HEIGHT - MDF_THICKNESS,
            front_setback=0,
            front_is_overlay=True,
        )
    elif style == "overlay_under_box":
        return dict(
            top_panel_width=BOX_WIDTH,
            top_x_min=BOX_SHELL_X_MIN,
            drawer_height_reduction=MDF_THICKNESS,
            face_top_ref_z=BOX_HEIGHT,
            front_setback=0,
            front_is_overlay=True,
        )
    elif style == "inset":
        return dict(
            # Unlike the other 2 styles, NOTHING here protrudes past the
            # shell to bridge the BOX_WIDTH -> FRAME_WIDTH gap: "inset"'s
            # own Face deliberately doesn't (that's the point of "inset"),
            # and unlike "overlay_under_box" there's no Face spanning
            # almost the box's whole length to do it incidentally either.
            # So the Top panel — the one thing actually bearing the
            # mattress — has to reach FRAME_WIDTH itself here, exactly like
            # "overlay_over_box", or the mattress silently overhangs
            # unsupported by MDF_THICKNESS on each long edge for the bed's
            # entire length (invisible whenever MATTRESS_TO_FRAME_GAP_WIDTH
            # > 0 already tucks the mattress in short of BOX_WIDTH anyway —
            # caught once STYLE=4 set that gap to 0). Bottom and the 2 side
            # walls stay inset (BOX_WIDTH) regardless — they don't bear the
            # mattress, and their now-visible edge is the intended frame
            # around the recessed drawer (DRAWER_OPENING_EDGE_MATCHES_BODY).
            top_panel_width=FRAME_WIDTH,
            top_x_min=0,
            drawer_height_reduction=MDF_THICKNESS,
            face_top_ref_z=BOX_HEIGHT - MDF_THICKNESS,  # matches the "Top reaches FRAME_WIDTH" family above; unused by "inset" Face sizing itself
            front_setback=DRAWER_FRONT_OVERLAY_AMOUNT,
            front_is_overlay=False,
        )
    raise ValueError(
        f"Unknown DRAWER_STYLE: {style!r}; known styles: "
        "overlay_over_box, overlay_under_box, inset"
    )


_drawer_geometry = _drawer_style_geometry(DRAWER_STYLE)
# Top panel's X footprint/start: flush with FRAME_WIDTH — bearing the
# mattress, it must always reach the true frame edge — in "overlay_over_
# box" and "inset" (nothing else bridges the gap in "inset", see above);
# matches the shell inset instead in "overlay_under_box", where the Face
# already bridges it (spanning nearly the box's whole length).
BOX_TOP_PANEL_WIDTH = _drawer_geometry["top_panel_width"]
BOX_TOP_X_MIN = _drawer_geometry["top_x_min"]
# Bottom + the 2 side walls' own X footprint/start: matches the Top panel
# exactly (so Top always rests on real material, not an unsupported
# overhang) in every style EXCEPT "overlay_over_box" — there, the Top's
# extra reach past BOX_WIDTH is specifically to cap the drawer Face's own
# overlay (see module docstring/CONTEXT.md's "a deliberate deviation from
# the reference, at the user's explicit request"), a mismatch that's fine
# to leave standing since it's driven by that overlay, not by mattress
# support. In "inset" there's no such overlay to justify the gap — caught
# via STYLE=5, where Bottom/the 2 side walls stopped 16mm short of the Top
# panel on each X edge for no structural reason.
BOX_SHELL_PANEL_WIDTH = (
    BOX_WIDTH if DRAWER_STYLE == "overlay_over_box" else BOX_TOP_PANEL_WIDTH
)
BOX_SHELL_PANEL_X_MIN = (
    BOX_SHELL_X_MIN if DRAWER_STYLE == "overlay_over_box" else BOX_TOP_X_MIN
)
# Height the drawer carcass gives up for the unmodeled rail-mount frame in
# "overlay_under_box"/"inset" (0 in "overlay_over_box"). Used by box.py.
DRAWER_HEIGHT_REDUCTION = _drawer_geometry["drawer_height_reduction"]
# Z reference the Face's top edge measures DRAWER_TOP_REVEAL_GAP down from
# — "overlay_*" styles only. Used by box.py.
DRAWER_FACE_TOP_REF_Z = _drawer_geometry["face_top_ref_z"]
# How far the structural front — and with it the whole carcass behind it
# (bottom/sides/back, and by extension where the internal transverse wall
# sits) — is set back from the shell's own open-face plane, along the
# drawer's opening axis (X). The Face always mounts flush against the
# front's own outer face and protrudes outward by DRAWER_FRONT_OVERLAY_AMOUNT
# (box.py); "inset"'s setback absorbs that protrusion entirely so the
# Face's outer surface lands flush with the shell instead of past it — the
# numeric answer to "the drawer needs to sit further back" for
# push-to-open.
DRAWER_FRONT_SETBACK = _drawer_geometry["front_setback"]
# Whether the Face protrudes past the shell ("overlay_over_box"/
# "overlay_under_box") or lands flush with it ("inset"). Used by box.py to
# pick Face sizing (carcass-driven vs. box-opening-driven) and by
# HAS_DRAWER_SIDE_SKIRT/DRAWER_OPENING_EDGE_MATCHES_BODY below.
DRAWER_FRONT_IS_OVERLAY = _drawer_geometry["front_is_overlay"]

# "inset" style only: the box shell panels bordering the drawer opening
# (Bottom, the 2 side walls — Top is already always visible/new) show a
# thin sliver of their own front-facing cut edge around the Face once the
# Face stops reaching out to cover them (see box.py's add_drawer and
# create_box). That edge would carry PVC banding (see CONTEXT.md) to hide
# the raw MDF core — modeled here as a color override only (no separate
# PVC panel object), so it reads as banded to match BODY_COLOR instead of
# showing each panel's own StockSource-based color (their usual
# RECLAIMED_MDF_COLOR/white). Does not change StockSource/PanelVisible —
# only a thin edge is actually visible, not the whole panel's face, so
# there's no reason to re-source the whole board as new stock.
DRAWER_OPENING_EDGE_MATCHES_BODY = not DRAWER_FRONT_IS_OVERLAY

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

# Skirt on the two long (drawer-carrying) faces of a box. Meaningful only
# in the 2 "overlay_*" DRAWER_STYLEs, where the Face panel's own reach
# below the box's bottom does this job (no separate panel — see
# CONTEXT.md). In "inset" (Model B, push-to-open) there is no drawer-side
# skirt at all: the Face doesn't protrude or reach down, so that space
# stays open.
HAS_DRAWER_SIDE_SKIRT = DRAWER_FRONT_IS_OVERLAY

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

# Whether the bed actually sits on a raised leg/support frame at all. Only
# meaningful to turn off for DRAWER_STYLE="inset" (push-to-open never
# needs to reach underneath the drawer, so there's no hand-clearance
# reason to raise the bed) — enforced below, since an "overlay_*" style
# with no leg frame would leave no way to open its handle-less drawers by
# hand. Set per style, see STYLES above.
HAS_LEG_FRAME = _style["has_leg_frame"]
if not HAS_LEG_FRAME and DRAWER_STYLE != "inset":
    raise ValueError(
        f'HAS_LEG_FRAME=False requires DRAWER_STYLE="inset" '
        f"(got {DRAWER_STYLE!r}) — the other styles need the leg frame's "
        "hand clearance to open their handle-less drawers."
    )

# The actual floor's Z coordinate. Normally below the box's own bottom
# (Z=0) by LEG_FRAME_HEIGHT; with no leg frame, the box's own bottom IS
# the floor. bed.py's EndFaceFoot/Headboard measure down from/to this,
# not a hardcoded -LEG_FRAME_HEIGHT, so they land on the actual floor
# either way instead of dangling in mid-air or burying themselves in it.
FLOOR_Z = -LEG_FRAME_HEIGHT if HAS_LEG_FRAME else 0

# --- Headboard (تاج) -----------------------------------------------------
# A single MDF panel standing at the head end (Y=0 — the end that butts
# against the room's wall), attached to the outer face of the first
# box's SideWallNear, same overlay/attachment pattern as EndFaceFoot but
# mirrored to the other end of the bed (see create_headboard in bed.py).
# Height is measured from the actual floor (Z = FLOOR_Z, above) up to the
# panel's own top edge — NOT from the box's own bottom (Z=0), which is why
# this is a separate param rather than derived from BOX_HEIGHT/
# SKIRT_HEIGHT.
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
#
# BODY_COLOR/DRAWER_FRONT_COLOR come from colors.py, which selects a named
# swatch per role (e.g. "misty" body + "brown" front) rather than a raw RGB
# here — see colors.py to try a different combination (COLOR_SCHEME env
# var), e.g. `COLOR_SCHEME=charcoal_front`.
RECLAIMED_MDF_COLOR = colors.swatch_rgb("white")

BODY_COLOR = colors.BODY_COLOR
DRAWER_FRONT_COLOR = colors.DRAWER_FRONT_COLOR

WOOD_COLOR = (0.76, 0.60, 0.42)  # decorative wood-toned panels, if used
RAIL_COLOR = (0.5, 0.5, 0.5)   # metal rails / hardware
