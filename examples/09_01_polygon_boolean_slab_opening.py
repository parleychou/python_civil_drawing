"""09_01_polygon_boolean_slab_opening.py — 2D 楼板电梯井与管井多边形布尔裁剪。

演示土木工程结构平面布置中的多边形布尔运算：
1. 建立一块 24m x 18m 的预应力混凝土大底板多边形；
2. 建立剪力墙核心筒电梯井开洞 (4m x 3m) 与设备管井 (2m x 1.5m)；
3. 执行多边形差集 (Cut) 运算，准确计算开洞后净面积与剩余面积；
4. 将开洞多边形拉伸为 3D 楼板实体并进行 PyVista 交互渲染。

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
    Polygon2D,
    RenderEngine,
)
import pyvista as pv


def main():
    parser = argparse.ArgumentParser(description="09_01 楼板电梯井多边形布尔开洞")
    parser.add_argument("--offscreen", action="store_true", help="无头离屏运行")
    args = parser.parse_args()

    print("=" * 70)
    print("【案例 09_01】2D 楼板多边形电梯井、设备管井布尔开洞分析")
    print("=" * 70)

    # 1. 建立主楼板多边形 24m x 18m
    slab = Polygon2D([(0.0, 0.0), (24.0, 0.0), (24.0, 18.0), (0.0, 18.0)])
    orig_area = slab.area()
    print(f"-> 原始大楼板面积: {orig_area:.2f} m²")

    # 2. 建立核心筒电梯井开洞 (8m~12m, 7m~11m) 面积 = 4 * 4 = 16
    elevator_hole = Polygon2D([(8.0, 7.0), (12.0, 7.0), (12.0, 11.0), (8.0, 11.0)])
    # 建立机电管井开洞 (16m~18m, 12m~14m) 面积 = 2 * 2 = 4
    pipe_hole = Polygon2D([(16.0, 12.0), (18.0, 12.0), (18.0, 14.0), (16.0, 14.0)])

    # 3. 连续执行布尔差集
    step1 = slab.difference(elevator_hole)
    assert len(step1) >= 1
    opened_slab = step1[0].difference(pipe_hole)
    assert len(opened_slab) >= 1
    final_slab = opened_slab[0]

    net_area = final_slab.area()
    expected_net = orig_area - elevator_hole.area() - pipe_hole.area()
    print(f"-> 电梯井洞口面积: {elevator_hole.area():.2f} m²")
    print(f"-> 机电管井洞口面积: {pipe_hole.area():.2f} m²")
    print(f"-> 开洞后实测净面积: {net_area:.2f} m² (理论理论值: {expected_net:.2f} m²)")

    # 4. 可视化渲染
    engine = RenderEngine(off_screen=args.offscreen)
    # 渲染多边形边界
    for poly in [final_slab]:
        pts_3d = [Point3D(p[0], p[1], 0.0) for p in poly.vertices]
        pts_3d.append(pts_3d[0])
        engine.render_curve([p.to_tuple() for p in pts_3d], color="blue", line_width=4.0)
        for hole in poly.holes:
            h_pts = [Point3D(p[0], p[1], 0.0) for p in hole]
            h_pts.append(h_pts[0])
            engine.render_curve([p.to_tuple() for p in h_pts], color="red", line_width=4.0)

    if args.offscreen:
        engine.plotter.screenshot("output_09_01.png")
        engine.plotter.close()
    else:
        engine.show()

    print("[SUCCESS] 案例 09_01 运行完成。")


if __name__ == "__main__":
    main()
