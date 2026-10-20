"""10_07_basement_mep_clash_scene.py — 大型地下室管综与土建全专业碰撞排查实战。

演示内容：
1. 搭建典型地下室车库 2x2 跨综合结构体系 (柱网 8.4m x 8.4m，框架梁、顶板楼板)；
2. 敷设 4 大机电专业管线：
   - 暖通专业 (HVAC): 1200x450 排烟主风管；
   - 给排水专业 (Plumbing): DN150 生活给水主管；
   - 消防专业 (FireProtection): DN100 环状喷淋水管；
   - 电气专业 (Electrical): 600x150 强电电缆桥架；
3. 构建完整土建-机电碰撞规则矩阵 (硬碰撞、软碰撞检修空间、同专业管件免检白名单)；
4. 运行全流程排查调度引擎 (ClashEngine)，完成空间网格哈希、窄阶段精检、DBSCAN 空间聚类收敛与报表生成；
5. 在 PyVista 视口中对全专业进行专业色彩编码：结构半透明灰度、暖通风管高亮蓝、水管绿、桥架黄，红色与洋红色警示球标定冲突工单。

命令行参数：
- --offscreen：无头后台离屏运行模式，用于自动化测试与 CI/CD。
"""

import argparse
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
)
from factories import create_box_mesh
import pyvista as pv


