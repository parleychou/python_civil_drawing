"""Render points and a polyline curve with the course RenderEngine."""

import sys
from pathlib import Path
_SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))


from render_engine import RenderEngine


def main() -> None:
    engine = RenderEngine()

    points = [
        (0, 0, 0),
        (3000, 0, 0),
        (6000, 1200, 0),
        (9000, 1200, 800),
    ]

    engine.render_point(points[0], label="Start")
    engine.render_points(points[1:], color="orange")
    engine.render_curve(points, color="steelblue", line_width=6)
    engine.print_mouse_controls()
    engine.show()


if __name__ == "__main__":
    main()
