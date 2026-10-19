"""Plane3D — a square plane patch defined by center, normal, and display size."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Optional

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

    # =========================================================================
    # 内置几何变换与投影 (Built-in Transform & Projection)
    # =========================================================================
    def transform(self, matrix) -> "Plane3D":
        """应用 4x4 仿射变换矩阵变换平面 (中心点作为点变换，法向量结合逆转置变换)。"""
        new_center = self.center.transform(matrix)
        try:
            inv = matrix.inverse() if hasattr(matrix, "inverse") else np.linalg.inv(matrix)
            inv_m = inv.matrix if hasattr(inv, "matrix") else np.asarray(inv, dtype=float)
            norm_matrix = inv_m[:3, :3].T
            n_arr = np.array([self.normal.x, self.normal.y, self.normal.z], dtype=float)
            new_n = norm_matrix @ n_arr
            new_normal = Vector3D(float(new_n[0]), float(new_n[1]), float(new_n[2])).normalized()
        except Exception:
            new_normal = self.normal.transform(matrix).normalized()

        return Plane3D(
            center=new_center,
            normal=new_normal,
            size=self.size,
            name=self.name,
        )

    def project_to_plane(self, plane) -> "Plane3D":
        """将平面中心点投影至目标平面 Plane3D。"""
        return Plane3D(
            center=self.center.project_to_plane(plane),
            normal=plane.normal,
            size=self.size,
            name=f"{self.name}_proj" if self.name else "",
        )

    # =========================================================================
    # 内置相交运算 (Built-in Intersection Operations)
    # =========================================================================
    def intersect(self, other: Any, tol: float = 1e-4) -> Any:
        """原生内置相交运算统一入口，自动多态分发."""
        from point3d import Point3D
        from line3d import Line3D
        from mesh_data import MeshData
        from brep_data import BrepData

        if isinstance(other, Point3D):
            return self.intersect_with_point(other, tol=tol)
        elif isinstance(other, Line3D):
            return self.intersect_with_line(other, segment_only=True, tol=tol)
        elif isinstance(other, Plane3D):
            return self.intersect_with_plane(other, tol=1e-9)
        elif isinstance(other, MeshData):
            return self.intersect_with_mesh(other, tol=tol)
        elif isinstance(other, BrepData):
            return self.intersect_with_mesh(other.to_triangulated_mesh(), tol=tol)
        raise TypeError(f"Plane3D 不支持与类型 {type(other).__name__} 的相交运算")

    def intersect_with_point(self, pt: Any, tol: float = 1e-4) -> Any:
        """平面与点相交判定."""
        from intersection import intersect_point_plane
        return intersect_point_plane(pt, self, tol=tol)

    def intersect_with_line(self, line: Any, segment_only: bool = True, tol: float = 1e-4) -> Any:
        """平面与线段穿透相交判定."""
        from intersection import intersect_line_plane
        return intersect_line_plane(line, self, segment_only=segment_only, tol=tol)

    def intersect_with_plane(self, other: "Plane3D", tol: float = 1e-9) -> Any:
        """双平面相交求无限交线."""
        from intersection import intersect_planes
        return intersect_planes(self, other, tol=tol)

    def intersect_with_mesh(self, mesh: Any, tol: float = 1e-4) -> Any:
        """剖切三维网格面片，提取截面交线段集合与轮廓环."""
        from intersection import slice_mesh_with_plane, assemble_contour_loops, IntersectionResult, IntersectionType
        segments = slice_mesh_with_plane(self, mesh, tol=tol)
        loops = assemble_contour_loops(segments, tol=tol)
        has_cut = len(segments) > 0
        return IntersectionResult(
            has_intersection=has_cut,
            type=IntersectionType.CONTOUR if loops else (IntersectionType.MULTI_SEGMENTS if has_cut else IntersectionType.NONE),
            lines=segments,
            contours=loops,
            description=f"剖切网格生成 {len(segments)} 条切片线段，缝合为 {len(loops)} 个轮廓环",
        )
