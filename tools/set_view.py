"""
Run this INSIDE FreeCAD's own GUI Python console (View > Panels > Python
console), same as apply_colors.py — needs a live Gui.Document.

Defines set_camera(yaw, pitch, distance, target=None) so you can dial in
an exact camera angle by number instead of hunting with the mouse or
guessing which Navigation Cube corner to click.

  yaw: degrees, rotation around the world Z (up) axis.
       0 = looking from the +X direction, 90 = from +Y, etc.
  pitch: degrees, elevation above the horizontal plane.
         0 = eye-level (horizon), 90 = straight down (top view),
         NEGATIVE = from below (e.g. -25 shows the underside, the skirt/
         drawer fronts, instead of the mattress-bearing top).
  distance: mm from the target point to the camera.
  target: App.Vector to look at — defaults to the center of the whole
          document's combined bounding box (every Shape object), so it
          re-centers automatically no matter what's currently open.

Usage:
    exec(open("/Users/divar/design/bedroom/tools/set_view.py").read())
    set_camera(yaw=45, pitch=25, distance=3000)
    set_camera(yaw=45, pitch=-25, distance=3000)   # from below
"""

import math

import FreeCAD as App
import FreeCADGui as Gui
from pivy import coin


def set_camera(yaw=45, pitch=25, distance=3000, target=None):
    doc = App.ActiveDocument
    view = Gui.activeDocument().activeView()

    if target is None:
        bbox = None
        for obj in doc.Objects:
            if hasattr(obj, "Shape") and obj.Shape and not obj.Shape.isNull():
                b = obj.Shape.BoundBox
                if bbox is None:
                    bbox = App.BoundBox(b)
                else:
                    bbox.add(b)
        target = bbox.Center if bbox else App.Vector(0, 0, 0)

    yaw_r = math.radians(yaw)
    pitch_r = math.radians(pitch)
    offset = App.Vector(
        distance * math.cos(pitch_r) * math.cos(yaw_r),
        distance * math.cos(pitch_r) * math.sin(yaw_r),
        distance * math.sin(pitch_r),
    )
    position = target + offset

    camera = view.getCameraNode()
    camera.position.setValue(position.x, position.y, position.z)
    camera.pointAt(
        coin.SbVec3f(target.x, target.y, target.z),
        coin.SbVec3f(0, 0, 1),
    )
    print(f"Camera at {position}, looking at {target} (yaw={yaw}, pitch={pitch}, distance={distance})")


print("set_camera(yaw, pitch, distance) is ready. Example: set_camera(yaw=45, pitch=25, distance=3000)")
