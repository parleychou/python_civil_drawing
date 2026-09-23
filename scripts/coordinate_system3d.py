"""CoordinateSystem3D — a local coordinate system."""

import math
from dataclasses import dataclass, field

import numpy as np
import pyvista as pv

from _base import GeometryData, PointTuple
from point3d import Point3D
from vector3d import Vector3D


def _point_from_vector(origin: Point3D, vector: Vector3D, length: float) -> Point3D:
    """Return a point at ``length`` along ``vector`` from ``origin``."""
    unit = vector.normalized()
    return Point3D(
        origin.x + unit.x * length,
        origin.y + unit.y * length,
        origin.z + unit.z * length,
    )


@dataclass
class CoordinateSystem3D(GeometryData):
    """A local coordinate system represented by origin and three axes."""

    origin: Point3D = field(default_factory=Point3D)
    x_axis: Vector3D = field(default_factory=lambda: Vector3D(1, 0, 0))
    y_axis: Vector3D = field(default_factory=lambda: Vector3D(0, 1, 0))
    z_axis: Vector3D = field(default_factory=lambda: Vector3D(0, 0, 1))
    axis_length: float = 1000.0

    @classmethod
    def from_origin_and_normal(
        cls,
        origin: Point3D,
        normal: Vector3D,
        axis_length: float = 1000.0,
        name: str = "",
    ) -> "CoordinateSystem3D":
        """Construct a coordinate system from an origin and a normal vector (as Z axis)."""
        z_axis = normal.normalized()
        # Find a temporary vector that is not collinear with z_axis
        if abs(z_axis.x) < 0.9:
            temp = Vector3D(1.0, 0.0, 0.0)
        else:
            temp = Vector3D(0.0, 1.0, 0.0)

        # Compute X and Y axes using cross product
        x_axis = temp.cross(z_axis).normalized()
        y_axis = z_axis.cross(x_axis).normalized()

        return cls(
            origin=origin,
            x_axis=x_axis,
            y_axis=y_axis,
            z_axis=z_axis,
            axis_length=axis_length,
            name=name,
        )

    @classmethod
    def from_origin_and_vectors(
        cls,
        origin: Point3D,
        x_dir: Vector3D,
        xy_dir: Vector3D,
        axis_length: float = 1000.0,
        name: str = "",
    ) -> "CoordinateSystem3D":
        """Construct a coordinate system from an origin and two vectors.

        The first vector (x_dir) defines the X axis.
        The second vector (xy_dir) lies in the XY plane.
        """
        x_axis = x_dir.normalized()
        cross_prod = x_axis.cross(xy_dir)
        if cross_prod.length() < 1e-12:
            raise ValueError("The two vectors defining the coordinate system cannot be collinear.")
        z_axis = cross_prod.normalized()
        y_axis = z_axis.cross(x_axis).normalized()

        return cls(
            origin=origin,
            x_axis=x_axis,
            y_axis=y_axis,
            z_axis=z_axis,
            axis_length=axis_length,
            name=name,
        )

    def axes(self) -> "list[Line3D]":
        from line3d import Line3D  # deferred – circular

        origin = self.origin
        return [
            Line3D(origin, _point_from_vector(origin, self.x_axis, self.axis_length), name="X"),
            Line3D(origin, _point_from_vector(origin, self.y_axis, self.axis_length), name="Y"),
            Line3D(origin, _point_from_vector(origin, self.z_axis, self.axis_length), name="Z"),
        ]

    def to_pyvista(self) -> "pv.DataSet":
        points: list[PointTuple] = []
        lines: list[int] = []
        for axis in self.axes():
            start_index = len(points)
            points.extend([axis.start.to_tuple(), axis.end.to_tuple()])
            lines.extend([2, start_index, start_index + 1])

        polydata = pv.PolyData(points)
        polydata.lines = lines
        return polydata

    def render(self, engine, color: str = "steelblue", show_edges: bool = True) -> None:
        """Render the coordinate system using three vectors (as arrows) from the origin."""
        colors = ["red", "green", "blue"]
        # Scale the axes vectors by axis_length
        x_vec = self.x_axis.scale(self.axis_length)
        y_vec = self.y_axis.scale(self.axis_length)
        z_vec = self.z_axis.scale(self.axis_length)

        x_vec.render(engine, base_point=self.origin, color=colors[0], show_edges=show_edges)
        y_vec.render(engine, base_point=self.origin, color=colors[1], show_edges=show_edges)
        z_vec.render(engine, base_point=self.origin, color=colors[2], show_edges=show_edges)
