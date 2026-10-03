"""
Named color swatches for the TV table (میز تلویزیون) model, and the 3 shared
color roles every furniture/ module understands the same way (see
furniture/bed/colors.py's own module docstring for the full picture):
  * main   — MAIN_COLOR env var, default "misty".
  * second — SECOND_COLOR env var, default "white".
  * reused — REUSED_MDF_COLOR env var, default "white".
Same 3 names/env vars in furniture/bed and furniture/wardrobe's own
colors.py, so one ORDER entry format works for every furniture/ item.

PART_ROLES (loaded from furniture/tv_table/part_roles.yaml) answers "what
color is X" for this module's fixed-role parts — edit that file to move a
part to a different role, nothing else needs to change. The drawer Face is the
"face" part.

The actual resolution rules (swatch_rgb/role_rgb/part_rgb/
part_effective_role/part_override_rgb) are shared by every furniture/
module's colors.py — see core/colors.py. This file supplies only the
data those rules run against: SWATCHES and PART_ROLES.
"""

import os

import yaml

import core.colors

SWATCHES = {
    "white": (1.0, 1.0, 1.0),
    "brown": (0.43, 0.35, 0.28),  # matches furniture/bed's "brown" (1126)
    "misty": (0.31, 0.44, 0.50),  # matches furniture/bed's "misty" (1128)
    "cuppuccino": (0.59, 0.52, 0.48),  # matches furniture/bed's "cuppuccino" (1123)
    "pearl": (0.97, 0.97, 0.96),  # matches furniture/bed's "pearl" (1124)
    "shale-gray": (0.79, 0.78, 0.79),  # matches furniture/bed's "shale-gray" (1134)
    "metal": (0.55, 0.55, 0.57),  # brushed-steel look, for the drawer handles
    "glass": (0.78, 0.83, 0.85),  # pale silvered-glass tint, for the optional mirror pane
}

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "part_roles.yaml")) as _f:
    PART_ROLES = yaml.safe_load(_f)

_resolver = core.colors.make_resolver(SWATCHES, PART_ROLES)

MAIN_COLOR = _resolver.main_color
SECOND_COLOR = _resolver.second_color
REUSED_COLOR = _resolver.reused_color

swatch_rgb = _resolver.swatch_rgb
role_rgb = _resolver.role_rgb
part_rgb = _resolver.part_rgb
part_effective_role = _resolver.part_effective_role
part_override_rgb = _resolver.part_override_rgb
