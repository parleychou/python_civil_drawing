"""test_09_03_boolean_union.py — 3D 实体并集 (Union) 算法测试。"""

import pytest
from factories import create_box_mesh
from point3d import Point3D
from boolean_ops import boolean_union_mesh, BooleanOperationType


def test_boolean_union_two_boxes():
    box_a = create_box_mesh(Point3D(0, 0, 0), 10.0, 10.0, 10.0)
    box_b = create_box_mesh(Point3D(5, 0, 0), 10.0, 10.0, 10.0)

    res = boolean_union_mesh(box_a, box_b)
    assert res.success is True
    assert res.operation == BooleanOperationType.UNION
    assert res.mesh is not None
    # 理论并集体积 = 1000 + 1000 - 500 = 1500
    assert res.result_volume == pytest.approx(1500.0, rel=1e-2)
    assert res.is_watertight is True
