"""Render basic geometry data through the course RenderEngine."""

from __future__ import annotations

import math

from src import (
    Arc3D,
    Circle3D,
    CoordinateSystem3D,
    Line3D,
    Plane3D,
    Point3D,
    RenderEngine,
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
