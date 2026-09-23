"""以特定颜色和参数网格线渲染参数化曲面（双曲抛物面与球面）。

利用 RenderEngine 的底层 plotter 直接添加 StructuredGrid 网格，
以浅海蓝色 (lightseagreen) 渲染曲面，并用深色网格线 (darkslategrey) 显示其采样网格，
展示解析连续曲面在离散采样后的网格拓扑。

- 默认渲染课件主讲案例：土木薄壳结构【双曲抛物面 (马鞍面)】
- 支持传入参数 --sphere 渲染已有保留案例：空间旋转壳体【参数球面】
"""

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

from brep_primitives import HyperbolicParaboloid, SphereSurface
from render_engine import RenderEngine


def render_hyperbolic_paraboloid() -> None:
    """渲染课件主讲案例：双曲抛物面 (马鞍面)。"""
    # 1. 实例化双曲抛物面
    saddle = HyperbolicParaboloid(
        a=1500.0,
        b=1500.0,
        c=600.0,
        u_range=(-1500.0, 1500.0),
        v_range=(-1500.0, 1500.0),
        u_resolution=36,
        v_resolution=36,
        name="Parametric_Hyperbolic_Paraboloid"
    )

    # 2. 生成 PyVista 结构化网格数据
    grid = saddle.to_pyvista()

    # 3. 初始化课件渲染引擎
    engine = RenderEngine(window_size=(1024, 768), show_grid=True)

    # 4. 渲染曲面：浅海绿曲面片 + 深石板灰参数网格线
    engine.plotter.add_mesh(
        grid,
        color="lightseagreen",      # 曲面片颜色：浅海绿
        show_edges=True,            # 显示参数网格等值线
        edge_color="darkslategrey", # 网格线颜色：深石板灰
        opacity=0.9,                # 曲面不透明度
    )

    # 5. 标示马鞍面典型几何特征点
    features = {
        "Saddle Center (K < 0)": (0.0, 0.0, 0.0),
        "Arch Peak (+X)": (1500.0, 0.0, 600.0),
        "Arch Peak (-X)": (-1500.0, 0.0, 600.0),
        "Sag Min (+Y)": (0.0, 1500.0, -600.0),
        "Sag Min (-Y)": (0.0, -1500.0, -600.0),
    }
    for name, coords in features.items():
        engine.render_point(
            coords,
            color="red",
            point_size=12.0,
            label=name
        )

    # 6. 显示窗口并提示控制指令
    print(f"[*] 正在渲染 Surface 课件主讲曲面【双曲抛物面 (马鞍面)】...")
    print(f"    - 曲面面片：浅海绿色 (lightseagreen)")
    print(f"    - 采样网格等值线：深石板灰色 (darkslategrey)")
    print(f"    - 特征标示：中心鞍点 (红色) 与双向主曲率拱顶/悬链低点")
    print(f"    - 💡 提示：运行 `python 02_render_surface_marked.py --sphere` 可切换至已有保留案例【球面】")
    engine.print_mouse_controls()
    engine.show()


def render_sphere_surface() -> None:
    """渲染已有保留案例：经纬度参数化球面。"""
    # 1. 实例化球面曲面
    sphere = SphereSurface(
        radius=1000.0,
        u_range=(0.0, 2 * math.pi),
        v_range=(-math.pi / 2, math.pi / 2),
        u_resolution=60,
        v_resolution=60,
        name="Parametric_Sphere_Surface"
    )

    # 2. 生成 PyVista 结构化网格数据
    grid = sphere.to_pyvista()

    # 3. 初始化课件渲染引擎
    engine = RenderEngine(window_size=(1024, 768), show_grid=True)

    # 4. 渲染曲面：使用底层 plotter 进行细致的参数控制
    engine.plotter.add_mesh(
        grid,
        color="lightseagreen",      # 曲面片颜色：浅海绿
        show_edges=True,            # 显示参数网格等值线
        edge_color="darkslategrey", # 网格线颜色：深石板灰
        opacity=0.9,                # 曲面不透明度
    )

    # 5. 在球面上渲染几个特征点以供标示
    features = {
        "Sphere North Pole": (0.0, 0.0, 1000.0),
        "Sphere South Pole": (0.0, 0.0, -1000.0),
        "Equator Point 1": (1000.0, 0.0, 0.0),
        "Equator Point 2": (0.0, 1000.0, 0.0),
    }
    for name, coords in features.items():
        engine.render_point(
            coords,
            color="red",
            point_size=12.0,
            label=name
        )

    # 6. 显示窗口并提示控制指令
    print(f"[*] 正在渲染 Surface 已有保留案例【经纬度参数球面】...")
    print(f"    - 曲面面片：浅海绿色 (lightseagreen)")
    print(f"    - 采样网格等值线：深石板灰色 (darkslategrey)")
    engine.print_mouse_controls()
    engine.show()


def main() -> None:
    parser = argparse.ArgumentParser(description="渲染参数化曲面（双曲抛物面 / 球面）")
    parser.add_argument(
        "--sphere",
        action="store_true",
        help="切换渲染已有案例：经纬度参数化球面（默认渲染课件主讲案例：双曲抛物面）"
    )
    args = parser.parse_args()

    if args.sphere:
        render_sphere_surface()
    else:
        render_hyperbolic_paraboloid()


if __name__ == "__main__":
    main()
