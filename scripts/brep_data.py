"""BrepData — custom B-Rep boundary representation data structure."""

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pyvista as pv

# Resolve import path to chapter 05 geometry primitives
from _common import find_chapter_scripts

_ch5 = find_chapter_scripts("05")
if _ch5.exists():
    sys.path.insert(0, str(_ch5))

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
