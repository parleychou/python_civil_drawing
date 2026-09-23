import numpy as np
import pyvista as pv

#for 循环

# 函数，参数，变量

def render_beam(height,color):
    beam = pv.Cube(
        center=(300, 0, height),
        x_length=6000,
        y_length=300,
        z_length=600,
    )
    plotter.add_mesh(beam, color=color, show_edges=True)

heights= np.linspace(0,30000,10)
print(heights)
plotter = pv.Plotter()

#if else 选择函数操作
for height in heights:
    if height<15000:
        render_beam(height,"green")
    else:
        render_beam(height,"red")


plotter.show()