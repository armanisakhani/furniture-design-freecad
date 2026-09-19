#!/bin/bash
# Rebuilds (optional) and opens the bed model in FreeCAD with colors and a
# default camera angle already applied — no manual console commands needed.
#
# Usage:
#   ./view_bed.sh                                # rebuild from params.py, then open (the default)
#   STYLE=inset-raised ./view_bed.sh              # rebuild with a named style preset (furniture/bed/styles.yaml)
#   ./view_bed.sh --view-only                     # skip rebuilding, just reopen the existing output file
#   ./view_bed.sh /path/to/other.FCStd             # open a different file (skips rebuilding too)

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"       # tools/
ROOT="$(dirname "$DIR")"                                  # repo root
BED_DIR="$ROOT/furniture/bed"
FREECADCMD="/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd"
FREECAD_BIN="/Applications/FreeCAD.app/Contents/MacOS/FreeCAD"
FILE="$BED_DIR/output/bed_test.FCStd"

if [ "$1" == "--view-only" ]; then
    shift
elif [ -z "$1" ]; then
    echo "Rebuilding from params.py..."
    "$FREECADCMD" "$BED_DIR/tests/bed_test.py"
fi

if [ -n "$1" ]; then
    FILE="$1"
fi

osascript -e 'tell application "FreeCAD" to quit' 2>/dev/null || true
sleep 1
"$FREECAD_BIN" "$FILE" "$DIR/apply_view_and_colors.py"
