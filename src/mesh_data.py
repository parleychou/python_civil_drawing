"""MeshData — custom Mesh data structure for polygonal rendering."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import numpy as np
import pyvista as pv

from _base import GeometryData
from point3d import Point3D


@dataclass
class MeshData(GeometryData):
    """Custom Mesh data structure.

    Keeps vertex positions and face topology, suitable for direct rendering.
    """

    vertices: tuple[Point3D, ...] = ()
    faces: tuple[tuple[int, ...], ...] = ()

    def to_pyvista(self) -> "pv.PolyData":
        """Convert Mesh data to a PyVista PolyData polygon mesh."""
        points = [v.to_tuple() if hasattr(v, "to_tuple") else v for v in self.vertices]

        pv_faces = []
        for face in self.faces:
            pv_faces.append(len(face))
            pv_faces.extend(face)

        return pv.PolyData(points, pv_faces)

    def get_vertices_polydata(self) -> "pv.PolyData":
        """Return all vertices as a standalone point cloud PolyData."""
        points = [v.to_tuple() if hasattr(v, "to_tuple") else v for v in self.vertices]
        return pv.PolyData(points)

    # =========================================================================
    # 内置几何变换与投影 (Built-in Transform & Projection)
    # =========================================================================
    def transform(self, matrix) -> "MeshData":
        """应用 4x4 仿射变换矩阵变换网格的所有顶点，保持面片拓扑连接不变。"""
        new_vertices = tuple(v.transform(matrix) for v in self.vertices)
        return MeshData(
            vertices=new_vertices,
            faces=self.faces,
            name=self.name,
        )

    def project_to_plane(self, plane) -> "MeshData":
        """将网格正交投影至指定平面 Plane3D。"""
        proj_vertices = tuple(v.project_to_plane(plane) for v in self.vertices)
        return MeshData(
            vertices=proj_vertices,
            faces=self.faces,
            name=f"{self.name}_proj" if self.name else "",
        )

    # =========================================================================
    # 内置相交运算 (Built-in Intersection Operations)
    # =========================================================================
    def intersect(self, other: Any, tol: float = 1e-4) -> Any:
        """原生内置相交运算统一入口，自动多态分发."""
        from point3d import Point3D
        from line3d import Line3D
        from plane3d import Plane3D
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
        raise TypeError(f"MeshData 不支持与类型 {type(other).__name__} 的相交运算")

    def intersect_with_point(self, pt: Any, tol: float = 1e-4) -> Any:
        """判断点是否在网格实体内部/体表."""
        from intersection import point_in_mesh
        return point_in_mesh(pt, self, tol=tol)

    def intersect_with_line(self, line: Any, tol: float = 1e-4) -> Any:
        """线段穿透三维实体网格，提取穿透区间与实厚度."""
        from intersection import intersect_line_mesh
        return intersect_line_mesh(line, self, tol=tol)

    def intersect_with_plane(self, plane: Any, tol: float = 1e-4) -> Any:
        """平面剖切网格面片，提取截面交线段集合与轮廓环."""
        from intersection import slice_mesh_with_plane, assemble_contour_loops, IntersectionResult, IntersectionType
        segments = slice_mesh_with_plane(plane, self, tol=tol)
        loops = assemble_contour_loops(segments, tol=tol)
        has_cut = len(segments) > 0
        return IntersectionResult(
            has_intersection=has_cut,
            type=IntersectionType.CONTOUR if loops else (IntersectionType.MULTI_SEGMENTS if has_cut else IntersectionType.NONE),
            lines=segments,
            contours=loops,
            description=f"网格被平面剖切产生 {len(segments)} 条切片线段，缝合为 {len(loops)} 个轮廓环",
        )

    def intersect_with_mesh(self, other: "MeshData", tol: float = 1e-4) -> Any:
        """网格与网格实体碰撞相交与完全包含检测."""
        from intersection import intersect_mesh_mesh
        return intersect_mesh_mesh(self, other, tol=tol)

    def is_self_intersecting(self, tol: float = 1e-4) -> tuple[bool, list[tuple[int, int]]]:
        """排查网格曲面是否存在自相交折叠面片."""
        from intersection import check_mesh_self_intersection
        return check_mesh_self_intersection(self, tol=tol)
