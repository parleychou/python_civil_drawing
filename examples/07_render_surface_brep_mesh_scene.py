"""对比渲染参数化曲面（HyperbolicParaboloid / Sphere）、B-Rep 实体与 Mesh 几何网格的综合场景。

在同一视口中并排显示三大几何体表达方式，用不同颜色和标记突出它们的结构差别：
- 参数化双曲抛物面 (Surface)：位于左侧 (X = -3000)，以浅海绿渲染，并带有深石板灰等值线；
- 长方体 (B-Rep)：位于中央 (X = 0)，以半透明蓝色渲染，其顶点（珊瑚红点）和拓扑棱边（钢青线）清晰可见；
- 四棱锥 (Mesh)：位于右侧 (X = +3000)，以浅麦色渲染，直接展示离散的三角面片和网格顶点（海绿点）。

命令行参数：
- 默认：渲染课件 Slide 23【双曲抛物面 + B-Rep 长方体 + Mesh 四棱锥】
- --sphere：切换为已有保留案例【球面 + B-Rep + Mesh】
- --all：同屏显示全部 4 种构件（包含马鞍面与球面）
"""

import sys
from pathlib import Path
_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))


import argparse
import math
import sys
from pathlib import Path

# 动态寻找第 04 章和第 05 章的脚本目录
def find_chapter_scripts(prefix: str) -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        try:
            for child in parent.iterdir():
                if child.is_dir() and child.name.startswith(prefix):
                    scripts_sub = child / "scripts"
                    return scripts_sub if scripts_sub.exists() else child
        except OSError:
            continue
    return Path()

scripts_dir = Path(__file__).resolve().parent
ch4_path = find_chapter_scripts("04")
sys.path.insert(0, str(scripts_dir))
if ch4_path.exists():
    sys.path.insert(0, str(ch4_path))

from brep_primitives import (
    create_box_brep,
    create_cube_brep,
    create_pyramid_mesh,
    HyperbolicParaboloid,
    SphereSurface,
    BrepData,
    MeshData,
    Point3D,
)
from render_engine import RenderEngine


