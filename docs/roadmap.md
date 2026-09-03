# Roadmap — Bed / Drawer-Box System (`furniture/bed/`)

This is the working, step-by-step execution plan for the bed design specifically. `plan.md` stays as the original project vision/onboarding doc. This file is what we actually follow, phase by phase, and gets updated as decisions are made and measurements come in. A future furniture design (bookshelf, shelving, ...) gets its own `docs/roadmap-<name>.md` rather than a section here — this file stays scoped to the bed.

Status legend: `[ ]` not started, `[~]` in progress, `[x]` done.

## Design decisions locked so far

* Coordinate/naming convention: `LENGTH` = head-to-toe direction of the bed
  (mattress 2000 mm), `WIDTH` = side-by-side direction (mattress 1800 mm).
  Matches `BED_LENGTH` / `BED_WIDTH` in `plan.md`.
* The bed is built from `BOX_COUNT` (currently 3) identical "bed box" units
  placed side by side. Each box is one shared shell (top, bottom, 2 long side
  walls, 1 center divider) containing 2 drawers that open from opposite faces.
  So each long side of the finished bed shows `BOX_COUNT` drawer fronts.
* First variant to build: **Model A** — drawer with no handle, opened by hand
  from underneath; a metal leg/support frame raises the whole bed off the
  floor to leave hand clearance under the drawer fronts. (Model B —
  push-to-open rails, no leg frame needed — comes later as an alternate
  configuration, not a rewrite.)
* The reference spreadsheet's "old vs new" columns were just an earlier manual
  attempt to shrink some dimensions to fit a 2000×1800 mattress — not two
  material sources and not two designs we need to support. We are dropping
  that distinction entirely now that dimensions are derived from parameters.
* Drawer bottom material: 3 mm fiber board (not 18/16 mm MDF). Confirmed.
* Panel thickness: purchased MDF is nominally ~16 mm, but the boxes in the
  reference photos imply ~20 mm of effective wall thickness — likely because
  of a laminate/veneer finish added on top of the core board. User is
  re-measuring the real panels; until then `PANEL_THICKNESS` is a clearly
  marked placeholder.
* All uncertain fabrication numbers (rail clearance, final panel thickness,
  skirt height, reveal gaps, etc.) become named parameters with a placeholder
  default and a `# TBD` comment — never hard-coded inline in geometry code.

## Open items (need real numbers before Phase 6, not blocking earlier phases)

* Drawer slide rail model — `RAIL_LENGTH`/`RAIL_CLEARANCE`/`RAIL_THICKNESS`/
  `RAIL_POSITION_Z` are all still placeholder values pending a chosen model
  and its datasheet.
* Leg/support frame height and construction (for Model A):
  `LEG_FRAME_HEIGHT` still placeholder.
* Which specific panel edges get PVC edge banding, and whether the core
  MDF cut size needs to shrink on those edges to hit the finished target
  dimension — decided per panel once panels are defined in Phase 2/3, not a
  global params.py value.

---

## Phase 0 — FreeCAD onboarding & toolchain verification

Purpose: you have never used FreeCAD before, so before any real modeling we
confirm the whole chain — IDE → script → FreeCAD → visible geometry — actually
works end to end on your Mac. No project geometry yet, just a smoke test.

* [x] Confirmed FreeCAD version and its bundled Python version.
  * FreeCAD: **1.1.3** (weekly/dev build, 2026-07-25)
  * Bundled Python: **3.11.14**
  * Install location: `/Applications/FreeCAD.app`
* [x] Decided the run method: **`freecadcmd`**, the headless CLI binary at
  `/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd`. It runs a
  plain `.py` file against FreeCAD's own Python with `FreeCAD`/`Part`/etc.
  importable, no GUI needed. We use the GUI only to *view* the resulting
  `.FCStd` file. Recipe:
  ```bash
  /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd path/to/script.py
  open -a FreeCAD path/to/output.FCStd   # to inspect the result visually
  ```
* [x] Wrote and ran the smoke-test script: [smoke_test.py](../furniture/bed/tests/smoke_test.py).
  It creates one `Part::Box` (400×300×18, X×Y×Z) and saves it to
  `output/phase0_smoke_test.FCStd`. Ran successfully; opened in the FreeCAD
  GUI and visually confirmed (box visible, selectable, default gray solid —
  pre-select highlight on hover is normal FreeCAD behavior). **Phase 0 done.**
