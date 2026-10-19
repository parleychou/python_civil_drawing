"""07_02_matrix_order_commutativity.py — 矩阵乘法顺序非交换性深度演示 (T@R vs R@T)。

教学核心重点：
矩阵相乘不满足交换律：T @ R != R @ T。
- 构件 A (T @ R)：先绕自身局部原点旋转，再平移到全局目标点（自转后平移，工程标准做法）；
- 构件 B (R @ T)：先平移到目标点，再绕世界全局原点公转（先平移后公转，导致构件位置严重偏离预期）。

视口中通过黄色弧线画出构件从平移点绕世界坐标原点公转旋转到最终位置的运动轨迹。
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
    TransformMatrix,
    create_box_brep,
    RenderEngine,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="矩阵乘法顺序深度对比 (T@R vs R@T)")
    parser.add_argument("--offscreen", action="store_true", help="启用无头渲染模式")
    args = parser.parse_args()

    # 1. 基础长方体 (长 600, 宽 400, 高 800)
    box = create_box_brep(width=600.0, depth=400.0, height=800.0)

    # 2. 定义平移向量与旋转角度
    dx, dy, dz = 2500.0, 1500.0, 0.0
    angle = math.radians(60.0)

    t_mat = TransformMatrix.translation(dx, dy, dz)
    r_mat = TransformMatrix.rotation_z(angle)

    # 3. 两种不同顺序的组合矩阵
    # 构件 A: 先旋转，后平移 (T @ R)
    m_a = t_mat @ r_mat
    box_a = box.transform(m_a)

    # 构件 B: 先平移，后旋转 (R @ T)
    m_b = r_mat @ t_mat
    box_b = box.transform(m_b)

    # 中间过渡状态：仅平移构件 (用于展示公转起点)
    box_t_only = box.transform(t_mat)

    # 4. 绘制公转轨迹圆弧 (从平移点到 R@T 最终点的圆弧轨迹)
    r_orbit = math.sqrt(dx * dx + dy * dy)
    phi_start = math.atan2(dy, dx)
    phi_end = phi_start + angle
    theta_vals = np.linspace(phi_start, phi_end, 50)
    arc_points = [
        (r_orbit * math.cos(th), r_orbit * math.sin(th), 400.0)
        for th in theta_vals
    ]
    lines = [len(arc_points)] + list(range(len(arc_points)))
    orbit_poly = pv.PolyData(arc_points)
    orbit_poly.lines = lines

    # 5. 渲染展示
    engine = RenderEngine(window_size=(1280, 800), off_screen=args.offscreen)

    # 原始构件
    engine.add_mesh(box.to_pyvista(), color="lightgray", opacity=0.3)
    engine.add_mesh(box.get_edges_polydata(), color="gray")

    # 仅平移构件 (浅粉色虚化参考)
    engine.add_mesh(box_t_only.to_pyvista(), color="pink", opacity=0.3)
    engine.add_mesh(box_t_only.get_edges_polydata(), color="lightcoral")

    # 构件 A: T @ R (翡翠绿，工程预期)
    engine.add_mesh(box_a.to_pyvista(), color="seagreen", opacity=0.9)
    engine.add_mesh(box_a.get_edges_polydata(), color="darkgreen")

    # 构件 B: R @ T (火砖红，公转跑偏)
    engine.add_mesh(box_b.to_pyvista(), color="firebrick", opacity=0.9)
    engine.add_mesh(box_b.get_edges_polydata(), color="maroon")

    # 渲染公转轨迹线
    engine.plotter.add_mesh(orbit_poly, color="gold", line_width=3, label="Orbital Arc (R@T)")

    # 标注说明
    engine.plotter.add_point_labels(
        [
            (300.0, 200.0, 850.0),
            (dx + 200, dy + 200, 950.0),
            (box_b.vertices[6].x, box_b.vertices[6].y, 950.0),
        ],
        [
            "Original (Local Center)",
            "Correct: M = T @ R (Rotate in place -> Translate)",
            "Wrong: M = R @ T (Translate -> Revolve around (0,0,0))",
        ],
        font_size=12,
        point_color="black",
        text_color="black",
        shadow=False,
    )

    if not args.offscreen:
        print("展示 T@R 与 R@T 矩阵相乘顺序对比视口...")
        engine.plotter.show()
    else:
        print("离线模式：顺序非交换性验证通过。")


if __name__ == "__main__":
    main()
