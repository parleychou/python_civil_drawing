"""Wrap common PyVista viewport setup in a function."""

import pyvista as pv


def create_engine(
    window_size: tuple[int, int] = (1200, 800),
    background: str = "white",
) -> pv.Plotter:
    """Create a configured PyVista plotter."""
    plotter = pv.Plotter(window_size=window_size)
    plotter.set_background(background)
    plotter.add_axes()
    # plotter.show_grid(
    #     color="lightgray",
    #     grid="back",
    #     location="outer",
    # )
    plotter.camera_position = "iso"
    plotter.enable_trackball_style()
    return plotter


def main() -> None:
    viewer = create_engine()
    beam = pv.Cube(
        center=(3000, 0, 300),
        x_length=6000,
        y_length=300,
        z_length=600,
    )
    viewer.add_mesh(beam, color="tan", show_edges=True)
    viewer.reset_camera()
    viewer.show()


if __name__ == "__main__":
    main()
