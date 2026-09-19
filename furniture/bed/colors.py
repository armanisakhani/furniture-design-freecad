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
"""

import os

import yaml

# --- Named swatches (references/colors/) --------------------------------
# RGB triples, 0-1 range, sampled/estimated by eye from the reference
# swatch photo. `code` is the manufacturer's own reference number (None
# for colors with no such reference, e.g. plain white).
SWATCHES = {
    "white": dict(code=None, rgb=(1.0, 1.0, 1.0)),
    "misty": dict(code=1128, rgb=(0.31, 0.44, 0.50)),  # 1128-misty.jpg
    "brown": dict(code=1126, rgb=(0.43, 0.35, 0.28)),  # 1126-brown.jpg
    "anthracite": dict(code=1129, rgb=(0.38, 0.37, 0.36)),  # 1129-anthracite.png
    "cuppuccino": dict(code=1123, rgb=(0.59, 0.52, 0.48)),  # 1123-cuppuccino.jpeg
    "pearl": dict(code=1124, rgb=(0.97, 0.97, 0.96)),  # 1124-pearl.jpeg
    "shale-gray": dict(code=1134, rgb=(0.79, 0.78, 0.79)),  # 1134-shale-gray.jpg
}


def swatch_rgb(name):
    if name not in SWATCHES:
        raise ValueError(f"Unknown color swatch {name!r}; known: {sorted(SWATCHES)}")
    return SWATCHES[name]["rgb"]


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
    a <PART>_SWATCH env var (e.g. BOX_TOP_SWATCH, from an order item's own
    box_top_swatch: key) names a specific swatch directly — independent
    of PART_ROLES/main-second-reused; or a <PART>_ROLE env var (e.g.
    BOX_TOP_ROLE, from an order item's own part_roles: {box_top: ...}
    block) reassigns which of main/second/reused it uses instead of
    part_roles.yaml's own default, without editing that file. SWATCH
    wins if both are somehow set."""
    swatch_override = os.environ.get(f"{part.upper()}_SWATCH")
    if swatch_override:
        return swatch_rgb(swatch_override)
    role_override = os.environ.get(f"{part.upper()}_ROLE")
    if role_override:
        return role_rgb(role_override)
    return part_rgb(part)


# --- Position swatches: one solid color per box, by position -----------
# An alternative to the box_top/box_edge_band/drawer_face split above:
# instead of each box having a 2-tone body/front, every box is a single
# solid color, and that color depends on the box's position — the middle
# box one color, the 2 side boxes another (e.g. a misty middle box between
# 2 solid-brown side boxes). Turned on via BOX_COLOR_BY_POSITION
# (params.py, set per STYLE) — a distinct feature from PART_ROLES above,
# not part of the main/second/reused vocabulary.
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
