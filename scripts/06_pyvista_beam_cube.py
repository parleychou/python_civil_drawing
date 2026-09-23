"""PyVista example: create a beam-like cube mesh."""

import pyvista as pv


def main() -> None:
    beam = pv.Cube(
        center=(3000, 0, 300),
        x_length=6000,
        y_length=300,
        z_length=600,
    )
    print("Points:", beam.n_points)
    print("Cells:", beam.n_cells)
    print("Bounds:", beam.bounds)

    # For interactive rendering, uncomment the lines below.
    plotter = pv.Plotter()
    # add_mesh 常用参数说明：
    #   mesh          - 要渲染的网格对象（PolyData / UnstructuredGrid 等）
    #   color         - 颜色，如 "tan"、(0.8, 0.6, 0.4)、"white"
    #   style         - 渲染风格："surface"（默认）、"wireframe"、"points"
    #   show_edges    - 是否显示单元边线，默认 False
    #   edge_color    - 边线颜色，默认 "black"
    #   line_width    - 线宽，默认 1.0
    #   opacity       - 不透明度 0.0~1.0，默认 1.0
    #   scalars       - 用于着色的标量数组名或数组
    #   cmap          - 颜色映射名，如 "coolwarm"、"jet"、"viridis"
    #   clim          - 标量范围 [min, max]，配合 cmap 使用
    #   show_scalar_bar - 是否显示颜色条，默认 True（需有 scalars）
    #   lighting      - 是否启用光照，默认 True
    #   smooth_shading - 是否平滑着色，默认 False
    #   log_scale     - 标量是否用对数刻度，默认 False
    #   rgb           - 传入的 scalars 是否为 RGB 颜色数组，默认 False
    #   pbr           - 是否启用 PBR 物理渲染，默认 False
    #   metallic      - PBR 金属度 0.0~1.0
    #   roughness     - PBR 粗糙度 0.0~1.0
    plotter.add_mesh(beam, color="tan", show_edges=True)
    plotter.add_axes()
    plotter.show()


if __name__ == "__main__":
    main()
