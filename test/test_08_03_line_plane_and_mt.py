"""Test 08.03: Line-Plane, Möller-Trumbore Ray-Triangle, Triangle-Triangle, and Benchmark."""

import pytest
import time
from point3d import Point3D
from line3d import Line3D
from plane3d import Plane3D
from vector3d import Vector3D
from intersection import (
    IntersectionType,
    intersect_line_plane,
    intersect_ray_triangle,
    intersect_triangle_triangle,
    benchmark_mt_vs_naive,
)


def test_line_plane_penetration():
    plane = Plane3D(Point3D(0, 0, 5), Vector3D(0, 0, 1))

    # 1. 有限穿透线段 (t=0.5)
    line_pen = Line3D(Point3D(0, 0, 0), Point3D(0, 0, 10))
    res = intersect_line_plane(line_pen, plane, segment_only=True)
    assert res.has_intersection is True
    assert res.type == IntersectionType.POINT
    assert pytest.approx(res.point.z) == 5.0
    assert pytest.approx(res.parameters["t"]) == 0.5

    # 2. 延长线相交 (t=2.0)
    line_ext = Line3D(Point3D(0, 0, 0), Point3D(0, 0, 2.5))
    res_ext = intersect_line_plane(line_ext, plane, segment_only=True)
    assert res_ext.has_intersection is False
    assert res_ext.parameters["is_on_extension"] is True

    # 3. 直线相交 (segment_only=False)
    res_inf = intersect_line_plane(line_ext, plane, segment_only=False)
    assert res_inf.has_intersection is True
    assert pytest.approx(res_inf.point.z) == 5.0

    # 4. 平行无交
    line_par = Line3D(Point3D(0, 0, 0), Point3D(10, 0, 0))
    res_par = intersect_line_plane(line_par, plane, segment_only=True)
    assert res_par.has_intersection is False
    assert res_par.clearance == pytest.approx(5.0, abs=1e-5)


def test_moller_trumbore_ray_triangle():
    v0 = Point3D(0, 0, 0)
    v1 = Point3D(10, 0, 0)
    v2 = Point3D(0, 10, 0)

    # 1. 正中穿透
    ray_start = Point3D(2, 2, -5)
    ray_dir = Vector3D(0, 0, 1)
    hit, pt, t, u, v = intersect_ray_triangle(ray_start, ray_dir, v0, v1, v2)
    assert hit is True
    assert pytest.approx(t) == 5.0
    assert pytest.approx(pt.x) == 2.0
    assert pytest.approx(pt.y) == 2.0
    assert pytest.approx(pt.z) == 0.0
    assert pytest.approx(u) == 0.2
    assert pytest.approx(v) == 0.2

    # 2. 脱靶 (在三角形平面外)
    ray_miss = Point3D(12, 12, -5)
    hit_m, _, _, _, _ = intersect_ray_triangle(ray_miss, ray_dir, v0, v1, v2)
    assert hit_m is False

    # 3. 反向射线 (t < 0)
    ray_back = Point3D(2, 2, 5)
    hit_b, _, t_b, _, _ = intersect_ray_triangle(ray_back, ray_dir, v0, v1, v2)
    assert hit_b is False


def test_triangle_triangle_intersection():
    # 两个空间相互正交交叉的三角形:
    # T1 在平面 Z=5, 顶点 (0, 0, 5), (10, 0, 5), (5, 10, 5)
    # T2 在平面 X=5, 顶点 (5, 5, 0), (5, 5, 10), (5, -5, 5)
    t1 = (Point3D(0, 0, 5), Point3D(10, 0, 5), Point3D(5, 10, 5))
    t2 = (Point3D(5, 5, 0), Point3D(5, 5, 10), Point3D(5, -5, 5))

    res = intersect_triangle_triangle(t1, t2)
    assert res.has_intersection is True
    assert res.type == IntersectionType.SEGMENT
    assert res.line is not None
    # 交线必定满足 X=5 且 Z=5
    assert pytest.approx(res.line.start.x, abs=1e-4) == 5.0
    assert pytest.approx(res.line.start.z, abs=1e-4) == 5.0
    assert pytest.approx(res.line.end.x, abs=1e-4) == 5.0
    assert pytest.approx(res.line.end.z, abs=1e-4) == 5.0


def test_benchmark_mt_reproducible():
    # 验证基准函数可正常执行并返回非负执行时间
    speedup = benchmark_mt_vs_naive(num_rays=500)
    assert speedup > 0.0
