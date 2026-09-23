"""SciPy example: calculate distances between column centers."""

import numpy as np
from scipy.spatial.distance import cdist


def main() -> None:
    columns = np.array(
        [
            [0.0, 0.0],
            [6000.0, 0.0],
            [6000.0, 6000.0],
        ]
    )
    distances = cdist(columns, columns)
    print(distances)


if __name__ == "__main__":
    main()
