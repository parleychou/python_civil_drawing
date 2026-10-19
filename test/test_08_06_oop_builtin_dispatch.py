"""Test 08.06: OOP Native Built-in Intersection Dispatch and Bidirectional Symmetry."""

import pytest
from point3d import Point3D
from line3d import Line3D
from plane3d import Plane3D
from vector3d import Vector3D
from factories import create_box_mesh, create_cube_brep
from intersection import IntersectionType


def test_point_dispatch_symmetry():
    # 点与线双向多态分发对称性
    pt = Point3D(5, 5, 0)
    line = Line3D(Point3D(0, 5, 0), Point3D(10, 5, 0))

    res1 = pt.intersect(line)
    res2 = line.intersect(pt)

    assert res1.has_intersection is True
    assert res2.has_intersection is True
    assert res1.type == IntersectionType.POINT
    assert res2.type == IntersectionType.POINT
    assert pytest.approx(res1.point.x) == 5.0
    assert pytest.approx(res2.point.x) == 5.0


def test_point_plane_dispatch_symmetry():
    # 点与平面双向多态分发对称性
    pt = Point3D(10, 20, 5)
    plane = Plane3D(Point3D(0, 0, 5), Vector3D(0, 0, 1))

    res1 = pt.intersect(plane)
    res2 = plane.intersect(pt)

    assert res1.has_intersection is True
    assert res2.has_intersection is True
    assert res1.type == IntersectionType.POINT
    assert res2.type == IntersectionType.POINT


def test_line_plane_oop():
    line = Line3D(Point3D(0, 0, 0), Point3D(0, 0, 10))
    plane = Plane3D(Point3D(0, 0, 5), Vector3D(0, 0, 1))

    res1 = line.intersect(plane)
    res2 = plane.intersect(line)

    assert res1.has_intersection is True
    assert res2.has_intersection is True
    assert pytest.approx(res1.point.z) == 5.0
    assert pytest.approx(res2.point.z) == 5.0


def test_line_mesh_oop():
    cube = create_box_mesh(Point3D(0, 0, 0), 10.0, 10.0, 10.0)
    line = Line3D(Point3D(-5, 5, 5), Point3D(15, 5, 5))

    res1 = line.intersect(cube)
    res2 = cube.intersect(line)

    assert res1.has_intersection is True
    assert res2.has_intersection is True
    assert len(res1.points) == 2
    assert len(res2.points) == 2


def test_plane_mesh_oop():
    cube = create_box_mesh(Point3D(0, 0, 0), 10.0, 10.0, 10.0)
    plane = Plane3D(Point3D(5, 5, 5), Vector3D(0, 0, 1))

    res1 = plane.intersect(cube)
    res2 = cube.intersect(plane)

    assert res1.has_intersection is True
    assert res2.has_intersection is True
    assert len(res1.lines) >= 4
    assert len(res2.lines) >= 4


def test_brep_triangulation_and_oop():
    # 测试 B-Rep 多面体边界表示的三角化适配器与求交分发
    brep = create_cube_brep(10.0, 10.0, 10.0)
    mesh = brep.to_triangulated_mesh()
    assert len(mesh.vertices) == 8
    assert len(mesh.faces) == 12  # 6 个四边形面三角化为 12 个三角面

    # B-Rep 与平面的相交
    plane = Plane3D(Point3D(5, 5, 5), Vector3D(0, 0, 1))
    res = brep.intersect(plane)
    assert res.has_intersection is True
    assert len(res.lines) >= 4
