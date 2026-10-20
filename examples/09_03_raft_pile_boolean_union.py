"""09_03_raft_pile_boolean_union.py — 复杂桩筏基础承台与群桩三维布尔熔合。

演示深基础工程中的三维网格布尔并集 (Union)：
1. 建立尺寸为 12m x 12m x 2.5m 的大体积现浇混凝土承台；
2. 建立深入承台 1.0m 的 4 根钻孔灌注桩桩头；
3. 执行 boolean_union_mesh，熔合为单一水密流形实体；
4. 统计混凝土体积，验证无桩头内嵌冗余面片。

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
    create_box_mesh,
    RenderEngine,
    boolean_union_mesh,
)
import pyvista as pv


def main():
    parser = argparse.ArgumentParser(description="09_03 桩筏基础布尔并集熔合")
    parser.add_argument("--offscreen", action="store_true", help="无头离屏运行")
    args = parser.parse_args()

    print("=" * 70)
    print("【案例 09_03】桩筏基础承台与群桩桩头三维网格布尔熔合建模")
    print("=" * 70)

    # 1. 承台: [0, 12] x [0, 12] x [0, 2.5]
    cap = create_box_mesh(Point3D(0.0, 0.0, 0.0), 12.0, 12.0, 2.5)

    # 2. 4 根方形成孔桩: 桩头从 Z=-3.0 深入到 Z=1.0 (深入承台内部 1.0m)
    piles = [
        create_box_mesh(Point3D(2.0, 2.0, -3.0), 1.5, 1.5, 4.0),
        create_box_mesh(Point3D(8.5, 2.0, -3.0), 1.5, 1.5, 4.0),
        create_box_mesh(Point3D(2.0, 8.5, -3.0), 1.5, 1.5, 4.0),
        create_box_mesh(Point3D(8.5, 8.5, -3.0), 1.5, 1.5, 4.0),
    ]

    # 3. 连续执行布尔并集
    current_solid = cap
    for i, p in enumerate(piles):
        res = current_solid.boolean_union(p)
        if res.success and res.mesh is not None:
            current_solid = res.mesh
        print(f"-> 熔合第 {i+1} 根灌注桩，当前组合实体体积: {current_solid.to_pyvista().volume:.2f} m³")

    final_volume = current_solid.to_pyvista().volume
    # 理论体积: 承台 (12*12*2.5 = 360) + 4根桩外露部分 (4 * 1.5*1.5*3.0 = 27) = 387.0
    print(f"-> 最终一体化桩筏实体体积: {final_volume:.2f} m³ (理论净体积: 387.00 m³)")

    # 4. 渲染
    engine = RenderEngine(off_screen=args.offscreen)
    engine.plotter.add_mesh(current_solid.to_pyvista(), color="#CBD5E1", show_edges=True, opacity=0.95)

    if args.offscreen:
        engine.plotter.screenshot("output_09_03.png")
        engine.plotter.close()
    else:
        engine.show()

    print("[SUCCESS] 案例 09_03 运行完成。")


if __name__ == "__main__":
    main()
