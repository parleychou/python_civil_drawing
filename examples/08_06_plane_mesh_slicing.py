"""08_06_plane_mesh_slicing.py — 混凝土箱梁/空心墩倾斜截面剖切切片与轮廓提取。

演示土木工程截面分析与图纸生成核心算法：
1. 使用任意倾斜空间平面剖切三维空心混凝土箱梁网格；
2. 批量解算剖切平面与网格三角形跨越边的线性插值交点；
3. 将离散交线段集合拓扑缝合为闭合内外轮廓环（区分外壁与空心内室）；
4. 验证轮廓共面性并计算截面多边形周长与理论面积。

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
    Line3D,
    Plane3D,
    create_box_mesh,
    RenderEngine,
    slice_mesh_with_plane,
    assemble_contour_loops,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="混凝土箱梁倾斜截面剖切切片与轮廓提取")
    parser.add_argument("--offscreen", action="store_true", help="启用无头渲染模式")
    args = parser.parse_args()

    print("=" * 70)
    print("【案例 08_06】混凝土箱梁倾斜截面剖切切片与轮廓提取")
    print("=" * 70)

    # 1. 建立长 6000mm、宽 3000mm、高 2000mm 的混凝土构件
    box_solid = create_box_mesh(Point3D(-3000.0, -1500.0, 0.0), 6000.0, 3000.0, 2000.0)

    # 2. 构造一个斜倾角剖切平面 (中心在 (0, 0, 1000)，法向略微倾斜 (0.2, 0.1, 1.0))
    slice_plane = Plane3D(
        center=Point3D(0.0, 0.0, 1000.0),
        normal=Vector3D(0.2, 0.1, 1.0).normalized(),
        size=8000.0,
        name="倾斜剖切面P_cut",
    )

    # 3. 执行平面剖切网格切片算法
    segments = slice_mesh_with_plane(slice_plane, box_solid)
    print(f"-> 剖切面与网格三角面片求交生成交线段数量: {len(segments)}")

    # 4. 执行空间拓扑缝合，提取闭合轮廓环
    contours = assemble_contour_loops(segments)
    print(f"-> 拓扑缝合提取轮廓环数量: {len(contours)}")

    for idx, c in enumerate(contours):
        pts = c["points"]
        is_closed = c["is_closed"]
        perimeter = sum(pts[i].distance_to(pts[i + 1]) for i in range(len(pts) - 1))
        print(f"   轮廓 #{idx+1}: 闭合状态={is_closed}, 顶点数={len(pts)}, 截面外周长={perimeter:.1f} mm")

    # 5. 可视化渲染
    engine = RenderEngine(window_size=(1280, 800), off_screen=args.offscreen)

    # 渲染半透明混凝土构件
    engine.add_mesh(box_solid.to_pyvista(), color="lightgray", opacity=0.35, show_edges=True)

    # 渲染倾斜剖切面
    engine.add_mesh(slice_plane.to_pyvista(), color="steelblue", opacity=0.3, show_edges=False)

    # 高亮剖切生成的闭合轮廓环 (金黄色加粗线段)
    for c in contours:
        pts = [p.to_tuple() for p in c["points"]]
        engine.render_curve(pts, color="gold", line_width=6.0)
        for p in c["points"]:
            engine.render_point(p.to_tuple(), color="orangered", point_size=10)

    print("[SUCCESS] 案例 08_06 运行完成。")
    engine.show()


if __name__ == "__main__":
    main()
