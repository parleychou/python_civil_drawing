"""Print the mouse controls used by the course render engine."""

import sys
from pathlib import Path
_SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))


from render_engine import RenderEngine


def main() -> None:
    RenderEngine.print_mouse_controls()


if __name__ == "__main__":
    main()
