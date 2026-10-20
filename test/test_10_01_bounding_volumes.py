"""test_10_01_bounding_volumes.py — 包围盒数学 (AABB/OBB) 与 SAT 分离轴定理测试。"""

import pytest
import numpy as np
from point3d import Point3D
from vector3d import Vector3D
from collision import (
    AABB,
    OBB,
    ClashType,
    ClashSeverity,
    ClashRecord,
    ClashReport,
)


def test_aabb_overlaps_and_tolerance():
    box_a = AABB(0.0, 0.0, 0.0, 10.0, 5.0, 4.0)
    box_b = AABB(8.0, 4.0, 2.0, 18.0, 9.0, 6.0)
    # 重叠在 X in [8, 10], Y in [4, 5], Z in [2, 4]
    assert box_a.overlaps(box_b) is True
    assert box_a.volume == pytest.approx(200.0)

    # 分离盒
    box_c = AABB(12.0, 0.0, 0.0, 20.0, 5.0, 4.0)
    assert box_a.overlaps(box_c) is False
    # 增加容差 2.5 mm，间距为 2.0 mm 时扩展后重叠
    assert box_a.overlaps(box_c, tolerance=2.5) is True


def test_aabb_from_points():
    pts = [
        Point3D(1.0, -2.0, 3.0),
        Point3D(5.0, 8.0, -1.0),
        Point3D(-3.0, 4.0, 2.0),
    ]
    bbox = AABB.from_points(pts)
    assert bbox.min_x == -3.0
    assert bbox.max_x == 5.0
    assert bbox.min_y == -2.0
    assert bbox.max_y == 8.0
    assert bbox.min_z == -1.0
    assert bbox.max_z == 3.0


def test_obb_sat_separation():
    # 构造两个轴对齐的 OBB
    axes = (Vector3D(1, 0, 0), Vector3D(0, 1, 0), Vector3D(0, 0, 1))
    obb1 = OBB(center=Point3D(0, 0, 0), axes=axes, half_extents=(5.0, 5.0, 5.0))
    obb2 = OBB(center=Point3D(8, 0, 0), axes=axes, half_extents=(5.0, 5.0, 5.0))
    # 中心距 8，半长之和 10 -> 重叠
    assert obb1.overlaps(obb2) is True

    # 沿 X 轴拉开至中心距 12 -> 分离
    obb3 = OBB(center=Point3D(12, 0, 0), axes=axes, half_extents=(5.0, 5.0, 5.0))
    assert obb1.overlaps(obb3) is False


def test_clash_data_structures():
    record = ClashRecord(
        clash_id="CLASH_001",
        clash_type=ClashType.HARD,
        severity=ClashSeverity.CRITICAL,
        object_a_id="BEAM_01",
        object_b_id="PIPE_02",
        location=Point3D(3000, 4000, 2800),
        clearance=0.0,
        penetration_depth=45.0,
        penetration_volume=12500.0,
        system_a="Structure",
        system_b="HVAC",
        recommendation="建议结构预留套管"
    )
    assert record.clash_type == ClashType.HARD
    assert record.severity == ClashSeverity.CRITICAL
    assert record.penetration_depth == 45.0

    report = ClashReport(
        total_elements_checked=150,
        candidate_pairs_screened=24,
        confirmed_clashes_count=1,
        clashes=[record],
        execution_time_ms=12.5
    )
    assert report.total_elements_checked == 150
    assert len(report.clashes) == 1
