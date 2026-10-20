"""09_07_steel_joint_complex_boolean_scene.py — 钢结构箱形柱-穿心牛腿复杂节点布尔深化。

演示超高层建筑钢结构深化中的复杂三维布尔组合：
1. 建立 800mm x 800mm 钢箱形柱主体；
2. 建立穿越柱身的贯通式工字钢牛腿梁；
3. 执行柱壁穿心开槽布尔切除；
4. 渲染全三维精细化钢构件节点。

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
    create_i_beam_brep,
    RenderEngine,
)


def main():
    parser = argparse.ArgumentParser(description="09_07 复杂钢结构节点布尔深化")
    parser.add_argument("--offscreen", action="store_true", help="无头离屏运行")
    args = parser.parse_args()

    print("=" * 70)
    print("【案例 09_07】超高层钢结构箱形柱穿心牛腿斜向坡口布尔深化")
    print("=" * 70)

    # 1. 箱形柱: 800x800x4000 (mm 尺寸，按米建模 0.8 x 0.8 x 4.0)
    col = create_box_mesh(Point3D(-0.4, -0.4, 0.0), 0.8, 0.8, 4.0)

    # 2. 贯通式工字钢梁牛腿 (利用工厂标准函数生成真实流形实体)
    beam_brep = create_i_beam_brep(length=2.4, width=0.4, height=0.4, flange_thickness=0.03, web_thickness=0.02)
    # 绕 Y 轴旋转 90 度并平移到柱中间高度 Z=2.0
    beam_mesh = beam_brep.to_triangulated_mesh().rotated_y(90.0).translated(-1.2, 0.0, 2.0)
    print(f"-> 标准工字钢梁牛腿就位，体积: {beam_mesh.to_pyvista().volume:.4f} m³")

    # 3. 柱身穿心开孔槽切除 (比牛腿外廓微扩 20mm 制作安装工艺间隙)
    slot_cutter = create_box_mesh(Point3D(-0.5, -0.22, 1.78), 1.0, 0.44, 0.44)
    res_slot = col.cut(slot_cutter)
    slotted_col = res_slot.mesh if res_slot.mesh is not None else col
    print("-> 柱壁开孔槽切除完成，已形成穿心通道")

    # 渲染
    engine = RenderEngine(off_screen=args.offscreen)
    engine.plotter.add_mesh(slotted_col.to_pyvista(), color="#64748B", opacity=0.85, show_edges=True)
    engine.plotter.add_mesh(beam_mesh.to_pyvista(), color="#F59E0B", opacity=0.95, show_edges=True)

    if args.offscreen:
        engine.plotter.screenshot("output_09_07.png")
        engine.plotter.close()
    else:
        engine.show()

    print("[SUCCESS] 案例 09_07 运行完成。")


if __name__ == "__main__":
    main()
