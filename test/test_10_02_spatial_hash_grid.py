"""test_10_02_spatial_hash_grid.py — 空间网格哈希 (Spatial Hash Grid) 与扫掠修剪测试。"""

import pytest
from collision import AABB, SpatialHashGrid, sweep_and_prune


def test_spatial_hash_grid_mapping_and_candidates():
    grid = SpatialHashGrid(cell_size=1000.0)

    # 构件 1: [0, 800] x [0, 800] x [0, 800] (落入 cell (0,0,0))
    grid.insert("OBJ_1", AABB(0, 0, 0, 800, 800, 800))
    # 构件 2: [500, 1200] x [500, 1200] x [0, 800] (跨越 cell (0,0,0) 与 (1,1,0) 等)
    grid.insert("OBJ_2", AABB(500, 500, 0, 1200, 1200, 800))
    # 构件 3: 遥远孤立体 [5000, 6000] x [5000, 6000] x [0, 800]
    grid.insert("OBJ_3", AABB(5000, 5000, 0, 6000, 6000, 800))

    candidates = grid.query_candidates()
    # 期望检测到 OBJ_1 与 OBJ_2 重叠，且不应检测到 OBJ_3
    assert ("OBJ_1", "OBJ_2") in candidates or ("OBJ_2", "OBJ_1") in candidates
    assert len(candidates) == 1


def test_sweep_and_prune_1d():
    objects = [
        ("A", AABB(0, 0, 0, 10, 10, 10)),
        ("B", AABB(5, 0, 0, 15, 10, 10)),
        ("C", AABB(30, 0, 0, 40, 10, 10)),
    ]
    candidates = sweep_and_prune(objects)
    assert len(candidates) == 1
    assert ("A", "B") in candidates or ("B", "A") in candidates
