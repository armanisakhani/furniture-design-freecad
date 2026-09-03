"""
Phase 3 — single Box assembly: one Box shell (top, bottom, 2 long side
walls, 2 internal transverse walls) plus its 2 Drawer_box carcasses (2
sides + structural front + back + bottom + Face each), built from Panel
objects (panel.py) and positioned with Placement so they butt together
using MDF_THICKNESS. See CONTEXT.md for Box vs Drawer_box; see roadmap.md
for the history of corrections behind each rule below.

Global axes (plan.md): X = WIDTH, Y = LENGTH (head-to-toe), Z = height.

Construction rules:
  * Box shell (bottom, 2 side walls, and the top panel in "rail_above_
    drawer" style) is inset by MDF_THICKNESS from FRAME_WIDTH on each
    side (BOX_WIDTH, starting at BOX_SHELL_X_MIN) — not flush at
    0..FRAME_WIDTH, so the Face's overlay lands exactly back on
    FRAME_WIDTH. Bottom/Top cap the 2 side walls at BOX_INTERIOR_HEIGHT
    (confirmed against the reference spreadsheet's "کناره" row — not
    BOX_HEIGHT). Side walls double as rail-mounting walls. Shell's X
    extremes are open — where the 2 drawers slide out. Top panel's own
    footprint additionally depends on DRAWER_OVERLAY_STYLE (params.py):
    full FRAME_WIDTH in "box_over_drawer" (caps the drawer from above),
    inset BOX_WIDTH in "rail_above_drawer" (an unmodeled rail frame reaches
    out instead).
  * Drawer depth is RAIL_LENGTH, not derived from FRAME_WIDTH (matches
    drawer-slide sizing convention: depth ≈ slide's nominal length). Since
    RAIL_LENGTH (650) is well under half of FRAME_WIDTH (1800), the 2
    drawers leave a real, intentionally unused gap between them.
  * Each drawer gets its own "internal transverse wall" (دیواره عرضی
    داخلی), RAIL_BACK_CLEARANCE behind its back — purely structural,
    keeps the top panel from sagging over the unsupported span. Trapped
    between the side walls (Y) and top/bottom (Z). The gap between the 2
    walls is intentionally left open/unmodeled (matches reference photos).
  * Drawer_box carcass: bottom (fiber) is the full external footprint;
    2 sides run the full depth, trapped in Z between bottom and top
    clearance; back is trapped between the 2 sides. Width insets
    RAIL_CLEARANCE per side.
  * Drawer_box front is 2 separate panels:
    - Structural front: flush/inset with the box's open face, same
      size/role as Back, part of the carcass, hidden once assembled.
    - Face (نما): attached to the structural front's outer face,
      protruding by its own thickness (DRAWER_FRONT_OVERLAY_AMOUNT) — the
      visible, overlaying panel. Taller than the carcass: top edge is
      DRAWER_TOP_REVEAL_GAP below whatever sits above it per
      DRAWER_OVERLAY_STYLE (params.py); bottom edge extends SKIRT_HEIGHT
      below the box's own bottom, doubling as the drawer-side skirt (no
      separate panel needed there, unlike HAS_END_SKIRT). Narrower than
      the box's Y-footprint by DRAWER_FACE_GAP (reveal against the
      neighboring box's Face).

visible/stock_source defaults below are reasonable per-role guesses for one
isolated box (CONTEXT.md: a judgment call, not a fixed rule) — e.g. a box's
long side walls are only actually visible at the head/foot end of the
assembled bed. Phase 6 should revisit these per box position.
"""

import FreeCAD as App

import params
from core.panel import create_assembly_panel, IDENTITY, ROT_X90, ROT_Y90

# Local aliases so the rest of this module's many call sites don't need
# renaming — IDENTITY/ROT_X90/ROT_Y90 live in core/panel.py since bed.py
# needs them too.
_IDENTITY = IDENTITY
_ROT_X90 = ROT_X90
_ROT_Y90 = ROT_Y90


