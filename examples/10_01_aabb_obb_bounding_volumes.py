"""10_01_aabb_obb_bounding_volumes.py — AABB 与 OBB 紧凑包围盒拟合及 SAT 碰撞判定。

演示内容：
1. 建立倾斜 45° 的大截面斜撑钢管构件；
2. 分别计算其 AABB (轴对齐包围盒) 与 OBB (有向紧凑包围盒)；
3. 对比两者的体积紧凑度，展示 AABB 在斜向构件下的“空隙体积膨胀”现象；
4. 引入另一根相近的管线，采用 SAT 分离轴定理 (15 轴) 精确判定空间是否碰撞；
5. 使用 RenderEngine 将构件实体、AABB 线框、OBB 线框与测试轴多重视口联合渲染。

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
    MeshData,
    TransformMatrix,
    RenderEngine,
    AABB,
    OBB,
)
from factories import create_box_mesh
import pyvista as pv


def main():
    parser = argparse.ArgumentParser(description="10_01 AABB 与 OBB 紧凑包围盒拟合及 SAT 碰撞判定")
    parser.add_argument("--offscreen", action="store_true", help="无头离屏运行")
    args = parser.parse_args()

    print("=" * 70)
    print("【案例 10_01】AABB 与 OBB 紧凑包围盒拟合及 SAT 15 轴分离定理分析")
    print("=" * 70)

    # 1. 创建一根长 4000mm、截面 300x300mm 的钢构件
    base_box = create_box_mesh(Point3D(-2000, -150, -150), 4000.0, 300.0, 300.0)

    # 绕 Z 轴旋转 45°，模拟空间斜撑
    rot_mat = TransformMatrix.rotation_z(math.radians(45.0))
    brace_mesh = base_box.transform(rot_mat)
    brace_mesh.name = "INCLINED_BRACE"

    # 2. 计算 AABB
    aabb = AABB.from_mesh(brace_mesh)
    print(f"-> AABB 范围: X[{aabb.min_x:.1f}, {aabb.max_x:.1f}], Y[{aabb.min_y:.1f}, {aabb.max_y:.1f}], Z[{aabb.min_z:.1f}, {aabb.max_z:.1f}]")
    print(f"-> AABB 体积: {aabb.volume / 1e9:.4f} m³")

    # 3. 计算 OBB (利用构件的主轴方向)
    # 主轴 1: (cos45, sin45, 0), 主轴 2: (-sin45, cos45, 0), 主轴 3: (0, 0, 1)
    cos45 = math.cos(math.radians(45.0))
    sin45 = math.sin(math.radians(45.0))
    obb_axes = (
        Vector3D(cos45, sin45, 0.0),
        Vector3D(-sin45, cos45, 0.0),
        Vector3D(0.0, 0.0, 1.0),
    )
    obb = OBB(center=Point3D(0, 0, 0), axes=obb_axes, half_extents=(2000.0, 150.0, 150.0))
    print(f"-> OBB 体积: {obb.volume / 1e9:.4f} m³")
    volume_ratio = aabb.volume / obb.volume
    print(f"-> AABB 体积膨胀率: {volume_ratio:.2f} 倍 (OBB 紧致度高出 {(volume_ratio - 1.0)*100:.1f}%)")

    # 4. 创建邻近构件测试 SAT
    # 构件 2: 放置在斜撑斜上方，与 AABB 重叠，但与 OBB 真实物理分离
    box2 = create_box_mesh(Point3D(1200, 100, 0), 400.0, 400.0, 400.0)
    box2.name = "TEST_BOX"
    aabb2 = AABB.from_mesh(box2)
    obb2 = aabb2.to_obb()

    # 判定 AABB 是否重叠
    aabb_overlap = aabb.overlaps(aabb2)
    # 判定 OBB (SAT) 是否重叠
    obb_overlap = obb.overlaps(obb2)

    print(f"-> AABB 碰撞检测判定: {'【相交】(伪碰撞虚警)' if aabb_overlap else '【分离】'}")
    print(f"-> OBB (SAT 15轴) 判定: {'【真实相交】' if obb_overlap else '【真实空间分离】(成功消除误报)'}")

    # 5. 可视化渲染
    engine = RenderEngine(off_screen=args.offscreen)

    # 渲染构件实体
    engine.render_mesh(brace_mesh, color="steelblue", opacity=0.8)
    engine.render_mesh(box2, color="orange", opacity=0.8)

    # 渲染 AABB 线框 (红色虚警)
    aabb_box_pv = pv.Box(bounds=(aabb.min_x, aabb.max_x, aabb.min_y, aabb.max_y, aabb.min_z, aabb.max_z))
    engine.plotter.add_mesh(aabb_box_pv.outline(), color="red", line_width=2.0)

    # 渲染 OBB 线框 (绿色紧致)
    obb_corners = [
        Point3D(-2000, -150, -150), Point3D(2000, -150, -150),
        Point3D(2000, 150, -150), Point3D(-2000, 150, -150),
        Point3D(-2000, -150, 150), Point3D(2000, -150, 150),
        Point3D(2000, 150, 150), Point3D(-2000, 150, 150),
    ]
    obb_corners_rot = [p.transform(rot_mat) for p in obb_corners]
    obb_mesh = MeshData(
        vertices=tuple(obb_corners_rot),
        faces=(
            (0, 1, 2, 3), (4, 5, 6, 7),
            (0, 1, 5, 4), (2, 3, 7, 6),
            (1, 2, 6, 5), (0, 3, 7, 4),
        )
    )
    engine.plotter.add_mesh(obb_mesh.to_pyvista().outline(), color="green", line_width=3.0)

    if args.offscreen:
        engine.plotter.screenshot("output_10_01.png")
        engine.plotter.close()
    else:
        engine.show()

    print("[SUCCESS] 案例 10_01 运行完成。")


if __name__ == "__main__":
    main()
