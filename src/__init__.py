"""土木工程几何数据与渲染核心系统 (Pure Geometry & Render System)

本包提供纯粹的几何建模、4x4矩阵变换、正交投影与渲染能力，所有几何对象均继承自统一抽象基类 GeometryData。
"""

import sys
from pathlib import Path

_SRC_DIR = str(Path(__file__).resolve().parent)
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

# NOTE: bare (top-level) imports are intentional. The submodules themselves
# use bare imports (``from _base import ...``) for their internal cross-references,
# so re-exporting via bare imports here keeps a single class object for each name.
# Using relative imports (``from ._base import``) would create a *second* module
# instance (``src._base``) with a *different* class object, which breaks
# ``isinstance`` and ``__eq__`` checks across the public API.
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
    create_box_mesh,
    create_pyramid_mesh,
    create_i_beam_brep,
    create_bridge_pier_brep,
)
from render_engine import RenderEngine
from transformation import TransformMatrix
from projection import ProjectionEngine
from transformable import (
    transform_geometry,
    transform_point,
    transform_vector,
    transform_line,
    transform_plane,
    transform_coordinate_system,
    transform_brep,
    transform_mesh,
    attach_transform_methods,
)
from intersection import (
    IntersectionType,
    IntersectionStatus,
    IntersectionResult,
    EPS_SPATIAL,
    EPS_ANGULAR,
    EPS_PARAM,
    intersect_point_point,
    intersect_point_line,
    intersect_point_plane,
    point_in_mesh,
    intersect_segments_2d,
    intersect_lines_3d,
    segment_distance_3d,
    check_polyline_self_intersection,
    intersect_line_plane,
    intersect_ray_triangle,
    intersect_triangle_triangle,
    intersect_line_mesh,
    slice_mesh_with_plane,
    assemble_contour_loops,
    intersect_planes,
    intersect_mesh_mesh,
    check_mesh_self_intersection,
)
from polygon2d import Polygon2D
from boolean_ops import (
    BooleanOperationType,
    FaceSpatialRelation,
    BooleanResult,
    boolean_union_mesh,
    boolean_difference_mesh,
    boolean_intersection_mesh,
    split_triangle_by_segments,
    validate_mesh_manifold,
)
from collision import (
    AABB,
    OBB,
    ClashType,
    ClashSeverity,
    ClashRecord,
    ClashReport,
    SpatialHashGrid,
    sweep_and_prune,
    BVHNode,
    BVHTree,
    calculate_mesh_minimum_clearance,
    check_narrow_phase_clash,
    cluster_clash_points_dbscan,
    cluster_clash_records,
    ClashRuleMatrix,
    ClashEngine,
)
from clash_report import (
    export_clash_report_csv_excel,
    export_bcf_viewpoint,
)


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
    "create_box_mesh",
    "create_pyramid_mesh",
    "create_i_beam_brep",
    "create_bridge_pier_brep",
    "RenderEngine",
    "TransformMatrix",
    "ProjectionEngine",
    "transform_geometry",
    "transform_point",
    "transform_vector",
    "transform_line",
    "transform_plane",
    "transform_coordinate_system",
    "transform_brep",
    "transform_mesh",
    "attach_transform_methods",
    "IntersectionType",
    "IntersectionStatus",
    "IntersectionResult",
    "EPS_SPATIAL",
    "EPS_ANGULAR",
    "EPS_PARAM",
    "intersect_point_point",
    "intersect_point_line",
    "intersect_point_plane",
    "point_in_mesh",
    "intersect_segments_2d",
    "intersect_lines_3d",
    "segment_distance_3d",
    "check_polyline_self_intersection",
    "intersect_line_plane",
    "intersect_ray_triangle",
    "intersect_triangle_triangle",
    "intersect_line_mesh",
    "slice_mesh_with_plane",
    "assemble_contour_loops",
    "intersect_planes",
    "intersect_mesh_mesh",
    "check_mesh_self_intersection",
    # Chapter 09: Boolean Operations
    "Polygon2D",
    "BooleanOperationType",
    "FaceSpatialRelation",
    "BooleanResult",
    "boolean_union_mesh",
    "boolean_difference_mesh",
    "boolean_intersection_mesh",
    "split_triangle_by_segments",
    "validate_mesh_manifold",
    # Chapter 10: Collision Detection & BIM Clash Management
    "AABB",
    "OBB",
    "ClashType",
    "ClashSeverity",
    "ClashRecord",
    "ClashReport",
    "SpatialHashGrid",
    "sweep_and_prune",
    "BVHNode",
    "BVHTree",
    "calculate_mesh_minimum_clearance",
    "check_narrow_phase_clash",
    "cluster_clash_points_dbscan",
    "cluster_clash_records",
    "ClashRuleMatrix",
    "ClashEngine",
    "export_clash_report_csv_excel",
    "export_bcf_viewpoint",
]
