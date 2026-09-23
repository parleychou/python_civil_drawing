"""Circle3D — a circle in the XY plane."""

import math
from dataclasses import dataclass, field

import numpy as np
import pyvista as pv

from curve import Curve
from point3d import Point3D
from plane3d import Plane3D


@dataclass
class Circle3D(Curve):
    """A circle in 3D space, defined by a plane (or center) and a radius."""

    center: Point3D = field(default_factory=Point3D)
    radius: float = 1.0
    plane: Plane3D | None = None

    def __post_init__(self):
        if self.plane is None:
            from vector3d import Vector3D
            self.plane = Plane3D(center=self.center, normal=Vector3D(0, 0, 1))
        else:
            self.center = self.plane.center

    def point_at(self, t: float) -> "Point3D":
        """Return the point at parameter t (0 <= t <= 1) along the 3D circle."""
        angle = 2.0 * math.pi * t
        u, v = self.plane.local_axes()
        
        # Calculate offset in 3D using local basis of the plane
        offset_u = u.scale(self.radius * math.cos(angle))
        offset_v = v.scale(self.radius * math.sin(angle))
        
        return Point3D(
            self.center.x + offset_u.x + offset_v.x,
            self.center.y + offset_u.y + offset_v.y,
            self.center.z + offset_u.z + offset_v.z,
        )

    def sample_points(self, count: int = 72) -> "list[Point3D]":
        return super().sample_points(count)

    def to_pyvista_native(self, count: int = 72) -> "pv.DataSet":
        """Convert this circle to PyVista dataset using PyVista's built-in generator as reference."""
        u, v = self.plane.local_axes()
        # The polar vector defines both starting direction and radius
        polar_vector = u.scale(self.radius)
        return pv.CircularArcFromNormal(
            center=self.center.to_tuple(),
            resolution=count,
            normal=self.plane.normal.to_tuple(),
            polar=polar_vector.to_tuple(),
            angle=360.0,
        )


Circle3d = Circle3D
