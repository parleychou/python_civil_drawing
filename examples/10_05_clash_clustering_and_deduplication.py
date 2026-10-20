"""10_05_clash_clustering_and_deduplication.py — DBSCAN 空间聚类与同源碰撞工单收敛。

演示内容：
1. 模拟一根主干管道连续穿透波纹腹板或双层剪力墙构造，在离散三角面求交时产生 30 余处密集的相交点；
2. 若直接输出报表，会导致施工现场收到海量碎片化工单，产生“告警风暴”；
3. 运行 DBSCAN 三维空间密度聚类算法 (eps=300mm)，将同源接触散点精确聚类收敛为 1 处高聚合的结构化工程开洞工单；
4. 计算聚类簇的质心坐标、最大侵入深度与累积穿透体积；
5. 可视化渲染：展示密集散点云与聚类收敛后的高亮开洞建议外框。

命令行参数：
- --offscreen：无头后台离屏运行模式，用于自动化测试与 CI/CD。
"""

import argparse
import random
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
    ClashRecord,
    ClashType,
    ClashSeverity,
    cluster_clash_points_dbscan,
    cluster_clash_records,
)
from factories import create_box_mesh
import pyvista as pv


def main():
    parser = argparse.ArgumentParser(description="10_05 DBSCAN 空间聚类与同源碰撞去重")
    parser.add_argument("--offscreen", action="store_true", help="无头离屏运行")
    args = parser.parse_args()

    print("=" * 70)
    print("【案例 10_05】DBSCAN 空间密度聚类收敛：消除碎片化碰撞告警风暴")
    print("=" * 70)

    # 固定随机种子
    random.seed(105)

    # 1. 建立剪力墙与穿墙管道
    wall_mesh = create_box_mesh(Point3D(0, 0, 0), 400.0, 4000.0, 3000.0)
    wall_mesh.name = "SHEAR_WALL"

    pipe_mesh = create_box_mesh(Point3D(-500, 1800, 1400), 1400.0, 300.0, 300.0)
    pipe_mesh.name = "PENETRATING_PIPE"

    # 2. 模拟底层三角面网格求交产生的密集相交点 (产生 35 处微观交点)
    raw_clashes: list[ClashRecord] = []
    print("-> 正在生成管壁与墙体离散相交点集...")
    for i in range(35):
        # 散布在穿墙区域 X in [0, 400], Y in [1800, 2100], Z in [1400, 1700]
        px = random.uniform(50.0, 350.0)
        py = random.uniform(1820.0, 2080.0)
        pz = random.uniform(1420.0, 1680.0)
        rec = ClashRecord(
            clash_id=f"RAW_CLASH_{i:03d}",
            clash_type=ClashType.HARD,
            severity=ClashSeverity.CRITICAL,
            object_a_id="SHEAR_WALL",
            object_b_id="PENETRATING_PIPE",
            location=Point3D(px, py, pz),
            clearance=0.0,
            penetration_depth=random.uniform(250.0, 300.0),
            penetration_volume=random.uniform(50000.0, 80000.0),
            system_a="Structure",
            system_b="HVAC",
        )
        raw_clashes.append(rec)

    print(f"-> 原始底层相交散点数量: {len(raw_clashes)} 处")
    print("   [警告] 若直接输出，现场工程师将面临 35 份重复的穿墙开洞整改单！")

    # 3. 运行 DBSCAN 空间聚类收敛
    eps_cluster = 350.0  # 聚类邻域半径 350mm
    merged_clashes = cluster_clash_records(raw_clashes, eps=eps_cluster)

    print(f"\n-> 执行 DBSCAN 空间密度聚类收敛 (ε = {eps_cluster} mm)...")
    print(f"-> 成功收敛为: 【{len(merged_clashes)} 处】结构化综合开洞工单！(工单降噪压缩比: {(1.0 - len(merged_clashes)/len(raw_clashes))*100:.1f}%)")

    final_order = merged_clashes[0]
    print(f"-> 推荐工单编号: {final_order.clash_id}")
    print(f"-> 开洞质心坐标: ({final_order.location.x:.1f}, {final_order.location.y:.1f}, {final_order.location.z:.1f})")
    print(f"-> 最大穿透深度: {final_order.penetration_depth:.1f} mm")
    print(f"-> 累计侵入体积: {final_order.penetration_volume / 1e6:.3f} L")
    print(f"-> 整改建议: {final_order.recommendation}")

    # 4. 可视化渲染
    engine = RenderEngine(off_screen=args.offscreen)

    # 渲染剪力墙与管道
    engine.render_mesh(wall_mesh, color="silver", opacity=0.6)
    engine.render_mesh(pipe_mesh, color="royalblue", opacity=0.8)

    # 渲染原始相交散点 (黄色小点云)
    raw_pts_pv = pv.PolyData([[r.location.x, r.location.y, r.location.z] for r in raw_clashes])
    engine.plotter.add_mesh(raw_pts_pv, color="gold", point_size=8.0, render_points_as_spheres=True)

    # 渲染 DBSCAN 聚类收敛后的开洞推荐区域 (红色立方体外框)
    hole_box = pv.Box(bounds=(-50, 450, 1750, 2150, 1350, 1750))
    engine.plotter.add_mesh(hole_box.outline(), color="red", line_width=4.0)

    # 渲染质心指示球
    centroid_pv = pv.Sphere(radius=40.0, center=(final_order.location.x, final_order.location.y, final_order.location.z))
    engine.plotter.add_mesh(centroid_pv, color="crimson")

    if args.offscreen:
        engine.plotter.screenshot("output_10_05.png")
        engine.plotter.close()
    else:
        engine.show()

    print("[SUCCESS] 案例 10_05 运行完成。")


if __name__ == "__main__":
    main()
