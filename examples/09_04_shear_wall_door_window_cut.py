"""09_04_shear_wall_door_window_cut.py — 剪力墙参数化门窗洞口布尔差集切除。

演示结构深化设计中的实体差集 (Difference / Cut)：
1. 建立 6000mm x 200mm x 3000mm 混凝土剪力墙；
2. 参数化构建标准入户门洞 (900mm x 2100mm) 与高窗 (1200mm x 1000mm)；
3. 应用外扩刀具消除共面退化，执行布尔差集切除；
4. 统计混凝土净体积与开洞减损量，输出洞口内侧壁网格。

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
    RenderEngine,
)


def main():
    parser = argparse.ArgumentParser(description="09_04 剪力墙门窗布尔差集开洞")
    parser.add_argument("--offscreen", action="store_true", help="无头离屏运行")
    args = parser.parse_args()

    print("=" * 70)
    print("【案例 09_04】混凝土剪力墙参数化门窗洞口布尔差集深化切除")
    print("=" * 70)

    # 1. 剪力墙: 长 6m, 厚 0.2m, 高 3m (原体积 3.6 m³)
    wall = create_box_mesh(Point3D(0.0, 0.0, 0.0), 6.0, 0.2, 3.0)
    orig_vol = wall.to_pyvista().volume
    print(f"-> 原始实心剪力墙体积: {orig_vol:.3f} m³")

    # 2. 门洞切割体: X in [1.0, 1.9], Y in [-0.1, 0.3] (外扩消除共面), Z in [-0.05, 2.1]
    # 切除净体积: 0.9 * 0.2 * 2.1 = 0.378 m³
    door_cutter = create_box_mesh(Point3D(1.0, -0.1, -0.05), 0.9, 0.4, 2.15)

    # 3. 窗洞切割体: X in [3.5, 4.7], Y in [-0.1, 0.3], Z in [1.2, 2.2]
    # 切除净体积: 1.2 * 0.2 * 1.0 = 0.240 m³
    window_cutter = create_box_mesh(Point3D(3.5, -0.1, 1.2), 1.2, 0.4, 1.0)

    # 4. 连续执行布尔差集
    res1 = wall.cut(door_cutter)
    opened_wall = res1.mesh
    res2 = opened_wall.cut(window_cutter)
    final_wall = res2.mesh

    final_vol = final_wall.to_pyvista().volume
    expected_vol = orig_vol - 0.378 - 0.240
    print(f"-> 门洞切除体积: 0.378 m³")
    print(f"-> 窗洞切除体积: 0.240 m³")
    print(f"-> 开洞后实测剩余体积: {final_vol:.3f} m³ (理论净体积: {expected_vol:.3f} m³)")

    # 5. 渲染
    engine = RenderEngine(off_screen=args.offscreen)
    engine.plotter.add_mesh(final_wall.to_pyvista(), color="#94A3B8", show_edges=True)

    if args.offscreen:
        engine.plotter.screenshot("output_09_04.png")
        engine.plotter.close()
    else:
        engine.show()

    print("[SUCCESS] 案例 09_04 运行完成。")


if __name__ == "__main__":
    main()
