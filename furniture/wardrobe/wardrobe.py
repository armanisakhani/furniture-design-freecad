"""
Wardrobe (کمد لباس): a hanging compartment (2 inset doors, 1 rod) over a
DRAWER_COUNT-drawer section (furniture/dresser's own design, unchanged).
Built from Panel objects (core/panel.py), positioned with Placement so
they butt together using MDF_THICKNESS — same primitives and
visible/stock_source convention as furniture/bed and furniture/dresser.

Global axes: X = WIDTH, Y = DEPTH (drawers/doors open toward -Y, through
the Y=0 face), Z = height, floor at Z=0. See params.py for LAYOUT.
"""

import FreeCAD as App

import params
from core.panel import create_assembly_panel, IDENTITY, ROT_X90, ROT_Y90


def create_wardrobe(doc):
    """Build the wardrobe per params.LAYOUT. Returns the list of all panels."""
    if params.LAYOUT == "one_piece":
        return _create_one_piece(doc)
    return _create_two_piece(doc)


def _make_add_panel(doc, panels):
    def add_panel(obj_name, label, length, width_, thickness, rotation,
                  target_min, material="MDF", color=None,
                  visible=True, stock_source="new"):
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
    return add_panel


def _create_one_piece(doc):
    """One continuous carcass: the same Left/Right/Back panels span both
    the drawer section and the hanging compartment above it."""
    t = params.MDF_THICKNESS
    width = params.WIDTH
    depth = params.DEPTH
    side_height = params.ONE_PIECE_SIDE_HEIGHT

    panels = []
    add_panel = _make_add_panel(doc, panels)

    add_panel(
        "Bottom", "Bottom Panel", width, depth, t,
        IDENTITY, App.Vector(0, 0, 0),
        visible=False, stock_source="reclaimed",
    )
    add_panel(
        "Left", "Left Side Panel", side_height, depth, t,
        ROT_Y90, App.Vector(0, 0, t),
        visible=True, stock_source="new",
    )
    add_panel(
        "Right", "Right Side Panel", side_height, depth, t,
        ROT_Y90, App.Vector(width - t, 0, t),
        visible=True, stock_source="new",
    )
    add_panel(
        "Back", "Back Panel", width, side_height, t,
        ROT_X90, App.Vector(0, depth - t, t),
        visible=False, stock_source="reclaimed",
    )

    drawer_x_min = t + params.RAIL_CLEARANCE
    for index in range(params.DRAWER_COUNT):
        band_z_min = t + index * params.DRAWER_FACE_HEIGHT
        _add_drawer(add_panel, index, drawer_x_min, band_z_min)

    # Divider: inset, closes the drawer section and floors the hanging
    # compartment.
    add_panel(
        "Divider", "Divider Panel", params.INTERIOR_WIDTH, depth, t,
        IDENTITY, App.Vector(t, 0, params.ONE_PIECE_DIVIDER_Z_MIN),
        visible=True, stock_source="new",
    )

    ceiling_z = params.ONE_PIECE_TOP_PANEL_Z_MIN
    _add_rod(add_panel, depth, ceiling_z)

    add_panel(
        "Top", "Top Panel", params.INTERIOR_WIDTH, depth, t,
        IDENTITY, App.Vector(t, 0, ceiling_z),
        visible=True, stock_source="new",
    )

    opening_bottom = params.ONE_PIECE_DIVIDER_Z_MIN + t
    _add_doors(add_panel, opening_bottom, ceiling_z)

    return panels


