"""实例化并采样参数化曲面的示例（双曲抛物面与球面）。

演示参数化曲面（Surface）的数学映射机制：
1. 主讲案例：土木薄壳结构经典【双曲抛物面 (马鞍面)】
2. 拓展对比案例：空间旋转壳体【参数化球面】

定义参数域范围和采样点分辨率，并在控制台打印部分采样点的
参数坐标 (u, v) 与其计算出的空间三维坐标 (x, y, z)，说明参数曲面采样的原理。
"""

import sys
from pathlib import Path
_SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))


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


def demo_hyperbolic_paraboloid() -> None:
    """演示课件主讲案例：双曲抛物面 (马鞍面) 的参数采样。"""
    # 实例化土木薄壳双曲抛物面
    # 解析方程: z = c * (u^2/a^2 - v^2/b^2)
    saddle = HyperbolicParaboloid(
        a=1500.0,
        b=1500.0,
        c=600.0,
        u_range=(-1500.0, 1500.0),
        v_range=(-1500.0, 1500.0),
        u_resolution=25,
        v_resolution=25,
        name="Hyperbolic_Paraboloid_Roof"
    )

    print("=" * 65)
    print(f" [案例一] 课件主讲曲面：{saddle.name} (双曲抛物面/马鞍面) ")
    print("=" * 65)
    print("解析方程: x = u, y = v, z = c * (u²/a² - v²/b²)")
    print(f"曲率尺度: a = {saddle.a:.1f} mm, b = {saddle.b:.1f} mm, 矢高 c = {saddle.c:.1f} mm")
    print(f"参数范围: u ∈ [{saddle.u_range[0]:.1f}, {saddle.u_range[1]:.1f}], v ∈ [{saddle.v_range[0]:.1f}, {saddle.v_range[1]:.1f}]")
    print(f"采样分辨率: {saddle.u_resolution} x {saddle.v_resolution} 网格点")
    print("-" * 65)

    test_params = [
        (0.0, 0.0, "中心鞍点 (高斯曲率 K < 0)"),
        (1500.0, 0.0, "X 轴向最高拱顶端点"),
        (-1500.0, 0.0, "X 轴向对侧拱顶端点"),
        (0.0, 1500.0, "Y 轴向下凹悬链线最低端点"),
        (1500.0, 1500.0, "双向开闭角点"),
    ]

    print("[空间坐标映射评估样例 (u, v) -> Point3D(x, y, z)]:")
    for u, v, desc in test_params:
        pt = saddle.evaluate(u, v)
        print(f"  参数 (u={u:7.1f}, v={v:7.1f}) ---> 空间点 ({pt.x:7.1f}, {pt.y:7.1f}, {pt.z:7.1f})  [{desc}]")

    grid = saddle.to_pyvista()
    print("-" * 65)
    print(f"[采样完成] PyVista 结构化网格信息:")
    print(f"  网格点总数: {grid.n_points} 个点")
    print(f"  网格面片数: {grid.n_cells} 个单元")
    print("=" * 65)


def demo_sphere_surface() -> None:
    """演示拓展对比案例：经纬度参数化球面。"""
    # 实例化球面对象
    sphere = SphereSurface(
        radius=1000.0,
        u_range=(0.0, 2 * math.pi),
        v_range=(-math.pi / 2, math.pi / 2),
        u_resolution=24,
        v_resolution=12,
        name="Parametric_Sphere_Surface"
    )

    print("\n" + "=" * 65)
    print(f" [案例二] 拓展对比曲面：{sphere.name} (经纬度参数球面) ")
    print("=" * 65)
    print("解析方程: x = R*cos(u)*cos(v), y = R*sin(u)*cos(v), z = R*sin(v)")
    print(f"球体半径: R = {sphere.radius:.1f} mm")
    print("参数范围: 经度 u ∈ [0, 2π], 纬度 v ∈ [-π/2, π/2]")
    print(f"采样分辨率: {sphere.u_resolution} x {sphere.v_resolution} 网格点")
    print("-" * 65)

    test_params = [
        (0.0, 0.0, "赤道起点"),
        (math.pi, 0.0, "赤道对侧点"),
        (0.0, math.pi / 2, "北极点"),
        (0.0, -math.pi / 2, "南极点"),
    ]

    print("[空间坐标映射评估样例 (u, v) -> Point3D(x, y, z)]:")
    for u, v, desc in test_params:
        pt = sphere.evaluate(u, v)
        print(f"  参数 (u={u:7.3f}, v={v:7.3f}) ---> 空间点 ({pt.x:7.1f}, {pt.y:7.1f}, {pt.z:7.1f})  [{desc}]")

    grid = sphere.to_pyvista()
    print("-" * 65)
    print(f"[采样完成] PyVista 结构化网格信息:")
    print(f"  网格点总数: {grid.n_points} 个点")
    print(f"  网格面片数: {grid.n_cells} 个单元")
    print("=" * 65)


def main() -> None:
    # 1. 运行课件主讲案例：双曲抛物面 (马鞍面)
    demo_hyperbolic_paraboloid()

    # 2. 运行已有保留案例：参数球面
    demo_sphere_surface()


if __name__ == "__main__":
    main()