def main():
    parser = argparse.ArgumentParser(description="10_07 地下室全专业管综碰撞排查实战")
    parser.add_argument("--offscreen", action="store_true", help="无头离屏运行")
    args = parser.parse_args()

    print("=" * 70)
    print("【案例 10_07】商业建筑地下室管线综合 (MEP) 与土建结构全流程碰撞排查实操")
    print("=" * 70)

    elements: list[dict] = []

    # 1. 结构专业构件生成 (4 根框架柱 + 4 根主梁 + 顶板)
    col_size = 600.0
    floor_h = 3600.0
    span = 8400.0

    # 4 根柱
    for ix, x in enumerate([0.0, span]):
        for iy, y in enumerate([0.0, span]):
            col = create_box_mesh(Point3D(x, y, 0), col_size, col_size, floor_h)
            col_id = f"COL_{ix}_{iy}"
            col.name = col_id
            elements.append({"id": col_id, "mesh": col, "system": "Structure"})

    # X 向主梁 (截面 400x700, 标高 2900~3600)
    b_x1 = create_box_mesh(Point3D(0, 0, 2900), span + col_size, 400.0, 700.0)
    b_x1.name = "BEAM_X1"
    b_x2 = create_box_mesh(Point3D(0, span, 2900), span + col_size, 400.0, 700.0)
    b_x2.name = "BEAM_X2"
    elements.append({"id": "BEAM_X1", "mesh": b_x1, "system": "Structure"})
    elements.append({"id": "BEAM_X2", "mesh": b_x2, "system": "Structure"})

    # Y 向主梁
    b_y1 = create_box_mesh(Point3D(0, 0, 2900), 400.0, span + col_size, 700.0)
    b_y1.name = "BEAM_Y1"
    b_y2 = create_box_mesh(Point3D(span, 0, 2900), 400.0, span + col_size, 700.0)
    b_y2.name = "BEAM_Y2"
    elements.append({"id": "BEAM_Y1", "mesh": b_y1, "system": "Structure"})
    elements.append({"id": "BEAM_Y2", "mesh": b_y2, "system": "Structure"})

    # 2. 机电管线系统生成
    # (1) 暖通风管: 1200x450 排烟主风管，沿 Y 方向横跨整个车库 (标高 2850~3300，直接与 BEAM_X1 和 BEAM_X2 腹板硬相交)
    hvac_duct = create_box_mesh(Point3D(3500, -1000, 2850), 1200.0, span + 2000.0, 450.0)
    hvac_duct.name = "DUCT_SMOKE_MAIN"
    elements.append({"id": "DUCT_SMOKE_MAIN", "mesh": hvac_duct, "system": "HVAC"})

    # (2) 给排水给水管: DN150，沿 X 向延伸 (高程 2820~2970，穿透 BEAM_Y1，并在空间中与 HVAC 风管立面立体交叉)
    water_pipe = create_box_mesh(Point3D(-1000, 4200, 2820), span + 2000.0, 150.0, 150.0)
    water_pipe.name = "WATER_PIPE_DN150"
    elements.append({"id": "WATER_PIPE_DN150", "mesh": water_pipe, "system": "Plumbing"})

    # (3) 强电桥架: 600x150，沿 X 向敷设 (高程 2700~2850，位于梁底正下方 50mm，未碰撞梁但与梁软碰撞)
    tray = create_box_mesh(Point3D(-1000, 6000, 2750), span + 2000.0, 600.0, 100.0)
    tray.name = "CABLE_TRAY_POWER"
    elements.append({"id": "CABLE_TRAY_POWER", "mesh": tray, "system": "Electrical"})

    # (4) 消防喷淋支管: 与主给水管交叉，测试机电管线间碰撞
    sprinkler = create_box_mesh(Point3D(3800, 3000, 2830), 100.0, 2500.0, 100.0)
    sprinkler.name = "FIRE_SPRINKLER_LINE"
    elements.append({"id": "FIRE_SPRINKLER_LINE", "mesh": sprinkler, "system": "FireProtection"})

    # 3. 规划专业间碰撞规则矩阵
    rules = ClashRuleMatrix()
    # 结构 vs 暖通: 0 容差硬相交
    rules.add_rule("Structure", "HVAC", min_clearance=0.0, severity=ClashSeverity.CRITICAL)
    # 结构 vs 给排水: 必须预留结构套管，硬相交
    rules.add_rule("Structure", "Plumbing", min_clearance=0.0, severity=ClashSeverity.CRITICAL)
    # 结构 vs 电气: 梁底与桥架需至少保留 100mm 检修吊架净距 (软碰撞)
    rules.add_rule("Structure", "Electrical", min_clearance=100.0, severity=ClashSeverity.MAJOR)
    # 机电管线互穿: 暖通风管与消防水管不可重叠
    rules.add_rule("HVAC", "FireProtection", min_clearance=50.0, severity=ClashSeverity.CRITICAL)
    # 结构内部柱梁相交豁免白名单
    rules.add_exclusion("Structure", "Structure")

    # 4. 执行调度引擎
    engine = ClashEngine(rule_matrix=rules, broad_phase_cell_size=4000.0, cluster_eps=300.0)
    report = engine.run(elements)

    print(f"\n[管综排查统计总报表]")
    print(f"-> 参与受检构件数: {report.total_elements_checked}")
    print(f"-> 空间初筛候选对数: {report.candidate_pairs_screened}")
    print(f"-> 确诊工程冲突工单: {report.confirmed_clashes_count}")
    print(f"-> 耗时: {report.execution_time_ms:.2f} ms")

    print(f"\n[明细工单清单]")
    for i, c in enumerate(report.clashes, start=1):
        print(f"  {i}. [{c.clash_type.value}][{c.severity.value}] {c.object_a_id} <--> {c.object_b_id}")
        print(f"     位置: ({c.location.x:.0f}, {c.location.y:.0f}, {c.location.z:.0f}), 侵入/净距: {c.penetration_depth:.1f}mm / {c.clearance:.1f}mm")
        print(f"     处理: {c.recommendation}")

    # 导出交付报表
    export_clash_report_csv_excel(report, "basement_clash_report.csv")
    print(f"\n-> 全专业碰撞排查电子报表已生成: basement_clash_report.csv")

    # 5. 三维场景可视化渲染
    render_eng = RenderEngine(off_screen=args.offscreen)

    # 渲染土建构件 (半透明冷灰)
    for elem in elements:
        sys_name = elem["system"]
        m = elem["mesh"]
        if sys_name == "Structure":
            render_eng.render_mesh(m, color="lightslategray", opacity=0.45)
        elif sys_name == "HVAC":
            render_eng.render_mesh(m, color="royalblue", opacity=0.85)
        elif sys_name == "Plumbing":
            render_eng.render_mesh(m, color="forestgreen", opacity=0.9)
        elif sys_name == "Electrical":
            render_eng.render_mesh(m, color="goldenrod", opacity=0.85)
        elif sys_name == "FireProtection":
            render_eng.render_mesh(m, color="crimson", opacity=0.95)

    # 标定碰撞冲突点工单
    for c in report.clashes:
        marker = pv.Sphere(radius=150.0, center=(c.location.x, c.location.y, c.location.z))
        color = "red" if c.clash_type == ClashType.HARD else "orange"
        render_eng.plotter.add_mesh(marker, color=color, opacity=0.9)

    if args.offscreen:
        render_eng.plotter.screenshot("output_10_07.png")
        render_eng.plotter.close()
    else:
        render_eng.show()

    print("[SUCCESS] 案例 10_07 运行完成。")


if __name__ == "__main__":
    main()
