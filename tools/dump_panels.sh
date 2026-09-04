#!/bin/bash
# Dumps the current bed assembly's panel list to furniture/bed/output/panels.json
# (tools/dump_panels.py) — no GUI needed, panel colors live on the
# Part::FeaturePython objects themselves, not the ViewObject.
#
# Usage:
#   tools/dump_panels.sh                                  # STYLE=1 default
#   STYLE=5 COLOR_SCHEME=navy_body tools/dump_panels.sh    # cut-list variant
#
# Then feed the result into the nesting/cut-list report:
#   .venv/bin/python tools/cutlist.py

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"       # tools/
FREECADCMD="/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd"

"$FREECADCMD" "$DIR/dump_panels.py"
