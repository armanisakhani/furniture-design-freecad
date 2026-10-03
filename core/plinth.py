"""
Shared plinth (پاسنگ/پاخور) for furniture/dresser and furniture/wardrobe's
floor-standing carcasses: when a plinth height is set, the Left/Right
sides run all the way to the floor, the Bottom panel is raised that far
and fits BETWEEN them, and 2 vertical MDF strips (front and back) close
the gap under it, between the sides. See each module's own params.py
(PLINTH_HEIGHT) for the numbers.
"""

import FreeCAD as App

from .placement import ROT_X90


def add_plinth(add_panel, width, depth, thickness, height, setback, front_kwargs, back_kwargs):
    """No-op when height <= 0. front_kwargs/back_kwargs are each strip's
    own color/visible/stock_source (the module's own part roles)."""
    if height <= 0:
        return
    length = width - 2 * thickness
    add_panel(
        "PlinthFront", "Plinth Front", length, height, thickness, ROT_X90,
        App.Vector(thickness, setback, 0), **front_kwargs,
    )
    add_panel(
        "PlinthBack", "Plinth Back", length, height, thickness, ROT_X90,
        App.Vector(thickness, depth - thickness, 0), **back_kwargs,
    )
