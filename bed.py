"""
Early, partial slice of Phase 6 (full bed assembly) — BOX_COUNT boxes
placed side by side along Y, a mattress-stop cap, one end Face (foot end),
a headboard (head end), plus a placeholder mattress on top so the overall
shape is easy to check visually. No separate end skirt panel (the end
Face's own bottom reach replaces it, see create_end_face) and no
drawer-side skirt (each Drawer_box's own Face already reaches down to it,
see CONTEXT.md) and no leg frame *panels* yet (LEG_FRAME_HEIGHT is used
already, by the headboard, but no actual leg/support-frame geometry is
built yet) — see roadmap.md.
"""

import FreeCAD as App

import params
from box import create_box
from panel import create_panel, place_panel, IDENTITY, ROT_X90

# Head end at Y=0 (frame sits flush with the mattress there — no
# MATTRESS_TO_FRAME_GAP_LENGTH-style gap, and it's the end that goes
# against a wall, confirmed with the user — but it DOES get a headboard,
# see create_headboard, since a headboard sits against that wall, not in
# open space). Foot end (Y=FRAME_LENGTH) is where the frame extends
# MATTRESS_TO_FRAME_GAP_LENGTH past the mattress, and gets the mattress-stop
# cap and the end Face. An arbitrary but documented choice, like other
# placeholder assumptions in this project — not confirmed against a
# specific reference photo.
# (سمت سر تخت روی Y=۰ (فریم اونجا با تشک هم‌تراز — بدون فاصله‌ی شبیه
# MATTRESS_TO_FRAME_GAP_LENGTH، و همون سمتیه که به دیوار می‌چسبه، تأییدشده —
# اما تاج می‌گیره، نگاه کن create_headboard، چون تاج به همون دیوار می‌چسبه، نه
# فضای باز). سمت پایین تخت (Y=FRAME_LENGTH) جاییه که فریم به اندازه‌ی
# MATTRESS_TO_FRAME_GAP_LENGTH از تشک جلوتر می‌ره، و کلاهک جلوگیری از تشک و
# نمای انتهایی اونجان. یه فرض مستند ولی دلبخواهی، مثل بقیه‌ی فرض‌های جاگذار
# این پروژه — با یه عکس مرجع خاص چک نشده.)


def create_mattress_placeholder(doc, y_offset=0.0):
    """A plain, undyed Part::Box — not a Panel, not part of the cut list
    (plan.md/CONTEXT.md: the mattress isn't something we fabricate), purely
    a visual reference for checking the overall assembly."""
    box = doc.addObject("Part::Box", "MattressPlaceholder")
    box.Label = "Mattress (placeholder)"
    box.Length = params.MATTRESS_WIDTH   # X
    box.Width = params.MATTRESS_LENGTH   # Y
    box.Height = params.MATTRESS_THICKNESS  # Z
    box.Placement = App.Placement(
        App.Vector(
            params.MATTRESS_TO_FRAME_GAP_WIDTH,
            y_offset,
            params.BOX_HEIGHT,
        ),
        App.Rotation(),
    )
    return box


def create_mattress_stop_foot(doc):
    """Flat MDF cap lying on top of the top panels' surface (not a raised
    wall — corrected this session), filling the foot-end gap between the
    mattress edge and the frame edge, AND capping over EndFaceFoot's own
    top edge (confirmed with the user against side-shape.jpg). Its width
    (Y) is exactly MATTRESS_TO_FRAME_GAP_LENGTH — same as the plain gap,
    matching MattressStopSide's own width — NOT inflated by an extra
    MDF_THICKNESS (an earlier version of this session did that, to reach
    over EndFaceFoot's thickness; corrected once BOX_LENGTH itself was
    fixed to leave EndFaceFoot fully nested inside this same span, see
    params.py — EndFaceFoot's whole Y-extent, [FRAME_LENGTH-MDF_THICKNESS,
    FRAME_LENGTH], sits entirely inside this cap's own Y-extent,
    [FRAME_LENGTH-MATTRESS_TO_FRAME_GAP_LENGTH, FRAME_LENGTH], so no
    inflation is needed to still cap over it). Length (X) is exactly
    FRAME_WIDTH — this layer (mattress + 2 side frames) always spans
    FRAME_WIDTH regardless of the box's own DRAWER_OVERLAY_STYLE
    (corrected this session: the earlier BOX_TOP_PANEL_WIDTH-based version
    could overshoot FRAME_WIDTH). Trimmed at both X ends by
    create_mattress_stop_side's own shortened Y-span (see there) so the
    two don't overlap at the corners — confirmed against side-shape.jpg:
    pieces butt at plain 90-degree joints, no miter."""
    obj = create_panel(
        doc, "MattressStopFoot", "Mattress Stop (Foot)",
        length=params.FRAME_WIDTH,
        width=params.MATTRESS_TO_FRAME_GAP_LENGTH,
        thickness=params.MDF_THICKNESS,
        color=params.BODY_COLOR, visible=True, stock_source="new",
    )
    place_panel(
        doc, obj, IDENTITY,
        App.Vector(
            0,
            params.FRAME_LENGTH - params.MATTRESS_TO_FRAME_GAP_LENGTH,
            params.BOX_HEIGHT,
        ),
    )
    return obj