def _create_two_piece(doc):
    """2 separate freestanding units stacked: a dresser-like bottom unit
    (its own Top panel resting on top of its sides, TOP_PANEL_MODE
    "on_top") with the hanging unit simply resting on top of it."""
    t = params.MDF_THICKNESS
    width = params.WIDTH
    depth = params.DEPTH

    panels = []
    add_panel = _make_add_panel(doc, panels)

    # --- Bottom unit (dresser-like) ---------------------------------
    bottom_side_height = params.BOTTOM_UNIT_SIDE_HEIGHT
    add_panel(
        "Bottom", "Bottom Panel", width, depth, t,
        IDENTITY, App.Vector(0, 0, 0),
        visible=False, stock_source="reclaimed",
    )
    add_panel(
        "BottomLeft", "Bottom Unit - Left Side", bottom_side_height, depth, t,
        ROT_Y90, App.Vector(0, 0, t),
        visible=True, stock_source="new",
    )
    add_panel(
        "BottomRight", "Bottom Unit - Right Side", bottom_side_height, depth, t,
        ROT_Y90, App.Vector(width - t, 0, t),
        visible=True, stock_source="new",
    )
    add_panel(
        "BottomBack", "Bottom Unit - Back", width, bottom_side_height, t,
        ROT_X90, App.Vector(0, depth - t, t),
        visible=False, stock_source="reclaimed",
    )

    drawer_x_min = t + params.RAIL_CLEARANCE
    for index in range(params.DRAWER_COUNT):
        band_z_min = t + index * params.DRAWER_FACE_HEIGHT
        _add_drawer(add_panel, index, drawer_x_min, band_z_min)

    # Full-width, flat: a real surface for the hanging unit to rest on.
    add_panel(
        "BottomTop", "Bottom Unit - Top Panel", width, depth, t,
        IDENTITY, App.Vector(0, 0, params.BOTTOM_UNIT_TOP_PANEL_Z_MIN),
        visible=True, stock_source="new",
    )

    # --- Hanging unit, resting on top of the bottom unit ------------
    base_z = params.BOTTOM_UNIT_HEIGHT
    hanging_side_height = params.HANGING_UNIT_SIDE_HEIGHT

    add_panel(
        "HangingBottom", "Hanging Unit - Bottom", width, depth, t,
        IDENTITY, App.Vector(0, 0, base_z),
        visible=False, stock_source="reclaimed",
    )
    add_panel(
        "HangingLeft", "Hanging Unit - Left Side", hanging_side_height, depth, t,
        ROT_Y90, App.Vector(0, 0, base_z + t),
        visible=True, stock_source="new",
    )
    add_panel(
        "HangingRight", "Hanging Unit - Right Side", hanging_side_height, depth, t,
        ROT_Y90, App.Vector(width - t, 0, base_z + t),
        visible=True, stock_source="new",
    )
    add_panel(
        "HangingBack", "Hanging Unit - Back", width, hanging_side_height, t,
        ROT_X90, App.Vector(0, depth - t, base_z + t),
        visible=False, stock_source="reclaimed",
    )

    ceiling_z = base_z + params.HANGING_UNIT_TOP_PANEL_Z_MIN
    _add_rod(add_panel, depth, ceiling_z)

    add_panel(
        "HangingTop", "Hanging Unit - Top Panel", params.INTERIOR_WIDTH, depth, t,
        IDENTITY, App.Vector(t, 0, ceiling_z),
        visible=True, stock_source="new",
    )

    opening_bottom = base_z + t
    _add_doors(add_panel, opening_bottom, ceiling_z)

    return panels


def _add_rod(add_panel, depth, ceiling_z):
    """Hanging rod, centered front-to-back, ROD_DROP below ceiling_z."""
    t = params.MDF_THICKNESS
    rod_y_min = (depth - params.ROD_THICKNESS) / 2
    rod_z_min = ceiling_z - params.ROD_DROP - params.ROD_THICKNESS
    add_panel(
        "Rod", "Hanging Rod", params.ROD_LENGTH, params.ROD_THICKNESS,
        params.ROD_THICKNESS, IDENTITY,
        App.Vector(t, rod_y_min, rod_z_min),
        material="Metal", color=params.ROD_COLOR,
        visible=True, stock_source="new",
    )


def _add_doors(add_panel, opening_bottom, opening_top):
    """2 Inset doors filling [opening_bottom, opening_top], with a
    DOOR_GAP_Z reveal top/bottom (see params.py for the X-axis split).
    Inset means flush with the shell's own front plane (Y=0) and receding
    INTO the case by DOOR_THICKNESS — same convention as the drawer Face —
    not protruding out past it (that would be Full Overlay)."""
    gap_z = params.DOOR_GAP_Z
    door_z_min = opening_bottom + gap_z / 2
    door_height = (opening_top - opening_bottom) - gap_z

    # Each door's handle sits near its own inner edge (by the center gap,
    # away from the hinge on the outer edge).
    inner_edges = {
        "Left": params.DOOR_LEFT_X_MIN + params.DOOR_WIDTH,
        "Right": params.DOOR_RIGHT_X_MIN,
    }
    for side, x_min in (("Left", params.DOOR_LEFT_X_MIN), ("Right", params.DOOR_RIGHT_X_MIN)):
        add_panel(
            f"Door{side}", f"Door ({side.lower()})",
            params.DOOR_WIDTH, door_height, params.DOOR_THICKNESS, ROT_X90,
            App.Vector(x_min, 0, door_z_min),
            color=params.DOOR_COLOR, visible=True, stock_source="new",
        )
        _add_door_handle(add_panel, side, inner_edges[side], door_z_min, door_height)


