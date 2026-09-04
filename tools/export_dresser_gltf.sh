#!/bin/bash
# Exports the dresser model to a colored, self-contained glTF binary
# (.glb), for sharing outside FreeCAD. Mirrors export_bed_gltf.sh.
#
# Usage:
#   ./export_dresser_gltf.sh                  # export the existing output file
#   ./export_dresser_gltf.sh --rebuild         # regenerate from params.py first

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"       # tools/
ROOT="$(dirname "$DIR")"                                  # repo root
DRESSER_DIR="$ROOT/furniture/dresser"
FREECADCMD="/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd"
FREECAD_BIN="/Applications/FreeCAD.app/Contents/MacOS/FreeCAD"
FILE="$DRESSER_DIR/output/dresser_test.FCStd"
EXPORT_PATH="${EXPORT_PATH:-$DRESSER_DIR/output/dresser.glb}"

if [ "$1" == "--rebuild" ]; then
    echo "Rebuilding from params.py..."
    "$FREECADCMD" "$DRESSER_DIR/tests/dresser_test.py"
fi

echo "Exporting to $EXPORT_PATH..."
EXPORT_PATH="$EXPORT_PATH" QT_QPA_PLATFORM=offscreen "$FREECAD_BIN" "$FILE" "$DIR/export_gltf.py"
echo "Done."