def create_mattress_stop_side(doc, x_min, label_suffix):
    """Same idea as create_mattress_stop_foot, rotated 90 degrees: a flat
    MDF cap on top of the top panels' surface, filling the WIDTH-direction
    gap (MATTRESS_TO_FRAME_GAP_WIDTH) between the mattress edge and the
    frame edge, on one of the 2 long (drawer-carrying) sides. Only built
    at all when that gap is nonzero (see create_bed) — with the gap at 0,
    same as before this session, there's nothing to fill. Runs
    FRAME_LENGTH - MATTRESS_TO_FRAME_GAP_LENGTH in Y (NOT the full
    FRAME_LENGTH — corrected: it used to overlap a full MATTRESS_TO_FRAME_
    GAP_LENGTH x MATTRESS_TO_FRAME_GAP_WIDTH square with
    create_mattress_stop_foot at each foot-end corner; the user caught this
    against side-shape.jpg, which shows the pieces butting at a plain
    90-degree joint with no overlap and no miter — so this piece stops
    exactly where the foot piece begins, instead of running underneath
    it)."""
    obj = create_panel(
        doc, f"MattressStopSide{label_suffix}", f"Mattress Stop (Side {label_suffix})",
        length=params.MATTRESS_TO_FRAME_GAP_WIDTH,
        width=params.FRAME_LENGTH - params.MATTRESS_TO_FRAME_GAP_LENGTH,
        thickness=params.MDF_THICKNESS,
        color=params.BODY_COLOR, visible=True, stock_source="new",
    )
    place_panel(doc, obj, IDENTITY, App.Vector(x_min, 0, params.BOX_HEIGHT))
    return obj


def create_end_face(doc):
    """Foot-end Face: one MDF panel attached to the outer face of the last
    box's SideWallFar (the wall that's actually the bed's visible foot
    end, not an internal seam between boxes) and extending further outward
    by its own thickness — same overlay pattern as the Drawer_box Face,
    applied here to the bed's own end wall. Corrected this session to be
    much bigger, absorbing what a separate EndSkirt panel used to do
    (removed — redundant once this panel covers the same span):
      * X: FRAME_WIDTH — this layer (mattress + 2 side frames) always
        spans FRAME_WIDTH, same as MattressStopFoot (corrected this
        session: the earlier BOX_TOP_PANEL_WIDTH-based version could
        overshoot FRAME_WIDTH).
      * Z top: up to the top of the MattressStop cap (box_height + t), not
        just the box's own interior height.
      * Z bottom: down to -SKIRT_HEIGHT, matching where each Drawer_box's
        Face reaches below the box's own bottom — this is what makes the
        separate EndSkirt panel unnecessary now.
      * Y: starts at FRAME_LENGTH - MDF_THICKNESS, NOT FRAME_LENGTH itself
        (corrected this session, together with BOX_LENGTH in params.py):
        the last box's own far wall now stops 1 MDF_THICKNESS short of
        FRAME_LENGTH specifically so this panel can sit flush in that gap
        and end exactly at FRAME_LENGTH, instead of poking out past it —
        before this fix, it stuck out to FRAME_LENGTH + MDF_THICKNESS,
        which is why MattressStopFoot had to be inflated to still reach
        over it.
    """
    t = params.MDF_THICKNESS
    z_min = -params.SKIRT_HEIGHT
    z_max = params.BOX_HEIGHT + t
    obj = create_panel(
        doc, "EndFaceFoot", "End Face (Foot)",
        length=params.FRAME_WIDTH,
        width=z_max - z_min,
        thickness=t,
        color=params.BODY_COLOR, visible=True, stock_source="new",
    )
    place_panel(
        doc, obj, ROT_X90,
        App.Vector(0, params.FRAME_LENGTH - t, z_min),
    )
    return obj


def create_headboard(doc):
    """Head-end 'crown' (تاج): a single MDF panel standing vertically at
    the head end (Y=0, the end that butts against the room's wall),
    attached to the outer face of the first box's SideWallNear and
    extending further outward (into negative Y) by its own thickness —
    same attachment pattern as EndFaceFoot, mirrored to the other end of
    the bed. Unlike EndFaceFoot, its own height (HEADBOARD_HEIGHT) is
    measured from the actual floor (Z=-LEG_FRAME_HEIGHT, where the leg/
    support frame ends), not from the box's own bottom — confirmed with
    the user: 1.4m total, floor to top edge. Same width as the frame layer
    (FRAME_WIDTH, X, same as MattressStopFoot/EndFaceFoot), same color as
    the box body (BODY_COLOR, confirmed with the user)."""
    t = params.MDF_THICKNESS
    z_min = -params.LEG_FRAME_HEIGHT
    obj = create_panel(
        doc, "Headboard", "Headboard (Crown)",
        length=params.FRAME_WIDTH,
        width=params.HEADBOARD_HEIGHT,
        thickness=t,
        color=params.BODY_COLOR, visible=True, stock_source="new",
    )
    place_panel(doc, obj, ROT_X90, App.Vector(0, -t, z_min))
    return obj


def create_bed(doc):
    """Create all BOX_COUNT boxes side by side along Y (each via
    create_box()'s own default y_offset = box_index * BOX_LENGTH, so they
    already line up with no extra placement logic here), the foot-end
    mattress-stop cap + Face, the head-end headboard, the 2 side
    mattress-stop caps (only if MATTRESS_TO_FRAME_GAP_WIDTH is nonzero),
    and the mattress placeholder on top. Returns
    (list_of_all_box_panels_plus_bed_level_panels, mattress_obj)."""
    all_panels = []
    for box_index in range(params.BOX_COUNT):
        all_panels.extend(create_box(doc, box_index))

    all_panels.append(create_mattress_stop_foot(doc))
    all_panels.append(create_end_face(doc))
    all_panels.append(create_headboard(doc))
    if params.MATTRESS_TO_FRAME_GAP_WIDTH > 0:
        all_panels.append(create_mattress_stop_side(doc, 0, "Near"))
        all_panels.append(
            create_mattress_stop_side(
                doc,
                params.FRAME_WIDTH - params.MATTRESS_TO_FRAME_GAP_WIDTH,
                "Far",
            )
        )

    mattress = create_mattress_placeholder(doc)

    return all_panels, mattress
