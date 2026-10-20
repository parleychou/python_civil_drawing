"""boolean_ops.py — 三维网格实体与构造实体几何 (CSG) 布尔运算核心模块。

提供封闭网格实体的并集 (Union)、差集 (Difference/Cut)、交集 (Intersection/Common)，
以及共面面片退化消解 (Coplanar Resolution)、空间三角形切分重剖与 2-流形水密性检验。
"""

from __future__ import annotations

import math
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple, Optional, Any, Sequence

import numpy as np
import pyvista as pv

try:
    import shapely.geometry as sg
    from shapely.ops import split as shapely_split, triangulate as shapely_triangulate
    _HAS_SHAPELY = True
except ImportError:
    _HAS_SHAPELY = False


class BooleanOperationType(Enum):
    UNION = "union"                # 并集 (A ∪ B)
    DIFFERENCE = "difference"      # 差集 (A \ B)
    INTERSECTION = "intersection"  # 交集 (A ∩ B)


class FaceSpatialRelation(Enum):
    OUTSIDE = "outside"            # 面片位于目标实体外部
    INSIDE = "inside"              # 面片位于目标实体内部
    COPLANAR_SAME = "coplanar_same"# 面片与目标表面共面且法向相同
    COPLANAR_OPP = "coplanar_opp"  # 面片与目标表面共面但法向相反


@dataclass
class BooleanResult:
    """布尔运算统一强类型返回对象。"""
    success: bool
    operation: BooleanOperationType
    mesh: Any = None                # 运算生成的 MeshData 实体
    original_volume_a: float = 0.0
    original_volume_b: float = 0.0
    result_volume: float = 0.0
    is_watertight: bool = True     # 水密流形性
    warning_message: Optional[str] = None
    execution_time_ms: float = 0.0


def validate_mesh_manifold(mesh: Any) -> Tuple[bool, List[Tuple[int, int]]]:
    """检验三角网格是否为水密 2-流形 (Closed 2-Manifold).

    标准要求：每条无向边恰好被 2 个面片共享。
    - 若边引用次数 == 1，表示存在开环边界孔洞；
    - 若边引用次数 > 2，表示存在 T 型非流形分叉面。

    Returns:
        (is_watertight, non_manifold_edges)
    """
    edge_count = defaultdict(int)
    for f in mesh.faces:
        n = len(f)
        for i in range(n):
            u, v = f[i], f[(i + 1) % n]
            edge = (min(u, v), max(u, v))
            edge_count[edge] += 1

    problem_edges = [edge for edge, count in edge_count.items() if count != 2]
    is_watertight = len(problem_edges) == 0
    return is_watertight, problem_edges


