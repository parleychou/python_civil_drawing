"""Test 07.01: 4x4 Transformation Matrix and Affine Operations."""

import math
import numpy as np
import pytest

from point3d import Point3D
from vector3d import Vector3D
from coordinate_system3d import CoordinateSystem3D
from transformation import TransformMatrix


def test_identity_matrix():
    m = TransformMatrix.identity()
    np.testing.assert_allclose(m.matrix, np.eye(4), atol=1e-12)
    pt = Point3D(1.0, 2.0, 3.0)
    transformed = m.apply_to_point(pt)
    assert transformed.to_tuple() == pt.to_tuple()


def test_translation():
    t = TransformMatrix.translation(100.0, -50.0, 25.0)
    pt = Point3D(10.0, 20.0, 30.0)
    res_pt = t.apply_to_point(pt)
    assert pytest.approx(res_pt.x) == 110.0
    assert pytest.approx(res_pt.y) == -30.0
    assert pytest.approx(res_pt.z) == 55.0

    # Vector should NOT be translated (w = 0)
    vec = Vector3D(1.0, 2.0, 3.0)
    res_vec = t.apply_to_vector(vec)
    assert pytest.approx(res_vec.x) == 1.0
    assert pytest.approx(res_vec.y) == 2.0
    assert pytest.approx(res_vec.z) == 3.0


def test_rotations_cardinal_axes():
    # 90 degrees around Z: (1, 0, 0) -> (0, 1, 0)
    rz = TransformMatrix.rotation_z(math.pi / 2)
    pt = Point3D(1.0, 0.0, 0.0)
    res_z = rz.apply_to_point(pt)
    assert pytest.approx(res_z.x, abs=1e-7) == 0.0
    assert pytest.approx(res_z.y, abs=1e-7) == 1.0
    assert pytest.approx(res_z.z, abs=1e-7) == 0.0

    # 90 degrees around X: (0, 1, 0) -> (0, 0, 1)
    rx = TransformMatrix.rotation_x(math.pi / 2)
    pt_y = Point3D(0.0, 1.0, 0.0)
    res_x = rx.apply_to_point(pt_y)
    assert pytest.approx(res_x.x, abs=1e-7) == 0.0
    assert pytest.approx(res_x.y, abs=1e-7) == 0.0
    assert pytest.approx(res_x.z, abs=1e-7) == 1.0

    # 90 degrees around Y: (0, 0, 1) -> (1, 0, 0)
    ry = TransformMatrix.rotation_y(math.pi / 2)
    pt_z = Point3D(0.0, 0.0, 1.0)
    res_y = ry.apply_to_point(pt_z)
    assert pytest.approx(res_y.x, abs=1e-7) == 1.0
    assert pytest.approx(res_y.y, abs=1e-7) == 0.0
    assert pytest.approx(res_y.z, abs=1e-7) == 0.0


def test_rotation_arbitrary_axis_rodrigues():
    # Rotate around axis (1, 1, 1)/sqrt(3) by 120 degrees (2*pi/3)
    # This permutes x -> y -> z -> x: (1, 0, 0) -> (0, 1, 0)
    axis = Vector3D(1.0, 1.0, 1.0).normalized()
    r_axis = TransformMatrix.rotation_axis(axis, 2.0 * math.pi / 3.0)
    res = r_axis.apply_to_point(Point3D(1.0, 0.0, 0.0))
    assert pytest.approx(res.x, abs=1e-6) == 0.0
    assert pytest.approx(res.y, abs=1e-6) == 1.0
    assert pytest.approx(res.z, abs=1e-6) == 0.0


def test_scaling():
    s = TransformMatrix.scaling(2.0, 0.5, 3.0)
    pt = Point3D(10.0, 20.0, 30.0)
    res = s.apply_to_point(pt)
    assert pytest.approx(res.x) == 20.0
    assert pytest.approx(res.y) == 10.0
    assert pytest.approx(res.z) == 90.0


def test_matrix_multiplication_and_non_commutativity():
    t = TransformMatrix.translation(10.0, 0.0, 0.0)
    r = TransformMatrix.rotation_z(math.pi / 2)

    # m1: Rotate first, then Translate -> T @ R
    m1 = t @ r
    # m2: Translate first, then Rotate -> R @ T
    m2 = r @ t

    pt = Point3D(1.0, 0.0, 0.0)
    # T @ R: (1, 0, 0) rotated by 90deg -> (0, 1, 0), then translated by (10, 0, 0) -> (10, 1, 0)
    res1 = m1.apply_to_point(pt)
    # R @ T: (1, 0, 0) translated by (10, 0, 0) -> (11, 0, 0), then rotated by 90deg -> (0, 11, 0)
    res2 = m2.apply_to_point(pt)

    assert pytest.approx(res1.x) == 10.0
    assert pytest.approx(res1.y) == 1.0
    assert pytest.approx(res2.x, abs=1e-7) == 0.0
    assert pytest.approx(res2.y) == 11.0
    # Confirms T @ R != R @ T
    assert not np.allclose(m1.matrix, m2.matrix)


def test_inverse_matrix():
    m = (
        TransformMatrix.translation(50.0, -30.0, 120.0)
        @ TransformMatrix.rotation_z(0.7)
        @ TransformMatrix.rotation_x(0.3)
        @ TransformMatrix.scaling(2.0, 1.5, 0.8)
    )
    inv = m.inverse()
    prod = (m @ inv).matrix
    np.testing.assert_allclose(prod, np.eye(4), atol=1e-7)

    # Test point recovery: pt == inv(m(pt))
    orig_pt = Point3D(15.0, 25.0, -10.0)
    trans_pt = m.apply_to_point(orig_pt)
    recovered_pt = inv.apply_to_point(trans_pt)
    assert pytest.approx(recovered_pt.x) == orig_pt.x
    assert pytest.approx(recovered_pt.y) == orig_pt.y
    assert pytest.approx(recovered_pt.z) == orig_pt.z


def test_from_coordinate_systems():
    # Local CS with origin at (100, 200, 300) and rotated axes
    origin = Point3D(100.0, 200.0, 300.0)
    # Local X is world Y, Local Y is -world X, Local Z is world Z (90 deg rotation)
    local_cs = CoordinateSystem3D(
        origin=origin,
        x_axis=Vector3D(0.0, 1.0, 0.0),
        y_axis=Vector3D(-1.0, 0.0, 0.0),
        z_axis=Vector3D(0.0, 0.0, 1.0),
    )
    world_cs = CoordinateSystem3D(
        origin=Point3D(0.0, 0.0, 0.0),
        x_axis=Vector3D(1.0, 0.0, 0.0),
        y_axis=Vector3D(0.0, 1.0, 0.0),
        z_axis=Vector3D(0.0, 0.0, 1.0),
    )

    # L2W transform
    m_l2w = TransformMatrix.from_coordinate_systems(local_cs, world_cs)
    # Local point (10, 0, 0) along local X should be at world (100, 210, 300)
    local_pt = Point3D(10.0, 0.0, 0.0)
    world_pt = m_l2w.apply_to_point(local_pt)
    assert pytest.approx(world_pt.x) == 100.0
    assert pytest.approx(world_pt.y) == 210.0
    assert pytest.approx(world_pt.z) == 300.0

    # W2L transform
    m_w2l = TransformMatrix.from_coordinate_systems(world_cs, local_cs)
    back_to_local = m_w2l.apply_to_point(world_pt)
    assert pytest.approx(back_to_local.x) == local_pt.x
    assert pytest.approx(back_to_local.y) == local_pt.y
    assert pytest.approx(back_to_local.z) == local_pt.z
