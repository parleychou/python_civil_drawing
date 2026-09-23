"""Render a beam-like cube with PyVista."""

import pyvista as pv


def main() -> None:
    beam = pv.Cube(
        center=(3000, 0, 300),
        x_length=6000,
        y_length=300,
        z_length=600,
    )

    plotter = pv.Plotter()
    plotter.add_mesh(beam, color="tan", show_edges=True)
    plotter.add_axes()
    plotter.show()


if __name__ == "__main__":
    main()
