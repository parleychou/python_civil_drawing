"""Point and vector data examples."""

from src import Point3D, RenderEngine


def main() -> None:
    column_center = Point3D(6000, 3000, 0, name="C1")
    beam_end = Point3D(12000, 3000, 0, name="B1 end")
    direction = beam_end - column_center

    print("Column center:", column_center)
    print("Beam direction:", direction)
    print("Direction length:", direction.length(), "mm")
    print("Point data structure:", column_center.data_structure())
    print("Vector data structure:", direction.data_structure())

    # Render scene
    engine = RenderEngine(show_grid=False)
    column_center.render(engine)
    beam_end.render(engine)
    direction.render(engine, base_point=column_center)
    engine.print_mouse_controls()
    engine.show()


if __name__ == "__main__":
    main()

