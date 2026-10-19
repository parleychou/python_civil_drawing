"""08_01_point_interactions_2d_3d.py — 施工测量放样验核器 & 空间构件内部测点判别。

演示土木工程现场常见点相交场景：
1. 施工测量放样点与设计轴线端点、吊装对齐校验；
2. 空间点在线段上的投影与垂足偏位检测；
3. 埋入式应变传感器测点在混凝土箱形构件内、体表或外部的三维射线奇偶性判别。

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
    intersect_point_point,
    intersect_point_line,
    intersect_point_plane,
    point_in_mesh,
    IntersectionType,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="施工测量放样验核器 & 构件内部传感器定位判别")
    parser.add_argument("--offscreen", action="store_true", help="启用无头渲染模式")
    args = parser.parse_args()

    print("=" * 70)
    print("【案例 08_01】施工测量放样验核器 & 构件内部传感器定位判别")
    print("=" * 70)

    # 1. 测量放样点比对验核
    design_pt = Point3D(5000.0, 3000.0, 1500.0, name="设计理论基准点")
    measured_pt1 = Point3D(5000.00003, 2999.99997, 1500.00002, name="实测放样点A(合格)")
    measured_pt2 = Point3D(5000.08, 3000.05, 1500.03, name="实测放样点B(偏位)")

    res_pt1 = intersect_point_point(design_pt, measured_pt1, tol=1e-4)
    res_pt2 = intersect_point_point(design_pt, measured_pt2, tol=1e-4)

    print(f"-> 放样点 A 比对: {res_pt1.description}, 偏差: {res_pt1.clearance * 1000:.3f} um")
    print(f"-> 放样点 B 比对: {res_pt2.description}, 偏差: {res_pt2.clearance:.3f} mm")

    # 2. 点在线段主梁轴线上的正交投影与垂足距离
    beam_axis = Line3D(Point3D(0.0, 0.0, 0.0), Point3D(10000.0, 0.0, 0.0), name="主梁设计中线")
    hanger_pt = Point3D(4500.0, 2.5, 0.0, name="牛腿吊点")
    res_line = intersect_point_line(hanger_pt, beam_axis, tol=1e-4)
    print(f"-> 牛腿吊点与主梁轴线: 沿线参数 t = {res_line.parameters.get('t', 0.0):.4f}, 垂偏 = {res_line.clearance:.3f} mm")

    # 3. 构件内部埋入式传感器测点三维空间判别 (奇偶微扰射线检验)
    concrete_box = create_box_mesh(Point3D(0.0, 0.0, 0.0), 3000.0, 3000.0, 2000.0)

    sensor_inside = Point3D(1500.0, 1500.0, 1000.0, name="内部传感器 S1")
    sensor_boundary = Point3D(3000.0, 1500.0, 1000.0, name="体表贴片 S2")
    sensor_outside = Point3D(3500.0, 1500.0, 1000.0, name="构件外探针 S3")

    res_s1 = point_in_mesh(sensor_inside, concrete_box)
    res_s2 = point_in_mesh(sensor_boundary, concrete_box)
    res_s3 = point_in_mesh(sensor_outside, concrete_box)

    print(f"-> S1 状态: {res_s1.type.value} ({res_s1.description})")
    print(f"-> S2 状态: {res_s2.type.value} ({res_s2.description})")
    print(f"-> S3 状态: {res_s3.type.value} ({res_s3.description})")

    # 4. 可视化渲染
    engine = RenderEngine(window_size=(1280, 800), off_screen=args.offscreen)
    engine.add_mesh(concrete_box.to_pyvista(), color="lightgray", opacity=0.35, show_edges=True)

    # 绿色表示内部，黄色表示体表，红色表示外部
    engine.render_point(sensor_inside.to_tuple(), color="green", point_size=16, label="S1: 内部")
    engine.render_point(sensor_boundary.to_tuple(), color="gold", point_size=16, label="S2: 体表")
    engine.render_point(sensor_outside.to_tuple(), color="crimson", point_size=16, label="S3: 外部")

    engine.render_curve([beam_axis.start.to_tuple(), beam_axis.end.to_tuple()], color="blue", line_width=4.0)
    engine.render_point(hanger_pt.to_tuple(), color="purple", point_size=14, label="牛腿吊点")

    print("[SUCCESS] 案例 08_01 运行完成。")
    engine.show()


if __name__ == "__main__":
    main()
