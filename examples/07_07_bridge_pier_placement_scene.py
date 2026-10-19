"""07_07_bridge_pier_placement_scene.py — 沿曲线桥梁轴线参数化批量变换放置桥墩与总平面图投影综合场景。

综合实战亮点：
1. 空间曲线参数化轴线：模拟一座平曲线 + 纵断面竖曲线的高架立交桥梁；
2. 批量 4x4 变换矩阵生成：沿曲线等距计算切线与法向，为每个墩位构建局部坐标系 CS_i；
3. 参数化构件自适应放置：根据桥面标高动态调整桥墩高度，通过 M_i 矩阵精确就位；
4. 全桥工程总平面图投影：将整座高架桥梁（梁段、桥墩、中心线）一键正交投影至地面 Z = 0，生成总平面图。
"""

import argparse
import math
import sys
from pathlib import Path
import numpy as np
import pyvista as pv

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src import (
    Point3D,
    Vector3D,
    CoordinateSystem3D,
    Plane3D,
    TransformMatrix,
    create_bridge_pier_brep,
    create_box_brep,
    ProjectionEngine,
    RenderEngine,
)


def bridge_centerline(t: float) -> tuple[float, float, float]:
    """桥梁中心线参数方程 (单位 mm): X = t, Y = 弯曲, Z = 纵坡标高"""
    x = t
    y = 1200.0 * math.sin(t / 2500.0)
    z = 2500.0 + 600.0 * math.sin(t / 3500.0)
    return x, y, z


def bridge_tangent(t: float) -> Vector3D:
    """计算中心线在参数 t 处的切线方向向量"""
    dt = 1.0
    x0, y0, z0 = bridge_centerline(t)
    x1, y1, z1 = bridge_centerline(t + dt)
    return Vector3D(x1 - x0, y1 - y0, z1 - z0).normalized()


