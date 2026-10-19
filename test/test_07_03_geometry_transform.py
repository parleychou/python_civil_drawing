"""Test 07.03: Direct Geometry Transformations and Engineering Factories."""

import math
import numpy as np
import pytest

from point3d import Point3D
from vector3d import Vector3D
from line3d import Line3D
from plane3d import Plane3D
from coordinate_system3d import CoordinateSystem3D
from brep_data import BrepData
from mesh_data import MeshData
from transformation import TransformMatrix
from factories import (
    create_box_brep,
    create_pyramid_mesh,
    create_i_beam_brep,
    create_bridge_pier_brep,
)


def test_point_and_vector_transform_method():
    t = TransformMatrix.translation(100.0, 200.0, 300.0)
    pt = Point3D(10.0, 20.0, 30.0)
    pt_t = pt.transform(t)
    assert pytest.approx(pt_t.x) == 110.0
    assert pytest.approx(pt_t.y) == 220.0
    assert pytest.approx(pt_t.z) == 330.0

    vec = Vector3D(1.0, 0.0, 0.0)
    vec_t = vec.transform(t)
    # Vector is invariant under translation
    assert pytest.approx(vec_t.x) == 1.0
    assert pytest.approx(vec_t.y) == 0.0
    assert pytest.approx(vec_t.z) == 0.0


def test_line_transform_method():
    line = Line3D(Point3D(0.0, 0.0, 0.0), Point3D(10.0, 0.0, 0.0))
    t = TransformMatrix.translation(50.0, 50.0, 50.0) @ TransformMatrix.rotation_z(math.pi / 2)
    line_t = line.transform(t)

    # (0, 0, 0) -> (50, 50, 50)
    assert pytest.approx(line_t.start.x) == 50.0
    assert pytest.approx(line_t.start.y) == 50.0
    assert pytest.approx(line_t.start.z) == 50.0

    # (10, 0, 0) rotated 90deg -> (0, 10, 0) + (50, 50, 50) -> (50, 60, 50)
    assert pytest.approx(line_t.end.x) == 50.0
    assert pytest.approx(line_t.end.y) == 60.0
    assert pytest.approx(line_t.end.z) == 50.0


def test_plane_transform_method():
    # Plane at origin with normal = (0, 0, 1)
    plane = Plane3D(center=Point3D(0.0, 0.0, 0.0), normal=Vector3D(0.0, 0.0, 1.0), size=500.0)
    # Rotate 90 degrees around X: normal becomes (0, -1, 0)
    t = TransformMatrix.translation(0.0, 100.0, 200.0) @ TransformMatrix.rotation_x(math.pi / 2)
    plane_t = plane.transform(t)

    assert pytest.approx(plane_t.center.x) == 0.0
    assert pytest.approx(plane_t.center.y) == 100.0
    assert pytest.approx(plane_t.center.z) == 200.0

    assert pytest.approx(plane_t.normal.x, abs=1e-7) == 0.0
    assert pytest.approx(plane_t.normal.y, abs=1e-7) == -1.0
    assert pytest.approx(plane_t.normal.z, abs=1e-7) == 0.0


def test_coordinate_system_transform_method():
    cs = CoordinateSystem3D(
        origin=Point3D(0.0, 0.0, 0.0),
        x_axis=Vector3D(1.0, 0.0, 0.0),
        y_axis=Vector3D(0.0, 1.0, 0.0),
        z_axis=Vector3D(0.0, 0.0, 1.0),
    )
    t = TransformMatrix.translation(100.0, 200.0, 300.0) @ TransformMatrix.rotation_z(math.pi / 2)
    cs_t = cs.transform(t)

    assert pytest.approx(cs_t.origin.x) == 100.0
    assert pytest.approx(cs_t.origin.y) == 200.0
    assert pytest.approx(cs_t.origin.z) == 300.0

    assert pytest.approx(cs_t.x_axis.x, abs=1e-7) == 0.0
    assert pytest.approx(cs_t.x_axis.y, abs=1e-7) == 1.0
    assert pytest.approx(cs_t.x_axis.z, abs=1e-7) == 0.0


def test_brep_transform_method():
    box = create_box_brep(width=100.0, depth=200.0, height=300.0)
    t = TransformMatrix.translation(500.0, 0.0, 0.0) @ TransformMatrix.scaling(2.0, 1.0, 1.0)
    box_t = box.transform(t)

    assert len(box_t.vertices) == 8
    assert len(box_t.edges) == 12
    assert len(box_t.faces) == 6

    # Original width 100 -> scaled to 200 -> translated by 500 -> x from 500 to 700
    x_coords = [v.x for v in box_t.vertices]
    assert pytest.approx(min(x_coords)) == 500.0
    assert pytest.approx(max(x_coords)) == 700.0


def test_mesh_transform_method():
    pyr = create_pyramid_mesh(width=100.0, depth=100.0, height=150.0)
    t = TransformMatrix.translation(0.0, 0.0, 500.0)
    pyr_t = pyr.transform(t)

    assert len(pyr_t.vertices) == 5
    assert len(pyr_t.faces) == 5
    z_coords = [v.z for v in pyr_t.vertices]
    assert pytest.approx(min(z_coords)) == 500.0
    assert pytest.approx(max(z_coords)) == 650.0


def test_create_i_beam_brep():
    beam = create_i_beam_brep(
        length=2000.0,
        width=300.0,
        height=500.0,
        flange_thickness=20.0,
        web_thickness=15.0,
    )
    assert isinstance(beam, BrepData)
    # An I-beam cross section has 12 vertices; extruded along length has 24 vertices
    assert len(beam.vertices) == 24
    assert len(beam.faces) == 14  # 12 side faces + 2 end faces


def test_create_bridge_pier_brep():
    pier = create_bridge_pier_brep(
        height=4000.0,
        top_width=1200.0,
        top_depth=800.0,
        bottom_width=1800.0,
        bottom_depth=1200.0,
    )
    assert isinstance(pier, BrepData)
    assert len(pier.vertices) == 8
    assert len(pier.faces) == 6


def test_convenience_transformation_methods():
    # Test translated(), rotated_z(), scaled() directly on geometry objects
    pt = Point3D(10.0, 20.0, 30.0)
    pt_moved = pt.translated(5.0, -10.0, 15.0)
    assert pytest.approx(pt_moved.x) == 15.0
    assert pytest.approx(pt_moved.y) == 10.0
    assert pytest.approx(pt_moved.z) == 45.0

    box = create_box_brep(width=100.0, depth=100.0, height=200.0)
    box_moved = box.translated(1000.0, 0.0, 0.0).rotated_z(math.pi / 2).scaled(2.0)
    assert isinstance(box_moved, BrepData)
    assert len(box_moved.vertices) == 8


def test_builtin_generate_three_views():
    # Test that geom.generate_three_views() works directly on BrepData and MeshData
    box = create_box_brep(width=200.0, depth=100.0, height=300.0)
    views = box.generate_three_views(offset=1500.0)

    assert "top" in views
    assert "front" in views
    assert "side" in views
    assert isinstance(views["top"], BrepData)
    for v in views["top"].vertices:
        assert pytest.approx(v.z) == -1500.0
