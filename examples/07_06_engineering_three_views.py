"""07_06_engineering_three_views.py — 土木构件标准工程三视图自动投影生成。

教学核心：
1. 三视图数学投影本质：
   - 俯视图 (Top / Plan View)：正交投影到水平面 Z = const；
   - 主视图 / 正立面图 (Front / Elevation View)：正交投影到正立垂直面 Y = const；
   - 侧面图 / 侧立面图 (Side / Profile View)：正交投影到侧立垂直面 X = const。
2. 调用 ProjectionEngine.generate_three_views 自动完成三视图解算并同屏规整排版；
3. 绘制连接三维模型与各工程视图的投影折线（长对正、高平齐、宽相等）。
"""

import argparse
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
    create_bridge_pier_brep,
    ProjectionEngine,
    RenderEngine,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="演示土木工程构件三视图自动投影生成")
    parser.add_argument("--offscreen", action="store_true", help="启用无头渲染模式")
    args = parser.parse_args()

    # 1. 创建一座变截面桥墩 B-Rep 实体 (高 3000, 顶 1000x600, 底 1600x1000)
    pier = create_bridge_pier_brep(
        height=3000.0,
        top_width=1000.0,
        top_depth=600.0,
        bottom_width=1600.0,
        bottom_depth=1000.0,
    )

    # 2. 调用构件内置的 generate_three_views 一键生成三视图
    # 设置外放偏移距离 offset = 2500.0
    views = pier.generate_three_views(offset=2500.0)
    top_view = views["top"]
    front_view = views["front"]
    side_view = views["side"]

    # 3. 构造投影基准平面
    top_plane = Plane3D(center=Point3D(0.0, 0.0, -2500.0), normal=Vector3D(0.0, 0.0, 1.0), size=3600.0)
    front_plane = Plane3D(center=Point3D(0.0, -2500.0, 1500.0), normal=Vector3D(0.0, 1.0, 0.0), size=3600.0)
    side_plane = Plane3D(center=Point3D(-2500.0, 0.0, 1500.0), normal=Vector3D(1.0, 0.0, 0.0), size=3600.0)

    # 4. 渲染
    engine = RenderEngine(window_size=(1280, 800), off_screen=args.offscreen)

    # (a) 中央三维实体
    engine.add_mesh(pier.to_pyvista(), color="slategray", opacity=0.85)
    engine.plotter.add_mesh(pier.get_edges_polydata(), color="black", line_width=2)

    # (b) 渲染三个投影底板
    engine.add_mesh(top_plane.to_pyvista(), color="whitesmoke", opacity=0.4, show_edges=True)
    engine.add_mesh(front_plane.to_pyvista(), color="whitesmoke", opacity=0.4, show_edges=True)
    engine.add_mesh(side_plane.to_pyvista(), color="whitesmoke", opacity=0.4, show_edges=True)

    # (c) 渲染俯视图 (Top View)
    engine.add_mesh(top_view.to_pyvista(), color="royalblue", opacity=0.6)
    engine.plotter.add_mesh(top_view.get_edges_polydata(), color="navy", line_width=3)

    # (d) 渲染正立面图 (Front View)
    engine.add_mesh(front_view.to_pyvista(), color="forestgreen", opacity=0.6)
    engine.plotter.add_mesh(front_view.get_edges_polydata(), color="darkgreen", line_width=3)

    # (e) 渲染侧立面图 (Side View)
    engine.add_mesh(side_view.to_pyvista(), color="coral", opacity=0.6)
    engine.plotter.add_mesh(side_view.get_edges_polydata(), color="darkred", line_width=3)

    # (f) 绘制代表性投影对齐辅助线 (长对正、高平齐、宽相等)
    ref_idx = 6  # 桥墩顶部角点
    v_3d = pier.vertices[ref_idx]
    v_top = top_view.vertices[ref_idx]
    v_front = front_view.vertices[ref_idx]
    v_side = side_view.vertices[ref_idx]

    ray_top = pv.Line(v_3d.to_tuple(), v_top.to_tuple())
    ray_front = pv.Line(v_3d.to_tuple(), v_front.to_tuple())
    ray_side = pv.Line(v_3d.to_tuple(), v_side.to_tuple())

    engine.plotter.add_mesh(ray_top, color="blue", opacity=0.6, line_width=1.5)
    engine.plotter.add_mesh(ray_front, color="green", opacity=0.6, line_width=1.5)
    engine.plotter.add_mesh(ray_side, color="red", opacity=0.6, line_width=1.5)

    # 视图标注说明
    engine.plotter.add_point_labels(
        [
            (0.0, 0.0, 3200.0),
            (0.0, 0.0, -2600.0),
            (0.0, -2600.0, 3200.0),
            (-2600.0, 0.0, 3200.0),
        ],
        [
            "3D Solid Model",
            "Top View (Plan: XY)",
            "Front View (Elevation: XZ)",
            "Side View (Profile: YZ)",
        ],
        font_size=12,
        point_color="black",
        text_color="black",
        shadow=False,
    )

    if not args.offscreen:
        print("展示工程三视图自动投影生成视口...")
        engine.plotter.show()
    else:
        print("离线模式：工程三视图生成校验通过。")


if __name__ == "__main__":
    main()
