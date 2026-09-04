"""
Named color swatches for the dresser (دراور) model. Mirrors
furniture/bed/colors.py's shape but kept minimal — no palette-switching
env var machinery yet, since the user gave a direct brief (brown body,
misty drawer fronts) rather than a set of combos to try. Revisit if/when
that changes.
"""

SWATCHES = {
    "white": (1.0, 1.0, 1.0),
    "brown": (0.43, 0.35, 0.28),  # matches furniture/bed's "brown" (1126)
    "misty": (0.31, 0.44, 0.50),  # matches furniture/bed's "misty" (1128)
}


def swatch_rgb(name):
    if name not in SWATCHES:
        raise ValueError(f"Unknown color swatch {name!r}; known: {sorted(SWATCHES)}")
    return SWATCHES[name]


BODY_COLOR = swatch_rgb("brown")
DRAWER_FRONT_COLOR = swatch_rgb("misty")
