"""
Phase 3 — single Box assembly: one Box shell (top, bottom, 2 long side
walls, 2 internal transverse walls) plus its 2 Drawer_box carcasses (2
sides + structural front + back + bottom + Face each), built from Panel
objects (panel.py) and positioned with FreeCAD Placement so they butt
together using MDF_THICKNESS — never naive touching boxes. See CONTEXT.md
for Box vs Drawer_box.

Global axes (see HANDOFF.md / plan.md): X = WIDTH (side-to-side), Y = LENGTH
(head-to-toe), Z = height.

Construction convention chosen here (one valid method among several — flag
it, per plan.md, rather than silently pick it and move on):
  * Box shell: bottom panel, the 2 long side walls, and (in "rail_above_
    drawer" style) the top panel share the same X-footprint, BOX_WIDTH
    (= FRAME_WIDTH - 2*MDF_THICKNESS, params.py) — inset by MDF_THICKNESS
    from FRAME_WIDTH on each side, starting at BOX_SHELL_X_MIN, NOT flush
    at X=0..FRAME_WIDTH (corrected this session: sitting flush there meant
    the Face panels' own overlay pushed the assembled box+Face past
    FRAME_WIDTH by 2*MDF_THICKNESS — insetting the shell is what makes the
    Face's overlay land exactly back on FRAME_WIDTH). Bottom/Top cap over
    the 2 long side walls (Z), which are trapped between them at the box's
    two Y extremes — their own height is BOX_INTERIOR_HEIGHT (250, not
    BOX_HEIGHT), confirmed against the reference spreadsheet's "کناره"
    (side) row. This also settles an apparent conflict from earlier in this
    session: an intermediate version made the side walls full-height
    instead (matching "کناره" by inflating them to BOX_HEIGHT), but the
    same spreadsheet's "دیواره عرضی داخلی" (internal transverse wall) row
    reports the *same* 25cm figure, and that wall is necessarily trapped
    between top/bottom (it's a structural brace, physically can't extend
    past them) — so the two rows only agree once BOX_HEIGHT itself is
    understood as derived (BOX_INTERIOR_HEIGHT + 2*t in params.py), with
    side walls trapped like everything else at the shared 250mm figure. The
    side walls also double as the rail-mounting walls, since both drawers
    slide along X. The shell's own X extremes are deliberately left open —
    that's where the 2 drawers slide out, one per face, matching "each long
    side of the bed shows BOX_COUNT drawer fronts" in roadmap.md. The Top
    panel's own footprint additionally depends on DRAWER_OVERLAY_STYLE (see
    params.py): full FRAME_WIDTH, flush with the Face's outer edge, in the
    default "box_over_drawer" (the Top panel itself reaches out to cap the
    drawer from above); same inset BOX_WIDTH as the rest of the shell in
    "rail_above_drawer" (an unmodeled rail-mount frame reaches out instead,
    and the drawer carcass loses one MDF_THICKNESS of height to make room
    for it).
  * Drawer depth is RAIL_LENGTH (not derived from FRAME_WIDTH) — confirmed
    against real drawer-slide sizing convention (drawer box depth should
    equal, or be very close to, the slide's own nominal length; see
    roadmap.md Phase 3 entry for sources). Since RAIL_LENGTH (650) is much
    less than half of FRAME_WIDTH (1800), the 2 drawers do NOT meet in the
    middle — there's a real gap of open, unused box interior between them.
    This corrects an earlier version of this file that derived drawer depth
    as half of FRAME_WIDTH; that was wrong (per the user, checked against
    bed-1-box.jpg and the reference cut-list spreadsheet).
  * Instead of one shared center divider, each drawer gets its own
    "internal transverse wall" (دیواره عرضی داخلی, per the reference
    spreadsheet) positioned RAIL_BACK_CLEARANCE behind that drawer's back —
    purely structural, to keep the top panel from sagging over the
    unsupported middle span. Trapped between the 2 long side walls (Y) and
    top/bottom (Z), same as the old single divider was. The open space
    between the 2 internal walls is intentionally unused (matches the
    reference photo, which shows hardware sitting loose in that gap — not
    modeled here, out of scope for Phase 3).
  * Drawer_box carcass: same trapping logic, one axis down. The bottom
    panel (fiber board) is the drawer's full external footprint; the 2 side
    panels (thin in Y, mount to the box's long side walls) run the full
    drawer depth and are trapped in Z between the bottom panel and the top
    clearance; back (thin in X) is trapped between the 2 sides (in Y).
    Width uses RAIL_CLEARANCE (confirmed by research to be the right kind
    of value for this, ~13mm/side) instead of an ad-hoc placeholder gap.
  * Drawer_box "front" is 2 separate panels (corrected this session — an
    earlier version combined them into one, which was wrong):
    - Structural front: flush/inset with the box's open X face, same size
      and role as Back (mirrored), part of the carcass, hidden once
      assembled.
    - Face (نما): a separate panel attached to the structural front's
      outer face, extending further outward by its own thickness
      (DRAWER_FRONT_OVERLAY_AMOUNT — that thickness IS the overlay amount,
      since it's mounted flush against the structural front and protrudes
      by its whole depth). This is what's actually visible. It's taller
      than the drawer's own carcass, on both ends — top edge is
      DRAWER_TOP_REVEAL_GAP below whatever actually sits above it, which
      depends on DRAWER_OVERLAY_STYLE (see params.py): the Top panel's own
      overhang in "box_over_drawer", or the box's very top line in
      "rail_above_drawer" (one full MDF_THICKNESS higher — there's no box
      MDF reaching out over the Face in that style, only the unmodeled
      rail frame, confirmed by the user: "کشو قراره بیاد لب به لبش قرار
      بگیره"). Bottom edge extends SKIRT_HEIGHT below the box's own bottom
      (Z=0) — doubling as the
      drawer-side skirt, so HAS_DRAWER_SIDE_SKIRT needs no separate panel
      on this face (unlike HAS_END_SKIRT, which still needs a real one,
      Phase 6). Narrower than the box's own Y-footprint by
      DRAWER_FACE_GAP, leaving a reveal against the neighboring box's Face.
    In "box_over_drawer" style, the Top panel's own footprint is sized to
    exactly match the Face's protrusion (both reach FRAME_WIDTH), so the
    top panel's outer X edge lines up flush with the Face's outer X face —
    confirmed by construction (both computed independently from the same
    params, not hand-tuned).

visible/stock_source defaults below are reasonable per-role guesses for one
isolated box (CONTEXT.md: a judgment call, not a fixed rule) — e.g. a box's
long side walls are only actually visible if that box sits at the head/foot
end of the assembled bed. Phase 6 (full 3-box assembly) should revisit
these per box position rather than trust the defaults blindly.
"""

