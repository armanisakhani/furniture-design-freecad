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
from core.panel import create_assembly_panel, IDENTITY, ROT_X90

# Head end at Y=0: frame flush with the mattress (no gap), against the
# room's wall — gets a headboard (create_headboard), not a mattress-stop.
# Foot end (Y=FRAME_LENGTH): frame extends MATTRESS_TO_FRAME_GAP_LENGTH past
# the mattress, gets the mattress-stop cap + end Face.


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
    """Flat MDF cap on top of the top panels' surface, filling the foot-end
    gap between the mattress and frame edges, and capping over EndFaceFoot's
    top edge. Width (Y) = MATTRESS_TO_FRAME_GAP_LENGTH, not inflated —
    EndFaceFoot's Y-extent sits entirely inside this span (see params.py),
    so no inflation is needed to still cap over it. Length (X) = FRAME_WIDTH
    always (not BOX_TOP_PANEL_WIDTH, which could overshoot). Trimmed at
    both X ends by create_mattress_stop_side's own shortened Y-span so the
    two butt at plain 90-degree joints (side-shape.jpg), no miter."""
    return create_assembly_panel(
        doc, "MattressStopFoot", "Mattress Stop (Foot)",
        length=params.FRAME_WIDTH,
        width=params.MATTRESS_TO_FRAME_GAP_LENGTH,
        thickness=params.MDF_THICKNESS,
        rotation=IDENTITY,
        target_min=App.Vector(
            0,
            params.FRAME_LENGTH - params.MATTRESS_TO_FRAME_GAP_LENGTH,
            params.BOX_HEIGHT,
        ),
        color=params.BODY_COLOR, visible=True, stock_source="new",
    )


def create_mattress_stop_side(doc, x_min, label_suffix):
    """Same idea as create_mattress_stop_foot, rotated 90 degrees: fills the
    WIDTH-direction gap (MATTRESS_TO_FRAME_GAP_WIDTH) on one long side. Only
    built when that gap is nonzero (see create_bed). Runs FRAME_LENGTH -
    MATTRESS_TO_FRAME_GAP_LENGTH in Y, not the full FRAME_LENGTH, so it
    stops exactly where create_mattress_stop_foot begins — a plain
    90-degree butt joint (side-shape.jpg), no overlap, no miter."""
    return create_assembly_panel(
        doc, f"MattressStopSide{label_suffix}", f"Mattress Stop (Side {label_suffix})",
        length=params.MATTRESS_TO_FRAME_GAP_WIDTH,
        width=params.FRAME_LENGTH - params.MATTRESS_TO_FRAME_GAP_LENGTH,
        thickness=params.MDF_THICKNESS,
        rotation=IDENTITY,
        target_min=App.Vector(x_min, 0, params.BOX_HEIGHT),
        color=params.BODY_COLOR, visible=True, stock_source="new",
    )


def create_end_face(doc):
    """Foot-end Face: attached to the outer face of the last box's
    SideWallFar (the bed's visible foot end), extending outward by its own
    thickness — same overlay pattern as the Drawer_box Face. Absorbs what a
    separate EndSkirt panel used to do (now redundant):
      * X: FRAME_WIDTH always (not BOX_TOP_PANEL_WIDTH, which could
        overshoot).
      * Z: from -SKIRT_HEIGHT (matches each Drawer_box Face) up to the top
        of the MattressStop cap (box_height + t).
      * Y: starts at FRAME_LENGTH - MDF_THICKNESS — the last box's own far
        wall stops 1 MDF_THICKNESS short of FRAME_LENGTH so this panel
        sits flush in that gap and ends exactly at FRAME_LENGTH.
    """
    t = params.MDF_THICKNESS
    z_min = -params.SKIRT_HEIGHT
    z_max = params.BOX_HEIGHT + t
    return create_assembly_panel(
        doc, "EndFaceFoot", "End Face (Foot)",
        length=params.FRAME_WIDTH,
        width=z_max - z_min,
        thickness=t,
        rotation=ROT_X90,
        target_min=App.Vector(0, params.FRAME_LENGTH - t, z_min),
        color=params.BODY_COLOR, visible=True, stock_source="new",
    )


def create_headboard(doc):
    """Head-end 'crown' (تاج): attached to the outer face of the first
    box's SideWallNear, extending into negative Y — mirrors EndFaceFoot's
    attachment pattern. Unlike EndFaceFoot, HEADBOARD_HEIGHT (1.4m) is
    measured from the actual floor (Z=-LEG_FRAME_HEIGHT), not from the
    box's own bottom."""
    t = params.MDF_THICKNESS
    z_min = -params.LEG_FRAME_HEIGHT
    return create_assembly_panel(
        doc, "Headboard", "Headboard (Crown)",
        length=params.FRAME_WIDTH,
        width=params.HEADBOARD_HEIGHT,
        thickness=t,
        rotation=ROT_X90,
        target_min=App.Vector(0, -t, z_min),
        color=params.BODY_COLOR, visible=True, stock_source="new",
    )


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
