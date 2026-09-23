"""Shapely example: check pipe-wall intersection in 2D."""

from shapely.geometry import LineString, Polygon


def main() -> None:
    pipe = LineString([(0, 0), (8000, 0)])
    wall = Polygon(
        [
            (3000, -200),
            (5000, -200),
            (5000, 200),
            (3000, 200),
        ]
    )

    print("Intersects:", pipe.intersects(wall))
    print("Intersection length:", pipe.intersection(wall).length)


if __name__ == "__main__":
    main()
