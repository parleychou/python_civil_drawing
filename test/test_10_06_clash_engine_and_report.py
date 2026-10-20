"""test_10_06_clash_engine_and_report.py — 面向对象原生内置集成、全流程引擎与报表导出测试。"""

import os
import json
import pytest
from point3d import Point3D
from factories import create_box_mesh
from collision import (
    ClashEngine,
    ClashRuleMatrix,
    ClashType,
    ClashSeverity,
)
from clash_report import (
    export_clash_report_csv_excel,
    export_bcf_viewpoint,
)


def test_mesh_data_oop_clash_with():
    # 构造两个相交箱体
    box_a = create_box_mesh(Point3D(0, 0, 0), 100.0, 100.0, 100.0)
    box_a.name = "COLUMN_01"

    box_b = create_box_mesh(Point3D(50, 50, 50), 100.0, 100.0, 100.0)
    box_b.name = "PIPE_01"

    # 调用内置方法
    rec = box_a.clash_with(box_b)
    assert rec is not None
    assert rec.clash_type == ClashType.HARD
    assert rec.object_a_id == "COLUMN_01"
    assert rec.object_b_id == "PIPE_01"
    assert rec.penetration_depth > 0.0

    # 验证 aabb 属性
    aabb = box_a.aabb
    assert aabb.min_x == 0.0
    assert aabb.max_x == 100.0


def test_clash_engine_full_pipeline(tmp_path):
    # 构造三维工程构件场景
    # 1. 结构大梁: X in [0, 6000], Y in [0, 400], Z in [2800, 3400]
    beam_mesh = create_box_mesh(Point3D(0, 0, 2800), 6000.0, 400.0, 600.0)
    beam_mesh.name = "BEAM_MAIN"

    # 2. 暖通空调主风管: X in [2500, 3500], Y in [-500, 2000], Z in [3000, 3300] (穿梁硬碰撞)
    duct_mesh = create_box_mesh(Point3D(2500, -500, 3000), 1000.0, 2500.0, 300.0)
    duct_mesh.name = "DUCT_HVAC"

    # 3. 给排水管道: X in [5000, 5200], Y in [-500, 2000], Z in [2700, 2750] (梁底下方 50mm，未穿梁，属于软碰撞)
    pipe_mesh = create_box_mesh(Point3D(5000, -500, 2700), 200.0, 2500.0, 50.0)
    pipe_mesh.name = "PIPE_PLUMBING"

    # 4. 给排水支管与管道相交: 但同属于 Plumbing 专业，白名单忽略
    branch_mesh = create_box_mesh(Point3D(5050, 1000, 2680), 100.0, 200.0, 90.0)
    branch_mesh.name = "PIPE_BRANCH"

    elements = [
        {"id": "BEAM_MAIN", "mesh": beam_mesh, "system": "Structure"},
        {"id": "DUCT_HVAC", "mesh": duct_mesh, "system": "HVAC"},
        {"id": "PIPE_PLUMBING", "mesh": pipe_mesh, "system": "Plumbing"},
        {"id": "PIPE_BRANCH", "mesh": branch_mesh, "system": "Plumbing"},
    ]

    rules = ClashRuleMatrix()
    # 结构 vs 暖通：硬碰撞检测
    rules.add_rule("Structure", "HVAC", min_clearance=0.0, severity=ClashSeverity.CRITICAL)
    # 结构 vs 给排水：软碰撞安全净距需 100mm (实测 50mm，将触发软碰撞)
    rules.add_rule("Structure", "Plumbing", min_clearance=100.0, severity=ClashSeverity.MAJOR)
    # 给排水内部自管接触白名单豁免
    rules.add_exclusion("Plumbing", "Plumbing")

    engine = ClashEngine(rule_matrix=rules, broad_phase_cell_size=3000.0, cluster_eps=200.0)
    report = engine.run(elements)

    assert report.total_elements_checked == 4
    assert report.confirmed_clashes_count >= 2

    # 验证含有硬碰撞与软碰撞
    clash_types = {c.clash_type for c in report.clashes}
    assert ClashType.HARD in clash_types
    assert ClashType.SOFT in clash_types

    # 导出 CSV 报表测试
    csv_file = str(tmp_path / "clash_report.csv")
    out_csv = export_clash_report_csv_excel(report, csv_file)
    assert os.path.exists(out_csv)
    with open(out_csv, "r", encoding="utf-8-sig") as f:
        content = f.read()
        assert "BEAM_MAIN" in content
        assert "DUCT_HVAC" in content

    # 导出 openBIM BCF 视点测试
    first_clash = report.clashes[0]
    bcf_file = str(tmp_path / "viewpoint.bcfv")
    bcf_dict = export_bcf_viewpoint(first_clash, filepath=bcf_file)

    assert "topic" in bcf_dict
    assert "viewpoint" in bcf_dict
    assert "perspective_camera" in bcf_dict["viewpoint"]
    assert os.path.exists(bcf_file)
    with open(bcf_file, "r", encoding="utf-8") as f:
        loaded = json.load(f)
        assert loaded["topic"]["guid"] == first_clash.clash_id
