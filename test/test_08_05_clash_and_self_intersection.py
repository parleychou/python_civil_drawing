"""Test 08.05: Plane-Plane Intersection, Solid Clash, Solid Containment, and Mesh Self-Intersection."""

import pytest
from point3d import Point3D
from line3d import Line3D
from plane3d import Plane3D
from vector3d import Vector3D
from factories import create_box_mesh
from intersection import (
    IntersectionType,
    intersect_planes,
    intersect_mesh_mesh,
    check_mesh_self_intersection,
)


def test_plane_plane_intersection():
    p1 = Plane3D(Point3D(0, 0, 0), Vector3D(1, 0, 0))   # YZ 面 (X=0)
    p2 = Plane3D(Point3D(0, 0, 0), Vector3D(0, 1, 0))   # XZ 面 (Y=0)
    res = intersect_planes(p1, p2)
    assert res.has_intersection is True
    assert res.type == IntersectionType.LINE
    assert res.line is not None

    # 交线方向必定沿 Z 轴 (0, 0, 1) 或 (0, 0, -1)
    dir_vec = res.line.direction().normalized()
    assert pytest.approx(abs(dir_vec.z), abs=1e-5) == 1.0
    assert pytest.approx(dir_vec.x, abs=1e-5) == 0.0
    assert pytest.approx(dir_vec.y, abs=1e-5) == 0.0

    # 基准点必须同时满足两平面方程 (X=0, Y=0)
    base_pt = res.line.start
    assert pytest.approx(base_pt.x, abs=1e-5) == 0.0
    assert pytest.approx(base_pt.y, abs=1e-5) == 0.0


def test_mesh_mesh_hard_clash():
    # 两个部分重叠的立方体
    c1 = create_box_mesh(Point3D(0, 0, 0), 10.0, 10.0, 10.0)
    c2 = create_box_mesh(Point3D(5, 5, 5), 10.0, 10.0, 10.0)
    res = intersect_mesh_mesh(c1, c2)
    assert res.has_intersection is True
    assert res.type in (IntersectionType.MULTI_SEGMENTS, IntersectionType.CONTOUR)
    assert len(res.lines) > 0


def test_mesh_mesh_nested_containment():
    # 小立方体完全嵌套在大立方体内部 (边界无任何交线，但实体完全重叠包含)
    big = create_box_mesh(Point3D(0, 0, 0), 20.0, 20.0, 20.0)
    small = create_box_mesh(Point3D(5, 5, 5), 5.0, 5.0, 5.0)
    res = intersect_mesh_mesh(big, small)
    assert res.has_intersection is True
    assert res.type == IntersectionType.CONTAINED


def test_mesh_mesh_disjoint():
    # 两个完全分离的立方体
    c1 = create_box_mesh(Point3D(0, 0, 0), 10.0, 10.0, 10.0)
    c2 = create_box_mesh(Point3D(50, 50, 50), 10.0, 10.0, 10.0)
    res = intersect_mesh_mesh(c1, c2)
    assert res.has_intersection is False
    assert res.type == IntersectionType.NONE


def test_mesh_self_intersection_positive_and_negative():
    # 1. 正常闭合立方体：不自交
    cube = create_box_mesh(Point3D(0, 0, 0), 10.0, 10.0, 10.0)
    is_self, pairs = check_mesh_self_intersection(cube)
    assert is_self is False
    assert len(pairs) == 0
