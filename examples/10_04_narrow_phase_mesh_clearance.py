"""10_04_narrow_phase_mesh_clearance.py — 窄阶段精检：硬碰撞穿透体积与软碰撞最小净距解算。

演示内容：
1. 建立钢筋混凝土大梁与穿越的空调风管；
2. 场景 A（硬碰撞 Hard Clash）：风管标高直接穿入结构梁腹板，精确解算穿透体积、侵入深度与冲突质心；
3. 场景 B（软碰撞 Soft Clash）：排污管道布置在梁底正下方 45mm 处，虽然物理无重叠，但侵入 100mm 最小安全检修缓冲区，触发软碰撞间距告警；
4. 使用 RenderEngine 将结构梁、机电管道、硬碰撞相交实体与软碰撞净距缓冲区进行多重视口对比渲染。

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
    MeshData,
    RenderEngine,
    check_narrow_phase_clash,
    calculate_mesh_minimum_clearance,
    ClashType,
)
from factories import create_box_mesh
import pyvista as pv


def main():
    parser = argparse.ArgumentParser(description="10_04 窄阶段精检与软硬碰撞解算")
    parser.add_argument("--offscreen", action="store_true", help="无头离屏运行")
    args = parser.parse_args()

    print("=" * 70)
    print("【案例 10_04】窄阶段网格精检：硬穿透体积与软碰撞空间净距解算")
    print("=" * 70)

    # 1. 建立结构大梁 (截面 400x700, 长 6000mm)
    beam_mesh = create_box_mesh(Point3D(0, 0, 2700), 6000.0, 400.0, 700.0)
    beam_mesh.name = "BEAM_CONCRETE"

    # 2. 场景 A: 暖通风管直接穿梁 (硬碰撞)
    # 风管尺寸: 宽 800, 高 350, 跨越梁身
    duct_mesh = create_box_mesh(Point3D(2000, -500, 2900), 800.0, 1400.0, 350.0)
    duct_mesh.name = "HVAC_DUCT"

    # 执行窄阶段硬碰撞判定
    rec_hard = check_narrow_phase_clash(
        id_a="BEAM_CONCRETE",
        mesh_a=beam_mesh,
        id_b="HVAC_DUCT",
        mesh_b=duct_mesh,
        clearance=0.0,
        system_a="Structure",
        system_b="HVAC",
    )

    print("\n--- [场景 A: 结构梁 vs 暖通风管 (硬碰撞)] ---")
    if rec_hard:
        print(f"-> 冲突类型: {rec_hard.clash_type.value} ({rec_hard.severity.value})")
        print(f"-> 冲突几何位置: ({rec_hard.location.x:.1f}, {rec_hard.location.y:.1f}, {rec_hard.location.z:.1f})")
        print(f"-> 穿透深度: {rec_hard.penetration_depth:.1f} mm")
        print(f"-> 穿透体积: {rec_hard.penetration_volume / 1e6:.3f} L")
        print(f"-> 整改建议: {rec_hard.recommendation}")

    # 3. 场景 B: 给排水主管敷设在梁底下方 (软碰撞)
    # 梁底高程为 2700mm，管道顶部位于 2655mm，实测空间净距为 2700 - 2655 = 45mm
    pipe_mesh = create_box_mesh(Point3D(4200, -500, 2455), 200.0, 1400.0, 200.0)
    pipe_mesh.name = "PLUMBING_PIPE"

    # 解算两网格物理净距
    measured_clearance = calculate_mesh_minimum_clearance(beam_mesh, pipe_mesh)
    required_clearance = 100.0  # 规范要求结构底与有压管线保留 100mm 检修净距

    rec_soft = check_narrow_phase_clash(
        id_a="BEAM_CONCRETE",
        mesh_a=beam_mesh,
        id_b="PLUMBING_PIPE",
        mesh_b=pipe_mesh,
        clearance=required_clearance,
        system_a="Structure",
        system_b="Plumbing",
    )

    print("\n--- [场景 B: 结构梁底 vs 给排水管 (软碰撞安全间距)] ---")
    print(f"-> 实测空间物理净距: {measured_clearance:.1f} mm (规范要求: {required_clearance:.1f} mm)")
    if rec_soft:
        print(f"-> 冲突类型: {rec_soft.clash_type.value} ({rec_soft.severity.value})")
        print(f"-> 侵入缓冲区深度: {rec_soft.penetration_depth:.1f} mm")
        print(f"-> 整改建议: {rec_soft.recommendation}")

    # 4. 可视化渲染
    engine = RenderEngine(off_screen=args.offscreen)

    # 渲染混凝土梁 (半透明灰色)
    engine.render_mesh(beam_mesh, color="darkgray", opacity=0.7)
    # 渲染风管 (硬碰撞红色)
    engine.render_mesh(duct_mesh, color="crimson", opacity=0.85)
    # 渲染水管 (软碰撞黄色)
    engine.render_mesh(pipe_mesh, color="gold", opacity=0.9)

    # 渲染硬碰撞实体相交包围块 (高亮洋红)
    if rec_hard:
        inter_box = pv.Box(bounds=(
            2000, 2800,
            0, 400,
            2900, 3250
        ))
        engine.plotter.add_mesh(inter_box, color="magenta", opacity=0.9)

    # 渲染软碰撞间距指示标线 (青色)
    engine.render_curve([(4300, 200, 2700), (4300, 200, 2655)], color="cyan", line_width=4.0)

    if args.offscreen:
        engine.plotter.screenshot("output_10_04.png")
        engine.plotter.close()
    else:
        engine.show()

    print("[SUCCESS] 案例 10_04 运行完成。")


if __name__ == "__main__":
    main()
