"""
Run this INSIDE FreeCAD's own GUI Python console (View > Panels > Python
console), not via freecadcmd — it needs a live Gui.Document, which only
exists when the GUI is running.

Why this exists: Panel's PanelColor is a plain data property (see panel.py),
correct and saved by any script. But actually *rendering* that color in the
3D view requires setting ViewObject.ShapeColor, and ViewObject only exists
once a document is open in the GUI — a headless freecadcmd script (how every
phaseN_*.py test in this project generates its .FCStd) has no ViewObject to
set, so the saved file never carries view/color data. This script bridges
that gap for whatever document is currently active in the GUI.

Usage: open your .FCStd file normally (open -a FreeCAD ...), then in the
Python console run:
    exec(open("/Users/divar/design/bedroom/tools/apply_colors.py").read())
"""

import FreeCAD as App

doc = App.ActiveDocument
if doc is None:
    print("No active document — open a .FCStd file first.")
else:
    # Recompute FIRST, not after: recomputing a Part::FeaturePython
    # reassigns its Shape, which resets ViewObject.DiffuseColor back to a
    # flat array matching ShapeColor — wiping out the per-face EdgeColor
    # split set below if it ran afterward instead (confirmed: the edge
    # silently tracked the body color instead of staying independent).
    doc.recompute()
    count = 0
    for obj in doc.Objects:
        if hasattr(obj, "PanelColor") and obj.ViewObject is not None:
            obj.ViewObject.ShapeColor = obj.PanelColor
            # EdgeColor (core/panel.py) colors just the panel's own 4
            # perimeter/cut-edge faces (e.g. PVC edge-banding), independent
            # of PanelColor's single ShapeColor — set as a per-face
            # DiffuseColor instead, relying on Part.makeBox's own stable
            # face order (Faces[0:4] = the 4 side faces, Faces[4:6] = the
            # 2 big flat faces — see EdgeColor's own docstring). Skipped
            # when EdgeColor matches PanelColor (the common case — most
            # panels have no independent edge treatment), so ShapeColor's
            # own single-color rendering is left untouched for those.
            if hasattr(obj, "EdgeColor") and hasattr(obj, "Shape"):
                edge_rgba = tuple(obj.EdgeColor)
                panel_rgba = tuple(obj.PanelColor)
                if edge_rgba != panel_rgba and len(obj.Shape.Faces) == 6:
                    obj.ViewObject.DiffuseColor = [edge_rgba] * 4 + [panel_rgba] * 2
            count += 1
    print(f"Applied PanelColor to {count} object(s) in '{doc.Name}'.")

    # Same missing-view-data issue, different symptom: a plain Part::Box
    # (the mattress placeholder, bed.py — not a Panel, so it's skipped
    # above) defaults to Visibility=False on a headless-created document,
    # unlike every Part::FeaturePython Panel, which defaults to visible.
    mattress = doc.getObject("MattressPlaceholder")
    if mattress is not None and mattress.ViewObject is not None:
        mattress.ViewObject.Visibility = True
