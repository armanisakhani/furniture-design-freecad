"""
Named color swatches for the wardrobe (کمد لباس) model, and the 3 shared
color roles every furniture/ module understands the same way (see
furniture/bed/colors.py's own module docstring for the full picture):
  * main   — MAIN_COLOR env var, default "misty".
  * second — SECOND_COLOR env var, default "white".
  * reused — REUSED_MDF_COLOR env var, default "white".
Same 3 names/env vars in furniture/bed and furniture/dresser's own
colors.py, so one ORDER entry format works for every furniture/ item.

PART_ROLES answers "what color is X" for this module's fixed-role parts
(currently just "body" — the carcass, both layout units). The door and
drawer Face colors are NOT here — they're picked by DOOR_COLOR_DIGIT and
DRAWER_COLOR_PATTERN (params.py), '1'/'0' digits choosing main/second per
instance — a distinct, preserved feature, not replaced by PART_ROLES.
"""

import os

SWATCHES = {
    "white": (1.0, 1.0, 1.0),
    "brown": (0.43, 0.35, 0.28),  # matches furniture/bed's "brown" (1126)
    "misty": (0.31, 0.44, 0.50),  # matches furniture/bed's "misty" (1128)
    "metal": (0.55, 0.55, 0.57),  # brushed-steel look, for the drawer handles/rod
}


def swatch_rgb(name):
    if name not in SWATCHES:
        raise ValueError(f"Unknown color swatch {name!r}; known: {sorted(SWATCHES)}")
    return SWATCHES[name]


# --- The 3 shared roles ---------------------------------------------------
MAIN_COLOR = swatch_rgb(os.environ.get("MAIN_COLOR") or "misty")
SECOND_COLOR = swatch_rgb(os.environ.get("SECOND_COLOR") or "white")
REUSED_COLOR = swatch_rgb(os.environ.get("REUSED_MDF_COLOR") or "white")

_ROLE_COLOR = {"main": MAIN_COLOR, "second": SECOND_COLOR, "reused": REUSED_COLOR}


def role_rgb(role):
    if role not in _ROLE_COLOR:
        raise ValueError(f"Unknown color role {role!r}; known: {sorted(_ROLE_COLOR)}")
    return _ROLE_COLOR[role]


# --- Which part uses which role -------------------------------------------
PART_ROLES = {
    "body": "main",  # Left/Right/Bottom/Top carcass panels, both units (wardrobe.py)
}


def part_rgb(part):
    if part not in PART_ROLES:
        raise ValueError(f"Unknown part {part!r}; known: {sorted(PART_ROLES)}")
    return role_rgb(PART_ROLES[part])
