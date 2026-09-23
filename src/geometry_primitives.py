"""Compatibility module: re-exports geometry primitive classes."""
from _base import GeometryData, PointTuple
from point3d import Point3D
from vector3d import Vector3D
from coordinate_system3d import CoordinateSystem3D
from plane3d import Plane3D
from curve import Curve
from line3d import Line3D, Line3d
from circle3d import Circle3D, Circle3d
from arc3d import Arc3D, Arc3d

__all__ = [
    "GeometryData",
    "PointTuple",
    "Point3D",
    "Vector3D",
    "CoordinateSystem3D",
    "Plane3D",
    "Curve",
    "Line3D",
    "Line3d",
    "Circle3D",
    "Circle3d",
    "Arc3D",
    "Arc3d",
]
