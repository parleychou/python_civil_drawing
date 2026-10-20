"""test_09_01_polygon_boolean.py — 2D 多边形布尔裁剪测试。"""

import pytest
from polygon2d import Polygon2D


def test_polygon_area_and_contains():
    # 10x10 正方形
    poly = Polygon2D([(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)])
    assert poly.area() == pytest.approx(100.0)
    assert poly.perimeter() == pytest.approx(40.0)
    assert poly.contains_point((5.0, 5.0)) is True
    assert poly.contains_point((15.0, 5.0)) is False
    assert poly.contains_point((-1.0, 5.0)) is False


def test_polygon_difference_slab_opening():
    # 模拟第1课随堂练习：底板 10x10，开洞 2x8 跨越边界
    slab = Polygon2D([(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)])
    # 切割盒 x in [4, 6], y in [-2, 6]
    cutter = Polygon2D([(4.0, -2.0), (6.0, -2.0), (6.0, 6.0), (4.0, 6.0)])
    
    diff_polys = slab.difference(cutter)
    # 应产生一个凹多边形，面积 = 100 - (2 * 6) = 88.0
    total_area = sum(p.area() for p in diff_polys)
    assert total_area == pytest.approx(88.0, rel=1e-3)
    # 验证开洞中心 (5, 3) 已不在多边形内部
    assert any(p.contains_point((5.0, 3.0)) for p in diff_polys) is False
    # 验证原未开洞点 (2, 2) 仍在内部
    assert any(p.contains_point((2.0, 2.0)) for p in diff_polys) is True


def test_polygon_union_overlap():
    poly_a = Polygon2D([(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)])
    poly_b = Polygon2D([(5.0, 0.0), (15.0, 0.0), (15.0, 10.0), (5.0, 10.0)])
    
    unions = poly_a.union(poly_b)
    # 面积 = 100 + 100 - 50 = 150
    total_area = sum(p.area() for p in unions)
    assert total_area == pytest.approx(150.0, rel=1e-3)
    assert any(p.contains_point((2.0, 5.0)) for p in unions) is True
    assert any(p.contains_point((12.0, 5.0)) for p in unions) is True


def test_polygon_intersection():
    poly_a = Polygon2D([(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)])
    poly_b = Polygon2D([(5.0, 0.0), (15.0, 0.0), (15.0, 10.0), (5.0, 10.0)])
    
    inter = poly_a.intersection(poly_b)
    # 重叠区域 x in [5, 10], y in [0, 10], 面积 50
    total_area = sum(p.area() for p in inter)
    assert total_area == pytest.approx(50.0, rel=1e-3)
    assert any(p.contains_point((7.5, 5.0)) for p in inter) is True
    assert any(p.contains_point((2.0, 5.0)) for p in inter) is False
