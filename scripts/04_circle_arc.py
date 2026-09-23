"""Circle and arc data examples."""

import math
import sys
from pathlib import Path

from geometry_primitives import Arc3D, Circle3D, Point3D

CURRENT_DIR = Path(__file__).resolve().parent
RENDER_ENGINE_DIR = CURRENT_DIR.parents[1] / "04-接入渲染引擎" / "scripts"
sys.path.append(str(RENDER_ENGINE_DIR))

from render_engine import RenderEngine  # noqa: E402


def main() -> None:
    pipe_section = Circle3D(Point3D(0, 0, 0), radius=500, name="Pipe section")
    road_curve = Arc3D(
        Point3D(0, 0, 0),
        radius=3000,
        start_angle=0,
        end_angle=math.pi / 2,
        name="Road curve",
    )

    print("Circle sample count:", len(pipe_section.sample_points()))
    print("Arc start:", road_curve.sample_points()[0])
    print("Arc end:", road_curve.sample_points()[-1])
    print("Circle data structure:", pipe_section.data_structure())
    print("Arc data structure:", road_curve.data_structure())

    # Render scene
    engine = RenderEngine(show_grid=False)
    pipe_section.render(engine)
    road_curve.render(engine)
    engine.print_mouse_controls()
    engine.show()


if __name__ == "__main__":
    main()

