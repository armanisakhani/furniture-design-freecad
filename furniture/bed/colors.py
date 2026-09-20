"""
Named color swatches (references/colors/) and the 3 shared color roles
every furniture/ module understands the same way (see docs/CONTEXT.md):
  * main   — MAIN_COLOR env var, default "misty". The structural/trim
    color (see PART_ROLES below for which parts use it).
  * second — SECOND_COLOR env var, default "white". The accent color.
  * reused — REUSED_MDF_COLOR env var, default "white". What reclaimed/
    hidden panels get, regardless of main/second (core/panel.py's own
    stock_source convention picks this automatically — no PART_ROLES
    entry needed for it).
Same 3 names/env vars in furniture/dresser and furniture/wardrobe's own
colors.py, so one ORDER entry format works for every furniture/ item,
e.g. `bed:1:MAIN_COLOR=misty;SECOND_COLOR=white`.

PART_ROLES (loaded from furniture/bed/part_roles.yaml) is the single
place that answers "what color is X" — box.py/bed.py look up a part's
role here and resolve it with part_rgb()/part_override_rgb(), instead of
deciding colors ad hoc at each call site.

The actual resolution rules (swatch_rgb/role_rgb/part_rgb/
part_effective_role/part_override_rgb) are shared by every furniture/
module's colors.py — see core/colors.py. This file supplies only the
data those rules run against: SWATCHES and PART_ROLES.
"""

import os

import yaml

import core.colors

# --- Named swatches (references/colors/) --------------------------------
# RGB triples, 0-1 range, sampled/estimated by eye from the reference
# swatch photo. Manufacturer reference numbers (where known) are noted in
# comments, not modeled as data — nothing reads them programmatically.
SWATCHES = {
    "white": (1.0, 1.0, 1.0),
    "misty": (0.31, 0.44, 0.50),  # 1128-misty.jpg
    "brown": (0.43, 0.35, 0.28),  # 1126-brown.jpg
    "anthracite": (0.38, 0.37, 0.36),  # 1129-anthracite.png
    "cuppuccino": (0.59, 0.52, 0.48),  # 1123-cuppuccino.jpeg
    "pearl": (0.97, 0.97, 0.96),  # 1124-pearl.jpeg
    "shale-gray": (0.79, 0.78, 0.79),  # 1134-shale-gray.jpg
}

# --- Which part uses which role -------------------------------------------
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


# --- Position swatches: one solid color per box, by position -----------
# An alternative to the box_top/box_edge_band/drawer_face split above:
# instead of each box having a 2-tone body/front, every box is a single
# solid color, and that color depends on the box's position — the middle
# box one color, the 2 side boxes another (e.g. a misty middle box between
# 2 solid-brown side boxes). Turned on via BOX_COLOR_BY_POSITION
# (params.py, set per STYLE) — a distinct feature from PART_ROLES above,
# not part of the main/second/reused vocabulary. Bed-specific: no
# equivalent in dresser/wardrobe, so it stays local to this file rather
# than in core/colors.py.
POSITION_SWATCHES = dict(middle="misty", side="brown")


def _resolve_position_swatches():
    swatches = dict(POSITION_SWATCHES)
    if os.environ.get("MIDDLE_BOX_SWATCH"):
        swatches["middle"] = os.environ["MIDDLE_BOX_SWATCH"]
    if os.environ.get("SIDE_BOX_SWATCH"):
        swatches["side"] = os.environ["SIDE_BOX_SWATCH"]
    return swatches


_position = _resolve_position_swatches()

MIDDLE_BOX_COLOR = swatch_rgb(_position["middle"])
SIDE_BOX_COLOR = swatch_rgb(_position["side"])
