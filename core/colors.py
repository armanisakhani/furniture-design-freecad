"""
Shared color-role resolution engine behind every furniture module's own
colors.py (furniture/bed, furniture/dresser, furniture/wardrobe). Each
module supplies its own SWATCHES (name -> (r, g, b) tuple, 0-1 range) and
PART_ROLES (part -> "main"/"second"/"reused", loaded from its own
part_roles.yaml) tables; make_resolver() binds the shared resolution
rules to that module's own two tables, so a module's colors.py becomes
just its data plus a thin re-export of the bound resolver's methods. See
docs/CONTEXT.md for the main/second/reused vocabulary itself.
"""

import os


class ColorResolver:
    """Bound to one furniture module's own SWATCHES/PART_ROLES. Reads the
    3 shared env vars (MAIN_COLOR/SECOND_COLOR/REUSED_MDF_COLOR) once, at
    construction — same as every colors.py did before this was shared."""

    def __init__(self, swatches, part_roles):
        self.swatches = swatches
        self.part_roles = part_roles
        self.main_color = self.swatch_rgb(os.environ.get("MAIN_COLOR") or "misty")
        self.second_color = self.swatch_rgb(os.environ.get("SECOND_COLOR") or "white")
        self.reused_color = self.swatch_rgb(os.environ.get("REUSED_MDF_COLOR") or "white")
        self._role_color = {
            "main": self.main_color,
            "second": self.second_color,
            "reused": self.reused_color,
        }

    def swatch_rgb(self, name):
        if name not in self.swatches:
            raise ValueError(f"Unknown color swatch {name!r}; known: {sorted(self.swatches)}")
        return self.swatches[name]

    def role_rgb(self, role):
        if role not in self._role_color:
            raise ValueError(f"Unknown color role {role!r}; known: {sorted(self._role_color)}")
        return self._role_color[role]

    def part_rgb(self, part):
        if part not in self.part_roles:
            raise ValueError(f"Unknown part {part!r}; known: {sorted(self.part_roles)}")
        return self.role_rgb(self.part_roles[part])

    def part_effective_role(self, part):
        """Which of main/second/reused `part`'s color ACTUALLY resolves to
        right now, accounting for the same <PART>_ROLE override as
        part_override_rgb() below — but NOT a <PART>_SWATCH override,
        which names a specific swatch with no single role of its own
        (reported as None, never "reused"). Lets a caller decide whether
        this part's own board can physically come from reclaimed scrap
        (always assumed a single color, REUSED_MDF_COLOR) or needs a real
        new sheet in a specific color — reclaimed stock can't supply an
        arbitrary color on demand, so a part resolving to anything but
        "reused" needs stock_source="new" regardless of what a caller
        might otherwise default it to (see core/panel.py's
        resolve_stock())."""
        if os.environ.get(f"{part.upper()}_SWATCH"):
            return None
        return os.environ.get(f"{part.upper()}_ROLE") or self.part_roles[part]

    def part_override_rgb(self, part):
        """part_rgb(part), unless overridden for just this one order/build:
        a <PART>_SWATCH env var (e.g. BOX_TOP_SWATCH, from an order item's
        own box_top_swatch: key) names a specific swatch directly —
        independent of PART_ROLES/main-second-reused; or a <PART>_ROLE env
        var (e.g. BOX_TOP_ROLE, from an order item's own part_roles:
        {box_top: ...} block) reassigns which of main/second/reused it
        uses instead of part_roles.yaml's own default, without editing
        that file. SWATCH wins if both are somehow set."""
        swatch_override = os.environ.get(f"{part.upper()}_SWATCH")
        if swatch_override:
            return self.swatch_rgb(swatch_override)
        role_override = os.environ.get(f"{part.upper()}_ROLE")
        if role_override:
            return self.role_rgb(role_override)
        return self.part_rgb(part)


def make_resolver(swatches, part_roles):
    return ColorResolver(swatches, part_roles)
