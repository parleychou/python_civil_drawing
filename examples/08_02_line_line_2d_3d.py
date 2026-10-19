"""08_02_line_line_2d_3d.py — 轴网平面打点 & 空间错层管线净距检测。

演示土木工程设计与机电深化核心线线关系：
1. 二维结构平面轴网交叉打点（跨立试验定位柱梁搭接点）；
2. 空间三维机电错层管线最短公垂线与净距计算；
3. 按照设计规范阈值（如净距不足 150mm 时警示红灯）进行安全验核。

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
    RenderEngine,
    intersect_segments_2d,
    intersect_lines_3d,
    IntersectionType,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="轴网平面打点 & 空间错层管线净距检测")
    parser.add_argument("--offscreen", action="store_true", help="启用无头渲染模式")
    args = parser.parse_args()

    print("=" * 70)
    print("【案例 08_02】轴网平面打点 & 空间错层管线净距检测")
    print("=" * 70)

    # 1. 二维轴网横纵相交解算 (1轴与A轴交叉)
    axis_1 = Line3D(Point3D(0.0, 3000.0, 0.0), Point3D(12000.0, 3000.0, 0.0), name="1轴")
    axis_a = Line3D(Point3D(4000.0, 0.0, 0.0), Point3D(4000.0, 8000.0, 0.0), name="A轴")

    res_2d = intersect_segments_2d(axis_1, axis_a)
    if res_2d.has_intersection and res_2d.point:
        print(f"-> 轴网交叉点 (1轴 x A轴): ({res_2d.point.x:.1f}, {res_2d.point.y:.1f}, {res_2d.point.z:.1f})")

    # 2. 三维空间错层管线净距计算 (给水管与桥架异面公垂线)
    pipe_water = Line3D(Point3D(0.0, 2000.0, 3200.0), Point3D(10000.0, 2000.0, 3200.0), name="DN100给水管")
    cable_tray = Line3D(Point3D(5000.0, 0.0, 3050.0), Point3D(5000.0, 6000.0, 3050.0), name="强电电缆桥架")

    res_3d = intersect_lines_3d(pipe_water, cable_tray)
    clearance = res_3d.clearance or 0.0
    c1 = res_3d.parameters.get("closest_pt1")
    c2 = res_3d.parameters.get("closest_pt2")

    print(f"-> 给水管与桥架空间垂直净距: {clearance:.1f} mm")
    if clearance < 150.0:
        print(f"   [警告] 空间净距 {clearance:.1f} mm < 规范安全阈值 150 mm，存在施工穿插风险！")
    else:
        print(f"   [合格] 空间净距 {clearance:.1f} mm 满足规范要求。")

    # 3. 渲染可视化
    engine = RenderEngine(window_size=(1280, 800), off_screen=args.offscreen)

    # 绘制二维轴网 (灰色虚线效果)
    engine.render_curve([axis_1.start.to_tuple(), axis_1.end.to_tuple()], color="darkgray", line_width=2.0)
    engine.render_curve([axis_a.start.to_tuple(), axis_a.end.to_tuple()], color="darkgray", line_width=2.0)
    if res_2d.point:
        engine.render_point(res_2d.point.to_tuple(), color="blue", point_size=12, label="1-A轴交点")

    # 绘制三维空间管线
    engine.render_curve([pipe_water.start.to_tuple(), pipe_water.end.to_tuple()], color="dodgerblue", line_width=6.0)
    engine.render_curve([cable_tray.start.to_tuple(), cable_tray.end.to_tuple()], color="darkorange", line_width=6.0)

    # 绘制空间最短公垂线段 (红色警示)
    if c1 and c2:
        engine.render_curve([c1.to_tuple(), c2.to_tuple()], color="crimson", line_width=4.0)
        engine.render_point(c1.to_tuple(), color="red", point_size=10, label=f"管线净距: {clearance:.1f}mm")
        engine.render_point(c2.to_tuple(), color="red", point_size=10)

    print("[SUCCESS] 案例 08_02 运行完成。")
    engine.show()


if __name__ == "__main__":
    main()
