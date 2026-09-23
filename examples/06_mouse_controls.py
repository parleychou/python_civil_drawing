"""Print the mouse controls used by the course render engine."""

import sys
from pathlib import Path
_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))


from render_engine import RenderEngine


def main() -> None:
    RenderEngine.print_mouse_controls()


if __name__ == "__main__":
    main()
