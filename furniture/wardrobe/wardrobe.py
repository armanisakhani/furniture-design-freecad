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

import colors
import params
from core.panel import create_assembly_panel, IDENTITY, ROT_X90, ROT_Y90


def create_wardrobe(doc):
    """Build the wardrobe per params.LAYOUT. Returns the list of all panels."""
    if params.LAYOUT == "one_piece":
        return _create_one_piece(doc)
    return _create_two_piece(doc)


def _make_add_panel(doc, panels):
    def add_panel(obj_name, label, length, width_, thickness, rotation,
                  target_min, material="MDF", color=None, edge_color=None,
                  visible=True, stock_source="new"):
        # Every call below that isn't reclaimed/hidden passes its own
        # explicit color (colors.py's part_override_rgb, per
        # part_roles.yaml) — new_color here is just a safety-net default,
        # not expected to actually be used.
        obj = create_assembly_panel(
            doc, obj_name, label,
            length, width_, thickness, rotation, target_min,
            material=material, color=color, edge_color=edge_color, visible=visible,
            stock_source=stock_source,
            reclaimed_color=colors.REUSED_COLOR,
            new_color=colors.REUSED_COLOR,
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
        color=colors.part_override_rgb("bottom"), visible=False,
        stock_source="reclaimed" if colors.part_effective_role("bottom") == "reused" else "new",
    )
    add_panel(
        "Left", "Left Side Panel", side_height, depth, t,
        ROT_Y90, App.Vector(0, 0, t),
        color=colors.part_override_rgb("left"), visible=True, stock_source="new",
    )
    add_panel(
        "Right", "Right Side Panel", side_height, depth, t,
        ROT_Y90, App.Vector(width - t, 0, t),
        color=colors.part_override_rgb("right"), visible=True, stock_source="new",
    )
    add_panel(
        "Back", "Back Panel", width, side_height, t,
        ROT_X90, App.Vector(0, depth - t, t),
        color=colors.part_override_rgb("back"), visible=False,
        stock_source="reclaimed" if colors.part_effective_role("back") == "reused" else "new",
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
        color=colors.part_override_rgb("top"), visible=True, stock_source="new",
    )

    ceiling_z = params.ONE_PIECE_TOP_PANEL_Z_MIN
    _add_rod(add_panel, depth, ceiling_z)

    add_panel(
        "Top", "Top Panel", width, depth, t,
        IDENTITY, App.Vector(0, 0, ceiling_z),
        color=colors.part_override_rgb("top"), visible=True, stock_source="new",
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
        color=colors.part_override_rgb("bottom"), visible=False,
        stock_source="reclaimed" if colors.part_effective_role("bottom") == "reused" else "new",
    )
    add_panel(
        "BottomLeft", "Bottom Unit - Left Side", bottom_side_height, depth, t,
        ROT_Y90, App.Vector(0, 0, t),
        color=colors.part_override_rgb("left"), visible=True, stock_source="new",
    )
    add_panel(
        "BottomRight", "Bottom Unit - Right Side", bottom_side_height, depth, t,
        ROT_Y90, App.Vector(width - t, 0, t),
        color=colors.part_override_rgb("right"), visible=True, stock_source="new",
    )
    add_panel(
        "BottomBack", "Bottom Unit - Back", width, bottom_side_height, t,
        ROT_X90, App.Vector(0, depth - t, t),
        color=colors.part_override_rgb("back"), visible=False,
        stock_source="reclaimed" if colors.part_effective_role("back") == "reused" else "new",
    )

    drawer_x_min = t + params.RAIL_CLEARANCE
    for index in range(params.DRAWER_COUNT):
        band_z_min = t + index * params.DRAWER_FACE_HEIGHT
        _add_drawer(add_panel, index, drawer_x_min, band_z_min)

    # Full-width, flat: a real surface for the hanging unit to rest on.
    # Sandwiched at the seam with HangingBottom below — its own big flat
    # faces are hidden inside that sandwich (cut from reclaimed stock,
    # own "bottom_top" role, own color independent of everything else),
    # but its cut-edge perimeter IS exposed right at the seam, so that
    # edge always matches "main" regardless (core/panel.py's EdgeColor —
    # a real per-face color, not a second overlapping object), same idea
    # as furniture/bed's box_edge_band role (see CONTEXT.md).
    add_panel(
        "BottomTop", "Bottom Unit - Top Panel", width, depth, t,
        IDENTITY, App.Vector(0, 0, params.BOTTOM_UNIT_TOP_PANEL_Z_MIN),
        color=colors.part_override_rgb("bottom_top"), edge_color=colors.role_rgb("main"),
        visible=True,
        stock_source="reclaimed" if colors.part_effective_role("bottom_top") == "reused" else "new",
    )

    # --- Hanging unit, resting on top of the bottom unit ------------
    base_z = params.BOTTOM_UNIT_HEIGHT
    hanging_side_height = params.HANGING_UNIT_SIDE_HEIGHT

    add_panel(
        # Same seam-sandwich reasoning as BottomTop above, mirrored (this
        # one sits ON TOP of BottomTop instead of below it) — own hidden
        # body (own "hanging_bottom" role) cut from reclaimed stock, own
        # cut-edge perimeter always "main" at the exposed seam.
        "HangingBottom", "Hanging Unit - Bottom", width, depth, t,
        IDENTITY, App.Vector(0, 0, base_z),
        color=colors.part_override_rgb("hanging_bottom"), edge_color=colors.role_rgb("main"),
        visible=False,
        stock_source="reclaimed" if colors.part_effective_role("hanging_bottom") == "reused" else "new",
    )
    add_panel(
        "HangingLeft", "Hanging Unit - Left Side", hanging_side_height, depth, t,
        ROT_Y90, App.Vector(0, 0, base_z + t),
        color=colors.part_override_rgb("left"), visible=True, stock_source="new",
    )
    add_panel(
        "HangingRight", "Hanging Unit - Right Side", hanging_side_height, depth, t,
        ROT_Y90, App.Vector(width - t, 0, base_z + t),
        color=colors.part_override_rgb("right"), visible=True, stock_source="new",
    )
    add_panel(
        "HangingBack", "Hanging Unit - Back", width, hanging_side_height, t,
        ROT_X90, App.Vector(0, depth - t, base_z + t),
        color=colors.part_override_rgb("back"), visible=False,
        stock_source="reclaimed" if colors.part_effective_role("back") == "reused" else "new",
    )

    ceiling_z = base_z + params.HANGING_UNIT_TOP_PANEL_Z_MIN
    _add_rod(add_panel, depth, ceiling_z)

    add_panel(
        "HangingTop", "Hanging Unit - Top Panel", width, depth, t,
        IDENTITY, App.Vector(0, 0, ceiling_z),
        color=colors.part_override_rgb("top"), visible=True, stock_source="new",
    )

    opening_bottom = base_z + t
    _add_doors(add_panel, opening_bottom, ceiling_z)

    _add_side_shelves(add_panel, width)

    return panels


