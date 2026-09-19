"""
Same as apply_view_and_colors.py, but with a camera yaw that actually
faces the dresser's front instead of its back.

furniture/bed has no single "front" (drawers open from both X ends, see
CONTEXT.md), so apply_view_and_colors.py's yaw=45 (positive X, positive Y
camera offset) always lands on some reasonable corner. furniture/dresser
is different: every drawer opens through one single face, Y=0 (see
furniture/dresser/params.py's own axes comment) — a positive-Y camera
offset puts the camera on the far (Y=DEPTH, Back panel) side, looking at
the piece from behind. yaw=-45 instead gives a negative-Y offset, putting
the camera in front of the Y=0 face, looking at the actual drawer fronts.
"""

import os

import FreeCADGui as Gui
from PySide import QtGui

BASE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(BASE, "apply_colors.py")).read())
exec(open(os.path.join(BASE, "set_view.py")).read())

view = Gui.activeDocument().activeView()
view.setCameraType("Perspective")
set_camera(yaw=-45, pitch=25, distance=3000)

# View > Panels > Model (the tree view dock, objectName "Model") — shown
# BEFORE the fit-all below, not after: docking/undocking it resizes the 3D
# viewport, and fitAll() computes against whatever viewport size is
# current at the moment it runs, so fitting first and reflowing the
# layout after left the model slightly mis-fit (per the user).
model_dock = Gui.getMainWindow().findChild(QtGui.QDockWidget, "Model")
if model_dock is not None:
    model_dock.setVisible(True)
    model_dock.raise_()

QtGui.QApplication.processEvents()  # flush the dock's resize before fitting
view.fitAll()  # Gui.SendMsgToActiveView("ViewFit") fails silently on FreeCAD
               # 1.1.3 ("Unknown view command: ViewFit") — call the real
               # ViewObject API method instead, not the string command.