* **Gotcha found and documented in the script**: `freecadcmd` runs a script
  with `__name__` set to the script's filename, not `"__main__"`. The usual
  `if __name__ == "__main__":` entry-point guard silently never fires under
  `freecadcmd` — call the entry function unconditionally instead.

## Phase 1 — Parameter architecture (`params.py`)

Purpose: agree on and encode every design "knob" in one place, with no
geometry logic mixed in, before writing a single panel.

Deliverable: [params.py](../furniture/bed/params.py) — a plain module (no FreeCAD import, no
geometry), grouped into Mattress / Frame / Drawer / Skirt / Support frame /
Material. `FRAME_LENGTH`/`FRAME_WIDTH` are derived from the mattress size
plus a gap, not set directly. Every value not yet confirmed is marked
`# TBD` with a placeholder that keeps the rest of the model runnable:

* `MATTRESS_TO_FRAME_GAP`, `PANEL_THICKNESS`, `DRAWER_FRONT_MODE`,
  `RAIL_LENGTH`, `RAIL_CLEARANCE`, `SKIRT_HEIGHT`, `SKIRT_THICKNESS`,
  `LEG_FRAME_HEIGHT`.

This is a draft for review — confirm names/grouping/placeholder values before
later phases start importing from it, since changing a name later means
updating every module that imports it.

