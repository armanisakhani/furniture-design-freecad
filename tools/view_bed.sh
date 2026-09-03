#!/bin/bash
# Rebuilds (optional) and opens the bed model in FreeCAD with colors and a
# default camera angle already applied — no manual console commands needed.
#
# Usage:
#   ./view_bed.sh                          # just reopen the existing output file
#   ./view_bed.sh --rebuild                 # regenerate from params.py first
#   STYLE=2 ./view_bed.sh --rebuild         # regenerate with a params.py style preset
#   ./view_bed.sh /path/to/other.FCStd       # open a different file

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"       # tools/
ROOT="$(dirname "$DIR")"                                  # repo root
BED_DIR="$ROOT/furniture/bed"
FREECADCMD="/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd"
FREECAD_BIN="/Applications/FreeCAD.app/Contents/MacOS/FreeCAD"
FILE="$BED_DIR/output/bed_test.FCStd"

if [ "$1" == "--rebuild" ]; then
    echo "Rebuilding from params.py..."
    "$FREECADCMD" "$BED_DIR/tests/bed_test.py"
    shift
fi

if [ -n "$1" ]; then
    FILE="$1"
fi

osascript -e 'tell application "FreeCAD" to quit' 2>/dev/null || true
sleep 1
"$FREECAD_BIN" "$FILE" "$DIR/apply_view_and_colors.py"