def main() -> None:
    parser = argparse.ArgumentParser(description="同屏对比渲染三大几何表达体系")
    parser.add_argument(
        "--sphere",
        action="store_true",
        help="曲面使用已有保留案例【球面】（默认使用课件主讲案例【双曲抛物面/马鞍面】）"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="同屏展示所有 4 种几何构件（双曲抛物面 + 球面 + B-Rep长方体 + Mesh四棱锥）"
    )
    args = parser.parse_args()

    # 初始化渲染引擎
    engine = RenderEngine(window_size=(1280, 800), show_grid=True)

    # =================================================================
    # 1. 渲染 Surface 曲面 (左侧 X = -3000)
    # =================================================================
    if args.sphere and not args.all:
        # 保留案例：经纬度球面
        sphere = SphereSurface(
            radius=1000.0,
            u_range=(0.0, 2 * math.pi),
            v_range=(-math.pi / 2, math.pi / 2),
            u_resolution=30,
            v_resolution=30,
            name="Sphere_Surface"
        )
        grid = sphere.to_pyvista()
        grid.translate([-3000.0, 0.0, 0.0], inplace=True)
        engine.plotter.add_mesh(
            grid,
            color="lightseagreen",
            show_edges=True,
            edge_color="darkslategrey",
            opacity=0.9
        )
        engine.render_point((-3000.0, 0.0, 1150.0), color="blue", point_size=1.0, label="Surface: Sphere")
    else:
        # 课件主讲案例：双曲抛物面 (马鞍面)
        saddle = HyperbolicParaboloid(
            a=1500.0,
            b=1500.0,
            c=600.0,
            u_range=(-1500.0, 1500.0),
            v_range=(-1500.0, 1500.0),
            u_resolution=30,
            v_resolution=30,
            name="Hyperbolic_Paraboloid_Roof"
        )
        grid = saddle.to_pyvista()
        grid.translate([-3000.0, 0.0, 0.0], inplace=True)
        engine.plotter.add_mesh(
            grid,
            color="lightseagreen",
            show_edges=True,
            edge_color="darkslategrey",
            opacity=0.9
        )
        engine.render_point((-3000.0, 0.0, 800.0), color="blue", point_size=1.0, label="Surface: Saddle Roof")

    # =================================================================
    # 2. 若启用 --all，在后侧 (Y = +3000) 渲染已有保留案例【球面】
    # =================================================================
    if args.all:
        sphere = SphereSurface(
            radius=900.0,
            u_range=(0.0, 2 * math.pi),
            v_range=(-math.pi / 2, math.pi / 2),
            u_resolution=24,
            v_resolution=24,
            name="Sphere_Dome"
        )
        s_grid = sphere.to_pyvista()
        s_grid.translate([-3000.0, 3000.0, 0.0], inplace=True)
        engine.plotter.add_mesh(
            s_grid,
            color="cadetblue",
            show_edges=True,
            edge_color="darkslategrey",
            opacity=0.85
        )
        engine.render_point((-3000.0, 3000.0, 1100.0), color="blue", point_size=1.0, label="Surface: Sphere Dome")

    # =================================================================
    # 3. 渲染 B-Rep 长方体 (中央 X = 0，居中对称)
    # =================================================================
    cube = create_box_brep(1500.0, 1500.0, 1500.0)
    # 将长方体底面中心对齐到 (0, 0, 0)
    centered_cube_verts = tuple(
        Point3D(v.x - 750.0, v.y - 750.0, v.z) for v in cube.vertices
    )
    centered_cube = BrepData(
        vertices=centered_cube_verts,
        edges=cube.edges,
        faces=cube.faces,
        name="BRep_Cube_Center"
    )

    # 表面
    engine.add_mesh(centered_cube.to_pyvista(), color="lightblue", show_edges=False, opacity=0.45)
    # 棱边
    engine.add_mesh(centered_cube.get_edges_polydata(), color="steelblue", show_edges=True)
    # 顶点与标签
    for idx, v in enumerate(centered_cube.vertices):
        engine.render_point(v.to_tuple(), color="coral", point_size=10.0)
    engine.render_point((0.0, 0.0, 1700.0), color="blue", point_size=1.0, label="B-Rep: Solid Box")

    # =================================================================
    # 4. 渲染 Mesh 四棱锥 (右侧 X = +3000，居中对称)
    # =================================================================
    pyramid = create_pyramid_mesh(1500.0, 1500.0, 1500.0)
    # 将四棱锥底面中心对齐到 (+3000, 0, 0)
    shifted_mesh_verts = tuple(
        Point3D(v.x - 750.0 + 3000.0, v.y - 750.0, v.z) for v in pyramid.vertices
    )
    shifted_pyramid = MeshData(
        vertices=shifted_mesh_verts,
        faces=pyramid.faces,
        name="Shifted_Mesh_Pyramid"
    )
    # 面片
    engine.add_mesh(shifted_pyramid.to_pyvista(), color="wheat", show_edges=True)
    # 顶点
    for v in shifted_pyramid.vertices:
        engine.render_point(v.to_tuple(), color="seagreen", point_size=10.0)
    engine.render_point((3000.0, 0.0, 1700.0), color="blue", point_size=1.0, label="Mesh: Pyramid")

    # =================================================================
    # 5. 启动与展示
    # =================================================================
    print(f"[*] 正在并排对比渲染三大几何表达模式 (与 Slide 23 完美对齐)...")
    print(f"    - [左侧 X=-3000]: Surface 曲面 (lightseagreen曲面, darkslategrey等值线)")
    print(f"    - [中央 X=    0]: B-Rep 长方体 (coral顶点, steelblue棱边, lightblue半透明面)")
    print(f"    - [右侧 X=+3000]: Mesh 四棱锥 (seagreen顶点, wheat面片)")
    if args.all:
        print(f"    - [后侧 Y=+3000]: 已有保留案例 Sphere Dome (球面穹顶)")
    else:
        print(f"    - 💡 提示：运行 `python 07_...py --sphere` 可切为球面曲面；运行 `python 07_...py --all` 可同屏显示全部构件")
    engine.print_mouse_controls()
    engine.show()


if __name__ == "__main__":
    main()