* [x] `params.py` written with the grouping above.
* [x] Reviewed and confirmed by you (names, grouping, placeholder values).
  Changes made during review:
  * `PANEL_THICKNESS` split into `MDF_THICKNESS` (16, confirmed — the
    board core, drives all box/drawer fitting) and `PVC_THICKNESS` (2,
    confirmed — edge-banding tape, cosmetic/edge-only, does not affect
    fitting geometry). The earlier "~20mm effective wall thickness" guess
    from the reference photos is explained by `MDF_THICKNESS + 2 *
    PVC_THICKNESS` (edge band wrapping both visible faces of a cut edge),
    not a face laminate.
  * `RAIL_THICKNESS` and `RAIL_POSITION_Z` added (`plan.md` listed both;
    they were missing from the draft).
  * `DRAWER_FRONT_MODE` decided: `"overlay"` to build first (`"inset"` stays
    supported through the same parameter, built second).
  * `DRAWER_FRONT_OVERLAY_AMOUNT` added (drives the box top overhang below).
  * Explored during review, then flagged as **NOT settled** — do not build
    on this without revisiting it first: an idea to drop the separate
    top-trim part and instead have the box's OWN top panel extend forward
    past the side walls (on both long faces) to cap over each overlay
    drawer front. Added `BOX_TOP_OVERHANG`, `DRAWER_TOP_REVEAL_GAP`, and
    `BOX_TOP_PANEL_WIDTH` (`FRAME_WIDTH + 2 * BOX_TOP_OVERHANG`) to
    `params.py`, but the user then noticed this conflates the
    mattress-bearing surface with the drawer-covering lip (e.g. it still
    adds a visible rim around the mattress even with
    `MATTRESS_TO_FRAME_GAP_WIDTH = 0`, where a flush fit is expected).
    Parked for later rather than fixed now — revisit before Phase 3 uses
    it. See the `# TBD` / "UNDER RECONSIDERATION" comments in `params.py`.
  * `SKIRT_THICKNESS` made independent of `MDF_THICKNESS` (was derived);
    `SKIRT_HEIGHT` confirmed at 30 (3cm).
  * Terminology: see `CONTEXT.md` for `Box` vs `Drawer_box`, the
    `visible`/`stock_source` per-panel concept (kept alive from `plan.md`,
    not dropped — the roadmap's earlier "dropping that distinction" note
    was about the reference spreadsheet's columns only), and `Box top
    overhang` (retires the earlier "top trim" idea).

## Phase 2 — Reusable parametric MDF panel primitive

* Implement `Panel` as a `Part::FeaturePython` object (custom `Proxy` class)
  with properties for length, width, thickness, name, material, color —
  driven by `params.py` values, not literals.
* Using a `FeaturePython` object (rather than a one-shot `Part.makeBox()`
  script) means changing a property and hitting Recompute in the GUI actually
  regenerates the shape — genuinely parametric, not "re-run the script".
* Test: generate one real panel from the reference set (e.g. the box top/
  bottom panel) and confirm it opens correctly and reports correct
  dimensions/volume in FreeCAD.

* [x] `Panel` implemented in [panel.py](../core/panel.py), tested by
  [panel_test.py](../furniture/bed/tests/panel_test.py) (generates the box top panel
  from `params.py`: `FRAME_LENGTH` × `BOX_TOP_PANEL_WIDTH` ×
  `MDF_THICKNESS`). Ran headlessly via `freecadcmd`; volume matched exactly,
  and a separate check confirmed changing `Thickness` + `doc.recompute()`
  genuinely regenerates the shape (not a one-shot script). **Phase 2 done.**
  Design choices made while implementing (not pre-specified, flagging for
  review):
  * `Length`/`Width`/`Thickness` are the panel's own **local** frame (Length
    → local X, Width → local Y, Thickness → local Z — same mapping
    `Part::Box` and `phase0_smoke_test.py` use), independent of the bed's
    global LENGTH/WIDTH/height axes. A panel used as a vertical side wall
    will get there via `Placement` in Phase 3, not by swapping which
    property means what.
  * `name` is `Panel.Label` (built into every FreeCAD object) — no separate
    custom name property.
  * `Material` is an `App::PropertyEnumeration` with 3 fixed choices —
    `"MDF"` / `"PVC"` / `"Fiber"` — matching `MDF_THICKNESS`,
    `PVC_THICKNESS`, `DRAWER_BOTTOM_THICKNESS` in `params.py`.
  * Color and the `visible`/`stock_source` pair (`CONTEXT.md`) are named
    `PanelColor` / `PanelVisible` on the object, deliberately not `Color` /
    `Visible`, to avoid confusion with FreeCAD's own GUI-facing
    `ViewObject` visibility/appearance concepts — `PanelVisible` is a
    fabrication meaning (visible in the finished assembly → new stock),
    unrelated to 3D-view show/hide.
  * `PanelColor` is stored as data only for now — not yet wired to
    `ViewObject.ShapeColor`. Deferred to Phase 9 (materials/appearance
    polish), since `freecadcmd` has no `ViewObject` to attach a custom
    `ViewProvider` to anyway.
  * Per-edge PVC banding info (mentioned in `plan.md` and this file's Open
    Items) is **not** a `Panel` property yet — deferred until Phase 3, where
    specific edges of specific panels are actually identified in the
    assembly.

## Phase 3 — Single bed-box assembly (no rails/skirt yet)

* Compose one full "bed box" from panels: top, bottom, 2 side walls, 1 center
  divider, positioned using `PANEL_THICKNESS` so panels butt together
  correctly (no naive "touching boxes").
* Add the 2 drawer carcasses (sides, front, back, bottom) sized against the
  box's internal opening — still without rail clearance math (placeholder
  gap).

* [x] Implemented in [box.py](../furniture/bed/box.py) (`create_box()`), tested by
  [box_test.py](../furniture/bed/tests/box_test.py) — builds one full Box (6 shell
  panels + 2 Drawer_box carcasses × 5 = 16 panels) and checks bounding
  boxes. Ran headlessly; overall footprint matches `FRAME_WIDTH ×
  BOX_LENGTH × BOX_HEIGHT` exactly, nothing overlaps. Visually confirmed in
  the FreeCAD GUI. **Phase 3 done.** Added `BOX_LENGTH` (`params.py`,
  `FRAME_LENGTH / BOX_COUNT`).
  * **First attempt was wrong, corrected same session**: originally built
    with one shared center divider and drawer depth = half of
    `FRAME_WIDTH` minus a placeholder gap (~882mm deep). The user caught
    this against `bed-1-box.jpg` and the reference cut-list spreadsheet
    (Google Sheet, "دیواره عرضی داخلی (پشت کشو)" row): real drawer depth is
    essentially fixed by the rail, independent of `FRAME_WIDTH`, and
    instead of one shared divider there are 2 separate "internal
    transverse walls" (one behind each drawer) with open, unused space
    between them — visible in the reference photo as the gap where loose
    hardware sits.
  * Verified against general drawer-slide sizing convention before
    rebuilding (web research, see Sources below): drawer box depth should
    match the slide's own nominal length; per-side width clearance for the
    slide hardware is commonly ~1/2" (12.7-13.5mm); the box/compartment
    should be a few mm (~3-5mm) deeper than the slide's nominal length so
    the drawer doesn't jam at full close; vertical clearance above the
    drawer for the slide hardware is at least ~1/2" (12mm). Applied
    directly: drawer depth = `RAIL_LENGTH` (650); drawer width uses
    `RAIL_CLEARANCE` (13, already a good placeholder — confirmed, not
    changed) per side; new `RAIL_BACK_CLEARANCE` (5) is the gap behind
    each drawer before its internal transverse wall; `DRAWER_TOP_REVEAL_GAP`
    bumped from an arbitrary 2 to 12 to match. Removed `DRAWER_FIT_GAP`
    (superseded — no longer needed now that real rail-derived params cover
    the same role).
    Sources: [Rockler — Choosing the Right Drawer Slide](https://www.rockler.com/learn/choosing-drawer-slide),
    [Firgelli — Drawer Slide Sizing Guide](https://www.firgelliauto.com/blogs/drawer-slides/what-size-of-drawer-slides-do-i-need),
    [Sawmill Creek — Drawer depth vs width using ball bearing slides](https://sawmillcreek.org/threads/drawer-depth-vs-width-using-ball-bearing-slides.303362/).
  * Construction convention used (flagging per `plan.md`'s "explain the
    assumption" instruction — one valid method among several, not verified
    against the reference photos' actual joinery beyond the 2 corrections
    on this page): top/bottom panels are the box's full external footprint
    and cap over the 2 long side walls, which are trapped between them (Z)
    at the box's two Y extremes, at height `BOX_INTERIOR_HEIGHT` (not
    `BOX_HEIGHT` — see below); these double as the rail-mounting walls,
    since both drawers slide along X. Each internal transverse wall is
    trapped the same way (Y, and between top/bottom in Z, also at
    `BOX_INTERIOR_HEIGHT`), positioned `RAIL_BACK_CLEARANCE` behind its
    drawer's back plane. The X=0/X=FRAME_WIDTH faces are deliberately left
    open for the 2 drawers. Same trapping logic one level down for each
    Drawer_box carcass (bottom → full footprint, 2 sides → trapped in Z,
    front/back → trapped between the sides in Y).
  * **Second and third corrections, same session** (this took 2 tries to
    get right — recorded in full since the reasoning is non-obvious): the
    first `box.py` draft derived side-wall height as `BOX_HEIGHT - 2*t` =
    218mm. The user caught this against the reference spreadsheet's
    "کناره" (side) row, which reports 25cm — an intermediate fix made the
    side walls full-`BOX_HEIGHT` (250mm) instead, trapping top/bottom in Y
    rather than the sides in Z. That was *also* wrong: the same
    spreadsheet's "دیواره عرضی داخلی" (internal transverse wall) row
    reports the same 25cm — and that wall is necessarily trapped between
    top/bottom (it's a structural brace, physically can't run past them),
    so both rows can only agree if 25cm is the *trapped/interior* height,
    not the box's true external height. The user's own framing settled it:
    "you can have a clear interior height that's 25, and a frame_height
    that's `25 + 2*mdf_thickness`." Implemented as a new base param,
    `BOX_INTERIOR_HEIGHT = 250` (confirmed, `params.py`), with `BOX_HEIGHT`
    now *derived* from it (`BOX_INTERIOR_HEIGHT + 2*MDF_THICKNESS` = 282) —
    matching the same "confirmed part dimension drives the derived total"
    pattern `FRAME_LENGTH`/`FRAME_WIDTH` already use elsewhere in
    `params.py`. `box.py` reverted to the original trapping direction
    (top/bottom full-footprint, sides trapped) with heights sourced from
    `BOX_INTERIOR_HEIGHT` throughout (side walls, internal transverse
    walls, and `drawer_side_height`) instead of re-deriving
    `box_height - 2*t` locally.
  * **Overlay drawer front + top overhang implemented** (same session,
    after the height corrections above): `BOX_TOP_OVERHANG` /
    `BOX_TOP_PANEL_WIDTH` were confirmed (no longer "under
    reconsideration" — the visible rim around the mattress on the WIDTH
    sides is accepted, intentional, per the user). `DRAWER_TOP_REVEAL_GAP`
    corrected from 12 to 6mm after follow-up research specifically on
    ball-bearing side-mount slides (~1/4"=6.35mm total vertical clearance,
    not the ~12mm a more generic source first suggested — see sources
    below). The Top panel's width grows by `BOX_TOP_OVERHANG` on both X
    sides to cap over the drawer front.
    Sources: [Firgelli — Drawer Slide Sizing Guide](https://www.firgelliauto.com/blogs/drawer-slides/what-size-of-drawer-slides-do-i-need) (1/4" min vertical clearance for ball-bearing slides).
  * **Correction, same session**: the first pass at this made the drawer
    "front" one panel doing double duty (structural + visible face). The
    user caught this too: a real Drawer_box front is 2 separate panels — a
    structural front (flush/inset with the box opening, same as the
    already-correct Back, hidden once assembled) plus a separate "Face"
    (نما) panel screwed onto it, which is what's actually visible and
    actually overlays. New param `DRAWER_FACE_GAP` (3, TBD placeholder —
    no real number chosen) is the reveal between 2 adjacent boxes' Face
    panels. The Face turned out to be much bigger than just "the drawer
    opening, pushed out": vertically it runs from the drawer's own top
    (aligned with the structural front/back, `DRAWER_TOP_REVEAL_GAP` below
    the Top panel) down to `SKIRT_HEIGHT` *below* the box's own bottom
    (Z=0) — meaning it doubles as the drawer-side skirt. Confirmed with the
    user: `HAS_DRAWER_SIDE_SKIRT` therefore needs no separate panel at all
    (the Face already does that job); only `HAS_END_SKIRT` (the short,
    drawer-less faces) still needs a real skirt panel, in Phase 6. Panel
    count per box went from 16 to 18 (added a Face per drawer).
    Verified: the Top panel's outer X edges land exactly flush with both
    Face panels' outer X faces (computed independently from the same
    params, confirmed by the test, not hand-tuned to match).
  * `visible`/`stock_source` on the shell's 2 long side walls assume an
    isolated box (both walls hidden/reclaimed-eligible). That's only true
    for the *middle* box once 3 are assembled side by side — the first and
    last box's outer long wall would actually be the bed's head/foot face
    (visible/new). Phase 6 should override this per box position rather
    than trust `create_box()`'s defaults.

## Phase 4 — Drawer rails & real clearances

* Introduce `RAIL_LENGTH` / `RAIL_CLEARANCE` for real, once the rail model is
  chosen, and adjust drawer external dimensions to fit inside the box opening
  with correct clearance on each side.

## Phase 5 — Cut list generation

* Walk every `Panel` object in the document, group by thickness/material,
  output a plain-text and CSV cut list (as sketched in `plan.md`).

## Phase 6 — Full bed assembly (3 boxes + skirt + leg frame, Model A)

* Arrange `BOX_COUNT` boxes side by side to form the full bed.
* Add the drawer-side skirt (always, `HAS_DRAWER_SIDE_SKIRT`) and end skirt
  (if `HAS_END_SKIRT`), accounting for `DRAWER_FRONT_MODE` when the drawer
  front protrudes past the box face.
* Add the leg/support frame as at least a simplified reference geometry.

* [~] Started early, out of order (user wanted a quick look at the whole
  bed): [bed.py](../furniture/bed/bed.py)'s `create_bed()` places all `BOX_COUNT` boxes side
  by side (just calling `create_box()` per index — its `y_offset` default
  was already built for exactly this reuse, back in Phase 3) plus a plain,
  undyed `Part::Box` mattress placeholder on top (not a `Panel`, not part
  of the cut list — the mattress isn't fabricated). `MATTRESS_THICKNESS`
  confirmed at 300 (30cm; started as a 200 guess, corrected by the user).
  * `place_panel`/`IDENTITY`/`ROT_X90`/`ROT_Y90` moved from `box.py` down
    into `panel.py` (a real refactor, not speculative — `bed.py` needed
    them too, so they belong one level down; `box.py` keeps its own
    `_place`/`_IDENTITY`/etc. names as local aliases so its many call sites
    didn't need touching).
  * **Head end butts a wall, confirmed with the user** — nothing at all is
    built there (no skirt, no Face). Only the foot end (`Y = FRAME_LENGTH`)
    gets the 3 pieces below. An earlier version of this file built a skirt
    at *both* ends; corrected to foot-only.
  * `MATTRESS_TO_FRAME_GAP_LENGTH` corrected from an earlier wrong 10 to
    100 (confirmed: 10cm) — the user had mistyped it. This changed
    `FRAME_LENGTH`/`BOX_LENGTH` too (2100 / 700, not 2010 / 670).
  * Added the **mattress-stop cap** (`create_mattress_stop_foot`): a FLAT
    MDF panel lying on top of the top panels' surface at the foot end (not
    a raised wall — an earlier version of this file got this wrong,
    building it as a vertical upstand; corrected). Its width (Y) fills
    exactly the foot-end gap, so it *is* `MATTRESS_TO_FRAME_GAP_LENGTH` —
    no separate param for it (an earlier `MATTRESS_STOP_HEIGHT` param
    existed briefly and was removed once this became clear). Its length
    (X) also grew to match `BOX_TOP_PANEL_WIDTH` (not just `FRAME_WIDTH`)
    — same corners as the Top panel and the Face panels.
    * Also added **`create_mattress_stop_side`**: the same idea, rotated
      90° — 2 caps filling the WIDTH-direction gap
      (`MATTRESS_TO_FRAME_GAP_WIDTH`) on the 2 long/drawer-carrying sides,
      running the full `FRAME_LENGTH`. Only built when that gap is
      nonzero (`create_bed` checks) — the user changed it from 0 to 100 as
      an explicit experiment to see the gap appear, then asked for these.
      Verified: both land at `Z=[282,298]`, same level as the foot-end cap.
    * **Third correction**: the foot cap and the 2 side caps overlapped a
      full `MATTRESS_TO_FRAME_GAP_LENGTH x MATTRESS_TO_FRAME_GAP_WIDTH`
      square (double MDF thickness) at each foot-end corner. The user sent
      a reference photo (`side-shape.jpg`) showing these pieces meeting at
      a plain 90-degree butt joint, no miter, no overlap. Fixed by
      shortening the 2 side caps' Y-span to
      `FRAME_LENGTH - MATTRESS_TO_FRAME_GAP_LENGTH` (they now stop exactly
      where the foot cap begins) rather than trimming the foot cap, since
      the foot cap's own width had to grow anyway (next point).
    * **Fourth correction**, same photo: `MattressStopFoot` also caps over
      `EndFaceFoot`'s own top edge — same "horizontal cap covers the
      vertical panel's end grain" pattern used everywhere else in this
      project (Top panel over the box's side walls, Top panel over the
      Drawer Face). Its width (Y) grew from just
      `MATTRESS_TO_FRAME_GAP_LENGTH` to
      `MATTRESS_TO_FRAME_GAP_LENGTH + MDF_THICKNESS`, verified to land
      exactly flush with `EndFaceFoot`'s own extent (`Y=[2100,2116]` is
      fully inside the cap's `Y=[2000,2116]`, both topping out at `Z=298`).
  * Added an **end Face**: an MDF panel attached to the outer face of the
    last box's `SideWallFar` (the bed's true visible foot end, not an
    internal seam between boxes) and extending further outward by its own
    thickness — same overlay pattern as the `Drawer_box` Face, applied to
    the bed's own end wall. **Corrected twice**: first version only
    matched the wall's own `BOX_INTERIOR_HEIGHT` in Z and `FRAME_WIDTH` in
    X, with a *separate* `EndSkirtFoot` panel handling the bottom reach —
    the user caught that this should be ONE panel instead: X grown to
    `BOX_TOP_PANEL_WIDTH` (same reach as the Top panel / Drawer Face), Z
    now spans from `-SKIRT_HEIGHT` (bottom, same as each Drawer_box's Face
    — this is what made the separate `EndSkirtFoot` panel redundant, so it
    was removed) up to the top of the MattressStop cap
    (`BOX_HEIGHT + MDF_THICKNESS`, verified by the test to land exactly
    flush with it). This is one way of fixing the long-flagged issue that
    a box's end-wall `visible`/`stock_source` depends on its position in
    the bed (see Phase 3 entry) — by adding a visible Face on top, rather
    than by changing the hidden structural wall's own properties.
  * Tested by [bed_test.py](../furniture/bed/tests/bed_test.py): 56 panels (3×18 +
    2 bed-level — `MattressStop` + `EndFaceFoot`), overall bounding box
    matches expectations.
  * **NOT done**: no leg frame, and the box's structural end-wall
    `visible`/`stock_source` itself (as opposed to the new Face covering
    it) still isn't corrected. Also: the head/foot orientation (which end
    of Y is "head") is an undocumented, arbitrary choice made in `bed.py`,
    not verified against a reference photo.

* **Fifth correction, same area, later session**: the box shell (Bottom,
  the 2 long side walls) sat flush at `X=[0,FRAME_WIDTH]`, and the
  overlay Face panels then poked *outward* past that by their own
  thickness — meaning the assembled Box+Face actually overshot
  `FRAME_WIDTH` by 2×`MDF_THICKNESS` on each box, silently, since nothing
  had checked the *total* assembled width against `FRAME_WIDTH` before.
  The user caught this by describing the 2 stacked layers explicitly: an
  outer layer (mattress + 2 side frames) that must total exactly
  `FRAME_WIDTH`, and an inner layer (box + drawer front) that must
  *also* total exactly `FRAME_WIDTH` once assembled — so the box shell
  itself has to be `FRAME_WIDTH - 2*MDF_THICKNESS` wide, letting the
  Face's overlay close the gap back up to `FRAME_WIDTH` exactly. Fixed by
  adding `BOX_WIDTH` (`params.py`) as this inset shell footprint and
  `BOX_SHELL_X_MIN` (`= MDF_THICKNESS`) as where it starts, applied to
  Bottom, the 2 side walls, and both drawer carcasses in `box.py`.
  `MattressStopFoot` / `EndFaceFoot` (`bed.py`) were also corrected to use
  `FRAME_WIDTH` directly instead of `BOX_TOP_PANEL_WIDTH` — they belong to
  the *outer* mattress/frame layer, which is always `FRAME_WIDTH`
  regardless of how the box's own Top panel behaves.
  Also **new**: the same conversation revealed 2 genuinely different ways
  the drawer can meet the box's Top panel, both still "overlay" — modeled
  as a new param, `DRAWER_OVERLAY_STYLE`:
    - `"box_over_drawer"` (default, matches what was already built): the
      Top panel itself reaches all the way out to `FRAME_WIDTH`, capping
      the drawer's Face from above. `BOX_TOP_PANEL_WIDTH` is now exactly
      `FRAME_WIDTH` in this mode (previously it was
      `FRAME_WIDTH + 2*BOX_TOP_OVERHANG`, i.e. wider than `FRAME_WIDTH` —
      that overshoot is what got corrected above).
    - `"rail_above_drawer"`: an unmodeled rail-mount frame (hardware, like
      `RAIL_*`) sits on top of the drawer and does the reaching instead,
      so the Top panel stays inset like the rest of the shell
      (`BOX_TOP_PANEL_WIDTH = BOX_WIDTH`), and the drawer carcass loses
      one `MDF_THICKNESS` of height (`drawer_side_height` in `box.py`) to
      leave room for that frame.
  `BOX_TOP_OVERHANG` (the old single-purpose param) was removed entirely,
  replaced by `BOX_TOP_PANEL_WIDTH` / `BOX_TOP_X_MIN` being computed
  directly from `DRAWER_OVERLAY_STYLE`. Verified via
  [box_test.py](../furniture/bed/tests/box_test.py) and
  [bed_test.py](../furniture/bed/tests/bed_test.py): in the default style, Box1's
  Top now spans exactly `X=[0,2000]` (was `X=[-16,2016]`), Bottom/side
  walls span `X=[16,1984]`, and the 2 drawer Faces exactly fill the
  remaining `X=[0,16]` / `X=[1984,2000]` gaps — total assembled width is
  exactly `FRAME_WIDTH`, no overshoot.

* **Sixth correction, same session**: `MattressStopFoot` had been inflated
  by an extra `MDF_THICKNESS` (10cm gap → 11.6cm) specifically so it could
  still cap over `EndFaceFoot`'s own thickness, which stuck out past
  `FRAME_LENGTH` by that same amount. The user caught that this treated a
  symptom rather than the cause: `MattressStopFoot`'s width should just
  equal `MATTRESS_TO_FRAME_GAP_LENGTH` (matching `MattressStopSide`'s own
  width, no reason for it to be special), and the real fix belonged in
  `BOX_LENGTH` — the boxes' own combined Y-footprint should stop 1
  `MDF_THICKNESS` short of `FRAME_LENGTH`, leaving exactly enough room for
  `EndFaceFoot` to sit flush inside that gap (the same "shell inset, Face
  pokes back out to the true boundary" pattern already used for
  `BOX_WIDTH`/`DRAWER_OVERLAY_STYLE` above, just applied to the LENGTH
  axis this time). Fixed:
    - `BOX_LENGTH` (`params.py`) changed from `FRAME_LENGTH / BOX_COUNT` to
      `(FRAME_LENGTH - MDF_THICKNESS) / BOX_COUNT` — since all `BOX_COUNT`
      boxes are identical and placed by a plain `box_index * BOX_LENGTH`
      offset (no per-box special-casing anywhere), the 1 `MDF_THICKNESS`
      is split evenly across all of them rather than only shrinking the
      last one; `MDF_THICKNESS`'s own definition had to move above
      `BOX_LENGTH` in the file since the formula now depends on it.
    - `create_end_face` (`bed.py`): Y position changed from `FRAME_LENGTH`
      to `FRAME_LENGTH - MDF_THICKNESS`, so it now ends exactly at
      `FRAME_LENGTH` instead of poking out past it.
    - `create_mattress_stop_foot` (`bed.py`): width reverted from
      `MATTRESS_TO_FRAME_GAP_LENGTH + MDF_THICKNESS` back to plain
      `MATTRESS_TO_FRAME_GAP_LENGTH`.
  Verified: `EndFaceFoot` now lands at `Y=[2084,2100]`, `MattressStopFoot`
  at `Y=[2000,2100]` — the former fully nested inside the latter, so it's
  still fully capped, and nothing pokes out past `FRAME_LENGTH=2100`
  anymore (the overall bed bounding box's Y-max dropped from 2116 to
  exactly 2100).

* **Architecture cleanup** (no geometry changes — verified identical bboxes
  before/after): `DRAWER_OVERLAY_STYLE`'s 4 scattered branches (2 in
  `params.py`, 2 in `box.py`) collapsed into one `_drawer_overlay_geometry()`
  in `params.py`, exposing `DRAWER_HEIGHT_REDUCTION`/`DRAWER_FACE_TOP_REF_Z`.
  `panel.py` gained `create_assembly_panel()` (create + place + the
  stock_source→color rule in one call); `box.py`'s `add_panel` and `bed.py`'s
  4 panel functions now delegate to it instead of duplicating that logic.
  `verify.py` (new) turns the phase test scripts' printed bounding boxes into
  real pass/fail assertions — this also caught 2 pre-existing wrong "expected"
  lines (`phase3_box_test.py`'s Z range ignored the Face's `-SKIRT_HEIGHT`
  reach; `phase6_bed_test.py`'s ignored the headboard extending past Y=0/Z=0).

## Phase 7 — Alternate variant: push-to-open (Model B)

* Reuse the same parametric core; switch `DRAWER_FRONT_MODE` / rail type and
  drop the leg frame, without duplicating the whole model.

## Phase 8 — Doors, touch-latch mechanism, wider bedroom furniture

* As in `plan.md`'s original Phase 7 — separate cabinets/wardrobe with doors,
  once the bed/drawer system is solid.

## Phase 9 — Materials, appearance, optional rendering polish

* As in `plan.md`'s original Phase 8.
* [~] Started early, out of order (user asked mid-Phase-3): real colors
  chosen from the user's swatch catalog (`colors/`) — `RECLAIMED_MDF_COLOR`
  (white, confirmed) added as a new param; `BODY_COLOR` changed to "Misty"
  1128 and `DRAWER_FRONT_COLOR` to "Brown" 1126 (both estimated by eye from
  the swatch JPEGs, no exact hex/RAL code given yet — refine if one turns
  up). Color model changed to be StockSource-first: any `reclaimed` panel
  gets `RECLAIMED_MDF_COLOR` regardless of role; `box.py`'s `add_panel()`
  now derives this automatically instead of every call site hardcoding a
  color. `ShapeColor` still isn't wired to actually render in the FreeCAD
  viewport (data-only, see Phase 2 entry) — [apply_colors.py](../tools/apply_colors.py)
  is a one-off helper to run inside the GUI's Python console (not
  freecadcmd) that copies `PanelColor` onto `ViewObject.ShapeColor` for
  whatever document is currently open, since headless scripts can't write
  view data into the .FCStd at all. A real fix (auto-apply on file open) is
  still open for whenever this phase is properly tackled.

---

Next step: **Phase 0**, the FreeCAD smoke test — confirming the toolchain
works before writing any real project code.
