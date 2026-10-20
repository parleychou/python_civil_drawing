"""09_06_tunnel_excavation_boolean.py — 盾构区间隧道推进与地质土体布尔开挖分析。

演示地下工程中的地质与隧道三维布尔开挖模拟：
1. 建立长宽高 50m x 50m x 30m 的复合地层实体；
2. 建立穿越土层的盾构掘进圆柱体 (外径 6.0m，长度 50m，轴线深度 Z=-15m)；
3. 执行布尔差集切除开挖土体，精确统计弃土体积；
4. 渲染半透明剖切土体与光滑隧道衬砌内腔。

命令行参数：
- --offscreen：无头后台离屏运行模式，用于自动化测试与 CI/CD。
"""

import argparse
import sys
import math
from pathlib import Path

# Ensure root is in sys.path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src import (
    Point3D,
    Vector3D,
    create_box_mesh,
    RenderEngine,
    boolean_difference_mesh,
)
import pyvista as pv


def main():
    parser = argparse.ArgumentParser(description="09_06 盾构隧道开挖布尔分析")
    parser.add_argument("--offscreen", action="store_true", help="无头离屏运行")
    args = parser.parse_args()

    print("=" * 70)
    print("【案例 09_06】盾构区间隧道地层推进与土体布尔开挖模拟")
    print("=" * 70)

    # 1. 地质土层块体: 50m x 50m x 30m (Z in [-30, 0])
    soil = create_box_mesh(Point3D(-25.0, 0.0, -30.0), 50.0, 50.0, 30.0)
    soil_vol = soil.to_pyvista().volume
    print(f"-> 地质土体总方量: {soil_vol:.2f} m³")

    # 2. 盾构圆柱开挖体: 外径 6.0m (半径 3.0m)，长度 60m (贯穿土层)
    # 轴线在 X=0, Z=-15, 沿 Y 方向推进
    tunnel_cyl = pv.Cylinder(center=(0.0, 25.0, -15.0), direction=(0.0, 1.0, 0.0), radius=3.0, height=60.0).triangulate().clean()
    from boolean_ops import _polydata_to_mesh_data
    tunnel_mesh = _polydata_to_mesh_data(tunnel_cyl)

    # 3. 执行布尔差集开挖
    res = soil.cut(tunnel_mesh)
    excavated_vol = math.pi * (3.0 ** 2) * 50.0  # ~1413.72 m³
    rem_vol = res.result_volume
    print(f"-> 盾构开挖土方量: {excavated_vol:.2f} m³")
    print(f"-> 开挖后剩余地层方量: {rem_vol:.2f} m³ (理论值: {soil_vol - excavated_vol:.2f} m³)")

    # 4. 渲染 (剖半展示内部隧道圆孔)
    engine = RenderEngine(off_screen=args.offscreen)
    # 半透明渲染开挖后土体
    engine.plotter.add_mesh(res.mesh.to_pyvista(), color="#D97706", opacity=0.4, show_edges=False)
    # 高亮内壁圆柱
    engine.plotter.add_mesh(tunnel_cyl, color="#0EA5E9", opacity=0.8, style="wireframe")

    if args.offscreen:
        engine.plotter.screenshot("output_09_06.png")
        engine.plotter.close()
    else:
        engine.show()

    print("[SUCCESS] 案例 09_06 运行完成。")


if __name__ == "__main__":
    main()
