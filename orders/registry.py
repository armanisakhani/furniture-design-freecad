"""
Registry of the project's furniture modules + ORDER spec parsing, for the
orders/ scripts that combine multiple furniture/<name>/ designs into one
order (run_order.py, build_item.py, combine_order.py, cutlist.py).

ORDER spec: comma-separated entries, each "name:qty[:KEY=VAL;KEY=VAL...]",
e.g.:
    "bed:1,dresser:2:STYLE=2,wardrobe:1:LAYOUT=two_piece;STYLE=1"
-> 1 bed (defaults), 2 dressers built with STYLE=2, 1 wardrobe built with
LAYOUT=two_piece and STYLE=1. Each override becomes an environment
variable for that one entry's own build (the same env vars each furniture
module's own params.py already reads: STYLE, MAIN_COLOR, COLOR_PATTERN,
LAYOUT, ...), scoped to that entry alone.

Every design does a bare `import params` / `import colors` relying on its
own directory being on sys.path — loading 2 designs (or 2 differently
configured builds of the same design) into the SAME Python process would
have them silently share one "params" module. So build_item.py builds
exactly one order entry per freecadcmd process, each into its own
instance_key ("<name>-<index in ORDER>") files under output/items/, so 2
differently configured entries of the same type never collide.
"""

import os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMS_DIR = os.path.join(_ROOT, "orders", "output", "items")

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


def parse_order(spec):
    """"bed:1,dresser:2:STYLE=2" -> [
        {"name": "bed", "qty": 1, "overrides": {}, "instance_key": "bed-0"},
        {"name": "dresser", "qty": 2, "overrides": {"STYLE": "2"}, "instance_key": "dresser-1"},
    ]"""
    entries = []
    for index, part in enumerate(spec.split(",")):
        part = part.strip()
        if not part:
            continue
        fields = part.split(":")
        name = fields[0].strip()
        if name not in FURNITURE:
            raise ValueError(f"Unknown furniture {name!r} in ORDER; known: {sorted(FURNITURE)}")
        qty = int(fields[1]) if len(fields) > 1 and fields[1] else 1
        overrides = {}
        if len(fields) > 2 and fields[2]:
            for pair in fields[2].split(";"):
                key, _, value = pair.partition("=")
                overrides[key.strip()] = value.strip()
        entries.append(dict(name=name, qty=qty, overrides=overrides, instance_key=f"{name}-{index}"))
    if not entries:
        raise ValueError(f"Empty ORDER={spec!r}; expected e.g. 'bed:1,dresser:1,wardrobe:1'")
    return entries


def item_paths(instance_key):
    return dict(
        fcstd=os.path.join(ITEMS_DIR, f"{instance_key}.FCStd"),
        panels_json=os.path.join(ITEMS_DIR, f"{instance_key}.panels.json"),
    )
