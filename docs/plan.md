# FreeCAD Parametric MDF Furniture Project

> Original project vision/spec, kept as a historical reference — not a live status doc. For current status see `roadmap.md` (bed design); a new furniture design gets its own `roadmap-<name>.md`. For current terminology see `CONTEXT.md`.

I want to build a parametric furniture-design workflow in FreeCAD using Python.

## Main goal

The goal is to design real MDF furniture (initially a bed / bedroom furniture and drawer boxes) in FreeCAD.

I don't want to manually model every MDF panel. I want the model to be generated and controlled through Python parameters.

The workflow should eventually be:

User parameters
→ Python script
→ FreeCAD 3D model
→ individual MDF panels
→ hardware / rails / doors
→ dimensions and relationships
→ cut list / bill of materials

The design should be suitable for actual MDF fabrication, not just visual 3D modeling.

## Software

* OS: macOS
* CAD: FreeCAD
* Programming language: Python
* The Python scripts should work with FreeCAD's Python API.
* Prefer open-source/free solutions whenever possible.
* Do not depend on paid FreeCAD add-ons unless absolutely necessary.

## Important design philosophy

The model should be PARAMETRIC.

I want important dimensions to exist as variables at the top of the script, for example:

```python
BED_WIDTH = 1800
BED_LENGTH = 2000
MDF_THICKNESS = 16  # provisional — user will confirm exact spec of purchased sheets

DRAWER_BOX_WIDTH = 735
DRAWER_BOX_DEPTH = 650
DRAWER_BOX_HEIGHT = 280

DRAWER_BOTTOM_THICKNESS = 6
```

Changing these values should regenerate/update the model correctly.

Avoid hard-coding dimensions throughout the script.

Create reusable functions/classes such as:

```python
create_panel(...)
create_drawer_box(...)
create_bed(...)
create_rail(...)
create_door(...)
```

The exact architecture can be improved as the project develops.

## Coordinate system

Use a consistent coordinate system:

* X = width
* Y = depth / length
* Z = height

All dimensions are in millimeters.

## Material sourcing / stock sheets

There are two sources of MDF stock:

1. **New sheets** — purchased new, standard size **1830 mm × 3660 mm** (183 × 366 cm), thickness **16 mm** (provisional, unconfirmed — user will update if it turns out different). There may be a separate new-sheet thickness for the ~6 mm drawer bottoms; not yet confirmed.
2. **Old / reclaimed sheets** — leftover MDF the user already owns. Exact dimensions/thickness of these are not yet known; the user will provide them later.

Constraint: **panels that are visible in the finished furniture must be cut from new sheets. Panels that are hidden from view (not visible once assembled) should be cut from the old/reclaimed sheets**, to reuse existing material without affecting appearance.

Implication for the model: each panel needs a `visible` (bool) attribute and a `stock_source` ("new" / "reclaimed") attribute, so the cut list can later be split per stock source and nested against the correct sheet size. Do not hard-code which panels are hidden — decide this per panel based on its role in the assembly (e.g. drawer back/bottom, cabinet back panel, internal dividers are typically hidden; drawer fronts, sides of open furniture, top surfaces are typically visible), and confirm with the user if a panel's visibility is ambiguous.

## MDF panels

Each MDF panel should ideally be represented as an individual FreeCAD object.

A panel should have:

* name
* quantity
* length
* width
* thickness
* material
* visible (bool) — whether the panel is visible in the finished piece
* stock_source ("new" / "reclaimed")
* optional edge information

For example:

```text
Side_Left
Side_Right
Top
Bottom
Back
Drawer_Left
Drawer_Right
Drawer_Front
Drawer_Back
Drawer_Bottom
```

The geometry should use the actual MDF thickness.

## Materials / appearance

I want to be able to assign different appearances to different components.

For example:

* MDF body: white
* wood/MDF decorative panels: wood color
* metal rails: gray

Later I may want to use actual wood/MDF textures.

Appearance is useful, but dimensional accuracy and fabrication information are more important.

## Drawer boxes

The first practical component we want to build is a drawer box.

Example dimensions:

* external width: 735 mm
* external depth: 650 mm
* external height: 280 mm
* body MDF: 18 mm
* drawer bottom: approximately 6 mm

The design must distinguish between:

* external dimensions
* internal dimensions
* MDF thickness
* drawer bottom thickness
* rail clearance

Do not assume dimensions without documenting the assumption.

## Drawer rails

I want the model to support real drawer slides/rails.

The rail should eventually have parameters such as:

```python
RAIL_LENGTH
RAIL_THICKNESS
RAIL_CLEARANCE
RAIL_POSITION_Z
```

The exact rail geometry can initially be simplified as a visual representation.

Later we can model a specific real rail if I provide its dimensions/model.

## Doors / touch opening

I may also have MDF doors using a touch-to-open mechanism.

The model should allow:

* door thickness
* door width
* door height
* gaps
* touch-latch position

The actual hardware can initially be represented schematically rather than with detailed manufacturer geometry.

## Cut list

A major goal is to automatically generate a cut list.

Example:

```text
CUT LIST

MDF 18mm
--------------------------------
Part             Qty    L      W
Side             2      700    650
Top              1      699    650
Bottom           1      699    650
Drawer Side      2      ...
Drawer Front     1      ...
Drawer Back      1      ...

MDF 6mm
--------------------------------
Drawer Bottom    1      ...
```

The cut list must be calculated from the parametric model, not manually typed.

Eventually I would like to export this to CSV/XLSX.

## Important fabrication considerations

Do not simply create visually touching boxes.

Dimensions must account for:

* MDF thickness
* internal vs external dimensions
* gaps
* drawer-slide clearance
* door gaps
* back-panel thickness
* assembly method
* overlaps / recesses where appropriate

When there are multiple valid construction methods, explain the assumption before implementing it.

## Development approach

Do NOT try to build the entire bedroom furniture system at once.

Build incrementally:

### Phase 1

Create one accurate MDF panel parametrically.

### Phase 2

Create a reusable `create_panel()` function.

### Phase 3

Create a parametric drawer box.

### Phase 4

Add drawer rails and clearances.

### Phase 5

Generate a cut list automatically.

### Phase 6

Create the complete bed / bedroom furniture.

### Phase 7

Add doors, touch mechanisms and hardware.

### Phase 8

Improve materials, appearance and optional rendering.

## Code quality

The code should be:

* modular
* readable
* heavily commented where necessary
* parameter-driven
* easy to modify
* compatible with FreeCAD on macOS
* avoid unnecessary dependencies

Prefer one main Python entry point, for example:

```text
main.py
```

with reusable modules if the project becomes large.

## Current state

FreeCAD is already installed on my Mac.

I have successfully opened the FreeCAD Python console and understand that Python can create FreeCAD objects.

I want to continue development from the IDE using an AI coding agent.

Your first task is NOT to build the whole system.

First inspect the FreeCAD Python API relevant to this project and propose a clean project structure.

Then implement Phase 1 and Phase 2:

1. A reusable parametric MDF panel.
2. A simple test that creates a 735 × 650 × 18 mm MDF panel.
3. Give the panel a useful object name and basic material/color.
4. Make sure the script can be executed from FreeCAD's Python environment.
5. Explain how I should run/debug the script from my IDE and FreeCAD.

After that, wait for my confirmation before implementing the drawer box.

Important: whenever a fabrication dimension is ambiguous, ask me rather than silently making an assumption.
