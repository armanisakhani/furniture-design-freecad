"""
Named color swatches (references/colors/) and selectable palettes, so
different body/drawer-front color combinations can be previewed without
hand-editing params.py. Mirrors the STYLES pattern in params.py: pick a
palette with the COLOR_SCHEME env var, e.g. `COLOR_SCHEME=charcoal_front
make test-bed`. BODY_SWATCH/DRAWER_FRONT_SWATCH can each still override
one role individually on top of a selected palette, same as STYLE's own
per-knob overrides.
"""

import os

# --- Named swatches (references/colors/) --------------------------------
# RGB triples, 0-1 range, sampled/estimated by eye from the reference
# swatch photo. `code` is the manufacturer's own reference number (None
# for colors with no such reference, e.g. plain white).
SWATCHES = {
    "white": dict(code=None, rgb=(1.0, 1.0, 1.0)),
    "misty": dict(code=1128, rgb=(0.31, 0.44, 0.50)),  # 1128-misty.jpg
    "brown": dict(code=1126, rgb=(0.43, 0.35, 0.28)),  # 1126-brown.jpg
    "anthracite": dict(code=1129, rgb=(0.38, 0.37, 0.36)),  # 1129-anthracite.png
    "navy": dict(code=None, rgb=(0.11, 0.15, 0.28)),  # سرمه‌ای — in-stock sheet, no swatch photo yet
}

# --- Palettes: which swatch plays which role ----------------------------
# "body" -> BODY_COLOR (Box body panels, e.g. Top), "drawer_front" ->
# DRAWER_FRONT_COLOR (the Drawer_box Face/نما panel only). Add an entry
# here for a new combination to try.
PALETTES = {
    "default": dict(body="misty", drawer_front="brown"),
    "charcoal_front": dict(body="misty", drawer_front="anthracite"),
    "navy_body": dict(body="navy", drawer_front="brown"),  # in-stock sheets: STYLE=5 cut list
}


def _resolve_palette():
    name = os.environ.get("COLOR_SCHEME") or "default"
    if name not in PALETTES:
        raise ValueError(f"Unknown COLOR_SCHEME={name!r}; known: {sorted(PALETTES)}")
    palette = dict(PALETTES[name])
    if os.environ.get("BODY_SWATCH"):
        palette["body"] = os.environ["BODY_SWATCH"]
    if os.environ.get("DRAWER_FRONT_SWATCH"):
        palette["drawer_front"] = os.environ["DRAWER_FRONT_SWATCH"]
    return palette


def swatch_rgb(name):
    if name not in SWATCHES:
        raise ValueError(f"Unknown color swatch {name!r}; known: {sorted(SWATCHES)}")
    return SWATCHES[name]["rgb"]


_palette = _resolve_palette()

BODY_COLOR = swatch_rgb(_palette["body"])
DRAWER_FRONT_COLOR = swatch_rgb(_palette["drawer_front"])
