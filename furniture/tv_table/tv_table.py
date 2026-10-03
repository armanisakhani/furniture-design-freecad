"""
TV table (میز تلویزیون): a low trapezoidal unit — wide front, narrow
back against the wall. Just one drawer (as wide as the trapezoid's short
side, its Face covering the whole front — full overlay, Y from
-MDF_THICKNESS to 0) under an MDF trapezoid Top (core/panel.py's
Outline), plus a second MDF trapezoid shelf on 4 metal legs above it.
No floor, sides or back, per the user. See params.py for the numbers.

Axes: X = left-right, Y = front-back (drawer opens toward -Y), Z = up.
"""

import FreeCAD as App

import colors
import params
from core.panel import create_assembly_panel, resolve_stock, IDENTITY, ROT_X90, ROT_Y90


def create_tv_table(doc):
    """Create the whole TV table. Returns the list of all panels."""
    t = params.MDF_THICKNESS
    width = params.FRONT_WIDTH
    depth = params.DEPTH
    panels = []

    def add_panel(obj_name, label, length, width_, thickness, rotation,
                  target_min, material="MDF", color=None,
                  visible=True, stock_source="new", outline=None):
        obj = create_assembly_panel(
            doc, obj_name, label,
            length, width_, thickness, rotation, target_min,
            material=material, color=color, visible=visible,
            stock_source=stock_source, outline=outline,
            reclaimed_color=colors.REUSED_COLOR,
            new_color=colors.REUSED_COLOR,
        )
        panels.append(obj)
        return obj

    def part_kwargs(part, visible):
        return dict(
            color=colors.part_override_rgb(part), visible=visible,
            stock_source=resolve_stock(colors.part_effective_role(part)),
        )

    add_panel(
        "Top", "Top Panel", width, depth, t, IDENTITY,
        App.Vector(0, 0, params.HEIGHT - t), outline=_trapezoid(), **part_kwargs("top", True),
    )
    _add_drawer(add_panel, part_kwargs)
    if params.HAS_SHELF:
        _add_shelf(add_panel, part_kwargs)
    return panels


def _trapezoid():
    """Plan outline shared by the Top and the upper shelf."""
    width, depth, inset = params.FRONT_WIDTH, params.DEPTH, params.SIDE_INSET
    return [
        App.Vector(0, 0, 0), App.Vector(width, 0, 0),
        App.Vector(width - inset, depth, 0), App.Vector(inset, depth, 0),
    ]


def _add_drawer(add_panel, part_kwargs):
    """One drawer: carcass (bottom, 2 sides, structural front, back) as
    wide as the trapezoid's short side, plus the full-front Face."""
    t = params.MDF_THICKNESS
    dw = params.DRAWER_WIDTH
    dd = params.DRAWER_DEPTH
    x_min = (params.FRONT_WIDTH - dw) / 2
    bottom_z = 0
    carcass_z = bottom_z + params.DRAWER_BOTTOM_THICKNESS
    ch = params.DRAWER_CARCASS_HEIGHT
    hidden = dict(visible=False, stock_source="reclaimed")

    add_panel(
        "Drawer_Bottom", "Drawer - Bottom", dw, dd, params.DRAWER_BOTTOM_THICKNESS,
        IDENTITY, App.Vector(x_min, 0, bottom_z), material="Fiber", **hidden,
    )
    add_panel(
        "Drawer_SideLeft", "Drawer - Side (left)", ch, dd - 2 * t, t,
        ROT_Y90, App.Vector(x_min, t, carcass_z), **hidden,
    )
    add_panel(
        "Drawer_SideRight", "Drawer - Side (right)", ch, dd - 2 * t, t,
        ROT_Y90, App.Vector(x_min + dw - t, t, carcass_z), **hidden,
    )
    add_panel(
        "Drawer_Front", "Drawer - Structural Front", dw - 2 * t, ch, t,
        ROT_X90, App.Vector(x_min + t, 0, carcass_z), **hidden,
    )
    add_panel(
        "Drawer_Back", "Drawer - Back", dw - 2 * t, ch, t,
        ROT_X90, App.Vector(x_min + t, dd - t, carcass_z), **hidden,
    )
    # Face: against the structural front's outer face, in front of the
    # whole shell.
    add_panel(
        "Drawer_Face", "Drawer - Face", params.FACE_WIDTH, params.FACE_HEIGHT,
        params.FACE_THICKNESS, ROT_X90, App.Vector(0, -params.FACE_THICKNESS, 0),
        **part_kwargs("face", True),
    )


def _add_shelf(add_panel, part_kwargs):
    """Upper MDF trapezoid on 4 metal legs standing on the Top panel."""
    width = params.FRONT_WIDTH
    depth = params.DEPTH
    inset = params.SIDE_INSET
    leg = params.SHELF_LEG_SIZE
    z_shelf = params.HEIGHT + params.SHELF_LEG_HEIGHT

    add_panel(
        "Shelf", "Upper Shelf", width, depth, params.SHELF_THICKNESS, IDENTITY,
        App.Vector(0, 0, z_shelf), outline=_trapezoid(), **part_kwargs("shelf", True),
    )
    for row, y_center in (("Front", params.SHELF_LEG_SETBACK), ("Back", depth - params.SHELF_LEG_SETBACK)):
        left = y_center * inset / depth  # slanted edge's x at this depth
        span = width - 2 * left
        for side, x_center in (
            ("Left", left + params.SHELF_LEG_SIDE_FRACTION * span),
            ("Right", width - left - params.SHELF_LEG_SIDE_FRACTION * span),
        ):
            add_panel(
                f"ShelfLeg{row}{side}", f"Shelf Leg ({row.lower()} {side.lower()})",
                leg, leg, params.SHELF_LEG_HEIGHT, IDENTITY,
                App.Vector(x_center - leg / 2, y_center - leg / 2, params.HEIGHT),
                material="Metal", color=params.LEG_COLOR,
            )
