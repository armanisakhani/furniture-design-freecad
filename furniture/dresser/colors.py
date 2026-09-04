"""
Named color swatches for the dresser (دراور) model. Mirrors
furniture/bed/colors.py's shape but kept minimal — no palette-switching
env var machinery here, that lives in params.py's MAIN_COLOR/STYLES
instead (picks which of COLOR_PAIR is the body color; the other becomes
the drawer accent automatically).
"""

SWATCHES = {
    "white": (1.0, 1.0, 1.0),
    "brown": (0.43, 0.35, 0.28),  # matches furniture/bed's "brown" (1126)
    "misty": (0.31, 0.44, 0.50),  # matches furniture/bed's "misty" (1128)
    "metal": (0.55, 0.55, 0.57),  # brushed-steel look, for the drawer handles
}

# The 2 swatches this design actually alternates between (params.py's
# MAIN_COLOR picks one; the other becomes the alternate automatically).
COLOR_PAIR = ("brown", "misty")


def swatch_rgb(name):
    if name not in SWATCHES:
        raise ValueError(f"Unknown color swatch {name!r}; known: {sorted(SWATCHES)}")
    return SWATCHES[name]
