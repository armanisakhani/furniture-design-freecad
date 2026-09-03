# Parametric Bed / Drawer-Box System

Domain glossary for the FreeCAD parametric bed and bedroom-furniture project. Geometry and fabrication logic live in code; this file only defines the vocabulary.

## Language

**Box** (also "bed box"):
One of `BOX_COUNT` (3) identical shared shell units placed side by side that together form the full bed. Each Box is one shell (top, bottom, 2 long side walls, 1 center divider) containing 2 Drawer_boxes that open from opposite faces.
_Avoid_: "drawer box" for this — that term now means something narrower (see below).

**Drawer_box**:
One individual pull-out drawer unit that sits inside a Box. `DRAWERS_PER_BOX` (2) live in each Box, opening from opposite faces, for `BOX_COUNT * DRAWERS_PER_BOX` (6) total across the bed.
_Avoid_: "drawer" alone (ambiguous with Box in conversation), "drawer box" as a synonym for Box.

**Visible panel / stock source**:
Every panel carries a `visible` (bool) and `stock_source` ("new" / "reclaimed") attribute. Panels not visible in the finished, assembled piece are cut from reclaimed MDF the user already owns, to save cost without affecting appearance; panels visible in the finished piece are cut from new stock. Assignment is a judgment call based on the panel's role in the assembly (e.g. drawer backs/bottoms and internal dividers are typically hidden), not a fixed rule.
_Avoid_: treating this as the same distinction as the reference spreadsheet's old/new columns — that was an unrelated, discarded attempt to shrink dimensions to fit the mattress, not a stock-sourcing decision.

## Fabrication

**MDF thickness**:
The core board's own face-to-face thickness (16 mm, confirmed). Drives all box and drawer fitting geometry.
_Avoid_: "panel thickness" as a synonym — that name is retired; it used to conflate the board core with the edge-banding finish.

**PVC edge banding**:
A thin tape (2 mm, confirmed) glued onto exposed cut edges to hide the raw MDF core. Wraps the edge only — it does not add to MDF thickness or affect box/drawer fitting geometry, only the visible edge profile and later the cut list. Which panel edges get it is a per-panel decision, made when panels are defined.
_Avoid_: assuming it changes overall panel dimensions the way MDF thickness does.

**Skirt** (apron):
A thin decorative MDF trim board hanging down from the underside of a Box, near the floor. Unrelated to drawer position — the drawer lives up near the top of the Box; the skirt is a separate board down near its base. Its height covers only part of the leg frame's height; the remaining gap below it stays open as hand-clearance space for reaching under the handle-less drawer front. Comes in two independently toggled kinds: the drawer-side skirt (on the two long, drawer-carrying faces) and the end skirt (on the two short head/foot faces, which carry no drawer — optional, purely for visual continuity, still a real separate panel in Phase 6).
_Correction_: the drawer-side skirt is **not** a separate panel — each Drawer_box's own Face panel already extends down `SKIRT_HEIGHT` below the box's bottom (see Face below), doing that job. Only the end skirt is still a real, separately built panel.

**Structural front** vs **Face** (نما):
A Drawer_box's front is 2 separate panels, not one. The structural front is flush/inset with the Box's open face, sized and positioned like Back (mirrored), part of the carcass, hidden once assembled. The Face is a separate panel screwed onto the structural front's outer face, extending further outward by its own thickness (`DRAWER_FRONT_OVERLAY_AMOUNT`) — this is the one that's actually visible and actually overlays. It's much taller than the drawer opening: top edge aligned with the drawer's own top, bottom edge extending `SKIRT_HEIGHT` below the Box's own bottom (see Skirt above), and narrower than the Box's own Y-footprint by `DRAWER_FACE_GAP` (a reveal against the neighboring Box's Face).
_Avoid_: treating "drawer front" as a single panel — an earlier Phase 3 draft this session did that, combining structural-front and visible-face into one piece; corrected.

**Internal transverse wall** (دیواره عرضی داخلی, "پشت کشو" = behind the drawer):
A purely structural MDF wall inside a Box, positioned `RAIL_BACK_CLEARANCE` behind a Drawer_box's back — not part of the drawer, not touching it. Its job is to keep the Box's top panel from sagging over the span between the box's two long side walls. Each Box has 2 of them, one behind each of its 2 drawers; since drawer depth (`RAIL_LENGTH`) is much less than half of `FRAME_WIDTH`, the 2 walls don't meet in the middle — there's real open, unused box interior between them (confirmed against `bed-1-box.jpg`, which shows hardware sitting loose in that gap, and the reference cut-list spreadsheet).
_Avoid_: "center divider" — an earlier, incorrect Phase 3 draft used one shared divider at the box's exact center with drawer depth derived as half of `FRAME_WIDTH`; that was wrong and has been replaced by this term/geometry. Also avoid assuming the gap between the 2 walls is itself a modeled part — it's just open space, not built in Phase 3.

**Box shell inset / `DRAWER_OVERLAY_STYLE`** (corrected this session, replaces the old "Box top overhang" entry):
The Box shell itself (Bottom, the 2 long side walls, and the drawer carcasses) is always inset from `FRAME_WIDTH` by `MDF_THICKNESS` on each X side — this is `BOX_WIDTH`. The Face panel's own overlay is what reaches back out to exactly `FRAME_WIDTH`; an earlier version had the shell sitting flush at `FRAME_WIDTH` already, so the assembled Box+Face actually overshot `FRAME_WIDTH` by 2×`MDF_THICKNESS` — this inset is what fixes that, so the mattress-bearing surface lands exactly at `FRAME_WIDTH`, no overshoot. There are 2 modes for how the Box's Top panel relates to the drawer, picked via `DRAWER_OVERLAY_STYLE`: `"box_over_drawer"` (default — the Top panel itself extends all the way to `FRAME_WIDTH` and caps the drawer's Face from above, instead of a separate top-trim part; the reference photos actually show a separate applied piece doing this job, but the user explicitly wants the Top panel itself to do it, a deliberate deviation from the reference) and `"rail_above_drawer"` (an unmodeled rail-mount frame sits above the drawer and does the reaching instead, so the Top panel stays inset like the rest of the shell, and the drawer carcass loses one `MDF_THICKNESS` of height to make room for that frame).
_Avoid_: "top trim" as a separate part — retired. Also avoid assuming the Box shell sits flush at `FRAME_WIDTH` — only the Top panel does, and only in `"box_over_drawer"` style.

## Geometry convention

**Length**:
The head-to-toe direction of the bed (mattress dimension 2000 mm).

**Width**:
The side-by-side direction of the bed (mattress dimension 1800 mm).

## Assembly variants

**Model A**:
The drawer variant being built first — no handle, opened by hand from underneath; requires a leg/support frame to raise the bed for finger clearance under the drawer fronts.

**Model B**:
An alternate configuration of the same parametric core, built later — push-to-open rails, no leg frame needed.
