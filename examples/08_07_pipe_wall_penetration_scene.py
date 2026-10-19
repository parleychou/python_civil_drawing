"""08_07_pipe_wall_penetration_scene.py — 地下室机电管综穿墙碰撞检测与套管放样报表系统。

演示土木与机电数字化建造综合实战：
1. 建立包含地下室剪力外墙、梁柱体系与多专业综合机电管线（给排水、消防喷淋、暖通风管）的综合场景；
2. 批量执行空间管线穿透实体网格算法，提取管线进墙点、出墙点与实体穿透厚度；
3. 自动生成施工现场亟需的《地下室管综穿墙预留套管放样报表》（含管线编号、专业、标高、穿墙实厚与开洞规格）；
4. 三维视口全真漫游与碰撞部位高亮预警。

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
    Vector3D,
    Line3D,
    create_box_mesh,
    RenderEngine,
    intersect_line_mesh,
    IntersectionType,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="地下室管综穿墙碰撞检测与套管放样报表系统")
    parser.add_argument("--offscreen", action="store_true", help="启用无头渲染模式")
    args = parser.parse_args()

    print("=" * 80)
    print("【案例 08_07 综合实战】地下室机电管综穿墙碰撞检测与套管放样报表系统")
    print("=" * 80)

    # 1. 建立地下室剪力外墙 (厚度 400mm，长 12000mm，高 4000mm，位于 X 轴向 [2800, 3200])
    wall_mesh = create_box_mesh(
        origin=Point3D(2800.0, 0.0, 0.0),
        width=400.0,
        depth=10000.0,
        height=4000.0,
    )

    # 2. 建立多专业穿越管线清单
    pipes = [
        {
            "id": "W-01",
            "name": "DN150生活给水管",
            "system": "给排水",
            "line": Line3D(Point3D(1000.0, 2000.0, 2800.0), Point3D(5000.0, 2000.0, 2800.0)),
            "sleeve_spec": "DN200 刚性防水套管",
            "color": "dodgerblue",
        },
        {
            "id": "F-01",
            "name": "DN100消火栓主干管",
            "system": "消防",
            "line": Line3D(Point3D(1000.0, 4500.0, 3200.0), Point3D(5000.0, 4500.0, 3200.0)),
            "sleeve_spec": "DN150 刚性防水套管",
            "color": "crimson",
        },
        {
            "id": "H-01",
            "name": "800x400排烟风管中心线",
            "system": "暖通",
            "line": Line3D(Point3D(1000.0, 7500.0, 3400.0), Point3D(5000.0, 7500.0, 3400.0)),
            "sleeve_spec": "900x500 预留钢板套管",
            "color": "darkorange",
        },
        {
            "id": "E-01",
            "name": "强电室外平行电缆(未穿墙)",
            "system": "电气",
            "line": Line3D(Point3D(1500.0, 1000.0, 2000.0), Point3D(1500.0, 9000.0, 2000.0)),
            "sleeve_spec": "无",
            "color": "forestgreen",
        },
    ]

    # 3. 批量执行穿墙碰撞检测与报表统计
    penetration_reports = []

    for p in pipes:
        res = intersect_line_mesh(p["line"], wall_mesh)
        if res.has_intersection and len(res.points) >= 2:
            p_in = res.points[0]
            p_out = res.points[1]
            solid_thick = res.parameters.get("solid_thickness", 0.0)
            center_pt = Point3D(
                (p_in.x + p_out.x) * 0.5,
                (p_in.y + p_out.y) * 0.5,
                (p_in.z + p_out.z) * 0.5,
            )
            penetration_reports.append({
                "id": p["id"],
                "name": p["name"],
                "system": p["system"],
                "center": center_pt,
                "thickness": solid_thick,
                "sleeve": p["sleeve_spec"],
            })

    # 4. 打印工程规范套管放样报表
    print(f"\n{'='*30} 地下室剪力墙预留套管深化报表 {'='*30}")
    print(f"{'编号':<6} {'系统':<8} {'管线名称':<20} {'套管中心(X, Y, Z)':<24} {'穿墙厚度':<10} {'推荐预留套管规格':<20}")
    print("-" * 92)
    for r in penetration_reports:
        c_str = f"({r['center'].x:.0f}, {r['center'].y:.0f}, {r['center'].z:.0f})"
        print(f"{r['id']:<6} {r['system']:<8} {r['name']:<20} {c_str:<24} {r['thickness']:<10.1f} {r['sleeve']:<20}")
    print("-" * 92)
    print(f"统计：共排查 {len(pipes)} 路主干管线，检出 {len(penetration_reports)} 处有效穿墙碰撞，已自动编排洞口。\n")

    # 5. 可视化渲染
    engine = RenderEngine(window_size=(1280, 800), off_screen=args.offscreen)

    # 渲染地下室剪力外墙 (半透明混凝土青灰色)
    engine.add_mesh(wall_mesh.to_pyvista(), color="lightgray", opacity=0.35, show_edges=True)

    # 绘制各专业管线
    for p in pipes:
        l = p["line"]
        engine.render_curve([l.start.to_tuple(), l.end.to_tuple()], color=p["color"], line_width=5.0)

    # 在穿墙中心点高亮发光套管预留标记球
    for r in penetration_reports:
        c = r["center"]
        engine.render_point(c.to_tuple(), color="gold", point_size=16, label=f"洞口:{r['id']}")

    print("[SUCCESS] 案例 08_07 运行完成。")
    engine.show()


if __name__ == "__main__":
    main()
