"""ProjectionEngine — Orthogonal and multi-view projection algorithms."""

from dataclasses import dataclass
import numpy as np

from _base import GeometryData
from point3d import Point3D
from vector3d import Vector3D
from line3d import Line3D
from plane3d import Plane3D
from coordinate_system3d import CoordinateSystem3D
from brep_data import BrepData
from mesh_data import MeshData


@dataclass
class ProjectionEngine:
    """Core projection calculation engine for civil engineering computational drafting.

    This engine provides convenient static utility access, delegating directly
    to the built-in projection methods of each geometry type.
    """

    @staticmethod
    def project_point_to_plane(pt: Point3D, plane: Plane3D) -> tuple[Point3D, float]:
        """Project a 3D point orthogonally onto a Plane3D.

        Returns:
            tuple[Point3D, float]: (projected_point, signed_distance_along_normal)
        """
        return pt.project_to_plane_with_distance(plane)

    @staticmethod
    def project_point_to_cs(
        pt: Point3D,
        cs: CoordinateSystem3D,
    ) -> tuple[Point3D, tuple[float, float, float]]:
        """Project a point onto the XY-plane of a CoordinateSystem3D and compute local coordinates.

        Returns:
            tuple[Point3D, tuple[float, float, float]]: (projected_point_in_world, (u, v, w))
        """
        return pt.project_to_cs(cs)

    @staticmethod
    def project_line_to_plane(line: Line3D, plane: Plane3D) -> Line3D:
        """Project a 3D line segment orthogonally onto a Plane3D."""
        return line.project_to_plane(plane)

    @staticmethod
    def project_brep_to_plane(brep: BrepData, plane: Plane3D) -> BrepData:
        """Project all vertices of a BrepData onto a Plane3D, retaining its topology."""
        return brep.project_to_plane(plane)

    @staticmethod
    def project_mesh_to_plane(mesh: MeshData, plane: Plane3D) -> MeshData:
        """Project all vertices of a MeshData onto a Plane3D, retaining face connectivity."""
        return mesh.project_to_plane(plane)

    @staticmethod
    def generate_three_views(
        geom: GeometryData,
        offset: float = 3000.0,
    ) -> dict[str, GeometryData]:
        """Generate orthogonal engineering 3-views (Top/Plan, Front/Elevation, Side/Profile).

        Args:
            geom: The 3D geometry object to project (BrepData, MeshData, Line3D, Point3D).
            offset: Distance from origin to place each projection plane.

        Returns:
            dict[str, GeometryData]: Mapping with keys 'top', 'front', 'side'.
        """
        return geom.generate_three_views(offset=offset)
