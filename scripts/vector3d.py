"""Vector3D — direction and magnitude in 3D space."""

import math
from dataclasses import dataclass

import numpy as np
import pyvista as pv

from _base import GeometryData, PointTuple


@dataclass
class Vector3D(GeometryData):
    """A direction and magnitude in 3D space."""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __repr__(self) -> str:
        label = f", name={self.name!r}" if self.name else ""
        return f"Vector3D(x={self.x!r}, y={self.y!r}, z={self.z!r}{label})"

    def to_tuple(self) -> PointTuple:
        return (float(self.x), float(self.y), float(self.z))

    def to_array(self) -> np.ndarray:
        return np.array(self.to_tuple(), dtype=float)

    def length(self) -> float:
        return float(np.linalg.norm(self.to_array()))

    def normalized(self) -> "Vector3D":
        length = self.length()
        if length < 1e-12:
            raise ValueError("Zero vector cannot be normalized")
        arr = self.to_array() / length
        return Vector3D(float(arr[0]), float(arr[1]), float(arr[2]))

    def scale(self, factor: float) -> "Vector3D":
        return Vector3D(self.x * factor, self.y * factor, self.z * factor)

    def __add__(self, other: "Vector3D") -> "Vector3D":
        """Add two vectors together."""
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Vector3D") -> "Vector3D":
        """Subtract one vector from another."""
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def dot(self, other: "Vector3D") -> float:
        """Calculate the dot product of two vectors."""
        return float(self.x * other.x + self.y * other.y + self.z * other.z)

    def cross(self, other: "Vector3D") -> "Vector3D":
        """Calculate the cross product of two vectors."""
        return Vector3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def to_pyvista(self) -> "pv.DataSet":
        length = self.length()
        if length < 1e-12:
            return pv.PointSet(np.zeros((1, 3)))
        return pv.Arrow(
            start=np.zeros(3),
            direction=np.array([self.x, self.y, self.z]),
            scale=length,
        )

    def render(
        self,
        engine,
        base_point: "Point3D | None" = None,
        color: str = "coral",
        show_edges: bool = True,
    ) -> None:
        """Render this vector in the viewport starting from a base point.

        Uses a line and arrow tip (via pyvista.Arrow) to represent the vector.
        """
        from point3d import Point3D  # deferred – circular

        if base_point is None:
            base_point = Point3D(0, 0, 0)

        length = self.length()
        if length < 1e-12:
            return

        arrow = pv.Arrow(
            start=base_point.to_tuple(),
            direction=self.to_tuple(),
            scale=length,
        )
        engine.add_mesh(arrow, color=color, show_edges=show_edges)
