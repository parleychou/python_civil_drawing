"""test_10_03_bvh_tree.py — 层次包围盒树 (BVH) 构建与树-树相交遍历测试。"""

import pytest
from collision import AABB, BVHTree
from point3d import Point3D
from vector3d import Vector3D


def test_bvh_tree_build_and_intersect():
    # 构件集合 A: 梁构件
    beams = [
        ("B1", AABB(0, 0, 2800, 6000, 300, 3400)),
        ("B2", AABB(0, 3000, 2800, 6000, 3300, 3400)),
    ]
    # 构件集合 B: 管道构件
    pipes = [
        ("P1", AABB(2500, -500, 3000, 2700, 5000, 3200)),  # 穿过 B1 和 B2
        ("P2", AABB(10000, 10000, 0, 10200, 10200, 500)),   # 远离
    ]

    tree_a = BVHTree.build_top_down(beams)
    tree_b = BVHTree.build_top_down(pipes)

    clashes = tree_a.intersect_tree(tree_b)
    # P1 穿透 B1 和 B2 -> 2 处相交
    assert ("B1", "P1") in clashes or ("P1", "B1") in clashes
    assert ("B2", "P1") in clashes or ("P1", "B2") in clashes
    assert len(clashes) == 2


def test_bvh_ray_cast():
    boxes = [
        ("BOX_1", AABB(10, -5, -5, 20, 5, 5)),
        ("BOX_2", AABB(50, -5, -5, 60, 5, 5)),
    ]
    tree = BVHTree.build_top_down(boxes)

    # 沿 +X 射线射出
    ray_origin = Point3D(0, 0, 0)
    ray_dir = Vector3D(1, 0, 0)
    hits = tree.ray_cast(ray_origin, ray_dir)

    assert "BOX_1" in hits
    assert "BOX_2" in hits
