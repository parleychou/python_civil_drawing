"""Transformable — Utility adapters delegating to built-in geometry transformation methods."""

from typing import TypeVar

from _base import GeometryData
from point3d import Point3D
from vector3d import Vector3D
from line3d import Line3D
from plane3d import Plane3D
from coordinate_system3d import CoordinateSystem3D
from brep_data import BrepData
from mesh_data import MeshData
from transformation import TransformMatrix

T = TypeVar("T", bound=GeometryData)


def transform_point(pt: Point3D, matrix: TransformMatrix) -> Point3D:
    """Transform a Point3D using its built-in .transform() method."""
    return pt.transform(matrix)


def transform_vector(vec: Vector3D, matrix: TransformMatrix) -> Vector3D:
    """Transform a Vector3D using its built-in .transform() method."""
    return vec.transform(matrix)


def transform_line(line: Line3D, matrix: TransformMatrix) -> Line3D:
    """Transform a Line3D using its built-in .transform() method."""
    return line.transform(matrix)


def transform_plane(plane: Plane3D, matrix: TransformMatrix) -> Plane3D:
    """Transform a Plane3D using its built-in .transform() method."""
    return plane.transform(matrix)


def transform_coordinate_system(cs: CoordinateSystem3D, matrix: TransformMatrix) -> CoordinateSystem3D:
    """Transform a CoordinateSystem3D using its built-in .transform() method."""
    return cs.transform(matrix)


def transform_brep(brep: BrepData, matrix: TransformMatrix) -> BrepData:
    """Transform a BrepData using its built-in .transform() method."""
    return brep.transform(matrix)


def transform_mesh(mesh: MeshData, matrix: TransformMatrix) -> MeshData:
    """Transform a MeshData using its built-in .transform() method."""
    return mesh.transform(matrix)


def transform_geometry(geom: GeometryData, matrix: TransformMatrix) -> GeometryData:
    """Polymorphic entry point to transform any GeometryData object via its built-in .transform()."""
    return geom.transform(matrix)


def attach_transform_methods() -> None:
    """No-op kept for backwards compatibility. All geometry types now have built-in methods."""
    pass
