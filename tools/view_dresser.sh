#!/bin/bash
# Rebuilds (optional) and opens the dresser model in FreeCAD with colors
# and a default camera angle already applied — no manual console commands
# needed. Mirrors view_bed.sh.
#
# Usage:
#   ./view_dresser.sh                      # just reopen the existing output file
#   ./view_dresser.sh --rebuild             # regenerate from params.py first
#   STYLE=2 ./view_dresser.sh --rebuild     # regenerate with a params.py style preset
#   ./view_dresser.sh /path/to/other.FCStd  # open a different file

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"       # tools/
ROOT="$(dirname "$DIR")"                                  # repo root
DRESSER_DIR="$ROOT/furniture/dresser"
FREECADCMD="/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd"
FREECAD_BIN="/Applications/FreeCAD.app/Contents/MacOS/FreeCAD"
FILE="$DRESSER_DIR/output/dresser_test.FCStd"

if [ "$1" == "--rebuild" ]; then
    echo "Rebuilding from params.py..."
    "$FREECADCMD" "$DRESSER_DIR/tests/dresser_test.py"
    shift
fi

if [ -n "$1" ]; then
    FILE="$1"
fi

osascript -e 'tell application "FreeCAD" to quit' 2>/dev/null || true
sleep 1
"$FREECAD_BIN" "$FILE" "$DIR/apply_view_and_colors_dresser.py"
