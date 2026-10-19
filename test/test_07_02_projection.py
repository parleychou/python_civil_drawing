"""Test 07.02: Geometric Projection Engine and Multi-View Generation."""

import math
import numpy as np
import pytest

from point3d import Point3D
from vector3d import Vector3D
from line3d import Line3D
from plane3d import Plane3D
from coordinate_system3d import CoordinateSystem3D
from factories import create_box_brep, create_pyramid_mesh
from projection import ProjectionEngine


def test_project_point_to_horizontal_plane():
    plane = Plane3D(center=Point3D(0.0, 0.0, 0.0), normal=Vector3D(0.0, 0.0, 1.0))
    pt = Point3D(150.0, 250.0, 400.0)
    proj_pt, dist = ProjectionEngine.project_point_to_plane(pt, plane)

    assert pytest.approx(proj_pt.x) == 150.0
    assert pytest.approx(proj_pt.y) == 250.0
    assert pytest.approx(proj_pt.z) == 0.0
    assert pytest.approx(dist) == 400.0

    # Orthogonality check: (pt - proj_pt) must be parallel to normal
    diff_vec = pt - proj_pt
    assert diff_vec.cross(plane.normal).length() < 1e-10


def test_project_point_to_inclined_plane():
    # 45-degree plane passing through origin, normal = (1, 0, 1) / sqrt(2)
    norm = Vector3D(1.0, 0.0, 1.0).normalized()
    plane = Plane3D(center=Point3D(0.0, 0.0, 0.0), normal=norm)
    pt = Point3D(10.0, 20.0, 10.0)

    proj_pt, dist = ProjectionEngine.project_point_to_plane(pt, plane)

    # Point (10, 20, 10) on normal line should project to (0, 20, 0)
    assert pytest.approx(proj_pt.x, abs=1e-7) == 0.0
    assert pytest.approx(proj_pt.y, abs=1e-7) == 20.0
    assert pytest.approx(proj_pt.z, abs=1e-7) == 0.0
    assert pytest.approx(dist) == 10.0 * math.sqrt(2.0)


def test_project_point_to_coordinate_system():
    # CS with origin at (100, 100, 100)
    cs = CoordinateSystem3D(
        origin=Point3D(100.0, 100.0, 100.0),
        x_axis=Vector3D(1.0, 0.0, 0.0),
        y_axis=Vector3D(0.0, 1.0, 0.0),
        z_axis=Vector3D(0.0, 0.0, 1.0),
    )
    pt = Point3D(150.0, 220.0, 350.0)
    proj_pt, local_coords = ProjectionEngine.project_point_to_cs(pt, cs)

    # Projection onto CS's XY plane has world Z = 100.0
    assert pytest.approx(proj_pt.x) == 150.0
    assert pytest.approx(proj_pt.y) == 220.0
    assert pytest.approx(proj_pt.z) == 100.0

    # Local coordinates (u, v, w) = (50, 120, 250)
    u, v, w = local_coords
    assert pytest.approx(u) == 50.0
    assert pytest.approx(v) == 120.0
    assert pytest.approx(w) == 250.0


def test_project_line_to_plane():
    plane = Plane3D(center=Point3D(0.0, 0.0, 0.0), normal=Vector3D(0.0, 0.0, 1.0))
    line = Line3D(Point3D(0.0, 0.0, 100.0), Point3D(200.0, 300.0, 500.0))
    proj_line = ProjectionEngine.project_line_to_plane(line, plane)

    assert pytest.approx(proj_line.start.x) == 0.0
    assert pytest.approx(proj_line.start.y) == 0.0
    assert pytest.approx(proj_line.start.z) == 0.0
    assert pytest.approx(proj_line.end.x) == 200.0
    assert pytest.approx(proj_line.end.y) == 300.0
    assert pytest.approx(proj_line.end.z) == 0.0


def test_project_brep_to_plane():
    plane = Plane3D(center=Point3D(0.0, 0.0, 0.0), normal=Vector3D(0.0, 0.0, 1.0))
    box = create_box_brep(width=200.0, depth=100.0, height=300.0)
    proj_brep = ProjectionEngine.project_brep_to_plane(box, plane)

    # All vertices should have Z = 0
    assert len(proj_brep.vertices) == 8
    for v in proj_brep.vertices:
        assert pytest.approx(v.z, abs=1e-7) == 0.0
    # Topology should be preserved
    assert len(proj_brep.edges) == 12
    assert len(proj_brep.faces) == 6


def test_project_mesh_to_plane():
    plane = Plane3D(center=Point3D(0.0, 0.0, 0.0), normal=Vector3D(0.0, 0.0, 1.0))
    pyramid = create_pyramid_mesh(width=100.0, depth=100.0, height=150.0)
    proj_mesh = ProjectionEngine.project_mesh_to_plane(pyramid, plane)

    assert len(proj_mesh.vertices) == 5
    for v in proj_mesh.vertices:
        assert pytest.approx(v.z, abs=1e-7) == 0.0
    assert len(proj_mesh.faces) == 5


def test_generate_three_views():
    box = create_box_brep(width=200.0, depth=100.0, height=300.0)
    views = ProjectionEngine.generate_three_views(box, offset=500.0)

    assert "top" in views
    assert "front" in views
    assert "side" in views

    # Top view on Z plane: all Z coords constant
    top_geom = views["top"]
    for v in top_geom.vertices:
        assert pytest.approx(v.z, abs=1e-7) == -500.0

    # Front view on Y plane: all Y coords constant
    front_geom = views["front"]
    for v in front_geom.vertices:
        assert pytest.approx(v.y, abs=1e-7) == -500.0

    # Side view on X plane: all X coords constant
    side_geom = views["side"]
    for v in side_geom.vertices:
        assert pytest.approx(v.x, abs=1e-7) == -500.0


def test_direct_builtin_projection_methods():
    """Verify that projection works directly as built-in methods on geometry classes."""
    plane = Plane3D(center=Point3D(0.0, 0.0, 0.0), normal=Vector3D(0.0, 0.0, 1.0))

    # Point3D
    pt = Point3D(10.0, 20.0, 30.0)
    p_proj = pt.project_to_plane(plane)
    assert p_proj.to_tuple() == (10.0, 20.0, 0.0)
    p_proj2, dist = pt.project_to_plane_with_distance(plane)
    assert p_proj2.to_tuple() == (10.0, 20.0, 0.0)
    assert pytest.approx(dist) == 30.0

    # Line3D
    line = Line3D(Point3D(0.0, 0.0, 10.0), Point3D(5.0, 5.0, 20.0))
    line_proj = line.project_to_plane(plane)
    assert line_proj.start.to_tuple() == (0.0, 0.0, 0.0)
    assert line_proj.end.to_tuple() == (5.0, 5.0, 0.0)

    # BrepData
    box = create_box_brep(width=100.0, depth=100.0, height=200.0)
    box_proj = box.project_to_plane(plane)
    for v in box_proj.vertices:
        assert pytest.approx(v.z, abs=1e-7) == 0.0

    # MeshData
    pyramid = create_pyramid_mesh(width=100.0, depth=100.0, height=150.0)
    pyr_proj = pyramid.project_to_plane(plane)
    for v in pyr_proj.vertices:
        assert pytest.approx(v.z, abs=1e-7) == 0.0
