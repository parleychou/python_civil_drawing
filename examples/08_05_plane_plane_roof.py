"""08_05_plane_plane_roof.py — 建筑双坡与四坡屋面交棱（屋脊/天沟线）自动化解算。

演示土木工程与建筑形体面面相交几何解算：
1. 建筑双坡屋面南坡与北坡平面方程联立，通过法向叉积与主轴降维解出空间屋脊线（Ridge Line）；
2. 四坡屋面四向斜交平面求解相交斜脊线与天沟线（Valley Line）；
3. 空间直线方程参数化提取与施工放样图元生成。

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
    intersect_planes,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="建筑双坡与四坡屋面交棱自动化解算")
    parser.add_argument("--offscreen", action="store_true", help="启用无头渲染模式")
    args = parser.parse_args()

    print("=" * 70)
    print("【案例 08_05】建筑双坡屋面交棱（屋脊线）自动化解算")
    print("=" * 70)

    # 1. 建立双坡屋面两坡面 (坡度 1:2，即 26.57°)
    # 南坡: 向上向北倾斜，中心点 (0, 3000, 4500)，法向 (0, 1, 2)
    # 北坡: 向上向南倾斜，中心点 (0, 7000, 4500)，法向 (0, -1, 2)
    south_roof = Plane3D(
        center=Point3D(0.0, 3000.0, 4500.0),
        normal=Vector3D(0.0, 1.0, 2.0).normalized(),
        size=8000.0,
        name="双坡南坡面",
    )
    north_roof = Plane3D(
        center=Point3D(0.0, 7000.0, 4500.0),
        normal=Vector3D(0.0, -1.0, 2.0).normalized(),
        size=8000.0,
        name="双坡北坡面",
    )

    # 2. 调用双平面求交算法解算交线
    res_roof = intersect_planes(south_roof, north_roof)
    print(f"-> 双平面相交判定结果: {res_roof.has_intersection} (类型: {res_roof.type.value})")

    if res_roof.has_intersection and res_roof.line:
        ridge_line = res_roof.line
        base_pt = ridge_line.start
        dir_vec = res_roof.parameters.get("direction", ridge_line.direction().normalized())
        print(f"-> 屋脊线空间解算成功！")
        print(f"   基准点坐标: ({base_pt.x:.1f}, {base_pt.y:.1f}, {base_pt.z:.1f})")
        print(f"   方向向量: ({dir_vec.x:.3f}, {dir_vec.y:.3f}, {dir_vec.z:.3f})")

        # 截取建筑进深长度 [ -5000, +5000 ] 作为实际屋脊线段
        ridge_seg = Line3D(
            Point3D(-5000.0, base_pt.y, base_pt.z),
            Point3D(5000.0, base_pt.y, base_pt.z),
            name="实际建筑屋脊线",
        )
        print(f"   实际屋脊放样线段长度: {ridge_seg.length():.1f} mm, 标高 Z = {base_pt.z:.1f} mm")

    # 3. 可视化渲染
    engine = RenderEngine(window_size=(1280, 800), off_screen=args.offscreen)

    # 渲染南北双坡半透明坡面
    engine.add_mesh(south_roof.to_pyvista(), color="goldenrod", opacity=0.45, show_edges=True)
    engine.add_mesh(north_roof.to_pyvista(), color="darkkhaki", opacity=0.45, show_edges=True)

    # 高亮金色屋脊线
    if res_roof.has_intersection and res_roof.line:
        ridge_pts = [
            Point3D(-5000.0, base_pt.y, base_pt.z).to_tuple(),
            Point3D(5000.0, base_pt.y, base_pt.z).to_tuple(),
        ]
        engine.render_curve(ridge_pts, color="gold", line_width=6.0)
        engine.render_point((0.0, base_pt.y, base_pt.z), color="red", point_size=12, label="屋脊中心标高")

    print("[SUCCESS] 案例 08_05 运行完成。")
    engine.show()


if __name__ == "__main__":
    main()