import FreeCAD as App

import params
from panel import create_panel, place_panel, IDENTITY, ROT_X90, ROT_Y90

# Local aliases so the rest of this module's many call sites don't need
# renaming — place_panel/IDENTITY/ROT_X90/ROT_Y90 now live in panel.py
# since bed.py needs them too.
_place = place_panel
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
        # Color follows StockSource first (see params.py Material section):
        # reclaimed panels are always RECLAIMED_MDF_COLOR regardless of
        # role; only a caller passing an explicit color (the Face panel,
        # DRAWER_FRONT_COLOR) overrides that for a new-stock, non-body role.
        if color is None:
            color = (
                params.RECLAIMED_MDF_COLOR
                if stock_source == "reclaimed"
                else params.BODY_COLOR
            )
        obj = create_panel(
            doc, f"{label_prefix}_{obj_name}", f"{label_prefix} - {label}",
            length, width, thickness, material=material, color=color,
            visible=visible, stock_source=stock_source,
        )
        _place(doc, obj, rotation, target_min)
        panels.append(obj)
        return obj

    # --- Box shell ----------------------------------------------------
    # Bottom / top: X-footprint is BOX_WIDTH (= FRAME_WIDTH - 2*t), inset by
    # t from FRAME_WIDTH on each side — NOT full frame_width (corrected this
    # session: the shell used to sit flush at frame_width, which meant the
    # Face's own overlay pushed the assembled box+Face past FRAME_WIDTH by
    # 2*t; insetting the shell is what makes the Face's overlay land exactly
    # back on FRAME_WIDTH — see params.py "DRAWER_OVERLAY_STYLE"). Bottom
    # caps over the 2 long side walls; so does Top, except Top's own
    # footprint (BOX_TOP_PANEL_WIDTH/BOX_TOP_X_MIN) depends on
    # DRAWER_OVERLAY_STYLE: full FRAME_WIDTH in "box_over_drawer" (it's the
    # one reaching out to meet the Face from above), same BOX_WIDTH inset as
    # everything else in "rail_above_drawer" (an unmodeled rail frame reaches
    # out instead).
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
    # the box's two Y extremes. X-footprint = BOX_WIDTH, same inset as
    # Bottom (not frame_width). Z-height=interior_height (=BOX_INTERIOR_
    # HEIGHT, confirmed against "کناره" in the reference spreadsheet — NOT
    # box_height, see module docstring).
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
    # Drawer depth = RAIL_LENGTH (confirmed convention: drawer box depth
    # should match the slide's own nominal length). Width is inset from the
    # box's internal Y-span by RAIL_CLEARANCE per side. The structural front
    # itself stays flush/inset with the box's own (now shell-inset) open
    # face — it's the separate Face panel, added below, that actually
    # overlays.
    drawer_depth = params.RAIL_LENGTH
    drawer_width = (box_length - 2 * t) - 2 * params.RAIL_CLEARANCE
    # In "rail_above_drawer" style, an unmodeled rail-mount frame sits on
    # top of the drawer (between it and the Top panel), so the drawer
    # carcass loses one extra MDF_THICKNESS of height versus "box_over_
    # drawer", where the Top panel itself reaches out and no such frame is
    # needed — see params.py "DRAWER_OVERLAY_STYLE".
    drawer_side_height = (
        interior_height - params.DRAWER_BOTTOM_THICKNESS
        - params.DRAWER_TOP_REVEAL_GAP
        - (t if params.DRAWER_OVERLAY_STYLE == "rail_above_drawer" else 0)
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
        # the carcass (same as Back, mirrored) — hidden once the Face panel
        # below is attached to it. NOT where the overlay happens.
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
        # Face (نما): separate panel attached to the structural front's
        # outer face, extending further outward by its own thickness
        # (DRAWER_FRONT_OVERLAY_AMOUNT) — this is what's actually visible
        # and actually overlays. Taller than the drawer opening (its own
        # carcass): bottom edge extends SKIRT_HEIGHT below the box's own
        # bottom (Z=0) — doubling as the drawer-side skirt, so no separate
        # skirt panel is needed on this face (see roadmap.md). Narrower
        # than the box's own Y-footprint by DRAWER_FACE_GAP, to leave a
        # reveal against the neighboring box's Face.
        #
        # Top edge is DRAWER_TOP_REVEAL_GAP below whatever's actually
        # sitting above the Face, which depends on DRAWER_OVERLAY_STYLE —
        # NOT simply the drawer carcass's own (possibly shorter) top, since
        # the Face is already taller than the carcass by design (confirmed
        # this session, per the user: "کشو قراره بیاد لب به لبش قرار
        # بگیره"). In "box_over_drawer", the Top panel's own MDF reaches
        # out and overhangs right above the Face, so the reveal is measured
        # from that overhang's underside (BOX_HEIGHT - t). In
        # "rail_above_drawer", the Top panel does NOT reach out over the
        # Face at all (see params.py) — there's no box MDF above it out
        # there, only the unmodeled rail frame — so the Face rises a full
        # MDF_THICKNESS higher, with the reveal now measured from the very
        # top line of the box (BOX_HEIGHT) instead.
        overlay = params.DRAWER_FRONT_OVERLAY_AMOUNT
        face_x = x_min - overlay if x_sign > 0 else x_min
        face_top_ref_z = (
            box_height
            if params.DRAWER_OVERLAY_STYLE == "rail_above_drawer"
            else box_height - t
        )
        face_top_z = face_top_ref_z - params.DRAWER_TOP_REVEAL_GAP
        face_height = face_top_z + params.SKIRT_HEIGHT
        face_width = box_length - params.DRAWER_FACE_GAP
        face_y_min = y_offset + params.DRAWER_FACE_GAP / 2
        add_panel(
            f"{name_prefix}_Face", f"{drawer_label} - Face",
            face_height, face_width, overlay,
            _ROT_Y90, App.Vector(face_x, face_y_min, -params.SKIRT_HEIGHT),
            color=params.DRAWER_FRONT_COLOR, visible=True, stock_source="new",
        )

    # Drawer carcasses align with the (now inset) shell edges, BOX_SHELL_
    # X_MIN and frame_width - t — not raw 0/frame_width — since the shell
    # itself no longer sits flush at frame_width (see Box shell above); only
    # the Face panels poke out past these to reach the true FRAME_WIDTH.
    shell_x_min = params.BOX_SHELL_X_MIN
    shell_x_max = frame_width - t
    # Drawer 1: opens from the shell's near X face, carcass grows toward
    # the middle.
    add_drawer("Drawer1", "Drawer 1", x_min=shell_x_min, x_sign=+1)
    # Drawer 2: opens from the shell's far X face, carcass grows toward the
    # middle from that face.
    add_drawer("Drawer2", "Drawer 2", x_min=shell_x_max, x_sign=-1)

    # --- Internal transverse walls (one behind each drawer) -------------
    # Purely structural (keeps the top panel from sagging over the
    # unsupported middle span) — not touching the drawer, not connected to
    # each other. Thin along X, trapped between the 2 long side walls (Y)
    # and top/bottom (Z), positioned RAIL_BACK_CLEARANCE behind each
    # drawer's own back plane. The space between the 2 walls is left open.
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
