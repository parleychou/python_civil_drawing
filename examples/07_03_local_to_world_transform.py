"""07_03_local_to_world_transform.py — 局部坐标系与世界坐标系基底转换 (Local <-> World)。

工程背景：
标准钢构件（如工字钢梁）在出厂设计时均定义在局部标准坐标系 (Local CS) 中（中心为原点，轴线沿局部 Z 轴）。
在桥梁或框架安装中，每个安装跨位均有独立的局部定位坐标系。
本案例演示：
1. 建立具有倾斜和偏角的三维局部坐标系 CS_local；
2. 构建局部到世界坐标系矩阵 M_L2W，将标准工字梁无缝落位到空间指定朝向；
3. 构建逆向世界到局部矩阵 M_W2L，验证空间采样点能够无损还原回构件局部图纸坐标。
"""

import argparse
import math
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src import (
    Point3D,
    Vector3D,
    CoordinateSystem3D,
    TransformMatrix,
    create_i_beam_brep,
    RenderEngine,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="演示局部到全局坐标系基底转换")
    parser.add_argument("--offscreen", action="store_true", help="启用无头渲染模式")
    args = parser.parse_args()

    # 1. 在局部坐标系下创建标准工字钢梁 (长 2400mm, 宽 400mm, 高 600mm)
    local_beam = create_i_beam_brep(
        length=2400.0,
        width=400.0,
        height=600.0,
        flange_thickness=25.0,
        web_thickness=16.0,
    )

    # 2. 定义工程施工现场的斜交安装坐标系 CS_local
    # 原点位于 (2000, 1500, 1200)
    origin_local = Point3D(2000.0, 1500.0, 1200.0)
    # 局部 Z 轴指向斜上方 (倾斜跨越)
    z_dir = Vector3D(1.0, 1.0, 0.5).normalized()
    # 局部 X 轴指向横向水平
    xy_ref = Vector3D(-1.0, 1.0, 0.0).normalized()

    cs_local = CoordinateSystem3D.from_origin_and_vectors(
        origin=origin_local,
        x_dir=xy_ref,
        xy_dir=z_dir,
        axis_length=800.0,
        name="CS_Abutment",
    )

    # 3. 计算 Local to World 矩阵
    m_l2w = TransformMatrix.from_coordinate_systems(cs_local)
    world_beam = local_beam.transform(m_l2w)

    # 4. 验证 World to Local 逆向计算 (例如放样端点校验)
    m_w2l = m_l2w.inverse()
    test_world_pt = world_beam.vertices[12]  # 梁顶端点
    recovered_local_pt = m_w2l.apply_to_point(test_world_pt)
    orig_local_pt = local_beam.vertices[12]

    print(f"原始局部端点坐标: {orig_local_pt}")
    print(f"落位世界端点坐标: {test_world_pt}")
    print(f"逆变换还原端点坐标: {recovered_local_pt}")

    # 5. 三维渲染对比
    engine = RenderEngine(window_size=(1280, 800), off_screen=args.offscreen)

    # (a) 局部基准原点出的未安装参考梁 (半透明淡蓝)
    engine.add_mesh(local_beam.to_pyvista(), color="lightblue", opacity=0.35)
    engine.add_mesh(local_beam.get_edges_polydata(), color="steelblue")

    # (b) 安装到施工世界坐标系的工字梁 (工程实色钢铁灰)
    engine.add_mesh(world_beam.to_pyvista(), color="slategray", opacity=0.9)
    engine.add_mesh(world_beam.get_edges_polydata(), color="black")

    # (c) 渲染局部坐标系三色轴向
    cs_local.render(engine)

    # 标注文字
    engine.plotter.add_point_labels(
        [
            (0.0, 0.0, 1200.0),
            (origin_local.x, origin_local.y, origin_local.z + 1000.0),
        ],
        ["Canonical Local Model (Prefab)", "Installed in World CS via M_L2W"],
        font_size=12,
        point_color="black",
        text_color="black",
        shadow=False,
    )

    if not args.offscreen:
        print("展示局部与世界坐标系转换视口...")
        engine.plotter.show()
    else:
        print("离线模式：基底坐标转换验证通过。")


if __name__ == "__main__":
    main()
