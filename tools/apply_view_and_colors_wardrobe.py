"""
Same as apply_view_and_colors_dresser.py, adapted for the wardrobe: every
door/drawer opens through the same single Y=0 face (see
furniture/wardrobe/params.py's own axes comment), so the same yaw=-45
front-facing camera applies.
"""

import os

import FreeCADGui as Gui
from PySide import QtGui

BASE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(BASE, "apply_colors.py")).read())
exec(open(os.path.join(BASE, "set_view.py")).read())

view = Gui.activeDocument().activeView()
view.setCameraType("Perspective")
set_camera(yaw=-45, pitch=25, distance=3500)
Gui.SendMsgToActiveView("ViewFit")

# View > Panels > Model (the tree view dock, objectName "Model").
model_dock = Gui.getMainWindow().findChild(QtGui.QDockWidget, "Model")
if model_dock is not None:
    model_dock.setVisible(True)
    model_dock.raise_()
