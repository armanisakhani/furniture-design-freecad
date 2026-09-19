"""
Registry of the project's furniture modules + named-order YAML loading, for
the orders/ scripts that combine multiple furniture/<name>/ designs into one
order (run_order.py, build_item.py, combine_order.py, order_cutlist.py,
generate_report.py).

An order is a YAML file under orders/specs/<name>.yaml, e.g.
orders/specs/default.yaml:

    colors:               # optional — applies to every item below
      main: misty
      second: white
    items:
      - furniture: bed
        qty: 1
      - furniture: dresser
        qty: 2
        style: 2
      - furniture: wardrobe
        layout: two_piece
        color_pattern: "1_0111"
        gap_after: 0      # mm gap after THIS item's own copies (0 = touching)

`colors` becomes MAIN_COLOR/SECOND_COLOR/REUSED_MDF_COLOR env vars applied
to every item's build. Every other per-item key (besides `furniture`, `qty`,
`gap_after`) is passed through as an env var for that one item's own build,
uppercased — the same env vars each furniture module's own params.py already
reads: STYLE, LAYOUT, COLOR_PATTERN, BOX_COLOR_BY_POSITION, ... See
load_order() below.

Every design does a bare `import params` / `import colors` relying on its
own directory being on sys.path — loading 2 designs (or 2 differently
configured builds of the same design) into the SAME Python process would
have them silently share one "params" module. So build_item.py builds
exactly one order entry per freecadcmd process, each into its own
instance_key ("<name>-<index in the order's items list>") files under
output/<order name>/items/, so 2 differently configured entries of the same
type never collide — and 2 different named orders never collide either,
since each gets its own output/<order name>/ directory.
"""

import os

import yaml

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECS_DIR = os.path.join(_ROOT, "orders", "specs")
OUTPUT_DIR = os.path.join(_ROOT, "orders", "output")

# flip: some designs measure their own Y=0 as the WALL side (the bed's
# headboard, see furniture/bed/bed.py's own "Head end at Y=0, against the
# room's wall" convention) while others measure Y=0 as the FRONT/open
# side (dresser/wardrobe's drawers). combine_order.py rotates a
# flip=True entry 180 degrees about Z so its wall side lands on the same
# combined-scene side as everything else, instead of its headboard facing
# the viewer where a front-opening face would be.
FURNITURE = {
    "bed": dict(dir=os.path.join(_ROOT, "furniture", "bed"), label="تخت", flip=True),
    "dresser": dict(dir=os.path.join(_ROOT, "furniture", "dresser"), label="دراور", flip=False),
    "wardrobe": dict(dir=os.path.join(_ROOT, "furniture", "wardrobe"), label="کمد لباس", flip=False),
}

# order-level `colors:` keys -> the env var each furniture module's own
# colors.py reads (see e.g. furniture/bed/colors.py's MAIN_COLOR/
# SECOND_COLOR/REUSED_COLOR).
_COLOR_ENV = {"main": "MAIN_COLOR", "second": "SECOND_COLOR", "reused": "REUSED_MDF_COLOR"}

# Per-item keys that are this loader's own concern (order layout), not a
# furniture module's env var override.
_ITEM_KEYS = {"furniture", "qty", "gap_after"}


def spec_path(name):
    return os.path.join(SPECS_DIR, f"{name}.yaml")


def load_order(name):
    """Loads orders/specs/<name>.yaml into
    {"name": name, "env": {"MAIN_COLOR": "brown", ...}, "entries": [
        {"name": "bed", "qty": 1, "overrides": {}, "instance_key": "bed-0", "gap_after": None},
        {"name": "dresser", "qty": 2, "overrides": {"STYLE": "2"}, "instance_key": "dresser-1", "gap_after": None},
    ]}."""
    path = spec_path(name)
    if not os.path.exists(path):
        raise SystemExit(
            f"No such order {name!r} — expected {path}. "
            f"Known orders: {sorted(n[:-5] for n in os.listdir(SPECS_DIR) if n.endswith('.yaml'))}"
        )
    with open(path) as f:
        spec = yaml.safe_load(f) or {}

    env = {}
    for key, value in (spec.get("colors") or {}).items():
        if key not in _COLOR_ENV:
            raise ValueError(f"Unknown colors key {key!r} in order {name!r}; expected one of {sorted(_COLOR_ENV)}")
        env[_COLOR_ENV[key]] = str(value)

    entries = []
    for index, item in enumerate(spec.get("items") or []):
        item = dict(item)
        furniture = item.pop("furniture", None)
        if furniture not in FURNITURE:
            raise ValueError(f"Unknown furniture {furniture!r} in order {name!r}; known: {sorted(FURNITURE)}")
        qty = int(item.pop("qty", 1))
        gap_after = item.pop("gap_after", None)
        overrides = {str(key).upper(): str(value) for key, value in item.items()}
        entries.append(dict(
            name=furniture, qty=qty, overrides=overrides, instance_key=f"{furniture}-{index}",
            gap_after=float(gap_after) if gap_after is not None else None,
        ))
    if not entries:
        raise ValueError(f"Order {name!r} has no items ({path})")

    return dict(name=name, env=env, entries=entries)


def order_paths(name):
    """Every output file for one named order, all under its own
    output/<name>/ directory so 2 named orders never share or overwrite
    each other's build."""
    out_dir = os.path.join(OUTPUT_DIR, name)
    return dict(
        dir=out_dir,
        items_dir=os.path.join(out_dir, "items"),
        fcstd=os.path.join(out_dir, "order.FCStd"),
        scene_json=os.path.join(out_dir, "order_scene.json"),
        render_png=os.path.join(out_dir, "order_render.png"),
        report_html=os.path.join(out_dir, "report.html"),
    )


def item_paths(order_name, instance_key):
    items_dir = order_paths(order_name)["items_dir"]
    return dict(
        fcstd=os.path.join(items_dir, f"{instance_key}.FCStd"),
        panels_json=os.path.join(items_dir, f"{instance_key}.panels.json"),
    )


def require_item_built(order_name, entry):
    """Raises a clear, loud error if build_item.py's freecadcmd subprocess
    for this entry didn't actually produce its output files — freecadcmd
    silently swallows an unhandled exception from the script it runs (e.g.
    params.py's own ValueError for an unknown STYLE or colors.py's for an
    unknown color swatch): it prints "Exception while processing file:
    ... [message]" to its own stdout/stderr but still exits 0, so a plain
    `subprocess.run(..., check=True)` never notices the failure and the
    pipeline would otherwise silently carry on with a missing item instead
    of stopping at the actual bad input. Call this right after that
    subprocess call, in run_order.py/generate_report.py — both plain
    Python processes, so a raised error here prints and propagates
    normally, unlike inside freecadcmd itself."""
    paths = item_paths(order_name, entry["instance_key"])
    missing = [p for p in (paths["fcstd"], paths["panels_json"]) if not os.path.exists(p)]
    if missing:
        overrides = " ".join(f"{k}={v}" for k, v in entry["overrides"].items())
        raise SystemExit(
            f"Building {entry['instance_key']!r} ({entry['name']}) produced no output "
            f"({', '.join(missing)} missing) — see the freecadcmd output above for the "
            f"actual error (often an unknown STYLE or color value). Reproduce it directly:\n"
            f"  FURNITURE={entry['name']} INSTANCE_KEY={entry['instance_key']} "
            f"ORDER_NAME={order_name} {overrides} freecadcmd orders/build_item.py"
        )
