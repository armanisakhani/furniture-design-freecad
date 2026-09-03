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
    exec(open("/Users/divar/design/bedroom/apply_colors.py").read())
"""

import FreeCAD as App

doc = App.ActiveDocument
if doc is None:
    print("No active document — open a .FCStd file first.")
else:
    count = 0
    for obj in doc.Objects:
        if hasattr(obj, "PanelColor") and obj.ViewObject is not None:
            obj.ViewObject.ShapeColor = obj.PanelColor
            count += 1
    doc.recompute()
    print(f"Applied PanelColor to {count} object(s) in '{doc.Name}'.")
