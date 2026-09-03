"""
Combines apply_colors.py + set_view.py into one step. Meant to be passed
as a second command-line argument to FreeCAD alongside a .FCStd file (see
view_bed.sh) — FreeCAD auto-runs a .py file passed this way against
whatever document it just opened, so this applies real colors, a default
camera angle, perspective projection, a fit-all, and the Model tree panel
with no manual clicking needed (previously done by hand after every open).

Still leaves set_camera(yaw, pitch, distance) defined afterward, so you
can keep adjusting the view by hand in the Python console once it's open.
"""

import os

import FreeCADGui as Gui
from PySide import QtGui

BASE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(BASE, "apply_colors.py")).read())
exec(open(os.path.join(BASE, "set_view.py")).read())

view = Gui.activeDocument().activeView()
view.setCameraType("Perspective")
set_camera(yaw=45, pitch=25, distance=3000)
Gui.SendMsgToActiveView("ViewFit")

# View > Panels > Model (the tree view dock, objectName "Model").
model_dock = Gui.getMainWindow().findChild(QtGui.QDockWidget, "Model")
if model_dock is not None:
    model_dock.setVisible(True)
    model_dock.raise_()
