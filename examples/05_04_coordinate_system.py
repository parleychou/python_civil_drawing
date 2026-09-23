"""Coordinate system data example."""

from src import CoordinateSystem3D, Point3D, RenderEngine


def main() -> None:
    local = CoordinateSystem3D(
        origin=Point3D(6000, 3000, 0, name="Local origin"),
        axis_length=1500,
        name="Column local system",
    )

    for axis in local.axes():
        print(axis.name, axis.start.to_tuple(), "->", axis.end.to_tuple())
    print("Coordinate system data structure:", local.data_structure())

    # Render scene
    engine = RenderEngine(show_grid=False)
    local.render(engine)
    engine.print_mouse_controls()
    engine.show()


if __name__ == "__main__":
    main()

