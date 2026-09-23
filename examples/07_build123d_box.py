"""build123d example: create and export a simple beam-like solid."""

from pathlib import Path

from build123d import Box, export_stl


def main() -> None:
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(exist_ok=True)

    beam = Box(6000, 300, 600)
    output_file = output_dir / "build123d_beam.stl"
    export_stl(beam, output_file)

    print("Solid type:", type(beam))
    print("Exported STL:", output_file)


if __name__ == "__main__":
    main()
