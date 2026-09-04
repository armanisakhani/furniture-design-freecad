"""
Same as apply_view_and_colors_dresser.py, for the combined order.FCStd
(orders/build_order.py): every item is laid out front-facing the same way
(Y=0), just side by side along X, so the same yaw=-45 camera works — just
a longer distance to fit the whole row.
"""

import os

import FreeCADGui as Gui
from PySide import QtGui

BASE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(BASE, "apply_colors.py")).read())
exec(open(os.path.join(BASE, "set_view.py")).read())

view = Gui.activeDocument().activeView()
view.setCameraType("Perspective")
set_camera(yaw=-45, pitch=25, distance=6000)
Gui.SendMsgToActiveView("ViewFit")

model_dock = Gui.getMainWindow().findChild(QtGui.QDockWidget, "Model")
if model_dock is not None:
    model_dock.setVisible(True)
    model_dock.raise_()
