"""
Named color swatches for the wardrobe (کمد لباس) model, and the 3 shared
color roles every furniture/ module understands the same way (see
furniture/bed/colors.py's own module docstring for the full picture):
  * main   — MAIN_COLOR env var, default "misty".
  * second — SECOND_COLOR env var, default "white".
  * reused — REUSED_MDF_COLOR env var, default "white".
Same 3 names/env vars in furniture/bed and furniture/dresser's own
colors.py, so one ORDER entry format works for every furniture/ item.

PART_ROLES (loaded from furniture/wardrobe/part_roles.yaml) answers "what
color is X" for this module's fixed-role parts — edit that file to move a
part to a different role, nothing else needs to change. The door and
drawer Face colors are NOT here — they're picked by DOOR_COLOR_DIGIT and
DRAWER_COLOR_PATTERN (params.py), '1'/'0' digits choosing main/second per
instance — a distinct, preserved feature, not replaced by PART_ROLES.
"""

import os

import yaml

SWATCHES = {
    "white": (1.0, 1.0, 1.0),
    "brown": (0.43, 0.35, 0.28),  # matches furniture/bed's "brown" (1126)
    "misty": (0.31, 0.44, 0.50),  # matches furniture/bed's "misty" (1128)
    "cuppuccino": (0.59, 0.52, 0.48),  # matches furniture/bed's "cuppuccino" (1123)
    "pearl": (0.97, 0.97, 0.96),  # matches furniture/bed's "pearl" (1124)
    "shale-gray": (0.79, 0.78, 0.79),  # matches furniture/bed's "shale-gray" (1134)
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
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "part_roles.yaml")) as _f:
    PART_ROLES = yaml.safe_load(_f)


def part_rgb(part):
    if part not in PART_ROLES:
        raise ValueError(f"Unknown part {part!r}; known: {sorted(PART_ROLES)}")
    return role_rgb(PART_ROLES[part])


def part_override_rgb(part):
    """part_rgb(part), unless overridden for just this one order/build:
    a <PART>_SWATCH env var (e.g. LEFT_SWATCH, from an order item's own
    left_swatch: key) names a specific swatch directly — independent of
    PART_ROLES/main-second-reused, same idea as furniture/bed's
    MIDDLE_BOX_SWATCH/SIDE_BOX_SWATCH; or a <PART>_ROLE env var (e.g.
    LEFT_ROLE, from an order item's own part_roles: {left: ...} block)
    reassigns which of main/second/reused it uses instead of
    part_roles.yaml's own default, without editing that file. SWATCH
    wins if both are somehow set."""
    swatch_override = os.environ.get(f"{part.upper()}_SWATCH")
    if swatch_override:
        return swatch_rgb(swatch_override)
    role_override = os.environ.get(f"{part.upper()}_ROLE")
    if role_override:
        return role_rgb(role_override)
    return part_rgb(part)
