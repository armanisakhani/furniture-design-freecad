"""
TV table (میز تلویزیون): a low trapezoidal cabinet — wide front, narrow
back against the wall — with one drawer. Top/Bottom are trapezoid
panels (core/panel.py's Outline); Left/Right are the 2 slanted sides,
cut so each one's inner front corner lands exactly on the front plane
(Y=0) and its outer back corner on the wall plane (Y=DEPTH); Back is a
rectangle across the narrow end. The drawer box is as wide as the
trapezoid's short side, and its Face covers the whole front (full
overlay, Y from -MDF_THICKNESS to 0). See params.py for the numbers.

Axes: X = left-right, Y = front-back (drawer opens toward -Y), Z = up.
"""

import math

import FreeCAD as App

import colors
import params
from core.panel import create_assembly_panel, resolve_stock, IDENTITY, ROT_X90, ROT_Y90


def create_tv_table(doc):
    """Create the whole TV table. Returns the list of all panels."""
    t = params.MDF_THICKNESS
    width = params.FRONT_WIDTH
    depth = params.DEPTH
    inset = params.SIDE_INSET
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

    trapezoid = [
        App.Vector(0, 0, 0), App.Vector(width, 0, 0),
        App.Vector(width - inset, depth, 0), App.Vector(inset, depth, 0),
    ]
    add_panel(
        "Bottom", "Bottom Panel", width, depth, t, IDENTITY,
        App.Vector(0, 0, 0), outline=trapezoid, **part_kwargs("bottom", False),
    )
    add_panel(
        "Top", "Top Panel", width, depth, t, IDENTITY,
        App.Vector(0, 0, params.HEIGHT - t), outline=trapezoid, **part_kwargs("top", True),
    )

    _add_sides(add_panel, part_kwargs)

    back_x_min = inset + params.SIDE_HORIZONTAL_THICKNESS
    add_panel(
        "Back", "Back Panel", width - 2 * back_x_min, params.INTERIOR_HEIGHT, t, ROT_X90,
        App.Vector(back_x_min, depth - t, t), **part_kwargs("back", False),
    )

    _add_drawer(add_panel, part_kwargs)
    return panels


def _add_sides(add_panel, part_kwargs):
    """The 2 slanted side boards. Each is a plain box turned about Z to
    follow its slanted edge; its position is derived from where the 4
    plan-view corners land (inner front corner on Y=0, outer back corner
    on Y=DEPTH — see module docstring)."""
    t = params.MDF_THICKNESS
    depth = params.DEPTH
    inset = params.SIDE_INSET
    slant = params.SIDE_SLANT_LENGTH

    # Left side, plan corners: outer front -> outer back, then the inner
    # face is that edge pushed inward by t along n = (depth, -inset)/slant.
    front_y = t * inset / slant
    front_x = front_y * inset / depth
    length = math.hypot(inset - front_x, depth - front_y)
    angle = math.degrees(math.atan2(depth, inset))
    rot_left = App.Rotation(App.Vector(0, 0, 1), angle).multiply(App.Rotation(App.Vector(1, 0, 0), 90))
    rot_right = App.Rotation(App.Vector(0, 0, 1), 180 - angle).multiply(App.Rotation(App.Vector(1, 0, 0), -90))
    # Right side is the mirror image: x -> FRONT_WIDTH - x. The left
    # side's plan bbox min is (front_x, 0) and its max x is the inner back
    # corner's, so the mirrored one's min x is FRONT_WIDTH minus that.
    left_x_max = inset + t * depth / slant
    add_panel(
        "Left", "Left Side Panel", length, params.INTERIOR_HEIGHT, t, rot_left,
        App.Vector(front_x, 0, t), **part_kwargs("left", True),
    )
    add_panel(
        "Right", "Right Side Panel", length, params.INTERIOR_HEIGHT, t, rot_right,
        App.Vector(params.FRONT_WIDTH - left_x_max, 0, t), **part_kwargs("right", True),
    )


def _add_drawer(add_panel, part_kwargs):
    """One drawer: carcass (bottom, 2 sides, structural front, back) as
    wide as the trapezoid's short side, plus the full-front Face."""
    t = params.MDF_THICKNESS
    dw = params.DRAWER_WIDTH
    dd = params.DRAWER_DEPTH
    x_min = (params.FRONT_WIDTH - dw) / 2
    bottom_z = t
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