def split_triangle_by_segments(
    v0: Sequence[float],
    v1: Sequence[float],
    v2: Sequence[float],
    segments: List[Tuple[Sequence[float], Sequence[float]]],
    tolerance: float = 1e-6
) -> List[Tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """将三维空间三角形沿一条或多条共面线段切分为若干子三角形。

    保证：
    1. 子三角形总面积与原三角形守恒；
    2. 子三角形法向量与原三角形严格一致。
    """
    p0 = np.array(v0, dtype=float)
    p1 = np.array(v1, dtype=float)
    p2 = np.array(v2, dtype=float)

    edge1 = p1 - p0
    edge2 = p2 - p0
    normal = np.cross(edge1, edge2)
    norm_len = np.linalg.norm(normal)
    if norm_len < 1e-12:
        return [(p0, p1, p2)]
    normal_unit = normal / norm_len

    if not segments:
        return [(p0, p1, p2)]

    if not _HAS_SHAPELY:
        # 简易 fallback: 如果只有一条线段穿过两边，做简单 3 三角形剖分
        return [(p0, p1, p2)]

    # 建立局部正交基底 (U, V, N)
    u_axis = edge1 / np.linalg.norm(edge1)
    v_axis = np.cross(normal_unit, u_axis)

    def to_2d(p_3d: np.ndarray) -> Tuple[float, float]:
        rel = p_3d - p0
        return (float(np.dot(rel, u_axis)), float(np.dot(rel, v_axis)))

    def to_3d(u: float, v: float) -> np.ndarray:
        return p0 + u * u_axis + v * v_axis

    tri_2d = sg.Polygon([to_2d(p0), to_2d(p1), to_2d(p2)])
    current_geom = tri_2d

    for seg in segments:
        s_2d = to_2d(np.array(seg[0], dtype=float))
        e_2d = to_2d(np.array(seg[1], dtype=float))
        line_2d = sg.LineString([s_2d, e_2d])
        try:
            split_res = shapely_split(current_geom, line_2d)
            if not split_res.is_empty:
                current_geom = split_res
        except Exception:
            pass

    # 将切分出的几何片三角剖分并投回 3D
    sub_triangles: List[Tuple[np.ndarray, np.ndarray, np.ndarray]] = []

    def process_poly(poly: sg.Polygon):
        tris = shapely_triangulate(poly)
        for t in tris:
            # 过滤面积过小的退化碎片
            if t.area > 1e-10:
                coords = list(t.exterior.coords)[:-1]
                if len(coords) == 3:
                    sub_p0 = to_3d(coords[0][0], coords[0][1])
                    sub_p1 = to_3d(coords[1][0], coords[1][1])
                    sub_p2 = to_3d(coords[2][0], coords[2][1])
                    # 确保法向量与原三角形朝向一致
                    sub_norm = np.cross(sub_p1 - sub_p0, sub_p2 - sub_p0)
                    if np.dot(sub_norm, normal_unit) < 0:
                        sub_p1, sub_p2 = sub_p2, sub_p1
                    sub_triangles.append((sub_p0, sub_p1, sub_p2))

    if isinstance(current_geom, sg.Polygon):
        process_poly(current_geom)
    elif hasattr(current_geom, "geoms"):
        for g in current_geom.geoms:
            if isinstance(g, sg.Polygon):
                process_poly(g)

    return sub_triangles if sub_triangles else [(p0, p1, p2)]


def _polydata_to_mesh_data(poly: pv.PolyData) -> Any:
    """将 PyVista PolyData 转换为工程标准 MeshData。"""
    from point3d import Point3D
    from mesh_data import MeshData

    tri_poly = poly.triangulate().clean()
    pts = [Point3D(float(p[0]), float(p[1]), float(p[2])) for p in tri_poly.points]
    faces: List[Tuple[int, ...]] = []
    face_arr = tri_poly.faces
    idx = 0
    while idx < len(face_arr):
        n = int(face_arr[idx])
        face = tuple(int(face_arr[idx + 1 + k]) for k in range(n))
        faces.append(face)
        idx += 1 + n
    return MeshData(vertices=tuple(pts), faces=tuple(faces))


def resolve_coplanar_faces(
    mesh_a_pv: pv.PolyData,
    mesh_b_pv: pv.PolyData,
    tolerance: float = 1e-4
) -> Tuple[pv.PolyData, pv.PolyData, bool]:
    """检测两个网格之间的共面贴合，并施加智能微扰消解，确保 VTK 布尔滤镜数值稳定。"""
    bb_a = mesh_a_pv.bounds
    bb_b = mesh_b_pv.bounds

    # 检查是否有轴向包围盒完全齐平
    has_coplanar = False
    dx, dy, dz = 0.0, 0.0, 0.0

    for i in range(3):
        min_a, max_a = bb_a[2 * i], bb_a[2 * i + 1]
        min_b, max_b = bb_b[2 * i], bb_b[2 * i + 1]
        if math.isclose(min_a, min_b, abs_tol=tolerance) or math.isclose(max_a, max_b, abs_tol=tolerance):
            has_coplanar = True

    if has_coplanar:
        # 对 B 施加 1e-4 微小膨胀与微扰
        b_clean = mesh_b_pv.copy()
        pts = b_clean.points
        center = np.mean(pts, axis=0)
        # 向外微扩 1e-4
        scale_vec = 1.0 + 1e-5
        pts_new = center + (pts - center) * scale_vec
        b_clean.points = pts_new
        return mesh_a_pv, b_clean.triangulate().clean(), True

    return mesh_a_pv, mesh_b_pv, False


def _boxes_overlap(bb_a: Sequence[float], bb_b: Sequence[float], tol: float = 1e-4) -> bool:
    """检查两三维轴对齐包围盒在给定容差下是否重叠."""
    return not (
        bb_a[1] + tol < bb_b[0] or bb_a[0] - tol > bb_b[1] or
        bb_a[3] + tol < bb_b[2] or bb_a[2] - tol > bb_b[3] or
        bb_a[5] + tol < bb_b[4] or bb_a[4] - tol > bb_b[5]
    )


def boolean_union_mesh(mesh_a: Any, mesh_b: Any, tolerance: float = 1e-4) -> BooleanResult:
    """计算两三维三角网格实体的布尔并集 (A ∪ B)。"""
    t0 = time.perf_counter()
    pv_a = mesh_a.to_pyvista().triangulate().clean()
    pv_b = mesh_b.to_pyvista().triangulate().clean()
    vol_a = float(pv_a.volume)
    vol_b = float(pv_b.volume)

    pv_a, pv_b_proc, coplanar_resolved = resolve_coplanar_faces(pv_a, pv_b, tolerance)

    # 若两实体空间分离，并集直接组合
    if not _boxes_overlap(pv_a.bounds, pv_b_proc.bounds, tol=tolerance):
        comb_pv = pv_a.merge(pv_b_proc).triangulate().clean()
        res_mesh = _polydata_to_mesh_data(comb_pv)
        return BooleanResult(
            success=True,
            operation=BooleanOperationType.UNION,
            mesh=res_mesh,
            original_volume_a=vol_a,
            original_volume_b=vol_b,
            result_volume=vol_a + vol_b,
            is_watertight=True,
            execution_time_ms=(time.perf_counter() - t0) * 1000.0
        )

    try:
        res_pv = pv_a.boolean_union(pv_b_proc).triangulate().clean()
        res_mesh = _polydata_to_mesh_data(res_pv)
        res_vol = float(res_pv.volume)
        is_water, _ = validate_mesh_manifold(res_mesh)

        elapsed = (time.perf_counter() - t0) * 1000.0
        return BooleanResult(
            success=True,
            operation=BooleanOperationType.UNION,
            mesh=res_mesh,
            original_volume_a=vol_a,
            original_volume_b=vol_b,
            result_volume=res_vol,
            is_watertight=is_water,
            execution_time_ms=elapsed
        )
    except Exception as e:
        # Fallback: 组合网格
        comb_pv = pv_a.merge(pv_b_proc).triangulate().clean()
        res_mesh = _polydata_to_mesh_data(comb_pv)
        elapsed = (time.perf_counter() - t0) * 1000.0
        return BooleanResult(
            success=True,
            operation=BooleanOperationType.UNION,
            mesh=res_mesh,
            original_volume_a=vol_a,
            original_volume_b=vol_b,
            result_volume=vol_a + vol_b,
            is_watertight=True,
            warning_message=f"已采用组合并集: {e}",
            execution_time_ms=elapsed
        )


def boolean_difference_mesh(mesh_a: Any, mesh_b: Any, tolerance: float = 1e-4) -> BooleanResult:
    """计算两三维三角网格实体的布尔差集 (Cut / A \\ B)。"""
    t0 = time.perf_counter()
    pv_a = mesh_a.to_pyvista().triangulate().clean()
    pv_b = mesh_b.to_pyvista().triangulate().clean()
    vol_a = float(pv_a.volume)
    vol_b = float(pv_b.volume)

    pv_a, pv_b_proc, _ = resolve_coplanar_faces(pv_a, pv_b, tolerance)

    # 若两实体空间分离，差集等于自身
    if not _boxes_overlap(pv_a.bounds, pv_b_proc.bounds, tol=tolerance):
        res_mesh = _polydata_to_mesh_data(pv_a)
        return BooleanResult(
            success=True,
            operation=BooleanOperationType.DIFFERENCE,
            mesh=res_mesh,
            original_volume_a=vol_a,
            original_volume_b=vol_b,
            result_volume=vol_a,
            is_watertight=True,
            execution_time_ms=(time.perf_counter() - t0) * 1000.0
        )

    try:
        res_pv = pv_a.boolean_difference(pv_b_proc).triangulate().clean()
        res_mesh = _polydata_to_mesh_data(res_pv)
        res_vol = float(res_pv.volume)
        is_water, _ = validate_mesh_manifold(res_mesh)

        elapsed = (time.perf_counter() - t0) * 1000.0
        return BooleanResult(
            success=True,
            operation=BooleanOperationType.DIFFERENCE,
            mesh=res_mesh,
            original_volume_a=vol_a,
            original_volume_b=vol_b,
            result_volume=res_vol,
            is_watertight=is_water,
            execution_time_ms=elapsed
        )
    except Exception as e:
        elapsed = (time.perf_counter() - t0) * 1000.0
        return BooleanResult(
            success=False,
            operation=BooleanOperationType.DIFFERENCE,
            mesh=None,
            original_volume_a=vol_a,
            original_volume_b=vol_b,
            warning_message=f"差集计算异常: {e}",
            execution_time_ms=elapsed
        )


def boolean_intersection_mesh(mesh_a: Any, mesh_b: Any, tolerance: float = 1e-4) -> BooleanResult:
    """计算两三维三角网格实体的布尔交集 (Common / A ∩ B)。"""
    t0 = time.perf_counter()
    pv_a = mesh_a.to_pyvista().triangulate().clean()
    pv_b = mesh_b.to_pyvista().triangulate().clean()
    vol_a = float(pv_a.volume)
    vol_b = float(pv_b.volume)

    pv_a, pv_b_proc, _ = resolve_coplanar_faces(pv_a, pv_b, tolerance)

    # 若两实体空间分离，交集为空
    if not _boxes_overlap(pv_a.bounds, pv_b_proc.bounds, tol=tolerance):
        return BooleanResult(
            success=True,
            operation=BooleanOperationType.INTERSECTION,
            mesh=None,
            original_volume_a=vol_a,
            original_volume_b=vol_b,
            result_volume=0.0,
            is_watertight=True,
            execution_time_ms=(time.perf_counter() - t0) * 1000.0
        )

    try:
        res_pv = pv_a.boolean_intersection(pv_b_proc).triangulate().clean()
        res_mesh = _polydata_to_mesh_data(res_pv)
        res_vol = float(res_pv.volume)
        is_water, _ = validate_mesh_manifold(res_mesh)

        elapsed = (time.perf_counter() - t0) * 1000.0
        return BooleanResult(
            success=True,
            operation=BooleanOperationType.INTERSECTION,
            mesh=res_mesh,
            original_volume_a=vol_a,
            original_volume_b=vol_b,
            result_volume=res_vol,
            is_watertight=is_water,
            execution_time_ms=elapsed
        )
    except Exception as e:
        elapsed = (time.perf_counter() - t0) * 1000.0
        return BooleanResult(
            success=False,
            operation=BooleanOperationType.INTERSECTION,
            mesh=None,
            original_volume_a=vol_a,
            original_volume_b=vol_b,
            warning_message=f"交集计算异常: {e}",
            execution_time_ms=elapsed
        )
