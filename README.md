# furniture-design-freecad

Parametric FreeCAD furniture designs, built for real MDF fabrication.

## Layout

- `core/` — shared across every design: the `Panel` primitive, placement helpers, and the test-verification helper. Furniture-agnostic; never imports a design's own `params.py`.
- `furniture/<name>/` — one design per subfolder (currently just `bed/`). Each has its own `params.py` (single source of truth for dimensions), its own assembly modules, a `tests/` folder (headless `freecadcmd` scripts, run after any change), and a `references/` folder (photos, cut-list spreadsheets, color swatches).
- `docs/` — `CONTEXT.md` (shared + per-design domain glossary), `roadmap.md` (the bed design's own phase-by-phase execution log), `plan.md` (original vision doc, historical).
- `tools/` — GUI helper scripts (`view_bed.sh` and friends) for opening a model with colors/camera already applied, no manual FreeCAD console typing needed.

## Adding a new furniture design

Create `furniture/<name>/` with its own `params.py`, assembly module(s), and `tests/`; import shared primitives from `core/` (e.g. `from core.panel import create_assembly_panel`). Add a `docs/roadmap-<name>.md` for its own execution log, and a new section in `docs/CONTEXT.md` for its own vocabulary.

## Running tests

```
make test-bed       # all 4 bed test scripts
make view-bed        # open the bed model in FreeCAD's GUI with colors/camera applied
make view-bed REBUILD=1   # regenerate from params.py first, then open
```

See `Makefile` for the underlying `freecadcmd` invocations.
