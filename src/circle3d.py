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

    # =========================================================================
    # 内置几何变换与投影 (Built-in Transform & Projection)
    # =========================================================================
    def transform(self, matrix) -> "Circle3D":
        """应用 4x4 仿射变换矩阵变换圆 (变换基准平面与圆心)。"""
        new_plane = self.plane.transform(matrix)
        return Circle3D(
            center=new_plane.center,
            radius=self.radius,
            plane=new_plane,
            name=self.name,
        )

    def project_to_plane(self, plane) -> "Circle3D":
        """将圆投影至指定平面 Plane3D。"""
        new_plane = self.plane.project_to_plane(plane)
        return Circle3D(
            center=new_plane.center,
            radius=self.radius,
            plane=new_plane,
            name=f"{self.name}_proj" if self.name else "",
        )


Circle3d = Circle3D
