"""Point3D — a point in 3D engineering coordinates."""

import math
from dataclasses import dataclass

import numpy as np
import pyvista as pv

from _base import GeometryData, PointTuple


@dataclass
class Point3D(GeometryData):
    """A point in 3D engineering coordinates."""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __repr__(self) -> str:
        label = f", name={self.name!r}" if self.name else ""
        return f"Point3D(x={self.x!r}, y={self.y!r}, z={self.z!r}{label})"

    def __sub__(self, other: "Point3D") -> "Vector3D":
        from vector3d import Vector3D  # deferred – circular

        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def to_tuple(self) -> PointTuple:
        return (float(self.x), float(self.y), float(self.z))

    def to_array(self) -> np.ndarray:
        return np.array(self.to_tuple(), dtype=float)

    def distance_to(self, other: "Point3D") -> float:
        return float(np.linalg.norm(self.to_array() - other.to_array()))

    def to_pyvista(self) -> "pv.DataSet":
        return pv.PolyData([self.to_tuple()])

    def render(self, engine, color: str = "coral", show_edges: bool = True) -> None:
        engine.render_point(self.to_tuple(), color=color, label=self.name or None)
