"""Line and plane data examples."""

import sys
from pathlib import Path

from geometry_primitives import Line3D, Plane3D, Point3D, Vector3D

CURRENT_DIR = Path(__file__).resolve().parent
RENDER_ENGINE_DIR = CURRENT_DIR.parents[1] / "04-接入渲染引擎" / "scripts"
sys.path.append(str(RENDER_ENGINE_DIR))

from render_engine import RenderEngine  # noqa: E402


def main() -> None:
    beam_axis = Line3D(
        start=Point3D(0, 0, 3300, name="B1 start"),
        end=Point3D(6000, 0, 3300, name="B1 end"),
        name="B1 axis",
    )
    floor_plane = Plane3D(
        center=Point3D(3000, 0, 0),
        normal=Vector3D(0, 0, 1),
        size=7000,
        name="Floor plane",
    )

    print("Line length:", beam_axis.length(), "mm")
    print("Plane normal:", floor_plane.normal.normalized())
    print("Line data structure:", beam_axis.data_structure())
    print("Plane data structure:", floor_plane.data_structure())

    # Render scene
    engine = RenderEngine(show_grid=False)
    beam_axis.render(engine)
    floor_plane.render(engine)
    engine.print_mouse_controls()
    engine.show()


if __name__ == "__main__":
    main()

