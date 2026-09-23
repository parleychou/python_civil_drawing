"""Render basic geometry data through the course RenderEngine."""

import sys
from pathlib import Path
_SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))


from __future__ import annotations

import math
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
RENDER_ENGINE_DIR = CURRENT_DIR.parents[1] / "04-接入渲染引擎" / "scripts"
sys.path.append(str(RENDER_ENGINE_DIR))

from render_engine import RenderEngine  # noqa: E402
from geometry_primitives import (  # noqa: E402
    Arc3D,
    Circle3D,
    CoordinateSystem3D,
    Line3D,
    Plane3D,
    Point3D,
    Vector3D,
)


def main() -> None:
    engine = RenderEngine(show_grid=False)
    objects = [
        CoordinateSystem3D(axis_length=1500, name="Global"),
        Point3D(6000, 3000, 0, name="Column center"),
        Line3D(Point3D(0, 0, 3300), Point3D(6000, 0, 3300), name="Beam axis"),
        Plane3D(Point3D(3000, 0, 0), Vector3D(0, 0, 1), size=7000, name="Floor"),
        Circle3D(Point3D(0, 0, 0), radius=500, name="Pipe section"),
        Arc3D(Point3D(0, 0, 0), radius=3000, start_angle=0, end_angle=math.pi / 2),
    ]

    for item in objects:
        item.render(engine)

    engine.print_mouse_controls()
    engine.show()


if __name__ == "__main__":
    main()
