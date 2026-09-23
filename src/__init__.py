"""土木工程几何数据与渲染核心系统 (Pure Geometry & Render System)

本包提供纯粹的几何建模与渲染能力，所有几何对象均继承自统一抽象基类 GeometryData。
"""

import sys
from pathlib import Path

_SRC_DIR = str(Path(__file__).resolve().parent)
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

try:
    from ._base import GeometryData
    from .point3d import Point3D
    from .vector3d import Vector3D
    from .coordinate_system3d import CoordinateSystem3D
    from .curve import Curve
    from .line3d import Line3D, Line3d
    from .plane3d import Plane3D
    from .circle3d import Circle3D
    from .arc3d import Arc3D
    from .parametric_surface import ParametricSurfaceData
    from .hyperbolic_paraboloid import HyperbolicParaboloid
    from .sphere_surface import SphereSurface
    from .brep_data import BrepData
    from .mesh_data import MeshData
    from .factories import (
        create_cube_brep,
        create_box_brep,
        create_pyramid_mesh,
    )
    from .render_engine import RenderEngine
except (ImportError, ValueError):
    from _base import GeometryData
    from point3d import Point3D
    from vector3d import Vector3D
    from coordinate_system3d import CoordinateSystem3D
    from curve import Curve
    from line3d import Line3D, Line3d
    from plane3d import Plane3D
    from circle3d import Circle3D
    from arc3d import Arc3D
    from parametric_surface import ParametricSurfaceData
    from hyperbolic_paraboloid import HyperbolicParaboloid
    from sphere_surface import SphereSurface
    from brep_data import BrepData
    from mesh_data import MeshData
    from factories import (
        create_cube_brep,
        create_box_brep,
        create_pyramid_mesh,
    )
    from render_engine import RenderEngine

__all__ = [
    "GeometryData",
    "Point3D",
    "Vector3D",
    "CoordinateSystem3D",
    "Curve",
    "Line3D",
    "Line3d",
    "Plane3D",
    "Circle3D",
    "Arc3D",
    "ParametricSurfaceData",
    "HyperbolicParaboloid",
    "SphereSurface",
    "BrepData",
    "MeshData",
    "create_cube_brep",
    "create_box_brep",
    "create_pyramid_mesh",
    "RenderEngine",
]
