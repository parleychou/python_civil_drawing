"""Use the reusable RenderEngine class."""

import sys
from pathlib import Path
_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))


import pyvista as pv

from render_engine import RenderEngine


def main() -> None:
    engine = RenderEngine()

    column = pv.Cube(
        center=(0, 0, 1800),
        x_length=600,
        y_length=600,
        z_length=3600,
    )
    beam = pv.Cube(
        center=(3000, 0, 3300),
        x_length=6000,
        y_length=300,
        z_length=600,
    )
    marker = pv.Sphere(center=(6000, 0, 3600), radius=220)

    engine.add_mesh(column, color="lightgray", show_edges=True)
    engine.add_mesh(beam, color="tan", show_edges=True)
    engine.add_mesh(marker, color="orange", show_edges=False)
    engine.print_mouse_controls()
    engine.show()


if __name__ == "__main__":
    main()