def _add_side_shelves(add_panel, width):
    """SIDE_SHELF_COUNT small open shelves on the wardrobe's own OUTSIDE
    side wall (params.SIDE_SHELF_SIDE), each held by 2 visible L-shaped
    metal brackets (front + back, so the shelf can't tip forward/back) —
    same box-only bracket construction as furniture/dresser's own
    _add_top_brackets, just mounted to the OUTSIDE face (visible
    fasteners are fine/expected here, unlike the dresser's inset Top)
    and reaching outward instead of inward. Placed on the Hanging Unit's
    own side panel — see params.py."""
    t = params.MDF_THICKNESS
    depth = params.SIDE_SHELF_DEPTH
    proj = params.SIDE_SHELF_PROJECTION
    leg = params.SIDE_SHELF_BRACKET_LEG
    bw = params.SIDE_SHELF_BRACKET_WIDTH
    bt = params.SIDE_SHELF_BRACKET_THICKNESS
    metal_kwargs = dict(material="Metal", color=params.HANDLE_COLOR, visible=True, stock_source="new")

    # Outward direction: +X reaching past the right side panel's own
    # outside face (X=width), or -X reaching past the left side panel's
    # own outside face (X=0).
    outward = +1 if params.SIDE_SHELF_SIDE == "right" else -1
    face_x = width if params.SIDE_SHELF_SIDE == "right" else 0
    vert_x_min = face_x if outward > 0 else face_x - bt
    arm_x_min = face_x if outward > 0 else face_x - leg

    for index in range(params.SIDE_SHELF_COUNT):
        z_shelf = params.SIDE_SHELF_START_Z + index * params.SIDE_SHELF_SPACING
        prefix = f"SideShelf{index + 1}"
        label = f"Side Shelf {index + 1}"

        # SIDE_SHELF_COLOR_PATTERN reads top to bottom (same convention as
        # DRAWER_COLOR_PATTERN); index counts from the bottom shelf up
        # (z_shelf grows with index), so flip it to index into the pattern.
        from_top = params.SIDE_SHELF_COUNT - 1 - index
        shelf_color = (
            colors.MAIN_COLOR if params.SIDE_SHELF_COLOR_PATTERN[from_top] == "1"
            else colors.SECOND_COLOR
        )
        shelf_x_min = face_x if outward > 0 else face_x - proj
        add_panel(
            prefix, label, proj, depth, t, IDENTITY,
            App.Vector(shelf_x_min, 0, z_shelf),
            color=shelf_color, visible=True, stock_source="new",
        )

        for side, y_center in (("Front", depth * 0.2), ("Back", depth * 0.8)):
            y_min = y_center - bw / 2
            add_panel(
                f"{prefix}Bracket{side}Vertical", f"{label} - Bracket ({side.lower()}, vertical leg)",
                bt, bw, leg, IDENTITY, App.Vector(vert_x_min, y_min, z_shelf - leg),
                **metal_kwargs,
            )
            add_panel(
                f"{prefix}Bracket{side}Horizontal", f"{label} - Bracket ({side.lower()}, horizontal leg)",
                leg, bw, bt, IDENTITY, App.Vector(arm_x_min, y_min, z_shelf - bt),
                **metal_kwargs,
            )

    # One spare of the exact Hanging Unit side panel the shelves are
    # screwed into — repeated bracket removal/reinstallation can strip the
    # screw holes over time, so a ready replacement avoids rebuilding the
    # whole side wall. Coincides exactly with the real panel (hidden, so
    # it adds no visual clutter and no extra footprint) — just one more
    # line in the cutlist/purchase count.
    side_name = params.SIDE_SHELF_SIDE.capitalize()
    side_x = 0 if params.SIDE_SHELF_SIDE != "right" else width - t
    add_panel(
        f"Hanging{side_name}Spare", f"Hanging Unit - {side_name} Side (Spare)",
        params.HANGING_UNIT_SIDE_HEIGHT, params.DEPTH, t, ROT_Y90,
        App.Vector(side_x, 0, params.BOTTOM_UNIT_HEIGHT + t),
        # Matches whichever side (left/right) it's a spare for.
        color=colors.part_override_rgb(params.SIDE_SHELF_SIDE), visible=False, stock_source="new",
    )


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
        colors.MAIN_COLOR if params.DRAWER_COLOR_PATTERN[from_top] == "1"
        else colors.SECOND_COLOR
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
