#!/bin/bash
# Builds a named order (1+ furniture items, each optionally with its own
# style/layout/color/etc. — see orders/specs/<name>.yaml and
# orders/registry.py's load_order), reports the combined cut list, and
# opens the result in FreeCAD. Every output lands under
# orders/output/<name>/, so different named orders never collide.
#
# Usage:
#   tools/order.sh <name>
#   tools/order.sh                       # same as tools/order.sh default
#   tools/order.sh <name> --no-view      # build + cutlist only, skip opening FreeCAD
#   tools/order.sh <name> --view-only    # skip (re)building, just reopen the existing order.FCStd
#   tools/order.sh <name> --report       # (re)build + open the full HTML cutlist report

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"       # tools/
ROOT="$(dirname "$DIR")"                                  # repo root
FREECAD_BIN="/Applications/FreeCAD.app/Contents/MacOS/FreeCAD"

NAME="default"
MODE=""
for arg in "$@"; do
    case "$arg" in
        --no-view|--view-only|--report) MODE="$arg" ;;
        *) NAME="$arg" ;;
    esac
done

ORDER_DIR="$ROOT/orders/output/$NAME"

if [ "$MODE" = "--report" ]; then
    "$ROOT/.venv/bin/python" "$ROOT/orders/generate_report.py" "$NAME"
    open "$ORDER_DIR/report.html"
    exit 0
fi

if [ "$MODE" != "--view-only" ]; then
    "$ROOT/.venv/bin/python" "$ROOT/orders/run_order.py" "$NAME"
fi

if [ "$MODE" != "--no-view" ]; then
    osascript -e 'tell application "FreeCAD" to quit' 2>/dev/null || true
    sleep 1
    "$FREECAD_BIN" "$ORDER_DIR/order.FCStd" "$DIR/apply_view_and_colors_order.py"
fi
