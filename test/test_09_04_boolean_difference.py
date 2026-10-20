"""test_09_04_boolean_difference.py — 3D 实体差集 (Difference / Cut) 算法测试。"""

import pytest
from factories import create_box_mesh
from point3d import Point3D
from boolean_ops import boolean_difference_mesh, BooleanOperationType


def test_boolean_difference_through_hole():
    # 立方体 [0, 10]^3 (体积 1000) 被中心通孔 [2, 8] x [2, 8] x [-1, 11] (孔面积 36, 高 10, 切除体积 360) 穿透
    cube = create_box_mesh(Point3D(0, 0, 0), 10.0, 10.0, 10.0)
    cutter = create_box_mesh(Point3D(2.0, 2.0, -1.0), 6.0, 6.0, 12.0)

    res = boolean_difference_mesh(cube, cutter)
    assert res.success is True
    assert res.operation == BooleanOperationType.DIFFERENCE
    assert res.mesh is not None
    # 剩余理论体积 = 1000 - 360 = 640
    assert res.result_volume == pytest.approx(640.0, rel=1e-2)
    assert res.is_watertight is True


def test_boolean_difference_corner_cut():
    # 角部缺口开槽：[0, 10]^3 减去 [5, 15] x [5, 15] x [5, 15] (角部切除 5x5x5 = 125)
    cube1 = create_box_mesh(Point3D(0, 0, 0), 10.0, 10.0, 10.0)
    cube2 = create_box_mesh(Point3D(5, 5, 5), 10.0, 10.0, 10.0)

    res = boolean_difference_mesh(cube1, cube2)
    assert res.success is True
    assert res.result_volume == pytest.approx(875.0, rel=1e-2)
    assert res.is_watertight is True
