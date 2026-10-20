"""10_06_bcf_and_excel_report_generator.py — 结构化 Excel 报表与 openBIM BCF 3.0 视点包导出。

演示内容：
1. 建立包含框架柱、结构梁、消防主干管、强电桥架的多专业冲突场景；
2. 配置专业碰撞规则矩阵 (ClashRuleMatrix) 与安全净距控制；
3. 执行全流程排查，生成包含硬碰撞、软碰撞与白名单豁免的 ClashReport；
4. 导出符合工程交付标准的 CSV 结构化电子报表 (UTF-8-SIG 兼容 Excel 直接双击打开)；
5. 导出 openBIM BCF (BIM Collaboration Format) 3.0 视点标记包，包含透视相机视角、选中构件 GUID、高亮色标与整改建议；
6. 使用 RenderEngine 将视点相机位置与受检构件进行直观视口呈现。

命令行参数：
- --offscreen：无头后台离屏运行模式，用于自动化测试与 CI/CD。
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Ensure root is in sys.path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src import (
    Point3D,
    MeshData,
    RenderEngine,
    ClashEngine,
    ClashRuleMatrix,
    ClashSeverity,
    ClashType,
    export_clash_report_csv_excel,
    export_bcf_viewpoint,
)
from factories import create_box_mesh
import pyvista as pv


def main():
    parser = argparse.ArgumentParser(description="10_06 结构化报表与 BCF 3.0 导出器")
    parser.add_argument("--offscreen", action="store_true", help="无头离屏运行")
    args = parser.parse_args()

    print("=" * 70)
    print("【案例 10_06】结构化工程报表与 openBIM BCF 3.0 视点标注包交付")
    print("=" * 70)

    # 1. 建立多专业构件
    col_mesh = create_box_mesh(Point3D(0, 0, 0), 600.0, 600.0, 3600.0)
    col_mesh.name = "COLUMN_C1"

    beam_mesh = create_box_mesh(Point3D(0, 0, 3000), 5000.0, 400.0, 600.0)
    beam_mesh.name = "BEAM_B1"

    # 消防喷淋水管 (穿梁硬碰撞)
    fire_pipe_mesh = create_box_mesh(Point3D(2200, -500, 3200), 150.0, 2000.0, 150.0)
    fire_pipe_mesh.name = "FIRE_PIPE_01"

    # 强电桥架 (梁底下方 30mm，软碰撞)
    cable_tray_mesh = create_box_mesh(Point3D(3500, -500, 2870), 400.0, 2000.0, 100.0)
    cable_tray_mesh.name = "ELEC_TRAY_01"

    elements = [
        {"id": "COLUMN_C1", "mesh": col_mesh, "system": "Structure"},
        {"id": "BEAM_B1", "mesh": beam_mesh, "system": "Structure"},
        {"id": "FIRE_PIPE_01", "mesh": fire_pipe_mesh, "system": "FireProtection"},
        {"id": "ELEC_TRAY_01", "mesh": cable_tray_mesh, "system": "Electrical"},
    ]

    # 2. 建立规则矩阵
    rules = ClashRuleMatrix()
    rules.add_rule("Structure", "FireProtection", min_clearance=0.0, severity=ClashSeverity.CRITICAL)
    rules.add_rule("Structure", "Electrical", min_clearance=80.0, severity=ClashSeverity.MAJOR)
    # 柱梁相交属于正常节点连接，设置同专业白名单
    rules.add_exclusion("Structure", "Structure")

    # 3. 运行调度引擎
    engine = ClashEngine(rule_matrix=rules, broad_phase_cell_size=2000.0, cluster_eps=100.0)
    report = engine.run(elements)

    print(f"-> 检查构件总数: {report.total_elements_checked}")
    print(f"-> 粗筛候选对数: {report.candidate_pairs_screened}")
    print(f"-> 确诊冲突总数: {report.confirmed_clashes_count}")
    print(f"-> 引擎执行耗时: {report.execution_time_ms:.2f} ms")

    # 4. 导出 CSV 电子报表
    csv_path = "output_clash_report.csv"
    export_clash_report_csv_excel(report, csv_path)
    print(f"\n-> [1] 结构化工程报表已导出: {os.path.abspath(csv_path)}")

    # 5. 导出 openBIM BCF 3.0 视点标注包
    bcf_files = []
    for i, clash in enumerate(report.clashes):
        bcf_filename = f"viewpoint_{clash.object_a_id}_{clash.object_b_id}.bcfv"
        export_bcf_viewpoint(clash, filepath=bcf_filename)
        bcf_files.append(bcf_filename)
        print(f"-> [2] openBIM BCF 3.0 视点文件已生成: {bcf_filename}")

    # 读取并打印第一个 BCF 的核心字段
    if bcf_files:
        with open(bcf_files[0], "r", encoding="utf-8") as f:
            bcf_sample = json.load(f)
            print("\n--- [BCF 3.0 交付元数据摘要] ---")
            print(f"GUID: {bcf_sample['topic']['guid']}")
            print(f"标题: {bcf_sample['topic']['title']}")
            print(f"透视相机视点: {bcf_sample['viewpoint']['perspective_camera']['camera_view_point']}")
            print(f"高亮构件 GUID: {bcf_sample['components']['selection']}")

    # 6. 可视化渲染
    render_eng = RenderEngine(off_screen=args.offscreen)

    render_eng.render_mesh(col_mesh, color="gray", opacity=0.7)
    render_eng.render_mesh(beam_mesh, color="darkgray", opacity=0.7)
    render_eng.render_mesh(fire_pipe_mesh, color="crimson", opacity=0.9)
    render_eng.render_mesh(cable_tray_mesh, color="gold", opacity=0.9)

    # 渲染冲突点标记球
    for c in report.clashes:
        marker = pv.Sphere(radius=80.0, center=(c.location.x, c.location.y, c.location.z))
        render_eng.plotter.add_mesh(marker, color="red" if c.clash_type == ClashType.HARD else "orange")

    if args.offscreen:
        render_eng.plotter.screenshot("output_10_06.png")
        render_eng.plotter.close()
    else:
        render_eng.show()

    print("[SUCCESS] 案例 10_06 运行完成。")


if __name__ == "__main__":
    main()