def main() -> None:
    parser = argparse.ArgumentParser(description="综合实战：曲线桥梁多墩位变换放置与投影")
    parser.add_argument("--offscreen", action="store_true", help="启用无头渲染模式")
    args = parser.parse_args()

    # 1. 沿全桥长度 (0 到 10000mm) 采集中心线点列用于渲染
    t_samples = np.linspace(0.0, 10000.0, 100)
    curve_pts = [bridge_centerline(t) for t in t_samples]
    curve_poly = pv.PolyData(curve_pts)
    curve_poly.lines = [len(curve_pts)] + list(range(len(curve_pts)))

    # 2. 选取 5 个墩位桩号参数 t
    pier_stations = [1000.0, 3000.0, 5000.0, 7000.0, 9000.0]

    placed_piers = []
    placed_cs_list = []

    # 3. 循环计算每个墩位的局部坐标系，并放置桥墩
    for i, t in enumerate(pier_stations):
        cx, cy, cz = bridge_centerline(t)
        pier_height = cz  # 墩高从地面 Z=0 到桥面底 Z=cz

        # 切向切向量作为局部 X 方向 (纵桥向)
        tangent = bridge_tangent(t)
        # 横桥向法向量 (水平面上与切线垂直)
        normal = Vector3D(-tangent.y, tangent.x, 0.0).normalized()
        # 竖向 Z 方向
        up = normal.cross(tangent).normalized()

        # 建立墩位局部坐标系 (原点置于地面 Z=0 处)
        origin_pt = Point3D(cx, cy, 0.0)
        cs_pier = CoordinateSystem3D(
            origin=origin_pt,
            x_axis=normal,    # 桥墩横向对应局部法向
            y_axis=tangent,   # 桥墩纵向对应桥梁切向
            z_axis=Vector3D(0.0, 0.0, 1.0),  # 桥墩竖直向上
            axis_length=800.0,
            name=f"Pier_CS_{i+1}",
        )
        placed_cs_list.append(cs_pier)

        # 基础变截面桥墩
        base_pier = create_bridge_pier_brep(
            height=pier_height,
            top_width=1200.0,
            top_depth=800.0,
            bottom_width=1800.0,
            bottom_depth=1200.0,
        )

        # 变换矩阵
        m_pier = TransformMatrix.from_coordinate_systems(cs_pier)
        placed_pier = base_pier.transform(m_pier)
        placed_piers.append(placed_pier)

    # 4. 创建桥面简支箱梁模型段并放置在各跨
    placed_girders = []
    for i in range(len(pier_stations) - 1):
        t0 = pier_stations[i]
        t1 = pier_stations[i + 1]
        mid_t = (t0 + t1) / 2.0
        mx, my, mz = bridge_centerline(mid_t)
        tangent = bridge_tangent(mid_t)
        normal = Vector3D(-tangent.y, tangent.x, 0.0).normalized()
        span_len = math.sqrt((t1 - t0)**2 + 1000**2)

        # 构造跨越箱梁 (长 span_len, 宽 1600, 高 400)
        box = create_box_brep(width=span_len * 0.95, depth=1400.0, height=350.0)
        # 居中平移到原点
        t_center = TransformMatrix.translation(-span_len * 0.95 / 2.0, -700.0, 0.0)
        cs_girder = CoordinateSystem3D(
            origin=Point3D(mx, my, mz),
            x_axis=tangent,
            y_axis=normal,
            z_axis=Vector3D(0.0, 0.0, 1.0),
        )
        m_girder = TransformMatrix.from_coordinate_systems(cs_girder) @ t_center
        placed_girders.append(box.transform(m_girder))

    # 5. 总平面图投影 (调用构件与点内置的 project_to_plane 投影到 Z = -500 地平面)
    proj_plane = Plane3D(center=Point3D(5000.0, 0.0, -500.0), normal=Vector3D(0.0, 0.0, 1.0), size=12000.0)
    proj_piers = [p.project_to_plane(proj_plane) for p in placed_piers]
    proj_girders = [g.project_to_plane(proj_plane) for g in placed_girders]

    # 投影中心线
    proj_curve_pts = [Point3D(p[0], p[1], p[2]).project_to_plane(proj_plane).to_tuple() for p in curve_pts]
    proj_curve_poly = pv.PolyData(proj_curve_pts)
    proj_curve_poly.lines = [len(proj_curve_pts)] + list(range(len(proj_curve_pts)))

    # 6. 渲染
    engine = RenderEngine(window_size=(1280, 800), off_screen=args.offscreen)

    # 地面投影板
    engine.add_mesh(proj_plane.to_pyvista(), color="whitesmoke", opacity=0.4, show_edges=True)

    # 渲染三维中心线 (金色)
    engine.plotter.add_mesh(curve_poly, color="gold", line_width=4, label="Bridge Centerline")

    # 渲染各墩柱
    for p in placed_piers:
        engine.add_mesh(p.to_pyvista(), color="slategray", opacity=0.9)
        engine.plotter.add_mesh(p.get_edges_polydata(), color="black", line_width=2)

    # 渲染各主梁段
    for g in placed_girders:
        engine.add_mesh(g.to_pyvista(), color="lightblue", opacity=0.85)
        engine.plotter.add_mesh(g.get_edges_polydata(), color="steelblue", line_width=2)

    # 渲染墩位局部坐标系
    for cs in placed_cs_list:
        cs.render(engine)

    # 渲染投影平面图
    engine.plotter.add_mesh(proj_curve_poly, color="darkorange", line_width=2)
    for pp in proj_piers:
        engine.add_mesh(pp.to_pyvista(), color="coral", opacity=0.7)
        engine.plotter.add_mesh(pp.get_edges_polydata(), color="darkred", line_width=2)
    for pg in proj_girders:
        engine.add_mesh(pg.to_pyvista(), color="lightgray", opacity=0.5)
        engine.plotter.add_mesh(pg.get_edges_polydata(), color="dimgray", line_width=1)

    # 标注文字
    engine.plotter.add_point_labels(
        [
            (5000.0, 1000.0, 4000.0),
            (5000.0, 0.0, -600.0),
        ],
        [
            "3D Curved Bridge with 5 Adaptive Piers",
            "Site Layout Plan (Projected at Z = -500)",
        ],
        font_size=13,
        point_color="black",
        text_color="black",
        shadow=False,
    )

    if not args.offscreen:
        print("展示曲线桥梁多墩位变换放置与全桥投影视口...")
        engine.plotter.show()
    else:
        print("离线模式：大型曲线桥梁实战场景执行通过。")


if __name__ == "__main__":
    main()
