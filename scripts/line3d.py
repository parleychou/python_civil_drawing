"""Line3D — a finite line segment defined by two endpoints."""

import math
from dataclasses import dataclass, field

import numpy as np
import pyvista as pv

from curve import Curve
from point3d import Point3D


@dataclass
class Line3D(Curve):
    """A finite line segment defined by two endpoints."""

    start: Point3D = field(default_factory=Point3D)
    end: Point3D = field(default_factory=lambda: Point3D(1, 0, 0))

    def point_at(self, t: float) -> "Point3D":
        """Return the linear interpolation between start (t=0) and end (t=1)."""
        arr = self.start.to_array() * (1.0 - t) + self.end.to_array() * t
        return Point3D(float(arr[0]), float(arr[1]), float(arr[2]))

    def direction(self) -> "Vector3D":
        from vector3d import Vector3D  # deferred – circular

        return self.end - self.start

    def length(self) -> float:
        return self.start.distance_to(self.end)

    def sample_points(self, count: int = 2) -> "list[Point3D]":
        return super().sample_points(count)

    def to_pyvista_native(self) -> "pv.DataSet":
        """Convert this line segment to a PyVista dataset using PyVista's built-in pv.Line as reference."""
        return pv.Line(
            pointa=self.start.to_tuple(),
            pointb=self.end.to_tuple(),
            resolution=1,
        )


Line3d = Line3D
