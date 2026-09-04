"""
Single dresser (دراور) carcass: Top, Bottom, Left, Right, Back shell
panels plus a recessed toe-kick board, and DRAWER_COUNT Drawer carcasses
stacked vertically, each opening from the front (Y=0) face. Built from
Panel objects (core/panel.py) and positioned with Placement so they butt
together using MDF_THICKNESS — same primitives and visible/stock_source
convention as furniture/bed (see docs/CONTEXT.md), adapted for a single
front-opening stack instead of furniture/bed's 2 opposite-opening rows.

First draft, for visual review — styled after
references/reference-page8.png's look only (visible carcass sides, a
recessed toe-kick board), not its connection hardware (drawer slides,
corner brackets, adjustable feet) or its Full Overlay drawer fronts (see
below): this design's own fastening is screws, and slide/feet hardware
isn't modeled yet. See params.py for what's still a placeholder.

Global axes: X = WIDTH (left-right), Y = DEPTH (front-back, drawers open
toward -Y, i.e. out through the Y=0 face), Z = height, floor at Z=0.

Each Drawer's front is 2 separate panels, same convention as
furniture/bed: a structural front (part of the carcass, hidden) plus a
Face (نما) screwed onto it, mounted flush against the structural front and
protruding toward the viewer by its own thickness
(DRAWER_FRONT_OVERLAY_AMOUNT). Inset, not Full Overlay (per the user's
explicit brief): the structural front sits back by that same thickness
(DRAWER_FRONT_SETBACK), so the Face's protrusion lands flush with the
shell instead of past it, and the Face itself (DRAWER_FACE_WIDTH) fits
between the Left/Right side panels rather than covering their own front
edge — same "inset" idea as furniture/bed's DRAWER_STYLE="inset". The Top
panel is inset the same way (TOP_PANEL_WIDTH), but the Left/Right/Back
panels run SIDE_TOP_LIP taller than it, so the side panels alone form a
small lip above the Top panel's own surface — no separate frame or tray
piece (see params.py).

The topmost drawer's own Face is taller than the rest by
TOP_DRAWER_FACE_EXTRA_HEIGHT, reaching flush with the Left/Right/Back
panels' own top edge instead of stopping under the Top panel — the Top
panel's own front edge retreats a little (TOP_PANEL_Y_MIN) to make room,
while that drawer's carcass stays the normal size. Each drawer's own Face
color comes from DRAWER_COLOR_PATTERN (params.py).
"""

import FreeCAD as App

import params
from core.panel import create_assembly_panel, IDENTITY, ROT_X90, ROT_Y90


