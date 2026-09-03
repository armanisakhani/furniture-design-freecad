"""
Phase 2 test.

Purpose: generate one real panel from panel.py's Panel FeaturePython
primitive — the box top panel, sized from params.py (BOX_TOP_PANEL_WIDTH /
FRAME_LENGTH / MDF_THICKNESS, never literals) — and confirm it reports
correct dimensions and volume. Open the saved .FCStd in the FreeCAD GUI,
change a property (e.g. Thickness), hit Recompute, and confirm the shape
actually regenerates — that's the point of using FeaturePython over a
one-shot script.

Note: freecadcmd runs a script with __name__ set to the script's filename,
not "__main__" — call main() unconditionally (see phase0_smoke_test.py).
"""

import os

import FreeCAD as App

import params
from panel import create_panel

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "phase2_panel_test.FCStd")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    doc = App.newDocument("Phase2PanelTest")

    top_panel = create_panel(
        doc,
        obj_name="Box1_TopPanel",
        label="Box 1 - Top Panel",
        length=params.FRAME_LENGTH,
        width=params.BOX_TOP_PANEL_WIDTH,
        thickness=params.MDF_THICKNESS,
        material="MDF",
        color=params.BODY_COLOR,
        visible=True,
        stock_source="new",
    )

    doc.recompute()
    doc.saveAs(OUTPUT_FILE)

    expected_volume = (
        params.FRAME_LENGTH * params.BOX_TOP_PANEL_WIDTH * params.MDF_THICKNESS
    )
    actual_volume = top_panel.Shape.Volume

    print(f"Created {OUTPUT_FILE}")
    print(
        "Panel dims (Length, Width, Thickness) = "
        f"({top_panel.Length.Value}, {top_panel.Width.Value}, "
        f"{top_panel.Thickness.Value})"
    )
    print(
        f"Volume: expected {expected_volume} mm^3, got {actual_volume} mm^3, "
        f"match={abs(expected_volume - actual_volume) < 1e-6}"
    )
    print(f"Material={top_panel.Material}, StockSource={top_panel.StockSource}, "
          f"PanelVisible={top_panel.PanelVisible}")


main()
