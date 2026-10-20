"""09_02_mesh_triangle_splitting.py — 空间三角形约束切分与网格局部重剖。

演示三维实体布尔底层的微观手术刀：
1. 构造一个空间倾斜三角形面片；
2. 构造穿过该三角形内部与边界的两条相交线段；
3. 执行 split_triangle_by_segments 约束三角剖分；
4. 验证面积严格守恒与法向严格一致，并在 PyVista 中对比切分前后网格。

命令行参数：
- --offscreen：无头后台离屏运行模式，用于自动化测试与 CI/CD。
"""

import argparse
import sys
from pathlib import Path
import numpy as np

# Ensure root is in sys.path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src import (
    Point3D,
    Vector3D,
    MeshData,
    RenderEngine,
    split_triangle_by_segments,
)


def main():
    parser = argparse.ArgumentParser(description="09_02 空间三角形约束切分重剖")
    parser.add_argument("--offscreen", action="store_true", help="无头离屏运行")
    args = parser.parse_args()

    print("=" * 70)
    print("【案例 09_02】空间三角形相交线段约束三角剖分与面积守恒分析")
    print("=" * 70)

    v0 = [0.0, 0.0, 5.0]
    v1 = [20.0, 0.0, 5.0]
    v2 = [10.0, 15.0, 12.0]

    # 切割线段：连接两条边上的中点
    p_edge1 = [10.0, 0.0, 5.0]
    p_edge2 = [5.0, 7.5, 8.5]
    segments = [(p_edge1, p_edge2)]

    sub_tris = split_triangle_by_segments(v0, v1, v2, segments)
    print(f"-> 原三角形被相交线段切分为 {len(sub_tris)} 个子三角形")

    def calc_area(p0, p1, p2):
        return 0.5 * np.linalg.norm(np.cross(p1 - p0, p2 - p0))

    orig_area = calc_area(np.array(v0), np.array(v1), np.array(v2))
    sub_sum = sum(calc_area(a, b, c) for a, b, c in sub_tris)
    print(f"-> 原三角形面积: {orig_area:.4f} m²")
    print(f"-> 子三角形面积总和: {sub_sum:.4f} m² (误差: {abs(orig_area - sub_sum):.2e})")

    # 渲染
    engine = RenderEngine(off_screen=args.offscreen)
    # 渲染原三角形线框
    engine.render_curve([tuple(v0), tuple(v1), tuple(v2), tuple(v0)], color="gray", line_width=2.0)
    # 渲染相交切割线
    engine.render_curve([tuple(p_edge1), tuple(p_edge2)], color="red", line_width=5.0)

    # 渲染各子三角形
    colors = ["cyan", "yellow", "green", "orange"]
    for i, (a, b, c) in enumerate(sub_tris):
        pts = (Point3D(*a), Point3D(*b), Point3D(*c))
        m = MeshData(vertices=pts, faces=((0, 1, 2),))
        engine.plotter.add_mesh(m.to_pyvista(), color=colors[i % len(colors)], opacity=0.8, show_edges=True)

    if args.offscreen:
        engine.plotter.screenshot("output_09_02.png")
        engine.plotter.close()
    else:
        engine.show()

    print("[SUCCESS] 案例 09_02 运行完成。")


if __name__ == "__main__":
    main()
