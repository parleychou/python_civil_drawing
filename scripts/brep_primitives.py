"""Compatibility module: re-exports B-Rep, Surface, and Mesh classes/factories."""
try:
    from _common import find_chapter_scripts
except ImportError:
    pass
from _base import GeometryData
from point3d import Point3D
from parametric_surface import ParametricSurfaceData
from sphere_surface import SphereSurface
from hyperbolic_paraboloid import HyperbolicParaboloid
from brep_data import BrepData
from mesh_data import MeshData
from factories import create_box_brep, create_cube_brep, create_pyramid_mesh

__all__ = [
    "GeometryData",
    "Point3D",
    "ParametricSurfaceData",
    "SphereSurface",
    "HyperbolicParaboloid",
    "BrepData",
    "MeshData",
    "create_box_brep",
    "create_cube_brep",
    "create_pyramid_mesh",
]