def create_dresser(doc):
    """Create one dresser: shell + toe-kick + DRAWER_COUNT stacked
    drawers, bottom to top. Returns the list of all panels."""
    t = params.MDF_THICKNESS
    width = params.WIDTH
    depth = params.DEPTH
    interior_height = params.INTERIOR_HEIGHT
    side_height = params.SIDE_HEIGHT
    bottom_z = params.TOE_KICK_HEIGHT

    panels = []

    def add_panel(obj_name, label, length, width_, thickness, rotation,
                  target_min, material="MDF", color=None,
                  visible=True, stock_source="new"):
        # core.panel.create_assembly_panel supplies the stock_source ->
        # color default rule (CONTEXT.md); this module's own colors
        # (RECLAIMED_MDF_COLOR/BODY_COLOR, from params.py) are passed in.
        obj = create_assembly_panel(
            doc, obj_name, label,
            length, width_, thickness, rotation, target_min,
            material=material, color=color, visible=visible,
            stock_source=stock_source,
            reclaimed_color=params.RECLAIMED_MDF_COLOR,
            new_color=params.BODY_COLOR,
        )
        panels.append(obj)
        return obj

    # --- Shell ------------------------------------------------------
    # Bottom: horizontal, full WIDTH x DEPTH footprint — the Left/Right
    # panels rest on top of its 2 edges. Hidden (underside, never seen).
    add_panel(
        "Bottom", "Bottom Panel", width, depth, t,
        IDENTITY, App.Vector(0, 0, bottom_z),
        visible=False, stock_source="reclaimed",
    )
    # Top: inset BETWEEN the Left/Right panels (TOP_PANEL_WIDTH), not
    # resting on top of them — see module docstring. Its own front edge
    # also retreats a little (TOP_PANEL_Y_MIN) to clear the topmost
    # drawer's taller Face (see _add_drawer). Still the one always-
    # visible new-stock panel, same role as furniture/bed's Top.
    add_panel(
        "Top", "Top Panel", params.TOP_PANEL_WIDTH, params.TOP_PANEL_DEPTH, t,
        IDENTITY,
        App.Vector(params.TOP_PANEL_X_MIN, params.TOP_PANEL_Y_MIN, bottom_z + t + interior_height),
        visible=True, stock_source="new",
    )
    # Left/Right: visible (free-standing piece, unlike furniture/bed's
    # boxes tucked into an assembly), full DEPTH, running side_height tall
    # — SIDE_TOP_LIP taller than the Top panel's own surface, forming the
    # lip on each end by themselves (no separate part).
    add_panel(
        "Left", "Left Side Panel", side_height, depth, t,
        ROT_Y90, App.Vector(0, 0, bottom_z + t),
        visible=True, stock_source="new",
    )
    add_panel(
        "Right", "Right Side Panel", side_height, depth, t,
        ROT_Y90, App.Vector(width - t, 0, bottom_z + t),
        visible=True, stock_source="new",
    )
    # Back: closes the far (Y=depth) end, same side_height as Left/Right
    # so the carcass stays fully enclosed up to the lip. Hidden — assumed
    # against a wall.
    add_panel(
        "Back", "Back Panel", width, side_height, t,
        ROT_X90, App.Vector(0, depth - t, bottom_z + t),
        visible=False, stock_source="reclaimed",
    )
    # Toe-kick: fills the raised gap at the front only, recessed by
    # TOE_KICK_SETBACK for toe clearance (see params.py) — the feet/legs
    # doing the actual raising aren't modeled yet.
    add_panel(
        "ToeKick", "Toe-Kick Board", width, params.TOE_KICK_HEIGHT,
        params.TOE_KICK_THICKNESS, ROT_X90,
        App.Vector(0, params.TOE_KICK_SETBACK, 0),
        visible=True, stock_source="new",
    )

    # --- Drawers ------------------------------------------------------
    # All drawers share the same X span (inset from WIDTH by the shell's
    # own Left/Right walls, then RAIL_CLEARANCE for slide hardware);  only
    # the Z band changes per drawer.
    drawer_x_min = t + params.RAIL_CLEARANCE
    for index in range(params.DRAWER_COUNT):
        band_z_min = bottom_z + t + index * params.DRAWER_FACE_HEIGHT
        _add_drawer(add_panel, index, drawer_x_min, band_z_min)

    return panels


