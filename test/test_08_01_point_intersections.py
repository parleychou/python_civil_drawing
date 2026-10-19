"""Test 08.01: Point-level Intersections (Point-Point, Point-Line, Point-Plane)."""

import pytest
from point3d import Point3D
from line3d import Line3D
from plane3d import Plane3D
from vector3d import Vector3D
from intersection import (
    IntersectionType,
    intersect_point_point,
    intersect_point_line,
    intersect_point_plane,
)


def test_point_point_coincidence():
    p1 = Point3D(100.0, 200.0, 300.0)
    p2 = Point3D(100.00005, 199.99995, 300.00002)
    res = intersect_point_point(p1, p2, tol=1e-4)
    assert res.has_intersection is True
    assert res.type == IntersectionType.POINT
    assert pytest.approx(res.point.x, abs=1e-5) == 100.000025
    assert pytest.approx(res.point.y, abs=1e-5) == 199.999975
    assert pytest.approx(res.point.z, abs=1e-5) == 300.00001
    expected_dist = p1.distance_to(p2)
    assert res.clearance == pytest.approx(expected_dist, abs=1e-6)

    p3 = Point3D(100.1, 200.0, 300.0)
    res_disjoint = intersect_point_point(p1, p3, tol=1e-4)
    assert res_disjoint.has_intersection is False
    assert res_disjoint.type == IntersectionType.NONE
    assert res_disjoint.clearance == pytest.approx(0.1, abs=1e-5)


def test_point_line_cases():
    line = Line3D(Point3D(0.0, 0.0, 0.0), Point3D(10.0, 0.0, 0.0))

    # 1. 严格线段内点
    p_mid = Point3D(5.0, 0.00002, 0.0)
    res_mid = intersect_point_line(p_mid, line, tol=1e-4)
    assert res_mid.has_intersection is True
    assert res_mid.type == IntersectionType.POINT
    assert pytest.approx(res_mid.parameters["t"], abs=1e-5) == 0.5
    assert res_mid.clearance == pytest.approx(0.00002, abs=1e-5)

    # 2. 端点
    p_end = Point3D(10.0, 0.0, 0.0)
    res_end = intersect_point_line(p_end, line, tol=1e-4)
    assert res_end.has_intersection is True
    assert pytest.approx(res_end.parameters["t"], abs=1e-5) == 1.0

    # 3. 延长线上点 (超出 [0, 1] 范围，非有限线段相交)
    p_ext = Point3D(12.0, 0.0, 0.0)
    res_ext = intersect_point_line(p_ext, line, tol=1e-4)
    assert res_ext.has_intersection is False
    assert res_ext.parameters["is_on_extension"] is True
    assert pytest.approx(res_ext.parameters["t"], abs=1e-5) == 1.2

    # 4. 离线点
    p_off = Point3D(5.0, 2.0, 0.0)
    res_off = intersect_point_line(p_off, line, tol=1e-4)
    assert res_off.has_intersection is False
    assert res_off.clearance == pytest.approx(2.0, abs=1e-5)


def test_point_plane_cases():
    plane = Plane3D(Point3D(0, 0, 10), Vector3D(0, 0, 1))

    # 1. 在支撑平面上
    p_on = Point3D(123.4, 567.8, 10.00003)
    res_on = intersect_point_plane(p_on, plane, tol=1e-4)
    assert res_on.has_intersection is True
    assert res_on.type == IntersectionType.POINT
    assert pytest.approx(res_on.point.z, abs=1e-5) == 10.00003

    # 2. 离面点
    p_off = Point3D(123.4, 567.8, 15.0)
    res_off = intersect_point_plane(p_off, plane, tol=1e-4)
    assert res_off.has_intersection is False
    assert res_off.clearance == pytest.approx(5.0, abs=1e-5)
