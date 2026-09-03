"""
Panel placement helpers + rotation constants shared by every furniture
module (furniture/bed/box.py, furniture/bed/bed.py, ...).
"""

import FreeCAD as App

# identity for horizontal panels (thickness along Z), ROT_X90 for vertical
# panels thin along Y ("side" walls), ROT_Y90 for vertical panels thin
# along X ("end" walls / dividers). See place_panel() for how these combine
# with position.
IDENTITY = App.Rotation()
ROT_X90 = App.Rotation(App.Vector(1, 0, 0), 90)
ROT_Y90 = App.Rotation(App.Vector(0, 1, 0), 90)


def place_panel(doc, obj, rotation, target_min):
    """Set obj.Placement so its rotated Shape's bounding-box minimum corner
    lands exactly at target_min (an App.Vector). Avoids hand-deriving the
    position offset a 90-degree rotation introduces (Part.makeBox's corner
    origin moves under rotation) — let FreeCAD compute it via BoundBox."""
    obj.Placement = App.Placement(App.Vector(0, 0, 0), rotation)
    doc.recompute()
    bbox = obj.Shape.BoundBox
    offset = App.Vector(
        target_min.x - bbox.XMin,
        target_min.y - bbox.YMin,
        target_min.z - bbox.ZMin,
    )
    obj.Placement = App.Placement(offset, rotation)
    doc.recompute()
