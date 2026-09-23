"""Validate that PyVista can be imported and can create a basic mesh."""

import pyvista as pv


def main() -> None:
    cube = pv.Cube()
    print("PyVista version:", pv.__version__)
    print("Cube points:", cube.n_points)
    print("Cube cells:", cube.n_cells)


if __name__ == "__main__":
    main()
