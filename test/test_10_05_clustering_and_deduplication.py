"""test_10_05_clustering_and_deduplication.py — 空间聚类收敛与规则矩阵测试。"""

import pytest
from point3d import Point3D
from collision import (
    cluster_clash_points_dbscan,
    cluster_clash_records,
    ClashRuleMatrix,
    ClashRecord,
    ClashType,
    ClashSeverity,
)


def test_dbscan_point_clustering():
    # 构造两组明显分离的空间点簇
    # 簇 1: 围绕 (100, 100, 100)
    cluster1_pts = [
        Point3D(100, 100, 100),
        Point3D(105, 102, 98),
        Point3D(95, 98, 102),
    ]
    # 簇 2: 围绕 (2000, 2000, 2000)
    cluster2_pts = [
        Point3D(2000, 2000, 2000),
        Point3D(2010, 1995, 2005),
    ]
    # 孤立点 (噪声或单个独立碰撞)
    noise_pt = Point3D(5000, 5000, 5000)

    all_pts = cluster1_pts + cluster2_pts + [noise_pt]

    # 设置半径 eps = 100.0, min_samples = 2
    clusters = cluster_clash_points_dbscan(all_pts, eps=100.0, min_samples=2)

    # 应该形成 2 个簇 (孤立点 noise_pt 被排除)
    assert len(clusters) == 2
    # 验证第一簇点数 3，第二簇点数 2
    lens = sorted([len(c) for c in clusters])
    assert lens == [2, 3]


def test_cluster_clash_records_deduplication():
    # 构造同构件对之间密集的 3 个微小相交点 (例如连续穿梁的波纹腹板或管道)
    records = [
        ClashRecord(
            clash_id="REC_01",
            clash_type=ClashType.HARD,
            severity=ClashSeverity.CRITICAL,
            object_a_id="BEAM_01",
            object_b_id="PIPE_01",
            location=Point3D(1000, 2000, 3000),
            clearance=0.0,
            penetration_depth=20.0,
            penetration_volume=500.0,
            system_a="Structure",
            system_b="HVAC",
        ),
        ClashRecord(
            clash_id="REC_02",
            clash_type=ClashType.HARD,
            severity=ClashSeverity.CRITICAL,
            object_a_id="BEAM_01",
            object_b_id="PIPE_01",
            location=Point3D(1010, 2005, 3002),
            clearance=0.0,
            penetration_depth=25.0,
            penetration_volume=600.0,
            system_a="Structure",
            system_b="HVAC",
        ),
        # 远端另一个独立冲突
        ClashRecord(
            clash_id="REC_03",
            clash_type=ClashType.HARD,
            severity=ClashSeverity.MAJOR,
            object_a_id="BEAM_02",
            object_b_id="PIPE_02",
            location=Point3D(5000, 5000, 3000),
            clearance=0.0,
            penetration_depth=15.0,
            penetration_volume=300.0,
            system_a="Structure",
            system_b="Plumbing",
        ),
    ]

    merged = cluster_clash_records(records, eps=100.0)
    # REC_01 和 REC_02 应收敛合并为单一工单，REC_03 保持独立 -> 共 2 个工单
    assert len(merged) == 2

    # 找到合并后的工单，验证穿透深度取最大值 25.0，体积累加为 1100.0
    beam1_clashes = [m for m in merged if m.object_a_id == "BEAM_01"]
    assert len(beam1_clashes) == 1
    c = beam1_clashes[0]
    assert c.penetration_depth == pytest.approx(25.0)
    assert c.penetration_volume == pytest.approx(1100.0)


def test_clash_rule_matrix():
    matrix = ClashRuleMatrix()

    # 规则 1: 结构与暖通必须满足 100mm 净距要求
    matrix.add_rule(
        system_a="Structure",
        system_b="HVAC",
        min_clearance=100.0,
        severity=ClashSeverity.CRITICAL,
        action="Flag",
    )

    # 规则 2: 给排水与给排水同专业接触属于正常接头，予以排除
    matrix.add_exclusion(
        system_a="Plumbing",
        system_b="Plumbing",
        reason="同专业管道连接件正常接触",
    )

    assert matrix.is_excluded("Plumbing", "Plumbing") is True
    assert matrix.is_excluded("Structure", "HVAC") is False
    assert matrix.get_required_clearance("Structure", "HVAC") == 100.0
    assert matrix.get_severity("Structure", "HVAC") == ClashSeverity.CRITICAL
