"""test_10_04_narrow_phase_clearance.py — 窄阶段精确相交与最小净距解算测试。"""

import pytest
from factories import create_box_mesh
from point3d import Point3D
from collision import (
    check_narrow_phase_clash,
    calculate_mesh_minimum_clearance,
    ClashType,
)


def test_narrow_phase_hard_clash():
    # 两相交立方体
    box_a = create_box_mesh(Point3D(0, 0, 0), 10.0, 10.0, 10.0)
    box_b = create_box_mesh(Point3D(5, 5, 5), 10.0, 10.0, 10.0)

    rec = check_narrow_phase_clash("BOX_A", box_a, "BOX_B", box_b, clearance=0.0)
    assert rec is not None
    assert rec.clash_type == ClashType.HARD
    assert rec.clearance == 0.0
    assert rec.penetration_depth > 0.0


def test_narrow_phase_soft_clearance():
    # 两分离立方体，中心距在 X 上相隔 5.0 (box1: [0, 10], box2: [15, 25])
    # 空间物理净距 = 15 - 10 = 5.0
    box_a = create_box_mesh(Point3D(0, 0, 0), 10.0, 10.0, 10.0)
    box_b = create_box_mesh(Point3D(15, 0, 0), 10.0, 10.0, 10.0)

    clearance = calculate_mesh_minimum_clearance(box_a, box_b)
    assert clearance == pytest.approx(5.0, abs=1e-2)

    # 设安全净距阈值为 8.0 -> 属于软碰撞
    rec_soft = check_narrow_phase_clash("BOX_A", box_a, "BOX_B", box_b, clearance=8.0)
    assert rec_soft is not None
    assert rec_soft.clash_type == ClashType.SOFT
    assert rec_soft.clearance == pytest.approx(5.0, abs=1e-2)

    # 设安全净距阈值为 3.0 -> 安全合规 (非碰撞)
    rec_safe = check_narrow_phase_clash("BOX_A", box_a, "BOX_B", box_b, clearance=3.0)
    assert rec_safe is None
