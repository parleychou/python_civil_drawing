"""Test 08.02: Line-level Intersections (2D/3D Line-Line, Segment Distance, Polyline Self-Intersection)."""

import pytest
from point3d import Point3D
from line3d import Line3D
from intersection import (
    IntersectionType,
    intersect_segments_2d,
    intersect_lines_3d,
    segment_distance_3d,
    check_polyline_self_intersection,
)


def test_2d_segment_strict_cross():
    # 严格十字交叉 (5, 5, 0)
    l1 = Line3D(Point3D(0, 5, 0), Point3D(10, 5, 0))
    l2 = Line3D(Point3D(5, 0, 0), Point3D(5, 10, 0))
    res = intersect_segments_2d(l1, l2)
    assert res.has_intersection is True
    assert res.type == IntersectionType.POINT
    assert pytest.approx(res.point.x) == 5.0
    assert pytest.approx(res.point.y) == 5.0
    assert pytest.approx(res.parameters["t1"]) == 0.5
    assert pytest.approx(res.parameters["t2"]) == 0.5


def test_2d_segment_collinear_overlap():
    # 共线部分重叠: l1 [0, 10], l2 [6, 15] -> 重叠 [6, 10]
    l1 = Line3D(Point3D(0, 0, 0), Point3D(10, 0, 0))
    l2 = Line3D(Point3D(6, 0, 0), Point3D(15, 0, 0))
    res = intersect_segments_2d(l1, l2)
    assert res.has_intersection is True
    assert res.type == IntersectionType.SEGMENT
    assert res.line is not None
    assert pytest.approx(res.line.start.x) == 6.0
    assert pytest.approx(res.line.end.x) == 10.0


def test_2d_segment_parallel_disjoint():
    l1 = Line3D(Point3D(0, 0, 0), Point3D(10, 0, 0))
    l2 = Line3D(Point3D(0, 5, 0), Point3D(10, 5, 0))
    res = intersect_segments_2d(l1, l2)
    assert res.has_intersection is False
    assert res.type == IntersectionType.NONE


def test_3d_skew_lines_and_distance():
    # 3D 异面错开线段: 轴线公垂线在 X=5, Y=0, Z 差为 4.0
    l1 = Line3D(Point3D(0, 0, 0), Point3D(10, 0, 0))
    l2 = Line3D(Point3D(5, -5, 4), Point3D(5, 5, 4))
    res = intersect_lines_3d(l1, l2)
    assert res.has_intersection is False
    assert res.clearance == pytest.approx(4.0, abs=1e-5)
    assert pytest.approx(res.parameters["closest_pt1"].x) == 5.0
    assert pytest.approx(res.parameters["closest_pt1"].y) == 0.0
    assert pytest.approx(res.parameters["closest_pt1"].z) == 0.0
    assert pytest.approx(res.parameters["closest_pt2"].x) == 5.0
    assert pytest.approx(res.parameters["closest_pt2"].y) == 0.0
    assert pytest.approx(res.parameters["closest_pt2"].z) == 4.0


def test_3d_lines_intersecting():
    # 3D 严格相交线段 (共面于 Z=0, 相交于 (5, 5, 0))
    l1 = Line3D(Point3D(0, 5, 0), Point3D(10, 5, 0))
    l2 = Line3D(Point3D(5, 0, 0), Point3D(5, 10, 0))
    res = intersect_lines_3d(l1, l2)
    assert res.has_intersection is True
    assert res.type == IntersectionType.POINT
    assert pytest.approx(res.point.x) == 5.0
    assert pytest.approx(res.point.y) == 5.0
    assert pytest.approx(res.point.z) == 0.0


def test_polyline_self_intersection():
    # 8字形自相交折线
    poly = [
        Point3D(0, 0, 0),
        Point3D(10, 10, 0),
        Point3D(0, 10, 0),
        Point3D(10, 0, 0),
    ]
    is_self, events = check_polyline_self_intersection(poly, is_closed=False)
    assert is_self is True
    assert len(events) == 1
    assert events[0]["seg_indices"] == (0, 2)
    assert pytest.approx(events[0]["point"].x) == 5.0
    assert pytest.approx(events[0]["point"].y) == 5.0