def _add_door_handle(add_panel, side, inner_edge_x, door_z_min, door_height):
    """Vertical bar handle (دستگیره), centered on the door's own height,
    near its inner edge — same "bridge pull" shape as the drawer handle
    (2 short posts + a bar), just rotated so the bar's long axis is Z
    instead of X (ROT_X90 puts Width along Z here, vs. IDENTITY's Width
    along Y for the drawer handle's own horizontal bar)."""
    bar_size = params.HANDLE_BAR_SIZE
    standoff = params.HANDLE_STANDOFF
    height = params.DOOR_HANDLE_HEIGHT
    gap = params.DOOR_HANDLE_EDGE_GAP

    center_x = inner_edge_x - gap if side == "Left" else inner_edge_x + gap
    bar_x_min = center_x - bar_size / 2
    handle_z_min = door_z_min + (door_height - height) / 2

    for post_side, z in (("Bottom", handle_z_min), ("Top", handle_z_min + height - bar_size)):
        add_panel(
            f"Door{side}HandlePost{post_side}", f"Door ({side.lower()}) Handle Post ({post_side.lower()})",
            bar_size, standoff, bar_size, IDENTITY,
            App.Vector(bar_x_min, -standoff, z),
            material="Metal", color=params.HANDLE_COLOR,
            visible=True, stock_source="new",
        )
    add_panel(
        f"Door{side}HandleBar", f"Door ({side.lower()}) Handle Bar",
        bar_size, height, bar_size, ROT_X90,
        App.Vector(bar_x_min, -standoff - bar_size, handle_z_min),
        material="Metal", color=params.HANDLE_COLOR,
        visible=True, stock_source="new",
    )


def _add_drawer(add_panel, index, x_min, band_z_min):
    """One Drawer carcass plus its Face (نما) and metal handle —
    furniture/dresser's own design, unchanged. index is 0 at the bottom."""
    t = params.MDF_THICKNESS
    prefix = f"Drawer{index + 1}"
    label_prefix = f"Drawer {index + 1}"

    def p(obj_name, label, *args, **kwargs):
        return add_panel(f"{prefix}_{obj_name}", f"{label_prefix} - {label}", *args, **kwargs)

    carcass_z = band_z_min + params.DRAWER_BOTTOM_THICKNESS
    carcass_height = params.DRAWER_CARCASS_HEIGHT
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

    overlay = params.DRAWER_FRONT_OVERLAY_AMOUNT
    gap_z = params.DRAWER_FACE_GAP_Z
    gap_x = params.DRAWER_FACE_SIDE_GAP
    face_height = params.DRAWER_FACE_HEIGHT - gap_z

    from_top = params.DRAWER_COUNT - 1 - index
    face_color = (
        params.BODY_COLOR if params.DRAWER_COLOR_PATTERN[from_top] == "1"
        else params.DRAWER_FRONT_COLOR
    )
    face_x_min = t + gap_x / 2
    face_z_min = band_z_min + gap_z / 2
    p(
        "Face", "Face", params.DRAWER_FACE_WIDTH, face_height, overlay,
        ROT_X90, App.Vector(face_x_min, setback - overlay, face_z_min),
        color=face_color, visible=True, stock_source="new",
    )

    _add_handle(p, params.DRAWER_FACE_WIDTH, face_x_min, face_height, face_z_min)


def _add_handle(p, face_width, face_x_min, face_height, face_z_min):
    """Metal bar handle (دستگیره), centered on one drawer's Face —
    furniture/dresser's own "bridge pull" design, unchanged."""
    bar_size = params.HANDLE_BAR_SIZE
    standoff = params.HANDLE_STANDOFF
    handle_x_min = face_x_min + (face_width - params.HANDLE_WIDTH) / 2
    handle_z_min = face_z_min + (face_height - bar_size) / 2

    for side, x in (("Left", handle_x_min), ("Right", handle_x_min + params.HANDLE_WIDTH - bar_size)):
        p(
            f"HandlePost{side}", f"Handle Post ({side.lower()})",
            bar_size, standoff, bar_size, IDENTITY,
            App.Vector(x, -standoff, handle_z_min),
            material="Metal", color=params.HANDLE_COLOR,
            visible=True, stock_source="new",
        )
    p(
        "HandleBar", "Handle Bar",
        params.HANDLE_WIDTH, bar_size, bar_size, IDENTITY,
        App.Vector(handle_x_min, -standoff - bar_size, handle_z_min),
        material="Metal", color=params.HANDLE_COLOR,
        visible=True, stock_source="new",
    )
