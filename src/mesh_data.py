"""MeshData — custom Mesh data structure for polygonal rendering."""

from dataclasses import dataclass

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
