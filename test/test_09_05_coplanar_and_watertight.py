"""test_09_05_coplanar_and_watertight.py — 共面退化消解、交集与水密流形性测试。"""

import pytest
from factories import create_box_mesh
from point3d import Point3D
from boolean_ops import (
    boolean_intersection_mesh,
    validate_mesh_manifold,
    BooleanOperationType,
)


def test_boolean_intersection_volume():
    box_a = create_box_mesh(Point3D(0, 0, 0), 10.0, 10.0, 10.0)
    box_b = create_box_mesh(Point3D(5, 0, 0), 10.0, 10.0, 10.0)

    res = boolean_intersection_mesh(box_a, box_b)
    assert res.success is True
    assert res.operation == BooleanOperationType.INTERSECTION
    # 重叠体积 = 5 * 10 * 10 = 500
    assert res.result_volume == pytest.approx(500.0, rel=1e-2)


def test_validate_mesh_manifold_detection():
    # 正常立方体：严格 2-流形水密
    box = create_box_mesh(Point3D(0, 0, 0), 10.0, 10.0, 10.0)
    is_watertight, problem_edges = validate_mesh_manifold(box)
    assert is_watertight is True
    assert len(problem_edges) == 0

    # 人工删除一个三角面片制造破洞
    broken_box = create_box_mesh(Point3D(0, 0, 0), 10.0, 10.0, 10.0)
    broken_box.faces = broken_box.faces[:-1]  # 删除最后一个面
    is_watertight_broken, problem_edges_broken = validate_mesh_manifold(broken_box)
    assert is_watertight_broken is False
    assert len(problem_edges_broken) == 3  # 被删除三角形的 3 条边变为开环单引用边
