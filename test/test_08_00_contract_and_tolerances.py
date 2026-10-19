"""Test 08.00: Contracts, Types, and Tolerances for Intersection Engine."""

import pytest
from point3d import Point3D
from line3d import Line3D
from intersection import (
    IntersectionType,
    IntersectionStatus,
    IntersectionResult,
    EPS_SPATIAL,
    EPS_ANGULAR,
    EPS_PARAM,
)


def test_tolerance_constants():
    assert EPS_SPATIAL == 1e-4      # 0.1 um 空间长度
    assert EPS_ANGULAR == 1e-9      # 弧度
    assert EPS_PARAM == 1e-7        # 无量纲参数


def test_intersection_result_defaults():
    res = IntersectionResult(has_intersection=False)
    assert res.has_intersection is False
    assert res.type == IntersectionType.NONE
    assert res.status == IntersectionStatus.SUCCESS
    assert res.points == []
    assert res.line is None
    assert res.lines == []
    assert res.contours == []
    assert res.parameters == {}
    assert res.clearance is None
    assert res.point is None


def test_intersection_result_properties():
    pt = Point3D(1.0, 2.0, 3.0)
    res = IntersectionResult(
        has_intersection=True,
        type=IntersectionType.POINT,
        points=[pt],
        parameters={"t_self": 0.5},
        clearance=0.0
    )
    assert res.has_intersection is True
    assert res.point == pt
    assert res.parameters["t_self"] == 0.5
    assert res.clearance == 0.0
