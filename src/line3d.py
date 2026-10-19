"""Line3D — a finite line segment defined by two endpoints."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Optional

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

    # =========================================================================
    # 内置几何变换与投影 (Built-in Transform & Projection)
    # =========================================================================
    def transform(self, matrix) -> "Line3D":
        """应用 4x4 仿射变换矩阵变换线段起点与终点。"""
        return Line3D(
            start=self.start.transform(matrix),
            end=self.end.transform(matrix),
            name=self.name,
        )

    def project_to_plane(self, plane) -> "Line3D":
        """将线段两端点正交投影至指定平面 Plane3D。"""
        return Line3D(
            start=self.start.project_to_plane(plane),
            end=self.end.project_to_plane(plane),
            name=f"{self.name}_proj" if self.name else "",
        )

    # =========================================================================
    # 内置相交运算 (Built-in Intersection Operations)
    # =========================================================================
    def intersect(self, other: Any, tol: float = 1e-4) -> Any:
        """原生内置相交运算统一入口，自动多态分发."""
        from point3d import Point3D
        from plane3d import Plane3D
        from mesh_data import MeshData
        from brep_data import BrepData

        if isinstance(other, Point3D):
            return self.intersect_with_point(other, tol=tol)
        elif isinstance(other, Line3D):
            return self.intersect_with_line(other, tol=tol)
        elif isinstance(other, Plane3D):
            return self.intersect_with_plane(other, segment_only=True, tol=tol)
        elif isinstance(other, MeshData):
            return self.intersect_with_mesh(other, tol=tol)
        elif isinstance(other, BrepData):
            return self.intersect_with_mesh(other.to_triangulated_mesh(), tol=tol)
        raise TypeError(f"Line3D 不支持与类型 {type(other).__name__} 的相交运算")

    def intersect_with_point(self, pt: Any, tol: float = 1e-4) -> Any:
        """线段与点相交判定."""
        from intersection import intersect_point_line
        return intersect_point_line(pt, self, tol=tol)

    def intersect_with_line(self, other: "Line3D", tol: float = 1e-4) -> Any:
        """线段与线段三维空间相交或异面判定."""
        from intersection import intersect_lines_3d
        return intersect_lines_3d(self, other, tol=tol)

    def intersect_with_plane(self, plane: Any, segment_only: bool = True, tol: float = 1e-4) -> Any:
        """线段与平面穿透相交判定."""
        from intersection import intersect_line_plane
        return intersect_line_plane(self, plane, segment_only=segment_only, tol=tol)

    def intersect_with_triangle(self, v0: Any, v1: Any, v2: Any) -> Any:
        """线段与空间三角形 Möller-Trumbore 相交判定."""
        from intersection import intersect_ray_triangle
        d = self.end - self.start
        length = d.length()
        if length < 1e-9:
            return False, None, 0.0, 0.0, 0.0
        return intersect_ray_triangle(self.start, d.normalized(), v0, v1, v2)

    def intersect_with_mesh(self, mesh: Any, tol: float = 1e-4) -> Any:
        """线段穿透三维实体网格，提取穿透区间与实厚度."""
        from intersection import intersect_line_mesh
        return intersect_line_mesh(self, mesh, tol=tol)

    def distance_to_line(self, other: "Line3D") -> tuple[float, Any, Any]:
        """计算与另一空间有限线段的最短距离及最近点对."""
        from intersection import segment_distance_3d
        return segment_distance_3d(self, other)


Line3d = Line3D
