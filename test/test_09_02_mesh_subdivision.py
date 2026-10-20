"""test_09_02_mesh_subdivision.py — 空间三角形约束切分重剖测试。"""

import pytest
import numpy as np
from boolean_ops import split_triangle_by_segments


def test_triangle_splitting_area_conservation():
    # 空间三角形 V0(0,0,0), V1(10,0,0), V2(0,10,0) (原面积 50)
    v0 = [0.0, 0.0, 0.0]
    v1 = [10.0, 0.0, 0.0]
    v2 = [0.0, 10.0, 0.0]

    # 切割线段 P1(5,0,0) -> P2(0,5,0)
    seg = ([5.0, 0.0, 0.0], [0.0, 5.0, 0.0])

    sub_tris = split_triangle_by_segments(v0, v1, v2, [seg])
    assert len(sub_tris) >= 2

    def tri_area(p0, p1, p2):
        return 0.5 * np.linalg.norm(np.cross(p1 - p0, p2 - p0))

    orig_area = tri_area(np.array(v0), np.array(v1), np.array(v2))
    sub_area_sum = sum(tri_area(p0, p1, p2) for p0, p1, p2 in sub_tris)

    assert orig_area == pytest.approx(50.0)
    assert sub_area_sum == pytest.approx(50.0, rel=1e-5)


def test_triangle_splitting_normal_direction():
    # 验证子三角形法向与原三角形朝向一致 (指向 +Z)
    v0 = [0.0, 0.0, 0.0]
    v1 = [10.0, 0.0, 0.0]
    v2 = [0.0, 10.0, 0.0]
    orig_normal = np.cross(np.array(v1) - np.array(v0), np.array(v2) - np.array(v0))
    orig_normal = orig_normal / np.linalg.norm(orig_normal)

    seg = ([5.0, 0.0, 0.0], [0.0, 5.0, 0.0])
    sub_tris = split_triangle_by_segments(v0, v1, v2, [seg])

    for p0, p1, p2 in sub_tris:
        sub_norm = np.cross(p1 - p0, p2 - p0)
        sub_norm_unit = sub_norm / np.linalg.norm(sub_norm)
        # 点积应接近 1.0
        assert np.dot(orig_normal, sub_norm_unit) == pytest.approx(1.0, abs=1e-4)
