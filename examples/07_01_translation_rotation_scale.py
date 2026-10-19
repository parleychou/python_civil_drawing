"""07_01_translation_rotation_scale.py — 基础平移、旋转与缩放矩阵演示。

展示在空间中对几何长方体应用三大基础仿射变换：
- 原始构件：位于原点，以半透明浅灰色表示；
- 平移构件：沿向量 (1500, 1000, 500) 平移，以珊瑚红 (coral) 显示；
- 旋转构件：绕 Z 轴旋转 45°，以钢青色 (steelblue) 显示；
- 缩放构件：沿 X 轴拉伸 1.5 倍，Y 轴缩放 0.6 倍，以橘黄色 (orange) 显示。

命令行参数：
- --offscreen：离线后台渲染模式，用于单元测试或批量出图。
"""

import argparse
import math
import sys
from pathlib import Path

# Ensure src is importable
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src import (
    Point3D,
    Vector3D,
    TransformMatrix,
    create_box_brep,
    RenderEngine,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="演示 4x4 基础平移、旋转与缩放矩阵")
    parser.add_argument("--offscreen", action="store_true", help="启用无头渲染模式")
    args = parser.parse_args()

    # 1. 建立基础构件 (长方体 600 x 400 x 800)
    base_box = create_box_brep(width=600.0, depth=400.0, height=800.0)

    # 2. 构建三大基础变换矩阵
    # (a) 平移矩阵
    t_mat = TransformMatrix.translation(1500.0, 1000.0, 500.0)
    translated_box = base_box.transform(t_mat)

    # (b) 旋转矩阵 (绕 Z 轴旋转 45 度)
    r_mat = TransformMatrix.rotation_z(math.radians(45.0))
    rotated_box = base_box.transform(r_mat)

    # (c) 非等比缩放矩阵
    s_mat = TransformMatrix.scaling(1.5, 0.6, 1.0)
    scaled_box = base_box.transform(s_mat)

    # 3. 接入渲染引擎
    engine = RenderEngine(window_size=(1280, 800), off_screen=args.offscreen)

    # 原始构件 (半透明参考)
    engine.add_mesh(base_box.to_pyvista(), color="lightgray", opacity=0.4)
    engine.add_mesh(base_box.get_edges_polydata(), color="dimgray")

    # 平移构件
    engine.add_mesh(translated_box.to_pyvista(), color="coral", opacity=0.85)
    engine.add_mesh(translated_box.get_edges_polydata(), color="darkred")

    # 旋转构件
    engine.add_mesh(rotated_box.to_pyvista(), color="steelblue", opacity=0.85)
    engine.add_mesh(rotated_box.get_edges_polydata(), color="navy")

    # 缩放构件
    engine.add_mesh(scaled_box.to_pyvista(), color="orange", opacity=0.85)
    engine.add_mesh(scaled_box.get_edges_polydata(), color="saddlebrown")

    # 添加文字标注
    engine.plotter.add_point_labels(
        [
            (300.0, 200.0, 850.0),
            (1800.0, 1200.0, 1350.0),
            (200.0, 500.0, 850.0),
            (500.0, 100.0, 850.0),
        ],
        ["Original (0,0,0)", "Translated (+1500, +1000, +500)", "Rotated Z (45°)", "Scaled (1.5, 0.6, 1.0)"],
        font_size=12,
        point_color="black",
        text_color="black",
        shadow=False,
    )

    if not args.offscreen:
        print("展示 4x4 基础平移、旋转与缩放效果视口...")
        engine.plotter.show()
    else:
        print("离线模式：场景构件加载校验成功。")


if __name__ == "__main__":
    main()
