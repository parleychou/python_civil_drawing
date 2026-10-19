"""Point3D — a point in 3D engineering coordinates."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Optional

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

    # =========================================================================
    # 内置几何变换与投影 (Built-in Transform & Projection)
    # =========================================================================
    def transform(self, matrix) -> "Point3D":
        """应用 4x4 仿射变换矩阵变换点坐标 (齐次坐标 [x, y, z, 1]^T)。"""
        if hasattr(matrix, "apply_to_point"):
            return matrix.apply_to_point(self)
        arr = np.asarray(matrix, dtype=float)
        v4 = np.array([self.x, self.y, self.z, 1.0], dtype=float)
        res = arr @ v4
        w = res[3] if abs(res[3]) > 1e-12 else 1.0
        return Point3D(float(res[0] / w), float(res[1] / w), float(res[2] / w), name=self.name)

    def project_to_plane(self, plane) -> "Point3D":
        """将点正交投影至指定平面 Plane3D，返回投影后的垂足点。"""
        proj_pt, _ = self.project_to_plane_with_distance(plane)
        return proj_pt

    def project_to_plane_with_distance(self, plane) -> tuple["Point3D", float]:
        """将点正交投影至指定平面 Plane3D，返回 (垂足点, 沿法向有符号距离)。"""
        n = plane.normal.normalized()
        diff = self - plane.center
        signed_dist = float(diff.dot(n))
        proj = Point3D(
            self.x - signed_dist * n.x,
            self.y - signed_dist * n.y,
            self.z - signed_dist * n.z,
            name=f"{self.name}_proj" if self.name else "",
        )
        return proj, signed_dist

    def project_to_cs(self, cs) -> tuple["Point3D", tuple[float, float, float]]:
        """将点投影至局部坐标系 cs 的 XY 平面，并解算局部 (u, v, w) 坐标。

        Returns:
            tuple[Point3D, tuple[float, float, float]]: (世界坐标系下的投影点, (u, v, w) 坐标分量)
        """
        ux = cs.x_axis.normalized()
        uy = cs.y_axis.normalized()
        uz = cs.z_axis.normalized()
        diff = self - cs.origin
        u = float(diff.dot(ux))
        v = float(diff.dot(uy))
        w = float(diff.dot(uz))

        proj_pt = Point3D(
            cs.origin.x + u * ux.x + v * uy.x,
            cs.origin.y + u * ux.y + v * uy.y,
            cs.origin.z + u * ux.z + v * uy.z,
            name=f"{self.name}_cs_proj" if self.name else "",
        )
        return proj_pt, (u, v, w)

    # =========================================================================
    # 内置相交运算 (Built-in Intersection Operations)
    # =========================================================================
    def intersect(self, other: Any, tol: float = 1e-4) -> Any:
        """原生内置相交运算统一入口，自动多态分发."""
        from line3d import Line3D
        from plane3d import Plane3D
        from mesh_data import MeshData
        from brep_data import BrepData

        if isinstance(other, Point3D):
            return self.intersect_with_point(other, tol=tol)
        elif isinstance(other, Line3D):
            return self.intersect_with_line(other, tol=tol)
        elif isinstance(other, Plane3D):
            return self.intersect_with_plane(other, tol=tol)
        elif isinstance(other, MeshData):
            return self.intersect_with_mesh(other, tol=tol)
        elif isinstance(other, BrepData):
            return self.intersect_with_mesh(other.to_triangulated_mesh(), tol=tol)
        raise TypeError(f"Point3D 不支持与类型 {type(other).__name__} 的相交运算")

    def intersect_with_point(self, other: "Point3D", tol: float = 1e-4) -> Any:
        """点与点重合相交判定."""
        from intersection import intersect_point_point
        return intersect_point_point(self, other, tol=tol)

    def intersect_with_line(self, line: Any, tol: float = 1e-4) -> Any:
        """点在线段上判定."""
        from intersection import intersect_point_line
        return intersect_point_line(self, line, tol=tol)

    def intersect_with_plane(self, plane: Any, tol: float = 1e-4) -> Any:
        """点在支撑平面上判定."""
        from intersection import intersect_point_plane
        return intersect_point_plane(self, plane, tol=tol)

    def intersect_with_mesh(self, mesh: Any, tol: float = 1e-4) -> Any:
        """点在网格实体内判别."""
        from intersection import point_in_mesh
        return point_in_mesh(self, mesh, tol=tol)