def _add_drawer(add_panel, index, x_min, band_z_min):
    """One Drawer carcass (bottom, 2 sides, structural front, back) plus
    its Face (نما), inside the DRAWER_FACE_HEIGHT band starting at
    band_z_min. index is 0 at the bottom, growing upward. add_panel
    already appends every created panel to the caller's own list — this
    just prefixes obj_name/label per drawer, no separate list of its own."""
    t = params.MDF_THICKNESS
    prefix = f"Drawer{index + 1}"
    label_prefix = f"Drawer {index + 1}"

    def p(obj_name, label, *args, **kwargs):
        return add_panel(f"{prefix}_{obj_name}", f"{label_prefix} - {label}", *args, **kwargs)

    carcass_z = band_z_min + params.DRAWER_BOTTOM_THICKNESS
    carcass_height = params.DRAWER_CARCASS_HEIGHT
    # Inset (per the user's brief): the whole carcass recedes from the
    # shell's own open face (Y=0) by the Face's own thickness, so the
    # Face's protrusion (added below) lands flush with the shell instead
    # of past it — see params.py's DRAWER_FRONT_SETBACK.
    setback = params.DRAWER_FRONT_SETBACK

    p(
        "Bottom", "Bottom", params.DRAWER_WIDTH, params.DRAWER_DEPTH,
        params.DRAWER_BOTTOM_THICKNESS, IDENTITY,
        App.Vector(x_min, t + setback, band_z_min),
        material="Fiber", visible=False, stock_source="reclaimed",
    )
    p(
        "SideLeft", "Side (left)", carcass_height, params.DRAWER_DEPTH, t,
        ROT_Y90, App.Vector(x_min, t + setback, carcass_z),
        visible=False, stock_source="reclaimed",
    )
    p(
        "SideRight", "Side (right)", carcass_height, params.DRAWER_DEPTH, t,
        ROT_Y90,
        App.Vector(x_min + params.DRAWER_WIDTH - t, t + setback, carcass_z),
        visible=False, stock_source="reclaimed",
    )
    # Structural front: set back from the shell's own open (Y=0) face by
    # `setback` — the Face panel, added below, is what actually lands
    # flush at Y=0.
    p(
        "Front", "Structural Front", params.DRAWER_WIDTH - 2 * t, carcass_height, t,
        ROT_X90, App.Vector(x_min + t, setback, carcass_z),
        visible=False, stock_source="reclaimed",
    )
    p(
        "Back", "Back", params.DRAWER_WIDTH - 2 * t, carcass_height, t,
        ROT_X90,
        App.Vector(x_min + t, setback + params.DRAWER_DEPTH, carcass_z),
        visible=False, stock_source="reclaimed",
    )

    # Face (نما): mounted flush against the structural front's own outer
    # face and protruding toward the viewer (-Y) by its own thickness —
    # since the front already sits back by that same thickness (setback),
    # the Face's own outer surface lands exactly at Y=0, flush with the
    # shell (Inset, not Full Overlay). Sized to DRAWER_FACE_WIDTH — fits
    # BETWEEN the Left/Right side panels rather than covering their own
    # front edge — and its own DRAWER_FACE_HEIGHT band, inset by
    # DRAWER_FACE_GAP_Z top/bottom and DRAWER_FACE_SIDE_GAP left/right for
    # reveal. The topmost drawer's Face is taller by
    # TOP_DRAWER_FACE_EXTRA_HEIGHT, reaching flush with the Left/Right/
    # Back panels' own top edge instead of stopping under the Top panel
    # (see params.py) — its own bottom edge/carcass are unaffected.
    overlay = params.DRAWER_FRONT_OVERLAY_AMOUNT
    gap_z = params.DRAWER_FACE_GAP_Z
    gap_x = params.DRAWER_FACE_SIDE_GAP
    is_top_drawer = index == params.DRAWER_COUNT - 1
    face_height = params.DRAWER_FACE_HEIGHT - gap_z
    if is_top_drawer:
        face_height += params.TOP_DRAWER_FACE_EXTRA_HEIGHT

    # Face color from DRAWER_COLOR_PATTERN (params.py): one '0'/'1' digit
    # per drawer, top to bottom — '1' matches BODY_COLOR, '0' is
    # DRAWER_FRONT_COLOR. index counts from the bottom, so flip it to read
    # the pattern string from the top.
    from_top = params.DRAWER_COUNT - 1 - index
    face_color = (
        params.BODY_COLOR if params.DRAWER_COLOR_PATTERN[from_top] == "1"
        else params.DRAWER_FRONT_COLOR
    )
    p(
        "Face", "Face", params.DRAWER_FACE_WIDTH, face_height, overlay,
        ROT_X90, App.Vector(t + gap_x / 2, setback - overlay, band_z_min + gap_z / 2),
        color=face_color, visible=True, stock_source="new",
    )
