"""
Single dresser (دراور) carcass: Top, Bottom, Left, Right, Back shell
panels plus a recessed toe-kick board, and DRAWER_COUNT Drawer carcasses
stacked vertically, each opening from the front (Y=0) face. Built from
Panel objects (core/panel.py) and positioned with Placement so they butt
together using MDF_THICKNESS — same primitives and visible/stock_source
convention as furniture/bed (see docs/CONTEXT.md), adapted for a single
front-opening stack instead of furniture/bed's 2 opposite-opening rows.

First draft, for visual review — styled after
references/reference-page8.png's look only (overlay drawer fronts,
visible carcass sides, a recessed toe-kick board), not its connection
hardware (drawer slides, corner brackets, adjustable feet): this design's
own fastening is screws, and slide/feet hardware isn't modeled yet. See
params.py for what's still a placeholder.

Global axes: X = WIDTH (left-right), Y = DEPTH (front-back, drawers open
toward -Y, i.e. out through the Y=0 face), Z = height, floor at Z=0.

Each Drawer's front is 2 separate panels, same convention as
furniture/bed: a structural front (part of the carcass, hidden) plus a
Face (نما) screwed onto it, mounted flush against the structural front and
protruding toward the viewer by its own thickness
(DRAWER_FRONT_OVERLAY_AMOUNT) — the Face spans the dresser's full WIDTH,
overlaying the Left/Right side panels' front edges (same "overlay_over_
box" idea as furniture/bed's default style).
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
    # Bottom/Top: horizontal, full WIDTH x DEPTH footprint, trapped in Z
    # around the Left/Right/Back panels (interior_height apart). Bottom is
    # hidden (underside, never seen); Top is the one always-visible new-
    # stock panel, same role as furniture/bed's Top.
    add_panel(
        "Bottom", "Bottom Panel", width, depth, t,
        IDENTITY, App.Vector(0, 0, bottom_z),
        visible=False, stock_source="reclaimed",
    )
    add_panel(
        "Top", "Top Panel", width, depth, t,
        IDENTITY, App.Vector(0, 0, bottom_z + t + interior_height),
        visible=True, stock_source="new",
    )
    # Left/Right: visible (free-standing piece, unlike furniture/bed's
    # boxes tucked into an assembly), full DEPTH, capped in Z by Bottom/
    # Top at interior_height.
    add_panel(
        "Left", "Left Side Panel", interior_height, depth, t,
        ROT_Y90, App.Vector(0, 0, bottom_z + t),
        visible=True, stock_source="new",
    )
    add_panel(
        "Right", "Right Side Panel", interior_height, depth, t,
        ROT_Y90, App.Vector(width - t, 0, bottom_z + t),
        visible=True, stock_source="new",
    )
    # Back: closes the far (Y=depth) end. Hidden — assumed against a wall.
    add_panel(
        "Back", "Back Panel", width, interior_height, t,
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

    p(
        "Bottom", "Bottom", params.DRAWER_WIDTH, params.DRAWER_DEPTH,
        params.DRAWER_BOTTOM_THICKNESS, IDENTITY,
        App.Vector(x_min, t, band_z_min),
        material="Fiber", visible=False, stock_source="reclaimed",
    )
    p(
        "SideLeft", "Side (left)", carcass_height, params.DRAWER_DEPTH, t,
        ROT_Y90, App.Vector(x_min, t, carcass_z),
        visible=False, stock_source="reclaimed",
    )
    p(
        "SideRight", "Side (right)", carcass_height, params.DRAWER_DEPTH, t,
        ROT_Y90,
        App.Vector(x_min + params.DRAWER_WIDTH - t, t, carcass_z),
        visible=False, stock_source="reclaimed",
    )
    # Structural front: flush with the shell's own open (Y=0) face — the
    # Face panel, added below, is what actually overlays outward.
    p(
        "Front", "Structural Front", params.DRAWER_WIDTH - 2 * t, carcass_height, t,
        ROT_X90, App.Vector(x_min + t, 0, carcass_z),
        visible=False, stock_source="reclaimed",
    )
    p(
        "Back", "Back", params.DRAWER_WIDTH - 2 * t, carcass_height, t,
        ROT_X90,
        App.Vector(x_min + t, t + params.DRAWER_DEPTH - t, carcass_z),
        visible=False, stock_source="reclaimed",
    )

    # Face (نما): flush against the structural front's outer (Y=0) face,
    # protruding toward the viewer (-Y) by its own thickness. Spans the
    # dresser's full WIDTH (overlaying the Left/Right side panels' front
    # edges) and its own DRAWER_FACE_HEIGHT band, inset by DRAWER_FACE_GAP_Z
    # top and bottom for reveal.
    overlay = params.DRAWER_FRONT_OVERLAY_AMOUNT
    gap = params.DRAWER_FACE_GAP_Z
    if params.ALTERNATE_DRAWER_COLORS:
        # Position counted from the top (index is counted from the
        # bottom) — the topmost drawer (from_top=0) gets DRAWER_FRONT_COLOR,
        # then alternates with BODY_COLOR going down.
        from_top = params.DRAWER_COUNT - 1 - index
        face_color = params.DRAWER_FRONT_COLOR if from_top % 2 == 0 else params.BODY_COLOR
    else:
        face_color = params.DRAWER_FRONT_COLOR
    p(
        "Face", "Face", params.WIDTH, params.DRAWER_FACE_HEIGHT - gap, overlay,
        ROT_X90, App.Vector(0, -overlay, band_z_min + gap / 2),
        color=face_color, visible=True, stock_source="new",
    )
