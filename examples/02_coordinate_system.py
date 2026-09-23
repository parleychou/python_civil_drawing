"""Coordinate system data example."""

import sys
from pathlib import Path
_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))


import sys
from pathlib import Path

from geometry_primitives import CoordinateSystem3D, Point3D

CURRENT_DIR = Path(__file__).resolve().parent
RENDER_ENGINE_DIR = CURRENT_DIR.parents[1] / "04-接入渲染引擎" / "scripts"
sys.path.append(str(RENDER_ENGINE_DIR))

from render_engine import RenderEngine  # noqa: E402


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

