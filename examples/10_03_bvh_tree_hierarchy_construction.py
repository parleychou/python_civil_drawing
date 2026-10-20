"""10_03_bvh_tree_hierarchy_construction.py — 层次包围盒树 (BVH) 构建与树-树递归剪枝。

演示内容：
1. 建立多跨双层结构梁系与空间穿越管线网；
2. 构建结构系统与机电系统的自顶向下平衡 BVH 层次包围盒树；
3. 执行树-树双向递归剪枝求交 (Tree-Tree Intersection)，观察层级剪枝过程；
4. 模拟三维激光扫描/施工放样视线射线求交拾取 (Ray Casting)；
5. 可视化渲染：展示二叉树不同层级的包围盒包络与被穿透构件。

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
    MeshData,
    RenderEngine,
    AABB,
    BVHTree,
)
from factories import create_box_mesh
import pyvista as pv


def main():
    parser = argparse.ArgumentParser(description="10_03 BVH 层次包围盒树构建与剪枝")
    parser.add_argument("--offscreen", action="store_true", help="无头离屏运行")
    args = parser.parse_args()

    print("=" * 70)
    print("【案例 10_03】层次包围盒树 (BVH Tree) 二叉划分与空间剪枝求交")
    print("=" * 70)

    # 1. 建立结构梁系统 (双跨框架梁)
    beams_data = [
        ("BEAM_1F_1", create_box_mesh(Point3D(0, 0, 3000), 6000.0, 400.0, 600.0)),
        ("BEAM_1F_2", create_box_mesh(Point3D(0, 4000, 3000), 6000.0, 400.0, 600.0)),
        ("BEAM_2F_1", create_box_mesh(Point3D(0, 0, 6600), 6000.0, 400.0, 600.0)),
        ("BEAM_2F_2", create_box_mesh(Point3D(0, 4000, 6600), 6000.0, 400.0, 600.0)),
    ]

    # 2. 建立机电管线系统 (斜穿主管与水平分支管)
    pipes_data = [
        # P1: 贯通 1 层穿透梁 BEAM_1F_1 与 BEAM_1F_2
        ("PIPE_MAIN_1F", create_box_mesh(Point3D(3000, -1000, 3200), 300.0, 6000.0, 200.0)),
        # P2: 2 层孤立排气管，不发生碰撞
        ("PIPE_EXHAUST_2F", create_box_mesh(Point3D(3000, 2000, 7500), 200.0, 1000.0, 200.0)),
    ]

    # 3. 自顶向下构建平衡 BVH 树
    beam_boxes = [(name, AABB.from_mesh(mesh)) for name, mesh in beams_data]
    pipe_boxes = [(name, AABB.from_mesh(mesh)) for name, mesh in pipes_data]

    bvh_beams = BVHTree.build_top_down(beam_boxes)
    bvh_pipes = BVHTree.build_top_down(pipe_boxes)

    print("-> 结构系统 BVH 树与机电系统 BVH 树自顶向下平衡划分完成。")
    print(f"-> 结构树总包围盒体积: {bvh_beams.root.aabb.volume / 1e9:.2f} m³")
    print(f"-> 管线树总包围盒体积: {bvh_pipes.root.aabb.volume / 1e9:.2f} m³")

    # 4. 执行树-树递归剪枝相交测试
    clashes = bvh_beams.intersect_tree(bvh_pipes)
    print(f"\n-> 树-树遍历检测完成，命中冲突对: {len(clashes)} 组:")
    for a, b in sorted(clashes):
        print(f"   [!] 冲突预警: {a} <---> {b}")

    # 5. 模拟空间射线扫描检测 (Ray Casting)
    # 模拟从测量站发射激光测距射线
    laser_origin = Point3D(3150, -2000, 3300)
    laser_direction = Vector3D(0.0, 1.0, 0.0)  # 沿 +Y 轴直射
    hit_objects = bvh_beams.ray_cast(laser_origin, laser_direction)
    print(f"\n-> 空间射线拾取测试 (Ray-AABB Kay-Kajiya):")
    print(f"   射线源: ({laser_origin.x}, {laser_origin.y}, {laser_origin.z}), 方向: +Y")
    print(f"   拾取命中构件序列: {hit_objects}")

    # 6. 可视化渲染
    engine = RenderEngine(off_screen=args.offscreen)

    # 渲染梁系
    for name, mesh in beams_data:
        engine.render_mesh(mesh, color="slategray", opacity=0.7)

    # 渲染管道
    for name, mesh in pipes_data:
        color = "red" if any(name in pair for pair in clashes) else "royalblue"
        engine.render_mesh(mesh, color=color, opacity=0.9)

    # 渲染 BVH 根节点包络线框 (黄色虚线框)
    root_box = pv.Box(bounds=(
        bvh_beams.root.aabb.min_x, bvh_beams.root.aabb.max_x,
        bvh_beams.root.aabb.min_y, bvh_beams.root.aabb.max_y,
        bvh_beams.root.aabb.min_z, bvh_beams.root.aabb.max_z,
    ))
    engine.plotter.add_mesh(root_box.outline(), color="gold", line_width=2.0)

    # 渲染射线
    engine.render_curve([(3150, -2000, 3300), (3150, 6000, 3300)], color="chartreuse", line_width=3.0)

    if args.offscreen:
        engine.plotter.screenshot("output_10_03.png")
        engine.plotter.close()
    else:
        engine.show()

    print("[SUCCESS] 案例 10_03 运行完成。")


if __name__ == "__main__":
    main()
