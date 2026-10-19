"""08_03_polyline_self_intersection.py — 道路规划红线与桥梁中线折线自交排查。

演示土木工程设计中线形几何缺陷排查：
1. 道路红线在复杂互通立交转弯处因参数错误产生的局部折叠打结（Self-Intersection）；
2. 自动检测非相邻线段间的相交点与线段对索引；
3. 三维视口中断言标红自相交异常点，辅助施工图出图前的几何清洗。

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
    RenderEngine,
    check_polyline_self_intersection,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="道路规划红线与桥梁中线折线自交排查")
    parser.add_argument("--offscreen", action="store_true", help="启用无头渲染模式")
    args = parser.parse_args()

    print("=" * 70)
    print("【案例 08_03】道路规划红线与桥梁中线折线自交排查")
    print("=" * 70)

    # 1. 构建一条在匝道处发生自扭绞的平面道路中线折线 (Z=0)
    road_centerline = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(3000.0, 2000.0, 0.0),
        Point3D(6000.0, 8000.0, 0.0),   # 顶点 2
        Point3D(1000.0, 8000.0, 0.0),   # 顶点 3
        Point3D(5000.0, 3000.0, 0.0),   # 顶点 4 (与 1-2 段相交发生扭绞)
        Point3D(9000.0, 4000.0, 0.0),
        Point3D(12000.0, 5000.0, 0.0),
    ]

    is_self, events = check_polyline_self_intersection(road_centerline, is_closed=False)
    print(f"-> 道路折线自交检测结果: {'[发现扭绞自交!]' if is_self else '[线形顺畅无自交]'}")
    print(f"-> 检出自交缺陷事件数量: {len(events)}")

    for idx, ev in enumerate(events):
        i, j = ev["seg_indices"]
        pt = ev["point"]
        print(f"   事件 #{idx+1}: 线段 S{i} 与 线段 S{j} 发生空间交叉，交点位置 ({pt.x:.1f}, {pt.y:.1f}, {pt.z:.1f})")

    # 2. 渲染可视化
    engine = RenderEngine(window_size=(1280, 800), off_screen=args.offscreen)

    # 绘制道路中线
    curve_pts = [p.to_tuple() for p in road_centerline]
    engine.render_curve(curve_pts, color="steelblue", line_width=4.0)

    # 绘制各节点
    for k, p in enumerate(road_centerline):
        engine.render_point(p.to_tuple(), color="navy", point_size=8, label=f"P{k}")

    # 标红警示自交点
    for ev in events:
        pt = ev["point"]
        engine.render_point(pt.to_tuple(), color="crimson", point_size=18, label="[自交报警点]")

    print("[SUCCESS] 案例 08_03 运行完成。")
    engine.show()


if __name__ == "__main__":
    main()
