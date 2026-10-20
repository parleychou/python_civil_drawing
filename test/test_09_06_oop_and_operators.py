"""test_09_06_oop_and_operators.py — 面向对象原生内置布尔方法与双目运算符测试。"""

import pytest
from factories import create_box_mesh, create_box_brep
from point3d import Point3D
from boolean_ops import BooleanOperationType


def test_mesh_oop_boolean_methods():
    box_a = create_box_mesh(Point3D(0, 0, 0), 10.0, 10.0, 10.0)
    box_b = create_box_mesh(Point3D(5, 0, 0), 10.0, 10.0, 10.0)

    # 1. union
    res_union = box_a.boolean_union(box_b)
    assert res_union.success is True
    assert res_union.result_volume == pytest.approx(1500.0, rel=1e-2)

    # 2. intersection
    res_inter = box_a.boolean_intersection(box_b)
    assert res_inter.success is True
    assert res_inter.result_volume == pytest.approx(500.0, rel=1e-2)

    # 3. difference
    cutter = create_box_mesh(Point3D(2, 2, -1), 6, 6, 12)
    res_diff = box_a.cut(cutter)
    assert res_diff.success is True
    assert res_diff.result_volume == pytest.approx(640.0, rel=1e-2)


def test_mesh_operators_overloading():
    box_a = create_box_mesh(Point3D(0, 0, 0), 10.0, 10.0, 10.0)
    box_b = create_box_mesh(Point3D(5, 0, 0), 10.0, 10.0, 10.0)

    # + 运算符 (Union)
    mesh_union = box_a + box_b
    assert mesh_union.to_pyvista().volume == pytest.approx(1500.0, rel=1e-2)

    # & 运算符 (Intersection)
    mesh_inter = box_a & box_b
    assert mesh_inter.to_pyvista().volume == pytest.approx(500.0, rel=1e-2)

    # - 运算符 (Difference)
    cutter = create_box_mesh(Point3D(2, 2, -1), 6, 6, 12)
    mesh_diff = box_a - cutter
    assert mesh_diff.to_pyvista().volume == pytest.approx(640.0, rel=1e-2)


def test_brep_oop_boolean_delegation():
    brep_a = create_box_brep(10.0, 10.0, 10.0)
    brep_b = create_box_brep(10.0, 10.0, 10.0).translated(5.0, 0.0, 0.0)

    res = brep_a.boolean_union(brep_b)
    assert res.success is True
    assert res.result_volume == pytest.approx(1500.0, rel=1e-2)