def create_box(doc, box_index, y_offset=None, label_prefix=None):
    """Create one Box (shell + 2 Drawer_box carcasses) in doc, at the given
    Y offset (defaults to box_index * BOX_LENGTH, so Phase 6 can place
    BOX_COUNT boxes side by side along Y just by varying box_index)."""
    if y_offset is None:
        y_offset = box_index * params.BOX_LENGTH
    if label_prefix is None:
        label_prefix = f"Box{box_index + 1}"

    t = params.MDF_THICKNESS
    box_length = params.BOX_LENGTH
    frame_width = params.FRAME_WIDTH
    box_height = params.BOX_HEIGHT
    interior_height = params.BOX_INTERIOR_HEIGHT

    panels = []

    def add_panel(obj_name, label, length, width, thickness, rotation,
                  target_min, material="MDF", color=None,
                  visible=True, stock_source="new"):
        # core.panel.create_assembly_panel supplies the stock_source ->
        # color default rule (CONTEXT.md); this box's own colors
        # (RECLAIMED_MDF_COLOR/BODY_COLOR, from this furniture's params.py)
        # are passed in — this closure only adds the label_prefix and
        # appends to this box's own panels list.
        obj = create_assembly_panel(
            doc, f"{label_prefix}_{obj_name}", f"{label_prefix} - {label}",
            length, width, thickness, rotation, target_min,
            material=material, color=color, visible=visible,
            stock_source=stock_source,
            reclaimed_color=params.RECLAIMED_MDF_COLOR,
            new_color=params.BODY_COLOR,
        )
        panels.append(obj)
        return obj

    # --- Box shell ----------------------------------------------------
    # Bottom: X-footprint BOX_WIDTH, inset by t from FRAME_WIDTH (see module
    # docstring). Top's footprint (BOX_TOP_PANEL_WIDTH/BOX_TOP_X_MIN)
    # instead varies by DRAWER_OVERLAY_STYLE — see params.py.
    add_panel(
        "Bottom", "Bottom Panel", params.BOX_WIDTH, box_length, t,
        _IDENTITY, App.Vector(params.BOX_SHELL_X_MIN, y_offset, 0),
        visible=False, stock_source="reclaimed",
    )
    add_panel(
        "Top", "Top Panel", params.BOX_TOP_PANEL_WIDTH, box_length, t,
        _IDENTITY, App.Vector(params.BOX_TOP_X_MIN, y_offset, box_height - t),
        visible=True, stock_source="new",
    )

    # 2 long side walls: thin along Y, trapped between top/bottom (Z), at
    # the box's two Y extremes. Same X inset as Bottom; height =
    # interior_height, not box_height (see module docstring).
    add_panel(
        "SideWallNear", "Side Wall (Y near)", params.BOX_WIDTH, interior_height, t,
        _ROT_X90, App.Vector(params.BOX_SHELL_X_MIN, y_offset, t),
        visible=False, stock_source="reclaimed",
    )
    add_panel(
        "SideWallFar", "Side Wall (Y far)", params.BOX_WIDTH, interior_height, t,
        _ROT_X90, App.Vector(params.BOX_SHELL_X_MIN, y_offset + box_length - t, t),
        visible=False, stock_source="reclaimed",
    )

    # --- Drawer_box carcasses ------------------------------------------
    # Drawer depth = RAIL_LENGTH; width inset from the box's internal
    # Y-span by RAIL_CLEARANCE per side. Structural front stays flush/inset
    # with the shell's own open face — the Face panel, added below, is what
    # actually overlays.
    drawer_depth = params.RAIL_LENGTH
    drawer_width = (box_length - 2 * t) - 2 * params.RAIL_CLEARANCE
    # DRAWER_HEIGHT_REDUCTION (params.py, DRAWER_OVERLAY_STYLE-dependent)
    # makes room for the unmodeled rail-mount frame in "rail_above_drawer".
    drawer_side_height = (
        interior_height - params.DRAWER_BOTTOM_THICKNESS
        - params.DRAWER_TOP_REVEAL_GAP
        - params.DRAWER_HEIGHT_REDUCTION
    )
    drawer_y_min = y_offset + t + params.RAIL_CLEARANCE
    drawer_bottom_z = t  # sits directly on the box's own bottom panel
    drawer_carcass_z = drawer_bottom_z + params.DRAWER_BOTTOM_THICKNESS

    def add_drawer(name_prefix, drawer_label, x_min, x_sign):
        """x_sign: +1 if the drawer opens from the shell's near X face
        (carcass grows in +X from x_min), -1 if it opens from the shell's
        far X face (carcass grows in -X, so x_min is actually the
        carcass's max)."""
        if x_sign > 0:
            carcass_x_min = x_min
        else:
            carcass_x_min = x_min - drawer_depth

        add_panel(
            f"{name_prefix}_Bottom", f"{drawer_label} - Bottom",
            drawer_depth, drawer_width, params.DRAWER_BOTTOM_THICKNESS,
            _IDENTITY, App.Vector(carcass_x_min, drawer_y_min, drawer_bottom_z),
            material="Fiber", visible=False, stock_source="reclaimed",
        )
        add_panel(
            f"{name_prefix}_SideNear", f"{drawer_label} - Side (Y near)",
            drawer_depth, drawer_side_height, t,
            _ROT_X90, App.Vector(carcass_x_min, drawer_y_min, drawer_carcass_z),
            visible=False, stock_source="reclaimed",
        )
        add_panel(
            f"{name_prefix}_SideFar", f"{drawer_label} - Side (Y far)",
            drawer_depth, drawer_side_height, t,
            _ROT_X90,
            App.Vector(carcass_x_min, drawer_y_min + drawer_width - t, drawer_carcass_z),
            visible=False, stock_source="reclaimed",
        )
        # Structural front: flush/inset with the box's open X face, part of
        # the carcass (same as Back, mirrored), hidden once the Face is
        # attached. Not where the overlay happens.
        front_x = x_min if x_sign > 0 else x_min - t
        back_x = carcass_x_min + drawer_depth - t if x_sign > 0 else carcass_x_min
        add_panel(
            f"{name_prefix}_Front", f"{drawer_label} - Structural Front",
            drawer_side_height, drawer_width - 2 * t, t,
            _ROT_Y90, App.Vector(front_x, drawer_y_min + t, drawer_carcass_z),
            visible=False, stock_source="reclaimed",
        )
        add_panel(
            f"{name_prefix}_Back", f"{drawer_label} - Back",
            drawer_side_height, drawer_width - 2 * t, t,
            _ROT_Y90, App.Vector(back_x, drawer_y_min + t, drawer_carcass_z),
            visible=False, stock_source="reclaimed",
        )
        # Face (نما): attached to the structural front's outer face,
        # protruding by DRAWER_FRONT_OVERLAY_AMOUNT — the visible,
        # overlaying panel. Bottom edge extends SKIRT_HEIGHT below the
        # box's own bottom (doubles as the drawer-side skirt). Narrower
        # than the box's Y-footprint by DRAWER_FACE_GAP (reveal against
        # the neighboring box's Face). Top edge sits DRAWER_TOP_REVEAL_GAP
        # below DRAWER_FACE_TOP_REF_Z (params.py, DRAWER_OVERLAY_STYLE-
        # dependent) — taller than the carcass by design, not just capped
        # at the carcass's own top.
        overlay = params.DRAWER_FRONT_OVERLAY_AMOUNT
        face_x = x_min - overlay if x_sign > 0 else x_min
        face_top_z = params.DRAWER_FACE_TOP_REF_Z - params.DRAWER_TOP_REVEAL_GAP
        face_height = face_top_z + params.SKIRT_HEIGHT
        face_width = box_length - params.DRAWER_FACE_GAP
        face_y_min = y_offset + params.DRAWER_FACE_GAP / 2
        add_panel(
            f"{name_prefix}_Face", f"{drawer_label} - Face",
            face_height, face_width, overlay,
            _ROT_Y90, App.Vector(face_x, face_y_min, -params.SKIRT_HEIGHT),
            color=params.DRAWER_FRONT_COLOR, visible=True, stock_source="new",
        )

    # Drawer carcasses align with the (inset) shell edges, not raw
    # 0/frame_width — only the Face panels poke out to FRAME_WIDTH.
    shell_x_min = params.BOX_SHELL_X_MIN
    shell_x_max = frame_width - t
    # Drawer 1 opens from the near X face, Drawer 2 from the far X face;
    # both grow toward the middle.
    add_drawer("Drawer1", "Drawer 1", x_min=shell_x_min, x_sign=+1)
    add_drawer("Drawer2", "Drawer 2", x_min=shell_x_max, x_sign=-1)

    # --- Internal transverse walls (one behind each drawer) -------------
    # Purely structural (keeps the top panel from sagging over the
    # unsupported span), RAIL_BACK_CLEARANCE behind each drawer's back.
    # The gap between the 2 walls is left open.
    wall1_x_min = shell_x_min + drawer_depth + params.RAIL_BACK_CLEARANCE
    add_panel(
        "InternalWallDrawer1", "Internal Wall (behind Drawer 1)",
        interior_height, box_length - 2 * t, t,
        _ROT_Y90, App.Vector(wall1_x_min, y_offset + t, t),
        visible=False, stock_source="reclaimed",
    )
    wall2_x_max = (shell_x_max - drawer_depth) - params.RAIL_BACK_CLEARANCE
    add_panel(
        "InternalWallDrawer2", "Internal Wall (behind Drawer 2)",
        interior_height, box_length - 2 * t, t,
        _ROT_Y90, App.Vector(wall2_x_max - t, y_offset + t, t),
        visible=False, stock_source="reclaimed",
    )

    return panels
