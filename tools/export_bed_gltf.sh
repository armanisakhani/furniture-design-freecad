#!/bin/bash
# Exports the bed model to a colored, self-contained glTF binary (.glb),
# for sharing outside FreeCAD. No visible window — runs the GUI binary
# under an offscreen Qt platform (needed for ViewObject/PanelColor, but no
# actual rendering happens).
#
# Usage:
#   ./export_bed_gltf.sh                  # export the existing output file
#   ./export_bed_gltf.sh --rebuild         # regenerate from params.py first
#   STYLE=2 ./export_bed_gltf.sh --rebuild # regenerate with a params.py style preset

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"       # tools/
ROOT="$(dirname "$DIR")"                                  # repo root
BED_DIR="$ROOT/furniture/bed"
FREECADCMD="/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd"
FREECAD_BIN="/Applications/FreeCAD.app/Contents/MacOS/FreeCAD"
FILE="$BED_DIR/output/bed_test.FCStd"
EXPORT_PATH="${EXPORT_PATH:-$BED_DIR/output/bed.glb}"

if [ "$1" == "--rebuild" ]; then
    echo "Rebuilding from params.py..."
    "$FREECADCMD" "$BED_DIR/tests/bed_test.py"
fi

echo "Exporting to $EXPORT_PATH..."
EXPORT_PATH="$EXPORT_PATH" QT_QPA_PLATFORM=offscreen "$FREECAD_BIN" "$FILE" "$DIR/export_gltf.py"
echo "Done."
