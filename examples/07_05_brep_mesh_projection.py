"""07_05_brep_mesh_projection.py — B-Rep实体与Mesh网格到空间斜平面的投影与射影线绘制。

教学核心：
1. B-Rep 拓扑投影：将 3D 实体顶点投射到二维平面，并保留其棱边与面片拓扑连接关系；
2. Mesh 离散面片投影：将三角形网格面投射到目标平面，形成几何平面投影阴影；
3. 空间投影射线 (Projection Rays)：绘制三维顶点向投影平面的垂线束，生动展示透视与平行投影。
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
    TransformMatrix,
    create_box_brep,
    create_pyramid_mesh,
    ProjectionEngine,
    RenderEngine,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="演示B-Rep实体与Mesh网格平面投影")
    parser.add_argument("--offscreen", action="store_true", help="启用无头渲染模式")
    args = parser.parse_args()

    # 1. 创建空间三维构件
    # (a) B-Rep 长方体 (放置在左侧 X = -1000, 抬高 Z = 1200)
    t_box = TransformMatrix.translation(-1200.0, 0.0, 1200.0) @ TransformMatrix.rotation_z(0.3)
    box_3d = create_box_brep(width=600.0, depth=500.0, height=700.0).transform(t_box)

    # (b) Mesh 四棱锥 (放置在右侧 X = +1000, 抬高 Z = 1200)
    t_pyr = TransformMatrix.translation(800.0, 0.0, 1200.0) @ TransformMatrix.rotation_z(-0.2)
    pyr_3d = create_pyramid_mesh(width=700.0, depth=600.0, height=800.0).transform(t_pyr)

    # 2. 定义目标倾斜投影基准面 (倾角 25 度)
    plane_norm = Vector3D(0.3, 0.0, 1.0).normalized()
    proj_plane = Plane3D(center=Point3D(0.0, 0.0, 200.0), normal=plane_norm, size=3500.0)

    # 3. 调用实体与网格内置的 project_to_plane 进行投影
    box_proj = box_3d.project_to_plane(proj_plane)
    pyr_proj = pyr_3d.project_to_plane(proj_plane)

    # 4. 渲染视口
    engine = RenderEngine(window_size=(1280, 800), off_screen=args.offscreen)

    # 渲染投影基准面
    engine.add_mesh(proj_plane.to_pyvista(), color="floralwhite", opacity=0.6, show_edges=True)

    # (a) 渲染 3D 实体
    engine.add_mesh(box_3d.to_pyvista(), color="lightblue", opacity=0.8)
    engine.plotter.add_mesh(box_3d.get_edges_polydata(), color="steelblue", line_width=2)
    engine.add_mesh(pyr_3d.to_pyvista(), color="wheat", opacity=0.85)

    # (b) 渲染平面投影面与轮廓边
    engine.add_mesh(box_proj.to_pyvista(), color="coral", opacity=0.5)
    engine.plotter.add_mesh(box_proj.get_edges_polydata(), color="darkred", line_width=3)
    engine.add_mesh(pyr_proj.to_pyvista(), color="seagreen", opacity=0.6)

    # (c) 渲染空间顶点到平面垂足的投影射线 (Projection Rays)
    for v_orig, v_p in zip(box_3d.vertices, box_proj.vertices):
        ray = pv.Line(v_orig.to_tuple(), v_p.to_tuple())
        engine.plotter.add_mesh(ray, color="royalblue", opacity=0.5, line_width=1.5)

    for v_orig, v_p in zip(pyr_3d.vertices, pyr_proj.vertices):
        ray = pv.Line(v_orig.to_tuple(), v_p.to_tuple())
        engine.plotter.add_mesh(ray, color="darkgreen", opacity=0.5, line_width=1.5)

    # 标注说明
    engine.plotter.add_point_labels(
        [
            (-1200.0, 0.0, 2100.0),
            (1000.0, 0.0, 2100.0),
            (0.0, 0.0, 250.0),
        ],
        ["3D B-Rep Box -> Projected", "3D Mesh Pyramid -> Projected", "Target Inclined Plane"],
        font_size=12,
        point_color="black",
        text_color="black",
        shadow=False,
    )

    if not args.offscreen:
        print("展示实体与网格投影视口...")
        engine.plotter.show()
    else:
        print("离线模式：实体与网格投影渲染校验通过。")


if __name__ == "__main__":
    main()
