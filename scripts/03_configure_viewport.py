"""Configure a reusable PyVista viewport style."""

import pyvista as pv


def main() -> None:
    plotter = pv.Plotter(window_size=(1200, 800))
    plotter.set_background("white")
    plotter.add_axes()
    plotter.show_grid(
        color="lightgray",
        grid="back",
        location="outer",
    )
    plotter.camera_position = "iso"
    plotter.enable_trackball_style()

    beam = pv.Cube(
        center=(3000, 0, 300),
        x_length=6000,
        y_length=300,
        z_length=600,
    )
    plotter.add_mesh(beam, color="tan", show_edges=True)
    plotter.show()


if __name__ == "__main__":
    main()
