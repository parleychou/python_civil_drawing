"""BrepData — custom B-Rep boundary representation data structure."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import numpy as np
import pyvista as pv

from _base import GeometryData
from point3d import Point3D


@dataclass
class BrepData(GeometryData):
    """Custom B-Rep boundary representation data structure.

    Contains vertex coordinates, edge index pairs connecting vertices,
    and face index loops forming closed rings.
    """

    vertices: tuple[Point3D, ...] = ()
    edges: tuple[tuple[int, int], ...] = ()
    faces: tuple[tuple[int, ...], ...] = ()

    def to_pyvista(self) -> "pv.PolyData":
        """Convert B-Rep face topology to a PyVista PolyData for face rendering."""
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

    def get_edges_polydata(self) -> "pv.PolyData":
        """Return all edges as standalone line segments PolyData."""
        points = [v.to_tuple() if hasattr(v, "to_tuple") else v for v in self.vertices]
        lines = []
        for edge in self.edges:
            lines.append(2)
            lines.extend(edge)
        return pv.PolyData(points, lines=lines)

    # =========================================================================
    # 内置几何变换与投影 (Built-in Transform & Projection)
    # =========================================================================
    def transform(self, matrix) -> "BrepData":
        """应用 4x4 仿射变换矩阵变换 B-Rep 实体的所有顶点，保持拓扑连接关系不变。"""
        new_vertices = tuple(v.transform(matrix) for v in self.vertices)
        return BrepData(
            vertices=new_vertices,
            edges=self.edges,
            faces=self.faces,
            name=self.name,
        )

    def project_to_plane(self, plane) -> "BrepData":
        """将 B-Rep 实体正交投影至指定平面 Plane3D，生成二维拓扑图元。"""
        proj_vertices = tuple(v.project_to_plane(plane) for v in self.vertices)
        return BrepData(
            vertices=proj_vertices,
            edges=self.edges,
            faces=self.faces,
            name=f"{self.name}_proj" if self.name else "",
        )

    def to_triangulated_mesh(self) -> "Any":
        """将多面体 B-Rep 的多边形面片扇形三角化为 MeshData 网格模型."""
        from mesh_data import MeshData
        tri_faces = []
        for face in self.faces:
            if len(face) == 3:
                tri_faces.append(face)
            elif len(face) >= 4:
                for k in range(1, len(face) - 1):
                    tri_faces.append((face[0], face[k], face[k + 1]))
        return MeshData(
            vertices=self.vertices,
            faces=tuple(tri_faces),
            name=f"{self.name}_tri_mesh" if self.name else "Brep_TriMesh",
        )

    # =========================================================================
    # 内置相交运算 (Built-in Intersection Operations)
    # =========================================================================
    def intersect(self, other: Any, tol: float = 1e-4) -> Any:
        """原生内置相交运算统一入口，自动委托三角化网格执行多态分发."""
        mesh = self.to_triangulated_mesh()
        return mesh.intersect(other, tol=tol)

    # =========================================================================
    # 内置实体布尔运算 (Built-in Boolean Operations)
    # =========================================================================
    def boolean_union(self, other: Any, tol: float = 1e-4) -> Any:
        """计算自身与目标实体的布尔并集 (A ∪ B)."""
        return self.to_triangulated_mesh().boolean_union(other, tol=tol)

    def boolean_difference(self, other: Any, tol: float = 1e-4) -> Any:
        """计算自身与目标实体的布尔差集 (Cut / A \\ B)."""
        return self.to_triangulated_mesh().boolean_difference(other, tol=tol)

    def cut(self, other: Any, tol: float = 1e-4) -> Any:
        """boolean_difference 的工程别名."""
        return self.boolean_difference(other, tol=tol)

    def boolean_intersection(self, other: Any, tol: float = 1e-4) -> Any:
        """计算自身与目标实体的布尔交集 (Common / A ∩ B)."""
        return self.to_triangulated_mesh().boolean_intersection(other, tol=tol)

    def common(self, other: Any, tol: float = 1e-4) -> Any:
        """boolean_intersection 的工程别名."""
        return self.boolean_intersection(other, tol=tol)
