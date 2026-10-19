"""08_04_line_plane_and_triangle.py — 机电管道斜穿剪力墙预留套管定位与 MT 重心坐标解算。

演示土木工程机电与结构交叉设计：
1. 空间机电管线斜向穿越混凝土剪力墙支撑平面，自动解算穿墙套管中心点空间三维坐标；
2. 利用 Möller-Trumbore 算法精确判定光线与墙体三角形面片交点，输出重心坐标 (u, v) 与深度 t；
3. 计算穿透点法向夹角，换算预留套管的椭圆开洞截面长短轴。

命令行参数：
- --offscreen：无头后台离屏运行模式，用于自动化测试与 CI/CD。
"""

import argparse
import math
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
    RenderEngine,
    intersect_line_plane,
    intersect_ray_triangle,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="管道斜穿剪力墙预留套管定位与 MT 重心坐标解算")
    parser.add_argument("--offscreen", action="store_true", help="启用无头渲染模式")
    args = parser.parse_args()

    print("=" * 70)
    print("【案例 08_04】管道斜穿剪力墙预留套管定位与 MT 算法")
    print("=" * 70)

    # 1. 剪力墙定位 (位于 X=3000 平面，法向指向 X 轴)
    wall_plane = Plane3D(Point3D(3000.0, 2000.0, 1500.0), Vector3D(1.0, 0.0, 0.0), size=4000.0, name="剪力墙Q1")

    # 2. 斜穿机电给排水管 (从 (0, 1000, 1200) 斜穿至 (6000, 3000, 1800))
    pipe_axis = Line3D(Point3D(0.0, 1000.0, 1200.0), Point3D(6000.0, 3000.0, 1800.0), name="DN200斜穿管")

    res_pierce = intersect_line_plane(pipe_axis, wall_plane, segment_only=True)
    if res_pierce.has_intersection and res_pierce.point:
        sleeve_center = res_pierce.point
        t_param = res_pierce.parameters.get("t", 0.0)
        print(f"-> 管道成功穿透剪力墙！")
        print(f"   穿透套管中心坐标: ({sleeve_center.x:.1f}, {sleeve_center.y:.1f}, {sleeve_center.z:.1f})")
        print(f"   管道穿透参数 t: {t_param:.4f}")

        # 计算管道轴线与墙体法向夹角
        pipe_dir = pipe_axis.direction().normalized()
        cos_theta = abs(pipe_dir.dot(wall_plane.normal.normalized()))
        theta_deg = math.degrees(math.acos(cos_theta))
        print(f"   穿墙倾角: {theta_deg:.2f}° (墙厚 300mm 时有效穿墙路径长度: {300.0 / cos_theta:.1f} mm)")

    # 3. Möller-Trumbore 射线-三角形算法精细验核
    v0 = Point3D(3000.0, 0.0, 0.0)
    v1 = Point3D(3000.0, 4000.0, 0.0)
    v2 = Point3D(3000.0, 2000.0, 3000.0)

    ray_origin = pipe_axis.start
    ray_dir = pipe_axis.direction().normalized()
    hit, hit_pt, mt_t, u, v = intersect_ray_triangle(ray_origin, ray_dir, v0, v1, v2)
    print(f"-> MT 射线三角形相交: hit={hit}, 距离 t={mt_t:.1f} mm, 重心坐标 (u={u:.3f}, v={v:.3f})")

    # 4. 可视化渲染
    engine = RenderEngine(window_size=(1280, 800), off_screen=args.offscreen)

    # 绘制剪力墙面
    engine.add_mesh(wall_plane.to_pyvista(), color="lightsteelblue", opacity=0.45, show_edges=True)

    # 绘制管道
    engine.render_curve([pipe_axis.start.to_tuple(), pipe_axis.end.to_tuple()], color="darkcyan", line_width=6.0)

    # 绘制穿透套管位置
    if res_pierce.point:
        engine.render_point(res_pierce.point.to_tuple(), color="gold", point_size=18, label="预留套管中心")

    # 绘制验核三角形
    tri_pts = [v0.to_tuple(), v1.to_tuple(), v2.to_tuple(), v0.to_tuple()]
    engine.render_curve(tri_pts, color="orange", line_width=2.5)

    print("[SUCCESS] 案例 08_04 运行完成。")
    engine.show()


if __name__ == "__main__":
    main()
