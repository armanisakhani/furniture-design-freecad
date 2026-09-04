#!/bin/bash
# Dumps a furniture assembly's panel list (label, world bbox, color,
# visible, material, stock_source) to JSON — no GUI needed. See
# dump_scene.py.
#
# Usage:
#   MODULE=dresser tools/dump_scene.sh
#   MODULE=bed CREATE_FN=create_bed tools/dump_scene.sh

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"       # tools/
FREECADCMD="/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd"

"$FREECADCMD" "$DIR/dump_scene.py"
