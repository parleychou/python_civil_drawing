"""Plane3D — a square plane patch defined by center, normal, and display size."""

import math
from dataclasses import dataclass, field

import numpy as np
import pyvista as pv

from _base import GeometryData
from point3d import Point3D
from vector3d import Vector3D


@dataclass
class Plane3D(GeometryData):
    """A square plane patch defined by center, normal, and display size."""

    center: Point3D = field(default_factory=Point3D)
    normal: Vector3D = field(default_factory=lambda: Vector3D(0, 0, 1))
    size: float = 1000.0

    def to_pyvista(self) -> "pv.DataSet":
        return pv.Plane(
            center=self.center.to_tuple(),
            direction=self.normal.to_tuple(),
            i_size=self.size,
            j_size=self.size,
        )

    def local_axes(self) -> tuple[Vector3D, Vector3D]:
        """Return two orthogonal unit vectors in the plane (local X and Y directions)."""
        z_axis = self.normal.normalized()
        # If normal is standard Z (or parallel to it), return standard X and Y directions
        if abs(z_axis.x) < 1e-9 and abs(z_axis.y) < 1e-9:
            sign = 1.0 if z_axis.z > 0 else -1.0
            return Vector3D(1.0, 0.0, 0.0), Vector3D(0.0, sign, 0.0)

        # Otherwise, compute local X and Y using a stable projection
        # If normal is close to vertical, use Y as helper, else use Z
        if abs(z_axis.z) < 0.9:
            ref = Vector3D(0.0, 0.0, 1.0)
        else:
            ref = Vector3D(0.0, 1.0, 0.0)

        # Compute X and Y axes using cross product
        x_axis = ref.cross(z_axis).normalized()
        y_axis = z_axis.cross(x_axis).normalized()
        return x_axis, y_axis

    def render(self, engine, color: str = "steelblue", show_edges: bool = True) -> None:
        """Render the plane patch, and its normal direction as an arrow from the center."""
        # Render the plane patch
        engine.add_mesh(self.to_pyvista(), color=color, show_edges=show_edges, opacity=0.5)
        # Render the normal vector (scaled by size * 0.25 to make it proportional)
        normal_length = self.size * 0.25
        scaled_normal = self.normal.normalized().scale(normal_length)
        scaled_normal.render(engine, base_point=self.center, color="darkred", show_edges=show_edges)
