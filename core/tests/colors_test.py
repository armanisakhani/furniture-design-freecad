"""
Unit test for core/colors.py's shared color-role resolver — the engine
behind every furniture/<name>/colors.py. Exercises the resolver directly,
past every furniture module's own call sites — the exact seam whose
absence let the same stock_source bug recur 3 times (once per furniture
module) before core/colors.py existed.

Runs under freecadcmd like every other test in this repo: core/panel.py
(for resolve_stock) transitively imports FreeCAD/Part via core/placement.py,
so this can't run under a plain python3 interpreter even though
core/colors.py itself has no FreeCAD dependency.

Note: freecadcmd runs a script with __name__ set to the script's
filename, not "__main__" — call main() unconditionally.
"""

import os
import sys

_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

from core.colors import make_resolver
from core.panel import resolve_stock

SWATCHES = {"white": (1.0, 1.0, 1.0), "misty": (0.31, 0.44, 0.50), "brown": (0.43, 0.35, 0.28)}
PART_ROLES = {"top": "main", "back": "reused", "left": "second"}

_ENV_VARS = ["MAIN_COLOR", "SECOND_COLOR", "REUSED_MDF_COLOR", "TOP_ROLE", "TOP_SWATCH"]


def with_clean_env(fn):
    """Run fn() with every env var this test touches unset, restoring
    whatever was there afterward — so one test's TOP_ROLE=... doesn't leak
    into the next."""
    saved = {name: os.environ.pop(name, None) for name in _ENV_VARS}
    try:
        fn()
    finally:
        for name, value in saved.items():
            if value is not None:
                os.environ[name] = value
            else:
                os.environ.pop(name, None)


def test_swatch_rgb_known_and_unknown():
    r = make_resolver(SWATCHES, PART_ROLES)
    assert r.swatch_rgb("misty") == (0.31, 0.44, 0.50)
    try:
        r.swatch_rgb("no-such-swatch")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_role_defaults_and_env_overrides():
    r = make_resolver(SWATCHES, PART_ROLES)
    assert r.role_rgb("main") == SWATCHES["misty"]  # default MAIN_COLOR
    assert r.role_rgb("second") == SWATCHES["white"]  # default SECOND_COLOR
    assert r.role_rgb("reused") == SWATCHES["white"]  # default REUSED_MDF_COLOR

    os.environ["MAIN_COLOR"] = "brown"
    r2 = make_resolver(SWATCHES, PART_ROLES)
    assert r2.role_rgb("main") == SWATCHES["brown"]
    assert r.role_rgb("main") == SWATCHES["misty"]  # r wasn't affected retroactively


def test_part_rgb_and_effective_role():
    r = make_resolver(SWATCHES, PART_ROLES)
    assert r.part_rgb("top") == r.main_color
    assert r.part_effective_role("top") == "main"
    assert r.part_effective_role("back") == "reused"

    os.environ["TOP_ROLE"] = "reused"
    r2 = make_resolver(SWATCHES, PART_ROLES)
    assert r2.part_effective_role("top") == "reused"
    assert r2.part_override_rgb("top") == r2.reused_color

    os.environ["TOP_SWATCH"] = "brown"
    r3 = make_resolver(SWATCHES, PART_ROLES)
    assert r3.part_effective_role("top") is None  # swatch override -> no single role
    assert r3.part_override_rgb("top") == SWATCHES["brown"]  # swatch wins over role


def test_resolve_stock_matches_effective_role():
    assert resolve_stock("reused") == "reclaimed"
    assert resolve_stock("main") == "new"
    assert resolve_stock("second") == "new"
    assert resolve_stock(None) == "new"  # a <PART>_SWATCH override


def main():
    with_clean_env(test_swatch_rgb_known_and_unknown)
    with_clean_env(test_role_defaults_and_env_overrides)
    with_clean_env(test_part_rgb_and_effective_role)
    with_clean_env(test_resolve_stock_matches_effective_role)
    print("core/colors.py resolver: all checks passed")


main()
