"""07_04_point_and_vector_projection.py — 点与向量到基准面与斜平面的正交投影。

教学核心：
1. 掌握空间点到平面垂直垂足 (Foot of Perpendicular) 的解析解算；
2. 掌握投影射线 (Projection Rays) 与垂线距离 (Signed Distance) 的几何意义；
3. 同屏展示水平地面与 45° 倾斜工作面上的投影落点分布。
"""

import argparse
import math
import sys
from pathlib import Path
import pyvista as pv

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src import (
    Point3D,
    Vector3D,
    Plane3D,
    Line3D,
    ProjectionEngine,
    RenderEngine,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="演示点与向量正交投影")
    parser.add_argument("--offscreen", action="store_true", help="启用无头渲染模式")
    args = parser.parse_args()

    # 1. 空间测试点集（模拟空间钢架关键节点）
    nodes = [
        Point3D(500.0, 500.0, 1200.0, name="Node_A"),
        Point3D(1500.0, 800.0, 1600.0, name="Node_B"),
        Point3D(1000.0, 1800.0, 1400.0, name="Node_C"),
        Point3D(2000.0, 1600.0, 1800.0, name="Node_D"),
    ]

    # 2. 定义投影目标平面：
    # (a) 水平地面基准面 (XY Plane at Z=0)
    ground_plane = Plane3D(center=Point3D(1250.0, 1250.0, 0.0), normal=Vector3D(0.0, 0.0, 1.0), size=2500.0)

    # (b) 45° 倾斜屋面 (过 (1250, 1250, 600)，法向 (0, -1, 1)/sqrt(2))
    inclined_norm = Vector3D(0.0, -1.0, 1.0).normalized()
    slope_plane = Plane3D(center=Point3D(1250.0, 1250.0, 600.0), normal=inclined_norm, size=2200.0)

    # 3. 调用点内置的 project_to_plane_with_distance 计算地面与斜面投影及垂距
    ground_projections = [pt.project_to_plane_with_distance(ground_plane) for pt in nodes]
    slope_projections = [pt.project_to_plane_with_distance(slope_plane) for pt in nodes]

    # 4. 渲染
    engine = RenderEngine(window_size=(1280, 800), off_screen=args.offscreen)

    # 渲染平面
    engine.add_mesh(ground_plane.to_pyvista(), color="lightgray", opacity=0.45, show_edges=True)
    engine.add_mesh(slope_plane.to_pyvista(), color="wheat", opacity=0.55, show_edges=True)

    # 渲染空间原点与投影点
    for pt in nodes:
        engine.plotter.add_mesh(pv.Sphere(radius=40.0, center=pt.to_tuple()), color="crimson")

    # 渲染地面投影点与虚线垂线
    for (orig_pt, (proj_pt, dist)) in zip(nodes, ground_projections):
        engine.plotter.add_mesh(pv.Sphere(radius=30.0, center=proj_pt.to_tuple()), color="steelblue")
        # 垂线
        drop_line = pv.Line(orig_pt.to_tuple(), proj_pt.to_tuple())
        engine.plotter.add_mesh(drop_line, color="royalblue", line_width=2)

    # 渲染斜面投影点与虚线垂线
    for (orig_pt, (proj_pt, dist)) in zip(nodes, slope_projections):
        engine.plotter.add_mesh(pv.Sphere(radius=30.0, center=proj_pt.to_tuple()), color="darkgreen")
        # 垂线
        drop_line = pv.Line(orig_pt.to_tuple(), proj_pt.to_tuple())
        engine.plotter.add_mesh(drop_line, color="seagreen", line_width=2)

    # 标注文字
    labels_pos = [p.to_tuple() for p in nodes]
    labels_text = [f"{p.name} ({p.x:.0f},{p.y:.0f},{p.z:.0f})" for p in nodes]
    engine.plotter.add_point_labels(
        labels_pos,
        labels_text,
        font_size=11,
        point_color="red",
        text_color="black",
        shadow=False,
    )

    if not args.offscreen:
        print("展示点到基准面与斜平面正交投影视口...")
        engine.plotter.show()
    else:
        print("离线模式：点与投影算法执行成功。")


if __name__ == "__main__":
    main()
