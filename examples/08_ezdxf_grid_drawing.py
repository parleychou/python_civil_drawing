"""ezdxf example: write a simple DXF grid drawing."""

from pathlib import Path

import ezdxf


def main() -> None:
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(exist_ok=True)

    document = ezdxf.new("R2010")
    modelspace = document.modelspace()
    modelspace.add_line((0, 0), (12000, 0))
    modelspace.add_circle((6000, 0), radius=300)
    modelspace.add_text("Grid A", height=250).set_placement((0, 400))

    output_path = output_dir / "grid.dxf"
    document.saveas(output_path)
    print("Saved:", output_path)


if __name__ == "__main__":
    main()
