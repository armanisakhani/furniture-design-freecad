"""
Named color swatches for the dresser (دراور) model, and the 3 shared
color roles every furniture/ module understands the same way (see
furniture/bed/colors.py's own module docstring for the full picture):
  * main   — MAIN_COLOR env var, default "misty".
  * second — SECOND_COLOR env var, default "white".
  * reused — REUSED_MDF_COLOR env var, default "white".
Same 3 names/env vars in furniture/bed and furniture/wardrobe's own
colors.py, so one ORDER entry format works for every furniture/ item.

PART_ROLES answers "what color is X" for this module's fixed-role parts
(currently just "body" — the carcass). The drawer Face's own color is
NOT here — it's picked per-drawer by DRAWER_COLOR_PATTERN (params.py),
a '1'/'0' digit string (one digit per drawer, top to bottom) choosing
main/second per drawer instance — a distinct, preserved feature, not
replaced by PART_ROLES.
"""

import os

SWATCHES = {
    "white": (1.0, 1.0, 1.0),
    "brown": (0.43, 0.35, 0.28),  # matches furniture/bed's "brown" (1126)
    "misty": (0.31, 0.44, 0.50),  # matches furniture/bed's "misty" (1128)
    "metal": (0.55, 0.55, 0.57),  # brushed-steel look, for the drawer handles
    "glass": (0.78, 0.83, 0.85),  # pale silvered-glass tint, for the optional mirror pane
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
    "body": "main",           # Left/Right/Bottom/Top carcass panels (dresser.py)
    "mirror_frame": "main",   # optional mirror's frame rails/stiles (dresser.py)
}


def part_rgb(part):
    if part not in PART_ROLES:
        raise ValueError(f"Unknown part {part!r}; known: {sorted(PART_ROLES)}")
    return role_rgb(PART_ROLES[part])
