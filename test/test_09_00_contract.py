"""test_09_00_contract.py — 布尔运算枚举与数据类契约测试。"""

import pytest
from boolean_ops import (
    BooleanOperationType,
    FaceSpatialRelation,
    BooleanResult,
)


def test_boolean_enums():
    assert BooleanOperationType.UNION.value == "union"
    assert BooleanOperationType.DIFFERENCE.value == "difference"
    assert BooleanOperationType.INTERSECTION.value == "intersection"

    assert FaceSpatialRelation.OUTSIDE.value == "outside"
    assert FaceSpatialRelation.INSIDE.value == "inside"
    assert FaceSpatialRelation.COPLANAR_SAME.value == "coplanar_same"
    assert FaceSpatialRelation.COPLANAR_OPP.value == "coplanar_opp"


def test_boolean_result_defaults():
    res = BooleanResult(success=True, operation=BooleanOperationType.UNION)
    assert res.success is True
    assert res.operation == BooleanOperationType.UNION
    assert res.mesh is None
    assert res.original_volume_a == 0.0
    assert res.original_volume_b == 0.0
    assert res.result_volume == 0.0
    assert res.is_watertight is True
    assert res.warning_message is None
    assert res.execution_time_ms == 0.0
