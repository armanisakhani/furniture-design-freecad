"""
Shared verification helper for every furniture module's tests/ scripts.
Replaces the "accumulate a bounding box, print it next to an expected
line, let a human diff them" pattern with one real pass/fail check.
"""

import FreeCAD as App


def combined_bbox(shapes):
    """Union bounding box across a list of shape-bearing FreeCAD objects."""
    bbox = App.BoundBox(shapes[0].Shape.BoundBox)
    for obj in shapes[1:]:
        bbox.add(obj.Shape.BoundBox)
    return bbox


def verify_footprint(label, shapes, expected, tolerance=1e-3):
    """Compare the combined bounding box of `shapes` against `expected` (a
    dict with any of xmin/xmax/ymin/ymax/zmin/zmax; omitted keys are not
    checked). Prints one line per checked bound and raises AssertionError on
    the first mismatch beyond `tolerance`."""
    bbox = combined_bbox(shapes)
    actual = dict(
        xmin=bbox.XMin, xmax=bbox.XMax,
        ymin=bbox.YMin, ymax=bbox.YMax,
        zmin=bbox.ZMin, zmax=bbox.ZMax,
    )
    print(
        f"[{label}] bounding box: "
        f"X[{actual['xmin']:.1f},{actual['xmax']:.1f}] "
        f"Y[{actual['ymin']:.1f},{actual['ymax']:.1f}] "
        f"Z[{actual['zmin']:.1f},{actual['zmax']:.1f}]"
    )
    for key, expected_value in expected.items():
        actual_value = actual[key]
        ok = abs(actual_value - expected_value) < tolerance
        print(
            f"  [{'PASS' if ok else 'FAIL'}] {key}: "
            f"expected {expected_value:.1f}, got {actual_value:.1f}"
        )
        if not ok:
            raise AssertionError(
                f"[{label}] {key} mismatch: expected {expected_value:.1f}, "
                f"got {actual_value:.1f}"
            )
    return bbox
