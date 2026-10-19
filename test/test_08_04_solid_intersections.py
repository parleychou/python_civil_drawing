"""Test 08.04: Solid-level Intersections (Point-in-Mesh, Line-Mesh Penetration, Plane-Mesh Slicing)."""

import pytest
from point3d import Point3D
from line3d import Line3D
from plane3d import Plane3D
from vector3d import Vector3D
from mesh_data import MeshData
from factories import create_box_mesh
from intersection import (
    IntersectionType,
    point_in_mesh,
    intersect_line_mesh,
    slice_mesh_with_plane,
    assemble_contour_loops,
)


def test_point_in_closed_cube():
    # 10x10x10 立方体 [0, 10]^3
    cube = create_box_mesh(Point3D(0, 0, 0), 10.0, 10.0, 10.0)

    # 1. 严格内部点
    p_in = Point3D(5.0, 5.0, 5.0)
    res_in = point_in_mesh(p_in, cube)
    assert res_in.has_intersection is True
    assert res_in.type == IntersectionType.CONTAINED

    # 2. 体表面点
    p_bound = Point3D(10.0, 5.0, 5.0)
    res_bound = point_in_mesh(p_bound, cube)
    assert res_bound.has_intersection is True
    assert res_bound.type == IntersectionType.TOUCH

    # 3. 外部点
    p_out = Point3D(15.0, 5.0, 5.0)
    res_out = point_in_mesh(p_out, cube)
    assert res_out.has_intersection is False
    assert res_out.type == IntersectionType.NONE


def test_line_mesh_penetration_multi_cavity():
    # 穿透立方体: 从 (-5, 5, 5) 穿透到 (15, 5, 5)
    cube = create_box_mesh(Point3D(0, 0, 0), 10.0, 10.0, 10.0)
    line = Line3D(Point3D(-5, 5, 5), Point3D(15, 5, 5))
    res = intersect_line_mesh(line, cube)
    assert res.has_intersection is True
    assert res.type == IntersectionType.MULTI_POINTS
    assert len(res.points) == 2
    assert pytest.approx(res.points[0].x, abs=1e-4) == 0.0
    assert pytest.approx(res.points[1].x, abs=1e-4) == 10.0
    # 实穿透总厚度应为 10.0
    assert pytest.approx(res.parameters["solid_thickness"], abs=1e-4) == 10.0
    assert len(res.parameters["intervals"]) == 1


def test_plane_mesh_slicing_cube():
    # 水平面 Z=5 剖切标准立方体 [0, 10]^3
    cube = create_box_mesh(Point3D(0, 0, 0), 10.0, 10.0, 10.0)
    slice_plane = Plane3D(Point3D(5, 5, 5), Vector3D(0, 0, 1))

    # 1. 提取切片线段
    segments = slice_mesh_with_plane(slice_plane, cube)
    assert len(segments) >= 4

    # 2. 拓扑缝合为闭合轮廓环
    contours = assemble_contour_loops(segments)
    assert len(contours) == 1
    assert contours[0]["is_closed"] is True
    assert contours[0]["is_hole"] is False
    assert len(contours[0]["points"]) >= 4

    # 验证轮廓上所有点均位于剖切平面 Z=5 上
    for pt in contours[0]["points"]:
        assert pytest.approx(pt.z, abs=1e-4) == 5.0
