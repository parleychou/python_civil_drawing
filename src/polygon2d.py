"""polygon2d.py — 二维平面多边形与截面布尔运算模块。

提供土木工程常用的 2D 截面多边形数据结构、面积/周长计算、点在多边形内判定、
以及基于集合论的多边形布尔运算（并集 Union、差集 Difference/Cut、交集 Intersection）。
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Tuple, Sequence, Optional, Union
import numpy as np

try:
    from shapely.geometry import Polygon as _ShapelyPolygon, MultiPolygon as _ShapelyMultiPolygon
    from shapely.ops import unary_union as _unary_union
    _HAS_SHAPELY = True
except ImportError:
    _HAS_SHAPELY = False


Point2DType = Tuple[float, float]


@dataclass
class Polygon2D:
    """二维封闭平面多边形。

    Attributes:
        vertices: 顺时针或逆时针排列的多边形外边界顶点坐标列表 [(x, y), ...]
        holes: 内部开孔环列表 [[(x, y), ...], ...]
    """
    vertices: List[Point2DType] = field(default_factory=list)
    holes: List[List[Point2DType]] = field(default_factory=list)

    def __post_init__(self):
        # 规整化顶点为 float 元组
        clean_verts: List[Point2DType] = []
        for pt in self.vertices:
            clean_verts.append((float(pt[0]), float(pt[1])))
        # 若首尾相连则移除重复末点以方便统一处理
        if len(clean_verts) > 1 and math.isclose(clean_verts[0][0], clean_verts[-1][0], abs_tol=1e-7) and \
           math.isclose(clean_verts[0][1], clean_verts[-1][1], abs_tol=1e-7):
            clean_verts = clean_verts[:-1]
        self.vertices = clean_verts

    def area(self) -> float:
        """使用鞋带公式 (Shoelace formula) 计算多边形净面积 (扣除内孔)。"""
        if len(self.vertices) < 3:
            return 0.0

        def _ring_area(pts: Sequence[Point2DType]) -> float:
            n = len(pts)
            area = 0.0
            for i in range(n):
                j = (i + 1) % n
                area += pts[i][0] * pts[j][1] - pts[j][0] * pts[i][1]
            return 0.5 * abs(area)

        outer_area = _ring_area(self.vertices)
        holes_area = sum(_ring_area(h) for h in self.holes if len(h) >= 3)
        return max(0.0, outer_area - holes_area)

    def perimeter(self) -> float:
        """计算外边界与内孔周长总和。"""
        if len(self.vertices) < 2:
            return 0.0

        def _ring_len(pts: Sequence[Point2DType]) -> float:
            n = len(pts)
            total = 0.0
            for i in range(n):
                j = (i + 1) % n
                dx = pts[j][0] - pts[i][0]
                dy = pts[j][1] - pts[i][1]
                total += math.hypot(dx, dy)
            return total

        return _ring_len(self.vertices) + sum(_ring_len(h) for h in self.holes)

    def contains_point(self, pt: Point2DType, tolerance: float = 1e-7) -> bool:
        """使用三维微扰射线奇偶法 (Jordan Curve Theorem) 判定点是否在多边形内部。"""
        x, y = float(pt[0]), float(pt[1])

        def _in_ring(pts: Sequence[Point2DType]) -> bool:
            n = len(pts)
            inside = False
            for i in range(n):
                j = (i + 1) % n
                xi, yi = pts[i]
                xj, yj = pts[j]

                # 点在边上判定
                dist_seg = _point_segment_distance_2d((x, y), (xi, yi), (xj, yj))
                if dist_seg <= tolerance:
                    return True

                intersect = ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi)
                if intersect:
                    inside = not inside
            return inside

        # 必须在外环内，且不在任何孔洞内
        if not _in_ring(self.vertices):
            return False
        for hole in self.holes:
            if _in_ring(hole):
                return False
        return True

    def _to_shapely(self) -> _ShapelyPolygon:
        if not _HAS_SHAPELY:
            raise RuntimeError("Shapely 库未安装，无法执行复杂多边形布尔运算。")
        return _ShapelyPolygon(self.vertices, holes=self.holes)

    @classmethod
    def _from_shapely(cls, geom: Any) -> List[Polygon2D]:
        results = []
        if geom.is_empty:
            return results
        if isinstance(geom, _ShapelyPolygon):
            geoms = [geom]
        elif isinstance(geom, _ShapelyMultiPolygon):
            geoms = list(geom.geoms)
        else:
            return results

        for g in geoms:
            ext = list(g.exterior.coords)[:-1]
            h_list = [list(h.coords)[:-1] for h in g.interiors]
            results.append(cls(vertices=ext, holes=h_list))
        return results

    def difference(self, other: Polygon2D) -> List[Polygon2D]:
        """计算自身与目标多边形的布尔差集 (Cut / A \\ B)。"""
        poly_a = self._to_shapely()
        poly_b = other._to_shapely()
        res = poly_a.difference(poly_b)
        return self._from_shapely(res)

    def cut(self, other: Polygon2D) -> List[Polygon2D]:
        """difference 的工程别名。"""
        return self.difference(other)

    def union(self, other: Polygon2D) -> List[Polygon2D]:
        """计算自身与目标多边形的布尔并集 (A ∪ B)。"""
        poly_a = self._to_shapely()
        poly_b = other._to_shapely()
        res = poly_a.union(poly_b)
        return self._from_shapely(res)

    def intersection(self, other: Polygon2D) -> List[Polygon2D]:
        """计算自身与目标多边形的布尔交集 (A ∩ B)。"""
        poly_a = self._to_shapely()
        poly_b = other._to_shapely()
        res = poly_a.intersection(poly_b)
        return self._from_shapely(res)

    def intersect(self, other: Polygon2D) -> List[Polygon2D]:
        """intersection 的工程别名。"""
        return self.intersection(other)


def _point_segment_distance_2d(p: Point2DType, a: Point2DType, b: Point2DType) -> float:
    px, py = p
    ax, ay = a
    bx, by = b
    dx = bx - ax
    dy = by - ay
    l2 = dx * dx + dy * dy
    if l2 == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / l2))
    proj_x = ax + t * dx
    proj_y = ay + t * dy
    return math.hypot(px - proj_x, py - proj_y)
