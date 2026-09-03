"""
Phase 2 — reusable parametric MDF panel primitive.

Panel is a genuine Part::FeaturePython object: its Proxy class rebuilds the
Shape in execute(), so editing a property (Length/Width/Thickness/...) and
hitting Recompute in the FreeCAD GUI regenerates the geometry — this is not a
one-shot Part.makeBox() script.

Local coordinate frame of a Panel's own shape (before any Placement is
applied by an assembly step, e.g. Phase 3): Length -> local X, Width ->
local Y, Thickness -> local Z. Same mapping Part::Box itself uses, and the
same one phase0_smoke_test.py used for its placeholder box. A Panel used as
a vertical side wall gets there via Placement (rotation + position), not by
swapping which property means what.
(چارچوب محلی خود شکل Panel، قبل از اینکه فاز ۳ روش Placement بذاره: Length
روی X محلی، Width روی Y محلی، Thickness روی Z محلی — همون نگاشتی که خود
Part::Box و phase0_smoke_test.py استفاده کردن. اگه یه Panel قراره دیواره‌ی
عمودی باشه، این کار با Placement انجام می‌شه، نه با عوض کردن معنی پراپرتی‌ها.)
"""

import FreeCAD as App
import Part

# Rotation families shared by every assembly module (box.py, bed.py, ...):
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


class Panel:
    """Proxy for a Part::FeaturePython representing one rectangular MDF/PVC/
    fiber panel. See CONTEXT.md for the visible/stock_source concept this
    implements."""

    MATERIALS = ["MDF", "PVC", "Fiber"]
    STOCK_SOURCES = ["new", "reclaimed"]

    def __init__(self, obj):
        obj.Proxy = self
        self._add_properties(obj)

    def _add_properties(self, obj):
        if not hasattr(obj, "Length"):
            obj.addProperty(
                "App::PropertyLength", "Length", "Panel",
                "Panel length, local X before Placement (mm)",
            ).Length = 100
        if not hasattr(obj, "Width"):
            obj.addProperty(
                "App::PropertyLength", "Width", "Panel",
                "Panel width, local Y before Placement (mm)",
            ).Width = 100
        if not hasattr(obj, "Thickness"):
            obj.addProperty(
                "App::PropertyLength", "Thickness", "Panel",
                "Panel thickness, local Z before Placement (mm)",
            ).Thickness = 16
        if not hasattr(obj, "Material"):
            obj.addProperty(
                "App::PropertyEnumeration", "Material", "Panel",
                "Board material this panel is cut from",
            )
            obj.Material = self.MATERIALS
            obj.Material = "MDF"
        if not hasattr(obj, "PanelColor"):
            obj.addProperty(
                "App::PropertyColor", "PanelColor", "Panel",
                "Finish color — see BODY_COLOR / DRAWER_FRONT_COLOR / "
                "WOOD_COLOR / RAIL_COLOR in params.py. Not yet wired to "
                "ViewObject.ShapeColor (deferred to Phase 9).",
            ).PanelColor = (1.0, 1.0, 1.0)
        if not hasattr(obj, "PanelVisible"):
            obj.addProperty(
                "App::PropertyBool", "PanelVisible", "Fabrication",
                "Whether this panel is visible in the finished, assembled "
                "piece (fabrication meaning — distinct from the GUI's own "
                "show/hide Visibility). Drives StockSource: hidden panels "
                "may be cut from reclaimed stock. See CONTEXT.md.",
            ).PanelVisible = True
        if not hasattr(obj, "StockSource"):
            obj.addProperty(
                "App::PropertyEnumeration", "StockSource", "Fabrication",
                "Which stock this panel is cut from",
            )
            obj.StockSource = self.STOCK_SOURCES
            obj.StockSource = "new"

    def execute(self, obj):
        length = obj.Length.Value
        width = obj.Width.Value
        thickness = obj.Thickness.Value
        obj.Shape = Part.makeBox(length, width, thickness)


def create_panel(
    doc,
    obj_name,
    label,
    length,
    width,
    thickness,
    material="MDF",
    color=(1.0, 1.0, 1.0),
    visible=True,
    stock_source="new",
):
    """Add one Panel FeaturePython object to doc and set its properties from
    params.py values (never pass literals in from geometry code)."""
    obj = doc.addObject("Part::FeaturePython", obj_name)
    Panel(obj)
    obj.Label = label
    obj.Length = length
    obj.Width = width
    obj.Thickness = thickness
    obj.Material = material
    obj.PanelColor = color
    obj.PanelVisible = visible
    obj.StockSource = stock_source
    return obj
