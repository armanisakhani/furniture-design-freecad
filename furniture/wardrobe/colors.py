"""
Named color swatches for the wardrobe (کمد لباس) model. Same palette as
furniture/dresser/colors.py — per the user, colors always stay
brown/misty, not a design choice specific to any one module.
"""

SWATCHES = {
    "white": (1.0, 1.0, 1.0),
    "brown": (0.43, 0.35, 0.28),  # matches furniture/bed's "brown" (1126)
    "misty": (0.31, 0.44, 0.50),  # matches furniture/bed's "misty" (1128)
    "metal": (0.55, 0.55, 0.57),  # brushed-steel look, for the drawer handles/rod
}

# The 2 swatches this design alternates between (params.py's MAIN_COLOR
# picks one; the other becomes the alternate automatically).
COLOR_PAIR = ("brown", "misty")


def swatch_rgb(name):
    if name not in SWATCHES:
        raise ValueError(f"Unknown color swatch {name!r}; known: {sorted(SWATCHES)}")
    return SWATCHES[name]
