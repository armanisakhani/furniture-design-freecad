#!/bin/bash
# Builds a combined "order" (1+ furniture items, each optionally with its
# own STYLE/LAYOUT/etc. override — see orders/registry.py's ORDER spec),
# reports the combined cut list, and opens the result in FreeCAD.
#
# Usage:
#   tools/order.sh
#   ORDER="dresser:2:STYLE=2,wardrobe:1:LAYOUT=two_piece" tools/order.sh
#   tools/order.sh --no-view     # build + cutlist only, skip opening FreeCAD
#   tools/order.sh --view-only   # skip (re)building, just reopen the existing order.FCStd

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"       # tools/
ROOT="$(dirname "$DIR")"                                  # repo root
FREECAD_BIN="/Applications/FreeCAD.app/Contents/MacOS/FreeCAD"

if [ "$1" != "--view-only" ]; then
    "$ROOT/.venv/bin/python" "$ROOT/orders/run_order.py"
fi

if [ "$1" != "--no-view" ]; then
    osascript -e 'tell application "FreeCAD" to quit' 2>/dev/null || true
    sleep 1
    "$FREECAD_BIN" "$ROOT/orders/output/order.FCStd" "$DIR/apply_view_and_colors_order.py"
fi
