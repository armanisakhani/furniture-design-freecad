# Handoff — Parametric Bed / Drawer-Box Project

Written for a fresh agent session with no prior context. Read this, then
`plan.md` (vision/spec) and `roadmap.md` (phased execution plan with a
checklist) for full detail. This file is a snapshot, not a source of truth —
`roadmap.md`'s checkboxes are the actual status tracker; update them as you
go instead of relying on this file staying current.

## Project

`/Users/divar/design/bedroom` — not a git repo. Files present:

* `plan.md` — original project vision/spec (English). Read-only reference,
  not meant to be re-executed literally; superseded in execution order by
  `roadmap.md`.
* `roadmap.md` — the actual phased plan we're following, with a status
  checklist per phase. **Check this first for current progress.**
* `params.py` — single source of truth for design parameters (Phase 1
  deliverable). Plain Python, no FreeCAD import.
* `phase0_smoke_test.py` — verified working FreeCAD toolchain smoke test.
* `output/phase0_smoke_test.FCStd` — generated artifact from the smoke test.
* Reference material for the real piece being modeled: `bed-0-whole.jpg`,
  `bed-1-box.jpg`, `bed-2-base.jpg` (photos of an existing similar bed the
  user built), and a `.xlsx` cut-list export (also readable from the
  original Google Sheet the user shared, if network access is available).

The user communicates in Persian; keep code/docs in English (matches the
existing files) and reply to the user in Persian.

## Where things stand

**Phase 0 (FreeCAD onboarding) — done and visually verified.**
* FreeCAD 1.1.3 (dev build) installed at `/Applications/FreeCAD.app`, bundled
  Python 3.11.14.
* Run scripts headlessly with:
  `/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd path/to/script.py`
* Inspect a result visually with: `open -a FreeCAD path/to/file.FCStd`
* **Gotcha**: under `freecadcmd`, a script's `__name__` is set to the
  filename, not `"__main__"`. Do not gate an entry point behind
  `if __name__ == "__main__":` — call it unconditionally, as
  `phase0_smoke_test.py` does.

**Phase 1 (`params.py`) — drafted, iterated once on user feedback, not yet
explicitly confirmed as final.** Recent changes the user requested, already
applied:
* Split `MATTRESS_TO_FRAME_GAP` into `MATTRESS_TO_FRAME_GAP_LENGTH` (applies
  once, foot end only — the head end sits flush, no frame overhang there)
  and `MATTRESS_TO_FRAME_GAP_WIDTH` (applies symmetrically, both sides).
  `FRAME_LENGTH`/`FRAME_WIDTH` are derived from these plus mattress size.
* Added a two-tone finish model: `BODY_COLOR` for carcass parts (frame, box
  bottom, dividers, skirt, etc.) vs `DRAWER_FRONT_COLOR` for drawer fronts
  only. Both are meant to represent a laminate/veneer glued on after
  cutting — a panel's laminate always matches whichever of the two groups it
  belongs to; a drawer front never gets the body laminate and vice versa.

Before writing more geometry code, it would be good to have the user do one
explicit pass confirming `params.py`'s names/grouping/placeholder values,
since every later phase imports from it and renames get expensive later.

## Key open items (marked `# TBD` in params.py — do not silently guess these)

* `MATTRESS_TO_FRAME_GAP_LENGTH` / `_WIDTH` — exact values.
* `PANEL_THICKNESS` — currently 20mm placeholder. Purchased MDF is nominally
  ~16mm, but reference photos imply ~20mm effective wall thickness, likely
  because of a laminate/veneer finish added on top of the core board. User
  is re-measuring the real panels.
* `DRAWER_FRONT_MODE` ("inset" vs "overlay") — affects whether the skirt
  needs a cutout around protruding drawer fronts.
* `RAIL_LENGTH` / `RAIL_CLEARANCE` — drawer slide rail model not chosen yet
  (reference notes 600 or 650mm nominal); need the real datasheet clearance
  once a model is picked.
* `SKIRT_HEIGHT`, `SKIRT_THICKNESS`, `LEG_FRAME_HEIGHT` — all placeholders.
* `DRAWER_FRONT_COLOR` — placeholder value, real color not yet decided.

Whenever a fabrication dimension is ambiguous, ask the user rather than
silently assuming — this is an explicit standing instruction from `plan.md`.

## Design decisions already locked (see `roadmap.md` for full detail)

* Coordinate convention: `LENGTH` = head-to-toe direction of the bed
  (mattress 2000mm), `WIDTH` = side-by-side direction (mattress 1800mm). `X`
  = width, `Y` = depth/length, `Z` = height (from `plan.md`).
* The bed is `BOX_COUNT` (3) identical "bed box" units side by side. Each box
  is one shared shell (top, bottom, 2 long side walls, 1 center divider)
  containing 2 drawers opening from opposite faces — so each long side of
  the finished bed shows `BOX_COUNT` drawer fronts.
* Building **Model A** first: drawer with no handle, opened by hand from
  underneath; a metal leg/support frame raises the bed for hand clearance
  under the drawer fronts. Model B (push-to-open rails, no leg frame) comes
  later as an alternate configuration of the same parametric core, not a
  separate rewrite.
* The reference spreadsheet's "old vs new" columns were an earlier manual
  attempt to shrink dimensions to fit a 2000×1800 mattress — not two
  material sources, not two designs to support. That distinction is dropped
  entirely now that dimensions are derived from parameters.
* Drawer bottom: 3mm fiber board (confirmed, not MDF).
* Architecture principle the user explicitly asked for: keep every design
  parameter in `params.py`, nothing hard-coded inline in geometry code. Use
  a `Part::FeaturePython` object (not a one-shot `Part.makeBox()` script) for
  panels, so changing a property and recomputing in the GUI actually
  regenerates the shape.

## Next step

**Phase 2** in `roadmap.md`: implement `Panel` as a `Part::FeaturePython`
object (custom `Proxy` class) with properties for length/width/thickness/
name/material/color, driven by `params.py`. Test by generating one real
panel (e.g. the box top/bottom) and confirming it opens correctly in the
FreeCAD GUI with correct dimensions and color, using the `freecadcmd` +
`open -a FreeCAD` workflow established in Phase 0.
