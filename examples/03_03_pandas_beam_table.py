"""Pandas example: build a beam quantity table."""

import pandas as pd


def main() -> None:
    beams = pd.DataFrame(
        {
            "id": ["B1", "B2"],
            "length_m": [6.0, 7.5],
            "width_m": [0.3, 0.3],
            "height_m": [0.6, 0.7],
        }
    )
    beams["volume_m3"] = (
        beams["length_m"] * beams["width_m"] * beams["height_m"]
    )
    print(beams)


if __name__ == "__main__":
    main()
