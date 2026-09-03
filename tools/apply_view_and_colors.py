"""
Combines apply_colors.py + set_view.py into one step. Meant to be passed
as a second command-line argument to FreeCAD alongside a .FCStd file (see
view_bed.sh) — FreeCAD auto-runs a .py file passed this way against
whatever document it just opened, so this applies real colors and a
default camera angle with no manual console typing needed.

Still leaves set_camera(yaw, pitch, distance) defined afterward, so you
can keep adjusting the view by hand in the Python console once it's open.
"""

import os

BASE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(BASE, "apply_colors.py")).read())
exec(open(os.path.join(BASE, "set_view.py")).read())
set_camera(yaw=45, pitch=25, distance=3000)
