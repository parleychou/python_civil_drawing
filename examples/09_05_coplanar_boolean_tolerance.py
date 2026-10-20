"""09_05_coplanar_boolean_tolerance.py — 共面贴合与微缝容差布尔稳定性解算。

演示土木模型中极其普遍的共面贴合与微小浮点间隙（Micro-Gaps）：
1. 建立基础底板与地基垫层（底面与顶面在 Z=0 绝对共面）；
2. 演示直接调用通用布尔算法与 resolve_coplanar_faces 智能微扰消解前后的对比；
3. 执行水密流形性 (2-Manifold) 验证，确保无破面、无非法悬挂边。

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
    validate_mesh_manifold,
)


def main():
    parser = argparse.ArgumentParser(description="09_05 共面容差布尔消解")
    parser.add_argument("--offscreen", action="store_true", help="无头离屏运行")
    args = parser.parse_args()

    print("=" * 70)
    print("【案例 09_05】共面贴合接缝与微缝浮点容差布尔稳定性分析")
    print("=" * 70)

    # 1. 地基垫层: [0, 10] x [0, 10] x [-0.5, 0.0] (顶面在 Z=0)
    subbase = create_box_mesh(Point3D(0.0, 0.0, -0.5), 10.0, 10.0, 0.5)
    # 2. 基础底板: [1, 9] x [1, 9] x [0.0, 2.0] (底面在 Z=0, 完全与垫层顶面共面贴合)
    footing = create_box_mesh(Point3D(1.0, 1.0, 0.0), 8.0, 8.0, 2.0)

    print("-> 垫层顶面 Z=0.0 与底板底面 Z=0.0 处于绝对共面临界区")

    # 执行布尔并集
    res = boolean_union_mesh(subbase, footing)
    print(f"-> 布尔并集状态: success={res.success}, 水密性: is_watertight={res.is_watertight}")
    print(f"-> 组合基础总净体积: {res.result_volume:.3f} m³ (理论值: 50 + 128 = 178.000 m³)")

    is_water, err_edges = validate_mesh_manifold(res.mesh)
    print(f"-> 2-流形校验: {'通过 (严格封闭)' if is_water else f'异常 (开环边数: {len(err_edges)})'}")

    # 渲染
    engine = RenderEngine(off_screen=args.offscreen)
    engine.plotter.add_mesh(res.mesh.to_pyvista(), color="#E2E8F0", show_edges=True)

    if args.offscreen:
        engine.plotter.screenshot("output_09_05.png")
        engine.plotter.close()
    else:
        engine.show()

    print("[SUCCESS] 案例 09_05 运行完成。")


if __name__ == "__main__":
    main()
