#!/bin/bash
# Rebuilds (optional) and opens the tv_table model in FreeCAD with colors
# and a default camera angle already applied — no manual console commands
# needed. Mirrors view_bed.sh.
#
# Usage:
#   ./view_tv_table.sh                            # rebuild from params.py, then open (the default)
#   FRONT_WIDTH=1800 ./view_tv_table.sh   # rebuild with an overridden knob (furniture/tv_table/example.yaml)
#   ./view_tv_table.sh --view-only                # skip rebuilding, just reopen the existing output file
#   ./view_tv_table.sh /path/to/other.FCStd        # open a different file (skips rebuilding too)

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"       # tools/
ROOT="$(dirname "$DIR")"                                  # repo root
TV_TABLE_DIR="$ROOT/furniture/tv_table"
FREECADCMD="/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd"
FREECAD_BIN="/Applications/FreeCAD.app/Contents/MacOS/FreeCAD"
FILE="$TV_TABLE_DIR/output/tv_table_test.FCStd"

if [ "$1" == "--view-only" ]; then
    shift
elif [ -z "$1" ]; then
    echo "Rebuilding from params.py..."
    "$FREECADCMD" "$TV_TABLE_DIR/tests/tv_table_test.py"
fi

if [ -n "$1" ]; then
    FILE="$1"
fi

osascript -e 'tell application "FreeCAD" to quit' 2>/dev/null || true
sleep 1
"$FREECAD_BIN" "$FILE" "$DIR/apply_view_and_colors_dresser.py"
