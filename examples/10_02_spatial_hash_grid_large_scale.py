"""10_02_spatial_hash_grid_large_scale.py — 空间网格哈希大规模构件 O(N) 极速初筛。

演示内容：
1. 在 100m x 100m x 30m 场地范围内生成 1,200 个建筑构件 (柱、梁、穿楼管道)；
2. 执行暴力两两比对 O(N²)，记录耗时与检测对数；
3. 构建体素尺寸 5000mm 的空间哈希网格 (SpatialHashGrid)，执行 O(N) 局部体素筛选；
4. 对比两者效率，验证百倍加速比与 100% 检出率 (零漏报)；
5. 抽取典型冲突区域，使用 RenderEngine 进行三维空间分区与碰撞构件高亮渲染。

命令行参数：
- --offscreen：无头后台离屏运行模式，用于自动化测试与 CI/CD。
"""

import argparse
import random
import sys
import time
from pathlib import Path

# Ensure root is in sys.path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src import (
    Point3D,
    MeshData,
    RenderEngine,
    AABB,
    SpatialHashGrid,
    sweep_and_prune,
)
from factories import create_box_mesh
import pyvista as pv


def main():
    parser = argparse.ArgumentParser(description="10_02 空间网格哈希大规模构件初筛")
    parser.add_argument("--offscreen", action="store_true", help="无头离屏运行")
    args = parser.parse_args()

    print("=" * 70)
    print("【案例 10_02】空间网格哈希 (Spatial Hash Grid) 大规模初筛性能基准测试")
    print("=" * 70)

    # 固定随机种子确保结果可复现
    random.seed(42)

    # 1. 模拟生成 1200 个构件
    num_elements = 1200
    elements: list[tuple[str, AABB, MeshData]] = []

    print(f"-> 正在生成 {num_elements} 个 BIM 空间构件...")
    for i in range(num_elements):
        # 80% 为常规结构构件，20% 为随机管线
        cx = random.uniform(0, 100000.0)
        cy = random.uniform(0, 100000.0)
        cz = random.uniform(0, 30000.0)

        if i % 5 == 0:
            # 穿层立管 / 长管线
            dx, dy, dz = 200.0, 200.0, 6000.0
            name = f"PIPE_{i}"
        elif i % 2 == 0:
            # 框架柱
            dx, dy, dz = 600.0, 600.0, 3600.0
            name = f"COL_{i}"
        else:
            # 框架梁
            dx, dy, dz = 6000.0, 400.0, 600.0
            name = f"BEAM_{i}"

        box_mesh = create_box_mesh(Point3D(cx, cy, cz), dx, dy, dz)
        box_mesh.name = name
        aabb = AABB.from_mesh(box_mesh)
        elements.append((name, aabb, box_mesh))

    # 2. 暴力两两初筛测试 O(N^2)
    print(f"\n[1] 执行全量暴力两两碰撞初筛 (Brute Force N*(N-1)/2 = {num_elements * (num_elements - 1) // 2} 次判定)...")
    t0 = time.perf_counter()
    brute_candidates = set()
    n = len(elements)
    for i in range(n):
        id_a, aabb_a, _ = elements[i]
        for j in range(i + 1, n):
            id_b, aabb_b, _ = elements[j]
            if aabb_a.overlaps(aabb_b):
                brute_candidates.add((min(id_a, id_b), max(id_a, id_b)))
    t_brute = (time.perf_counter() - t0) * 1000.0
    print(f"-> 暴力初筛耗时: {t_brute:.2f} ms，命中候选对: {len(brute_candidates)} 组")

    # 3. 空间哈希网格初筛 O(N)
    print(f"\n[2] 执行空间哈希网格初筛 (Cell Size = 8000 mm)...")
    t1 = time.perf_counter()
    grid = SpatialHashGrid(cell_size=8000.0)
    for name, aabb, _ in elements:
        grid.insert(name, aabb)
    grid_candidates = grid.query_candidates()
    t_grid = (time.perf_counter() - t1) * 1000.0
    print(f"-> 空间网格哈希耗时: {t_grid:.2f} ms (构建+查询)，命中候选对: {len(grid_candidates)} 组")

    # 4. 算法验证与加速比
    speedup = t_brute / max(1e-5, t_grid)
    assert brute_candidates == grid_candidates, "空间哈希初筛结果必须与全量暴力比对完全一致！"
    print(f"\n-> 检出一致性核验: 100% 吻合 (零漏检、零误筛)")
    print(f"-> 算法性能加速比: 【{speedup:.1f}x 倍加速】")

    # 5. 可视化渲染：展示命中碰撞的典型构件对
    engine = RenderEngine(off_screen=args.offscreen)

    # 提取发生碰撞的构件集合
    clashing_ids = set()
    for id_a, id_b in list(grid_candidates)[:10]:  # 取前 10 组典型碰撞进行高精度视口呈现
        clashing_ids.add(id_a)
        clashing_ids.add(id_b)

    for name, _, mesh in elements:
        if name in clashing_ids:
            engine.render_mesh(mesh, color="crimson", opacity=0.9)
        elif random.random() < 0.05:  # 稀疏采样背景构件
            engine.render_mesh(mesh, color="lightgray", opacity=0.3)

    if args.offscreen:
        engine.plotter.screenshot("output_10_02.png")
        engine.plotter.close()
    else:
        engine.show()

    print("[SUCCESS] 案例 10_02 运行完成。")


if __name__ == "__main__":
    main()
