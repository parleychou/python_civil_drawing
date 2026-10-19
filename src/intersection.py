"""第08章 相交运算核心算法模块 — 几何体相交统一门面与计算引擎.

实现点 (Point)、线 (Line)、面 (Plane)、体 (Solid/Mesh/Brep) 的 4x4 完备相交运算。
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any, TYPE_CHECKING
import numpy as np

from point3d import Point3D
from vector3d import Vector3D
from line3d import Line3D
from plane3d import Plane3D

# 三层公差体系
EPS_SPATIAL: float = 1e-4   # 空间长度公差 (0.1 um / mm)
EPS_ANGULAR: float = 1e-9   # 角度公差 (rad)
EPS_PARAM: float = 1e-7     # 无量纲参数公差


class IntersectionType(Enum):
    NONE = "none"                      # 不相交 / 分离
    POINT = "point"                    # 单点相交
    MULTI_POINTS = "multi_points"      # 离散多点相交
    SEGMENT = "segment"                # 有限线段相交 / 重叠
    MULTI_SEGMENTS = "multi_segments"  # 多条线段相交
    LINE = "line"                      # 无限空间直线 (如双平面相交)
    CONTOUR = "contour"                # 截面闭合或开放轮廓环
    COPLANAR_AREA = "coplanar_area"    # 共面面积重叠
    CONTAINED = "contained"            # 完全包含 (如小体在大体内)
    TOUCH = "touch"                    # 边界接触 (切触)


class IntersectionStatus(Enum):
    SUCCESS = "success"                # 正常计算完成
    INVALID_INPUT = "invalid_input"    # 输入几何退化或非封闭
    UNSUPPORTED = "unsupported"        # 暂不支持的类型组合
    INDETERMINATE = "indeterminate"    # 处于公差临界区不确定


@dataclass
class IntersectionResult:
    """相交运算统一强类型返回结果对象."""
    has_intersection: bool
    type: IntersectionType = IntersectionType.NONE
    status: IntersectionStatus = IntersectionStatus.SUCCESS
    points: list[Any] = field(default_factory=list)
    line: Optional[Any] = None
    lines: list[Any] = field(default_factory=list)
    contours: list[dict[str, Any]] = field(default_factory=list)
    parameters: dict[str, Any] = field(default_factory=dict)
    clearance: Optional[float] = None
    description: str = ""

    @property
    def point(self) -> Optional[Any]:
        return self.points[0] if self.points else None


# ==============================================================================
# Phase B: 点与线层级 2D/3D 基础谓词
# ==============================================================================

def intersect_point_point(p1: Point3D, p2: Point3D, tol: float = EPS_SPATIAL) -> IntersectionResult:
    """点与点重合相交判定."""
    dist = p1.distance_to(p2)
    if dist <= tol:
        mid_pt = Point3D(
            (p1.x + p2.x) * 0.5,
            (p1.y + p2.y) * 0.5,
            (p1.z + p2.z) * 0.5,
        )
        return IntersectionResult(
            has_intersection=True,
            type=IntersectionType.POINT,
            points=[mid_pt],
            clearance=dist,
            description="两点在容差范围内重合",
        )
    return IntersectionResult(
        has_intersection=False,
        type=IntersectionType.NONE,
        clearance=dist,
        description="两点分离",
    )


def intersect_point_line(pt: Point3D, line: Line3D, tol: float = EPS_SPATIAL) -> IntersectionResult:
    """点与有限线段相交判定."""
    v = line.end - line.start
    l_sq = v.dot(v)
    if l_sq < tol * tol:
        return intersect_point_point(pt, line.start, tol)

    u = pt - line.start
    t = u.dot(v) / l_sq
    p_proj = Point3D(
        line.start.x + t * v.x,
        line.start.y + t * v.y,
        line.start.z + t * v.z,
    )
    dist = pt.distance_to(p_proj)

    is_on_seg = (dist <= tol) and (-EPS_PARAM <= t <= 1.0 + EPS_PARAM)
    is_on_ext = (dist <= tol) and not is_on_seg

    if is_on_seg:
        t_clamped = max(0.0, min(1.0, t))
        res_pt = Point3D(
            line.start.x + t_clamped * v.x,
            line.start.y + t_clamped * v.y,
            line.start.z + t_clamped * v.z,
        )
        return IntersectionResult(
            has_intersection=True,
            type=IntersectionType.POINT,
            points=[res_pt],
            parameters={"t": t_clamped, "is_on_extension": False},
            clearance=dist,
            description="点在有限线段上",
        )
    return IntersectionResult(
        has_intersection=False,
        type=IntersectionType.NONE,
        parameters={"t": t, "is_on_extension": is_on_ext},
        clearance=dist,
        description="点不在有限线段上" if not is_on_ext else "点在线段延长线上（非有限线段相交）",
    )


def intersect_point_plane(pt: Point3D, plane: Plane3D, tol: float = EPS_SPATIAL) -> IntersectionResult:
    """点在无限支撑平面上的相交判定."""
    n = plane.normal.normalized()
    diff = pt - plane.center
    signed_dist = diff.dot(n)
    abs_dist = abs(signed_dist)

    if abs_dist <= tol:
        return IntersectionResult(
            has_intersection=True,
            type=IntersectionType.POINT,
            points=[pt],
            clearance=abs_dist,
            parameters={"signed_distance": signed_dist},
            description="点在平面上",
        )
    return IntersectionResult(
        has_intersection=False,
        type=IntersectionType.NONE,
        clearance=abs_dist,
        parameters={"signed_distance": signed_dist},
        description="点不在平面上",
    )


def intersect_segments_2d(l1: Line3D, l2: Line3D, tol: float = EPS_SPATIAL) -> IntersectionResult:
    """二维平面内线段与线段相交检测 (跨立试验与共线重叠判定)."""
    ax, ay = l1.start.x, l1.start.y
    bx, by = l1.end.x, l1.end.y
    cx, cy = l2.start.x, l2.start.y
    dx, dy = l2.end.x, l2.end.y

    # 1. 快速排斥实验 (2D AABB 盒)
    if (max(ax, bx) < min(cx, dx) - tol or max(cx, dx) < min(ax, bx) - tol or
            max(ay, by) < min(cy, dy) - tol or max(cy, dy) < min(ay, by) - tol):
        return IntersectionResult(has_intersection=False, type=IntersectionType.NONE)

    # 2. 向量叉积
    # cross_2d(u, v) = u.x * v.y - u.y * v.x
    ab_x, ab_y = bx - ax, by - ay
    cd_x, cd_y = dx - cx, dy - cy
    ac_x, ac_y = cx - ax, cy - ay

    denom = ab_x * cd_y - ab_y * cd_x

    # 3. 平行或共线
    if abs(denom) < EPS_ANGULAR:
        cross_ac_ab = ac_x * ab_y - ac_y * ab_x
        # 检查是否共线
        len_ab = math.hypot(ab_x, ab_y)
        if len_ab > 0 and abs(cross_ac_ab) / len_ab <= tol:
            # 共线！在一维轴上求投影区间
            # 选择主投影轴
            if abs(ab_x) >= abs(ab_y):
                s1_start, s1_end = min(ax, bx), max(ax, bx)
                s2_start, s2_end = min(cx, dx), max(cx, dx)
                overlap_min = max(s1_start, s2_start)
                overlap_max = min(s1_end, s2_end)
                if overlap_max - overlap_min > tol:
                    # 求重叠线段
                    ratio_start = (overlap_min - ax) / ab_x if ab_x != 0 else 0.0
                    ratio_end = (overlap_max - ax) / ab_x if ab_x != 0 else 0.0
                    pt_start = Point3D(overlap_min, ay + ratio_start * ab_y, l1.start.z)
                    pt_end = Point3D(overlap_max, ay + ratio_end * ab_y, l1.end.z)
                    return IntersectionResult(
                        has_intersection=True,
                        type=IntersectionType.SEGMENT,
                        line=Line3D(pt_start, pt_end),
                        description="两线段共线且部分重叠",
                    )
            else:
                s1_start, s1_end = min(ay, by), max(ay, by)
                s2_start, s2_end = min(cy, dy), max(cy, dy)
                overlap_min = max(s1_start, s2_start)
                overlap_max = min(s1_end, s2_end)
                if overlap_max - overlap_min > tol:
                    ratio_start = (overlap_min - ay) / ab_y
                    ratio_end = (overlap_max - ay) / ab_y
                    pt_start = Point3D(ax + ratio_start * ab_x, overlap_min, l1.start.z)
                    pt_end = Point3D(ax + ratio_end * ab_x, overlap_max, l1.end.z)
                    return IntersectionResult(
                        has_intersection=True,
                        type=IntersectionType.SEGMENT,
                        line=Line3D(pt_start, pt_end),
                        description="两线段共线且部分重叠",
                    )
        return IntersectionResult(has_intersection=False, type=IntersectionType.NONE)

    # 4. 跨立试验求解参数 t 与 u
    t = (ac_x * cd_y - ac_y * cd_x) / denom
    u = (ac_x * ab_y - ac_y * ab_x) / denom

    if (-EPS_PARAM <= t <= 1.0 + EPS_PARAM) and (-EPS_PARAM <= u <= 1.0 + EPS_PARAM):
        t_clamped = max(0.0, min(1.0, t))
        u_clamped = max(0.0, min(1.0, u))
        ix = ax + t_clamped * ab_x
        iy = ay + t_clamped * ab_y
        iz = (l1.start.z + l1.end.z + l2.start.z + l2.end.z) * 0.25
        return IntersectionResult(
            has_intersection=True,
            type=IntersectionType.POINT,
            points=[Point3D(ix, iy, iz)],
            parameters={"t1": t_clamped, "t2": u_clamped},
            description="两线段在平面内相交于一点",
        )

    return IntersectionResult(
        has_intersection=False,
        type=IntersectionType.NONE,
        parameters={"t1": t, "t2": u},
    )


def segment_distance_3d(l1: Line3D, l2: Line3D) -> tuple[float, Point3D, Point3D]:
    """计算三维空间中两有限线段的最短距离及最近点对 (有限域截断法)."""
    p1 = l1.start
    d1 = l1.end - l1.start
    p2 = l2.start
    d2 = l2.end - l2.start
    r = p1 - p2

    a = d1.dot(d1)  # 严格非负
    e = d2.dot(d2)  # 严格非负
    f = d2.dot(r)

    # 检查是否退化为点
    if a <= EPS_SPATIAL * EPS_SPATIAL and e <= EPS_SPATIAL * EPS_SPATIAL:
        return p1.distance_to(p2), p1, p2
    if a <= EPS_SPATIAL * EPS_SPATIAL:
        s = 0.0
        t = max(0.0, min(1.0, f / e))
    else:
        c = d1.dot(r)
        if e <= EPS_SPATIAL * EPS_SPATIAL:
            t = 0.0
            s = max(0.0, min(1.0, -c / a))
        else:
            b = d1.dot(d2)
            denom = a * e - b * b
            if denom > EPS_ANGULAR:
                s = max(0.0, min(1.0, (b * f - c * e) / denom))
            else:
                s = 0.0

            t = (b * s + f) / e
            if t < 0.0:
                t = 0.0
                s = max(0.0, min(1.0, -c / a))
            elif t > 1.0:
                t = 1.0
                s = max(0.0, min(1.0, (b - c) / a))

    closest1 = Point3D(p1.x + s * d1.x, p1.y + s * d1.y, p1.z + s * d1.z)
    closest2 = Point3D(p2.x + t * d2.x, p2.y + t * d2.y, p2.z + t * d2.z)
    return closest1.distance_to(closest2), closest1, closest2


def intersect_lines_3d(l1: Line3D, l2: Line3D, tol: float = EPS_SPATIAL) -> IntersectionResult:
    """三维空间有限线段相交或异面公垂线最近距离检测."""
    dist, c1, c2 = segment_distance_3d(l1, l2)
    if dist <= tol:
        mid_pt = Point3D((c1.x + c2.x) * 0.5, (c1.y + c2.y) * 0.5, (c1.z + c2.z) * 0.5)
        return IntersectionResult(
            has_intersection=True,
            type=IntersectionType.POINT,
            points=[mid_pt],
            clearance=dist,
            parameters={"closest_pt1": c1, "closest_pt2": c2},
            description="三维空间线段相交",
        )
    return IntersectionResult(
        has_intersection=False,
        type=IntersectionType.NONE,
        clearance=dist,
        parameters={"closest_pt1": c1, "closest_pt2": c2},
        description="三维空间线段异面或平行分离",
    )


def check_polyline_self_intersection(
    points: list[Point3D], is_closed: bool = False, tol: float = EPS_SPATIAL
) -> tuple[bool, list[dict[str, Any]]]:
    """折线/多段线自相交排查 (检出非相邻线段间的相交点)."""
    n = len(points)
    if n < 3:
        return False, []

    # 构造线段列表
    segments = []
    num_segs = n if is_closed else n - 1
    for i in range(num_segs):
        segments.append(Line3D(points[i], points[(i + 1) % n]))

    events = []
    for i in range(num_segs):
        for j in range(i + 1, num_segs):
            # 排除相邻线段
            if abs(i - j) <= 1:
                continue
            if is_closed and i == 0 and j == num_segs - 1:
                continue

            res = intersect_lines_3d(segments[i], segments[j], tol)
            if res.has_intersection and res.point is not None:
                events.append({
                    "seg_indices": (i, j),
                    "point": res.point,
                    "parameters": res.parameters,
                })

    return len(events) > 0, events


# ==============================================================================
# Phase C: 射线平面、Möller-Trumbore 算法与三角形求交
# ==============================================================================

def intersect_line_plane(
    line: Line3D, plane: Plane3D, segment_only: bool = True, tol: float = EPS_SPATIAL
) -> IntersectionResult:
    """空间直线/线段与平面的相交判定."""
    d = line.end - line.start
    n = plane.normal.normalized()
    denom = d.dot(n)

    if abs(denom) < EPS_ANGULAR:
        # 平行或在平面内
        dist_start = (line.start - plane.center).dot(n)
        if abs(dist_start) <= tol:
            return IntersectionResult(
                has_intersection=True,
                type=IntersectionType.COPLANAR_AREA,
                line=line,
                clearance=0.0,
                description="线段完全在平面内（共面）",
            )
        return IntersectionResult(
            has_intersection=False,
            type=IntersectionType.NONE,
            clearance=abs(dist_start),
            description="直线/线段与平面平行无交",
        )

    t = (plane.center - line.start).dot(n) / denom
    hit_pt = Point3D(
        line.start.x + t * d.x,
        line.start.y + t * d.y,
        line.start.z + t * d.z,
    )

    is_on_segment = (-EPS_PARAM <= t <= 1.0 + EPS_PARAM)

    if segment_only:
        if is_on_segment:
            t_clamped = max(0.0, min(1.0, t))
            pt_clamped = Point3D(
                line.start.x + t_clamped * d.x,
                line.start.y + t_clamped * d.y,
                line.start.z + t_clamped * d.z,
            )
            return IntersectionResult(
                has_intersection=True,
                type=IntersectionType.POINT,
                points=[pt_clamped],
                parameters={"t": t_clamped, "is_on_extension": False},
                description="有限线段穿透平面",
            )
        return IntersectionResult(
            has_intersection=False,
            type=IntersectionType.NONE,
            parameters={"t": t, "is_on_extension": True},
            description="线段延长线穿透平面（非有限线段相交）",
        )

    # segment_only = False (无限直线穿透)
    return IntersectionResult(
        has_intersection=True,
        type=IntersectionType.POINT,
        points=[hit_pt],
        parameters={"t": t, "is_on_extension": not is_on_segment},
        description="无限空间直线穿透平面",
    )


def intersect_ray_triangle(
    ray_origin: Point3D,
    ray_dir: Vector3D,
    v0: Point3D,
    v1: Point3D,
    v2: Point3D,
    tol: float = EPS_ANGULAR,
) -> tuple[bool, Optional[Point3D], float, float, float]:
    """Möller-Trumbore 射线-三角形快速相交算法.

    Returns:
        (hit, hit_point, t, u, v)
    """
    e1 = v1 - v0
    e2 = v2 - v0
    pvec = ray_dir.cross(e2)
    det = e1.dot(pvec)

    if abs(det) < tol:
        return False, None, 0.0, 0.0, 0.0

    inv_det = 1.0 / det
    tvec = ray_origin - v0
    u = tvec.dot(pvec) * inv_det
    if u < -EPS_PARAM or u > 1.0 + EPS_PARAM:
        return False, None, 0.0, 0.0, 0.0

    qvec = tvec.cross(e1)
    v = ray_dir.dot(qvec) * inv_det
    if v < -EPS_PARAM or (u + v) > 1.0 + EPS_PARAM:
        return False, None, 0.0, 0.0, 0.0

    t = e2.dot(qvec) * inv_det
    if t < -EPS_PARAM:
        return False, None, t, u, v

    t_val = max(0.0, t)
    hit_pt = Point3D(
        ray_origin.x + t_val * ray_dir.x,
        ray_origin.y + t_val * ray_dir.y,
        ray_origin.z + t_val * ray_dir.z,
    )
    return True, hit_pt, t_val, max(0.0, min(1.0, u)), max(0.0, min(1.0, v))


def intersect_triangle_triangle(
    t1: tuple[Point3D, Point3D, Point3D],
    t2: tuple[Point3D, Point3D, Point3D],
    tol: float = EPS_SPATIAL,
) -> IntersectionResult:
    """Möller 三角形-三角形空间相交算法 (非共面相交线段与共面重叠检测)."""
    a0, a1, a2 = t1
    b0, b1, b2 = t2

    # 平面 1 法向与点到平面距离
    e1_a = a1 - a0
    e2_a = a2 - a0
    n1 = e1_a.cross(e2_a)
    n1_len = n1.length()
    if n1_len < EPS_ANGULAR:
        return IntersectionResult(has_intersection=False, status=IntersectionStatus.INVALID_INPUT)
    n1 = n1.scale(1.0 / n1_len)

    d_b0 = (b0 - a0).dot(n1)
    d_b1 = (b1 - a0).dot(n1)
    d_b2 = (b2 - a0).dot(n1)

    if (d_b0 > tol and d_b1 > tol and d_b2 > tol) or (d_b0 < -tol and d_b1 < -tol and d_b2 < -tol):
        return IntersectionResult(has_intersection=False, type=IntersectionType.NONE)

    # 平面 2 法向与点到平面距离
    e1_b = b1 - b0
    e2_b = b2 - b0
    n2 = e1_b.cross(e2_b)
    n2_len = n2.length()
    if n2_len < EPS_ANGULAR:
        return IntersectionResult(has_intersection=False, status=IntersectionStatus.INVALID_INPUT)
    n2 = n2.scale(1.0 / n2_len)

    d_a0 = (a0 - b0).dot(n2)
    d_a1 = (a1 - b0).dot(n2)
    d_a2 = (a2 - b0).dot(n2)

    if (d_a0 > tol and d_a1 > tol and d_a2 > tol) or (d_a0 < -tol and d_a1 < -tol and d_a2 < -tol):
        return IntersectionResult(has_intersection=False, type=IntersectionType.NONE)

    # 交线方向 D = n1 x n2
    d_line = n1.cross(n2)
    d_line_len = d_line.length()

    if d_line_len < EPS_ANGULAR:
        # 共面情况: 检查 T1 的 3 条边与 T2 是否相交，或顶点在内部
        res_pts = []
        for i in range(3):
            edge = Line3D(t1[i], t1[(i + 1) % 3])
            # 测试 edge 与 t2 的三条边相交
            for j in range(3):
                edge2 = Line3D(t2[j], t2[(j + 1) % 3])
                res_e = intersect_lines_3d(edge, edge2, tol)
                if res_e.has_intersection and res_e.point:
                    res_pts.append(res_e.point)
        if res_pts:
            return IntersectionResult(
                has_intersection=True,
                type=IntersectionType.COPLANAR_AREA,
                points=res_pts,
                description="两共面三角形发生重叠相交",
            )
        return IntersectionResult(has_intersection=False, type=IntersectionType.NONE)

    d_dir = d_line.scale(1.0 / d_line_len)

    # 提取 T1 与 平面 2 的交点区间
    pts_t1 = []
    t1_verts = [a0, a1, a2]
    d_a = [d_a0, d_a1, d_a2]
    for i in range(3):
        j = (i + 1) % 3
        if (d_a[i] * d_a[j]) <= 0.0 and abs(d_a[i] - d_a[j]) > EPS_ANGULAR:
            alpha = d_a[i] / (d_a[i] - d_a[j])
            p_inter = Point3D(
                t1_verts[i].x + alpha * (t1_verts[j].x - t1_verts[i].x),
                t1_verts[i].y + alpha * (t1_verts[j].y - t1_verts[i].y),
                t1_verts[i].z + alpha * (t1_verts[j].z - t1_verts[i].z),
            )
            pts_t1.append(p_inter)

    # 提取 T2 与 平面 1 的交点区间
    pts_t2 = []
    t2_verts = [b0, b1, b2]
    d_b = [d_b0, d_b1, d_b2]
    for i in range(3):
        j = (i + 1) % 3
        if (d_b[i] * d_b[j]) <= 0.0 and abs(d_b[i] - d_b[j]) > EPS_ANGULAR:
            alpha = d_b[i] / (d_b[i] - d_b[j])
            p_inter = Point3D(
                t2_verts[i].x + alpha * (t2_verts[j].x - t2_verts[i].x),
                t2_verts[i].y + alpha * (t2_verts[j].y - t2_verts[i].y),
                t2_verts[i].z + alpha * (t2_verts[j].z - t2_verts[i].z),
            )
            pts_t2.append(p_inter)

    if len(pts_t1) < 2 or len(pts_t2) < 2:
        return IntersectionResult(has_intersection=False, type=IntersectionType.NONE)

    # 沿交线方向 d_dir 投影求解 1D 重叠区间
    ref_pt = pts_t1[0]
    s1_0 = (pts_t1[0] - ref_pt).dot(d_dir)
    s1_1 = (pts_t1[1] - ref_pt).dot(d_dir)
    s1_min, s1_max = min(s1_0, s1_1), max(s1_0, s1_1)

    s2_0 = (pts_t2[0] - ref_pt).dot(d_dir)
    s2_1 = (pts_t2[1] - ref_pt).dot(d_dir)
    s2_min, s2_max = min(s2_0, s2_1), max(s2_0, s2_1)

    overlap_min = max(s1_min, s2_min)
    overlap_max = min(s1_max, s2_max)

    if overlap_max - overlap_min > tol:
        start_pt = Point3D(
            ref_pt.x + overlap_min * d_dir.x,
            ref_pt.y + overlap_min * d_dir.y,
            ref_pt.z + overlap_min * d_dir.z,
        )
        end_pt = Point3D(
            ref_pt.x + overlap_max * d_dir.x,
            ref_pt.y + overlap_max * d_dir.y,
            ref_pt.z + overlap_max * d_dir.z,
        )
        return IntersectionResult(
            has_intersection=True,
            type=IntersectionType.SEGMENT,
            line=Line3D(start_pt, end_pt),
            description="两三角形相交于一条公共空间线段",
        )
    elif abs(overlap_max - overlap_min) <= tol:
        contact_pt = Point3D(
            ref_pt.x + overlap_min * d_dir.x,
            ref_pt.y + overlap_min * d_dir.y,
            ref_pt.z + overlap_min * d_dir.z,
        )
        return IntersectionResult(
            has_intersection=True,
            type=IntersectionType.POINT,
            points=[contact_pt],
            description="两三角形边界接触于单点",
        )

    return IntersectionResult(has_intersection=False, type=IntersectionType.NONE)


def benchmark_mt_vs_naive(num_rays: int = 1000) -> float:
    """可复现基准评测：Möller-Trumbore 算法执行时间评测."""
    import time
    v0 = Point3D(0, 0, 0)
    v1 = Point3D(100, 0, 0)
    v2 = Point3D(0, 100, 0)

    # 生成测试射线
    np.random.seed(42)
    origins = [Point3D(float(x), float(y), -50.0) for x, y in np.random.uniform(0, 50, (num_rays, 2))]
    d = Vector3D(0, 0, 1)

    t0 = time.perf_counter()
    for o in origins:
        intersect_ray_triangle(o, d, v0, v1, v2)
    t_elapsed = time.perf_counter() - t0
    # 返回每秒光线计算次数 (Rays per second) 或耗时比率
    return float(num_rays / max(t_elapsed, 1e-9))


# ==============================================================================
# Phase D: 网格空间查询、点在体内与平面剖切网格切片
# ==============================================================================

def _mesh_to_triangles(mesh: Any) -> list[tuple[Point3D, Point3D, Point3D]]:
    """将 MeshData 的任意多边形面片三角化为三顶点元组列表."""
    triangles = []
    verts = mesh.vertices
    for face in mesh.faces:
        if len(face) == 3:
            triangles.append((verts[face[0]], verts[face[1]], verts[face[2]]))
        elif len(face) >= 4:
            # 扇形三角化
            for k in range(1, len(face) - 1):
                triangles.append((verts[face[0]], verts[face[k]], verts[face[k + 1]]))
    return triangles


def point_in_mesh(pt: Point3D, mesh: Any, tol: float = EPS_SPATIAL) -> IntersectionResult:
    """判别点在三维闭合实体内、体表或外部 (微扰多射线投票奇偶检验法)."""
    triangles = _mesh_to_triangles(mesh)
    if not triangles:
        return IntersectionResult(has_intersection=False, status=IntersectionStatus.INVALID_INPUT)

    # 1. 前置体表边界距离检查
    for v0, v1, v2 in triangles:
        e1 = v1 - v0
        e2 = v2 - v0
        n = e1.cross(e2)
        n_len = n.length()
        if n_len < EPS_ANGULAR:
            continue
        n_unit = n.scale(1.0 / n_len)
        dist_plane = (pt - v0).dot(n_unit)
        if abs(dist_plane) <= tol:
            # 投影到面片平面检查是否在三角形内
            p_proj = Point3D(pt.x - dist_plane * n_unit.x, pt.y - dist_plane * n_unit.y, pt.z - dist_plane * n_unit.z)
            # 计算重心坐标
            v0_proj = v0
            tvec = p_proj - v0_proj
            d00 = e1.dot(e1)
            d01 = e1.dot(e2)
            d11 = e2.dot(e2)
            d20 = tvec.dot(e1)
            d21 = tvec.dot(e2)
            denom = d00 * d11 - d01 * d01
            if abs(denom) > EPS_ANGULAR:
                u = (d11 * d20 - d01 * d21) / denom
                v = (d00 * d21 - d01 * d20) / denom
                if (-EPS_PARAM <= u <= 1.0 + EPS_PARAM and
                        -EPS_PARAM <= v <= 1.0 + EPS_PARAM and
                        u + v <= 1.0 + EPS_PARAM):
                    return IntersectionResult(
                        has_intersection=True,
                        type=IntersectionType.TOUCH,
                        points=[pt],
                        clearance=abs(dist_plane),
                        description="点在网格实体表面上",
                    )

    # 2. 三向微扰无理数射线投票策略 (避开网格边与顶点奇异性)
    ray_dirs = [
        Vector3D(1.0, 0.577350269, 0.333333333).normalized(),
        Vector3D(0.333333333, 1.0, 0.577350269).normalized(),
        Vector3D(0.577350269, 0.333333333, 1.0).normalized(),
    ]

    votes_inside = 0
    for r_dir in ray_dirs:
        hit_ts = []
        for v0, v1, v2 in triangles:
            hit, hit_pt, t, u, v = intersect_ray_triangle(pt, r_dir, v0, v1, v2)
            if hit and t > tol:
                hit_ts.append(t)
        # 去重相近交点 (共享边穿透去重)
        hit_ts.sort()
        dedup_hits = []
        for t in hit_ts:
            if not dedup_hits or (t - dedup_hits[-1]) > tol:
                dedup_hits.append(t)

        if len(dedup_hits) % 2 == 1:
            votes_inside += 1

    if votes_inside >= 2:
        return IntersectionResult(
            has_intersection=True,
            type=IntersectionType.CONTAINED,
            points=[pt],
            clearance=0.0,
            description="点在网格实体内部",
        )

    return IntersectionResult(
        has_intersection=False,
        type=IntersectionType.NONE,
        clearance=None,
        description="点在网格实体外部",
    )


def intersect_line_mesh(line: Line3D, mesh: Any, tol: float = EPS_SPATIAL) -> IntersectionResult:
    """空间线段穿透三维实体网格，提取有序交点与多区间实体厚度."""
    triangles = _mesh_to_triangles(mesh)
    if not triangles:
        return IntersectionResult(has_intersection=False, status=IntersectionStatus.INVALID_INPUT)

    d = line.end - line.start
    line_len = d.length()
    if line_len < tol:
        return point_in_mesh(line.start, mesh, tol)

    d_dir = d.scale(1.0 / line_len)

    raw_hits: list[tuple[float, Point3D]] = []
    for v0, v1, v2 in triangles:
        hit, hit_pt, t, u, v = intersect_ray_triangle(line.start, d_dir, v0, v1, v2)
        if hit and (-tol <= t <= line_len + tol) and hit_pt is not None:
            raw_hits.append((t, hit_pt))

    # 按沿线参数 t 排序并去重
    raw_hits.sort(key=lambda x: x[0])
    dedup_hits: list[Point3D] = []
    dedup_ts: list[float] = []
    for t, pt in raw_hits:
        if not dedup_hits or pt.distance_to(dedup_hits[-1]) > tol:
            dedup_hits.append(pt)
            dedup_ts.append(t)

    if not dedup_hits:
        return IntersectionResult(has_intersection=False, type=IntersectionType.NONE)

    # 成对组装材料穿透区间并计算实穿厚度
    intervals = []
    solid_thickness = 0.0
    for i in range(0, len(dedup_hits) - 1, 2):
        p_in = dedup_hits[i]
        p_out = dedup_hits[i + 1]
        thick = p_in.distance_to(p_out)
        intervals.append((p_in, p_out, thick))
        solid_thickness += thick

    res_type = IntersectionType.MULTI_POINTS if len(dedup_hits) > 1 else IntersectionType.POINT

    return IntersectionResult(
        has_intersection=True,
        type=res_type,
        points=dedup_hits,
        parameters={
            "solid_thickness": solid_thickness,
            "intervals": intervals,
            "t_list": dedup_ts,
        },
        description=f"线段穿透实体，产生 {len(dedup_hits)} 个交点，穿透实厚度 {solid_thickness:.4f}",
    )


def slice_mesh_with_plane(plane: Plane3D, mesh: Any, tol: float = EPS_SPATIAL) -> list[Line3D]:
    """空间剖切平面与网格面片求交，生成离散切片交线段集合."""
    triangles = _mesh_to_triangles(mesh)
    segments: list[Line3D] = []
    n = plane.normal.normalized()

    for v0, v1, v2 in triangles:
        d0 = (v0 - plane.center).dot(n)
        d1 = (v1 - plane.center).dot(n)
        d2 = (v2 - plane.center).dot(n)

        # 检查是否跨越平面
        if (d0 > tol and d1 > tol and d2 > tol) or (d0 < -tol and d1 < -tol and d2 < -tol):
            continue

        verts = [v0, v1, v2]
        dists = [d0, d1, d2]
        cut_pts = []

        for i in range(3):
            j = (i + 1) % 3
            if (dists[i] * dists[j]) <= 0.0 and abs(dists[i] - dists[j]) > EPS_ANGULAR:
                alpha = dists[i] / (dists[i] - dists[j])
                cut_p = Point3D(
                    verts[i].x + alpha * (verts[j].x - verts[i].x),
                    verts[i].y + alpha * (verts[j].y - verts[i].y),
                    verts[i].z + alpha * (verts[j].z - verts[i].z),
                )
                if not cut_pts or cut_p.distance_to(cut_pts[-1]) > tol:
                    cut_pts.append(cut_p)

        if len(cut_pts) == 2 and cut_pts[0].distance_to(cut_pts[1]) > tol:
            segments.append(Line3D(cut_pts[0], cut_pts[1]))

    return segments


def assemble_contour_loops(segments: list[Line3D], tol: float = EPS_SPATIAL) -> list[dict[str, Any]]:
    """将离散空间切片线段缝合为闭合或开放轮廓环 (识别外环与内孔洞)."""
    if not segments:
        return []

    remaining = list(segments)
    loops: list[dict[str, Any]] = []

    while remaining:
        current_seg = remaining.pop(0)
        loop_pts = [current_seg.start, current_seg.end]

        extended = True
        while extended:
            extended = False
            # 尝试在尾部拼接
            tail = loop_pts[-1]
            for idx, seg in enumerate(remaining):
                if tail.distance_to(seg.start) <= tol:
                    loop_pts.append(seg.end)
                    remaining.pop(idx)
                    extended = True
                    break
                elif tail.distance_to(seg.end) <= tol:
                    loop_pts.append(seg.start)
                    remaining.pop(idx)
                    extended = True
                    break

            # 尝试在头部拼接
            head = loop_pts[0]
            for idx, seg in enumerate(remaining):
                if head.distance_to(seg.end) <= tol:
                    loop_pts.insert(0, seg.start)
                    remaining.pop(idx)
                    extended = True
                    break
                elif head.distance_to(seg.start) <= tol:
                    loop_pts.insert(0, seg.end)
                    remaining.pop(idx)
                    extended = True
                    break

        is_closed = (loop_pts[0].distance_to(loop_pts[-1]) <= tol) and len(loop_pts) >= 4
        loops.append({
            "points": loop_pts,
            "is_closed": is_closed,
            "is_hole": False,
        })

    return loops


# ==============================================================================
# Phase E: 双平面相交、体体干涉、包含判定与网格自交
# ==============================================================================

def intersect_planes(p1: Plane3D, p2: Plane3D, tol: float = EPS_ANGULAR) -> IntersectionResult:
    """双平面相交求交线 (主轴稳态降维解 2x2 方程组)."""
    n1 = p1.normal.normalized()
    n2 = p2.normal.normalized()
    d_line = n1.cross(n2)
    d_len = d_line.length()

    c1 = (n1.x * p1.center.x + n1.y * p1.center.y + n1.z * p1.center.z)
    c2 = (n2.x * p2.center.x + n2.y * p2.center.y + n2.z * p2.center.z)

    if d_len < tol:
        # 平行或共面
        diff = p1.center - p2.center
        dist = abs(diff.dot(n1))
        if dist <= EPS_SPATIAL:
            return IntersectionResult(
                has_intersection=True,
                type=IntersectionType.COPLANAR_AREA,
                clearance=0.0,
                description="双平面完全重合共面",
            )
        return IntersectionResult(
            has_intersection=False,
            type=IntersectionType.NONE,
            clearance=dist,
            description="双平面相互平行无交",
        )

    # 选取主轴分量最大者设为 0，求解 2x2 方程组
    abs_x, abs_y, abs_z = abs(d_line.x), abs(d_line.y), abs(d_line.z)

    if abs_z >= abs_x and abs_z >= abs_y:
        # 令 z = 0, 解 x 与 y
        det = n1.x * n2.y - n1.y * n2.x
        x = (c1 * n2.y - c2 * n1.y) / det
        y = (n1.x * c2 - n2.x * c1) / det
        z = 0.0
    elif abs_y >= abs_x and abs_y >= abs_z:
        # 令 y = 0, 解 x 与 z
        det = n1.x * n2.z - n1.z * n2.x
        x = (c1 * n2.z - c2 * n1.z) / det
        y = 0.0
        z = (n1.x * c2 - n2.x * c1) / det
    else:
        # 令 x = 0, 解 y 与 z
        det = n1.y * n2.z - n1.z * n2.y
        x = 0.0
        y = (c1 * n2.z - c2 * n1.z) / det
        z = (n1.y * c2 - n2.y * c1) / det

    base_pt = Point3D(x, y, z)
    dir_unit = d_line.scale(1.0 / d_len)
    line_seg = Line3D(base_pt, Point3D(base_pt.x + dir_unit.x, base_pt.y + dir_unit.y, base_pt.z + dir_unit.z))

    return IntersectionResult(
        has_intersection=True,
        type=IntersectionType.LINE,
        line=line_seg,
        parameters={"direction": dir_unit, "base_point": base_pt},
        description="双平面相交于无限空间直线",
    )


def intersect_mesh_mesh(m1: Any, m2: Any, tol: float = EPS_SPATIAL) -> IntersectionResult:
    """实体网格与实体网格相交与完全包含碰撞检测 (AABB粗筛 -> 面片相交细筛 -> 实体包含检测)."""
    # 1. AABB 包围盒粗筛
    v1 = m1.vertices
    v2 = m2.vertices
    if not v1 or not v2:
        return IntersectionResult(has_intersection=False, status=IntersectionStatus.INVALID_INPUT)

    min1_x = min(p.x for p in v1)
    max1_x = max(p.x for p in v1)
    min1_y = min(p.y for p in v1)
    max1_y = max(p.y for p in v1)
    min1_z = min(p.z for p in v1)
    max1_z = max(p.z for p in v1)

    min2_x = min(p.x for p in v2)
    max2_x = max(p.x for p in v2)
    min2_y = min(p.y for p in v2)
    max2_y = max(p.y for p in v2)
    min2_z = min(p.z for p in v2)
    max2_z = max(p.z for p in v2)

    if (max1_x < min2_x - tol or max2_x < min1_x - tol or
            max1_y < min2_y - tol or max2_y < min1_y - tol or
            max1_z < min2_z - tol or max2_z < min1_z - tol):
        return IntersectionResult(has_intersection=False, type=IntersectionType.NONE, description="AABB包围盒分离无碰撞")

    # 2. 面片三角形细筛
    t1_list = _mesh_to_triangles(m1)
    t2_list = _mesh_to_triangles(m2)

    clash_lines: list[Line3D] = []
    for tri1 in t1_list:
        for tri2 in t2_list:
            res_tt = intersect_triangle_triangle(tri1, tri2, tol)
            if res_tt.has_intersection and res_tt.line is not None:
                clash_lines.append(res_tt.line)

    if clash_lines:
        return IntersectionResult(
            has_intersection=True,
            type=IntersectionType.MULTI_SEGMENTS,
            lines=clash_lines,
            description=f"实体表面发生干涉碰撞，产生 {len(clash_lines)} 条交线段",
        )

    # 3. 实体完全包含检验 (防止无表面交线的嵌套实体漏报)
    p_in_1 = point_in_mesh(v2[0], m1, tol)
    if p_in_1.has_intersection and p_in_1.type == IntersectionType.CONTAINED:
        return IntersectionResult(
            has_intersection=True,
            type=IntersectionType.CONTAINED,
            description="实体 2 完全嵌套包含于实体 1 内部",
        )

    p_in_2 = point_in_mesh(v1[0], m2, tol)
    if p_in_2.has_intersection and p_in_2.type == IntersectionType.CONTAINED:
        return IntersectionResult(
            has_intersection=True,
            type=IntersectionType.CONTAINED,
            description="实体 1 完全嵌套包含于实体 2 内部",
        )

    return IntersectionResult(has_intersection=False, type=IntersectionType.NONE, description="实体表面未相交且无相互包含")


def check_mesh_self_intersection(mesh: Any, tol: float = EPS_SPATIAL) -> tuple[bool, list[tuple[int, int]]]:
    """检测三维网格曲面是否存在非相邻面片自相交 (防止折叠破面)."""
    faces = mesh.faces
    num_faces = len(faces)
    if num_faces < 4:
        return False, []

    triangles = []
    face_map = []
    verts = mesh.vertices
    for f_idx, face in enumerate(faces):
        if len(face) == 3:
            triangles.append((verts[face[0]], verts[face[1]], verts[face[2]]))
            face_map.append(f_idx)
        elif len(face) >= 4:
            for k in range(1, len(face) - 1):
                triangles.append((verts[face[0]], verts[face[k]], verts[face[k + 1]]))
                face_map.append(f_idx)

    intersecting_pairs: list[tuple[int, int]] = []
    num_tris = len(triangles)
    for i in range(num_tris):
        orig_i = face_map[i]
        fi_verts = set(faces[orig_i])
        for j in range(i + 1, num_tris):
            orig_j = face_map[j]
            if orig_i == orig_j:
                continue
            # 排除拓扑共享顶点/边
            fj_verts = set(faces[orig_j])
            if len(fi_verts.intersection(fj_verts)) > 0:
                continue

            res = intersect_triangle_triangle(triangles[i], triangles[j], tol)
            if res.has_intersection and res.line is not None:
                pair = (min(orig_i, orig_j), max(orig_i, orig_j))
                if pair not in intersecting_pairs:
                    intersecting_pairs.append(pair)

    return len(intersecting_pairs) > 0, intersecting_pairs
