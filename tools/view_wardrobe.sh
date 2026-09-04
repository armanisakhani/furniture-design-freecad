#!/bin/bash
# Rebuilds (optional) and opens the wardrobe model in FreeCAD with colors
# and a default camera angle already applied — no manual console commands
# needed. Mirrors view_dresser.sh.
#
# Usage:
#   ./view_wardrobe.sh                      # just reopen the existing output file
#   ./view_wardrobe.sh --rebuild             # regenerate from params.py first
#   STYLE=2 ./view_wardrobe.sh --rebuild     # regenerate with a params.py style preset
#   LAYOUT=two_piece ./view_wardrobe.sh --rebuild  # regenerate the 2-piece layout
#   ./view_wardrobe.sh /path/to/other.FCStd  # open a different file

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"       # tools/
ROOT="$(dirname "$DIR")"                                  # repo root
WARDROBE_DIR="$ROOT/furniture/wardrobe"
FREECADCMD="/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd"
FREECAD_BIN="/Applications/FreeCAD.app/Contents/MacOS/FreeCAD"
FILE="$WARDROBE_DIR/output/wardrobe_test.FCStd"

if [ "$1" == "--rebuild" ]; then
    echo "Rebuilding from params.py..."
    "$FREECADCMD" "$WARDROBE_DIR/tests/wardrobe_test.py"
    shift
fi

if [ -n "$1" ]; then
    FILE="$1"
fi

osascript -e 'tell application "FreeCAD" to quit' 2>/dev/null || true
sleep 1
"$FREECAD_BIN" "$FILE" "$DIR/apply_view_and_colors_wardrobe.py"
