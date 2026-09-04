#!/bin/bash
# Exports the wardrobe model to a colored, self-contained glTF binary
# (.glb), for sharing outside FreeCAD. Mirrors export_dresser_gltf.sh.
#
# Usage:
#   ./export_wardrobe_gltf.sh                  # export the existing output file
#   ./export_wardrobe_gltf.sh --rebuild         # regenerate from params.py first

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"       # tools/
ROOT="$(dirname "$DIR")"                                  # repo root
WARDROBE_DIR="$ROOT/furniture/wardrobe"
FREECADCMD="/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd"
FREECAD_BIN="/Applications/FreeCAD.app/Contents/MacOS/FreeCAD"
FILE="$WARDROBE_DIR/output/wardrobe_test.FCStd"
EXPORT_PATH="${EXPORT_PATH:-$WARDROBE_DIR/output/wardrobe.glb}"

if [ "$1" == "--rebuild" ]; then
    echo "Rebuilding from params.py..."
    "$FREECADCMD" "$WARDROBE_DIR/tests/wardrobe_test.py"
fi

echo "Exporting to $EXPORT_PATH..."
EXPORT_PATH="$EXPORT_PATH" QT_QPA_PLATFORM=offscreen "$FREECAD_BIN" "$FILE" "$DIR/export_gltf.py"
echo "Done."
