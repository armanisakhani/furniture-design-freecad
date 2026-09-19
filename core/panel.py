"""
Reusable parametric MDF panel primitive, shared by every furniture module
in furniture/ (originated as the bed project's Phase 2 — see docs/roadmap.md).

Panel is a genuine Part::FeaturePython: its Proxy rebuilds the Shape in
execute(), so editing a property (Length/Width/Thickness/...) and hitting
Recompute in the FreeCAD GUI regenerates the geometry — not a one-shot
Part.makeBox() script.

Local coordinate frame, before any Placement is applied: Length -> local X,
Width -> local Y, Thickness -> local Z (same mapping Part::Box uses). A
Panel used as a vertical wall gets there via Placement, not by swapping
which property means what.
"""

import Part

from .placement import place_panel, IDENTITY, ROT_X90, ROT_Y90


class Panel:
    """Proxy for a Part::FeaturePython representing one rectangular MDF/PVC/
    fiber/glass panel. See CONTEXT.md for the visible/stock_source concept
    this implements."""

    MATERIALS = ["MDF", "PVC", "Fiber", "Metal", "Glass"]
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
                "Finish color — see the owning furniture module's own "
                "params.py. Not yet wired to ViewObject.ShapeColor "
                "(deferred to Phase 9).",
            ).PanelColor = (1.0, 1.0, 1.0)
        if not hasattr(obj, "EdgeColor"):
            obj.addProperty(
                "App::PropertyColor", "EdgeColor", "Panel",
                "Finish color for just this panel's own 4 perimeter/cut-edge "
                "faces (e.g. PVC edge-banding tape) — the board's face and "
                "its edge tape are 2 independent attributes of the same "
                "board. Defaults to PanelColor's own value (see "
                "create_panel), so a panel with no independent edge "
                "treatment still renders as one uniform color. Applied via "
                "ViewObject.DiffuseColor (per-face), not PanelColor's own "
                "single ShapeColor — see tools/apply_colors.py. Relies on "
                "Part.makeBox's own stable face order: Faces[0:4] are the "
                "4 side faces at the Length/Width extremes (the cut edges "
                "around the panel's own perimeter), Faces[4:6] are the 2 "
                "big flat faces at the Thickness extremes (confirmed "
                "empirically, not officially documented by FreeCAD, but a "
                "basic property of how OCC's box primitive is built, "
                "unlikely to change).",
            ).EdgeColor = (1.0, 1.0, 1.0)
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
    edge_color=None,
    visible=True,
    stock_source="new",
):
    """Add one Panel FeaturePython object to doc and set its properties from
    params.py values (never pass literals in from geometry code). edge_color
    (see Panel's own EdgeColor property) defaults to matching `color` — a
    single uniform color — when not given its own independent value."""
    obj = doc.addObject("Part::FeaturePython", obj_name)
    Panel(obj)
    obj.Label = label
    obj.Length = length
    obj.Width = width
    obj.Thickness = thickness
    obj.Material = material
    obj.PanelColor = color
    obj.EdgeColor = edge_color if edge_color is not None else color
    obj.PanelVisible = visible
    obj.StockSource = stock_source
    return obj


def create_assembly_panel(
    doc,
    obj_name,
    label,
    length,
    width,
    thickness,
    rotation,
    target_min,
    material="MDF",
    color=None,
    edge_color=None,
    visible=True,
    stock_source="new",
    reclaimed_color=None,
    new_color=None,
):
    """create_panel() + place_panel() in one call, applying the shared
    stock_source -> color default rule (CONTEXT.md): if color is None, it's
    reclaimed_color or new_color depending on stock_source. Each furniture
    module passes its own two colors from its own params.py (e.g.
    RECLAIMED_MDF_COLOR / BODY_COLOR) — this module stays furniture-
    agnostic. Pass an explicit color to override the rule entirely (e.g.
    the Drawer_box Face's DRAWER_FRONT_COLOR)."""
    if color is None:
        color = reclaimed_color if stock_source == "reclaimed" else new_color
    obj = create_panel(
        doc, obj_name, label, length, width, thickness,
        material=material, color=color, edge_color=edge_color, visible=visible,
        stock_source=stock_source,
    )
    place_panel(doc, obj, rotation, target_min)
    return obj
