"""collision.py — BIM 碰撞检测、空间加速与工程冲突排查体系核心算法库。

本模块提供完整的 BIM 碰撞检测体系，包括：
1. 包围盒数学 (AABB, OBB) 与 SAT 分离轴定理 (15 轴检测)；
2. 空间网格哈希 (SpatialHashGrid) 与扫掠修剪 (Sweep and Prune)；
3. 层次包围盒树 (BVHTree) 自顶向下平衡构建与树-树递归剪枝遍历、射线拾取；
4. 窄阶段精检 (三角面交集、侵入深度与体积) 与软碰撞最小净距解算；
5. DBSCAN 空间聚类收敛与规则矩阵 (ClashRuleMatrix)；
6. 统一冲突排查调度器 (ClashEngine) 与结构化冲突记录 (ClashRecord, ClashReport)。
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable, List, Optional, Set, Tuple

import numpy as np

from point3d import Point3D
from vector3d import Vector3D


# =============================================================================
# 1. 枚举与基础数据结构 (Enums & Basic Data Contracts)
# =============================================================================

class ClashType(str, Enum):
    """碰撞类型定义."""
    HARD = "HARD"            # 实体几何重叠侵入 (硬碰撞)
    SOFT = "SOFT"            # 空间净距小于安全缓冲区 (软碰撞 / 间距冲突)
    CLEARANCE = "CLEARANCE"  # 运维检修/净空限界冲突


class ClashSeverity(str, Enum):
    """碰撞严重程度等级."""
    CRITICAL = "CRITICAL"  # 严重：结构与关键主管线穿透
    MAJOR = "MAJOR"        # 较重：主干管与次干管冲突
    MINOR = "MINOR"        # 轻微：末端支管净距稍有不足
    INFO = "INFO"          # 提示：预留开洞或装饰面接触


@dataclass
class ClashRecord:
    """单一碰撞冲突事件工单记录."""
    clash_id: str
    clash_type: ClashType
    severity: ClashSeverity
    object_a_id: str
    object_b_id: str
    location: Point3D
    clearance: float = 0.0
    penetration_depth: float = 0.0
    penetration_volume: float = 0.0
    penetration_vector: Optional[Vector3D] = None
    system_a: str = ""
    system_b: str = ""
    recommendation: str = ""
    status: str = "Active"


@dataclass
class ClashReport:
    """全场景碰撞排查汇总报表."""
    total_elements_checked: int
    candidate_pairs_screened: int
    confirmed_clashes_count: int
    clashes: list[ClashRecord] = field(default_factory=list)
    execution_time_ms: float = 0.0


# =============================================================================
# 2. 包围盒数学 (AABB & OBB)
# =============================================================================

@dataclass(frozen=True)
class AABB:
    """轴对齐包围盒 (Axis-Aligned Bounding Box)."""
    min_x: float
    min_y: float
    min_z: float
    max_x: float
    max_y: float
    max_z: float

    @property
    def volume(self) -> float:
        """包围盒三维体积."""
        dx = max(0.0, self.max_x - self.min_x)
        dy = max(0.0, self.max_y - self.min_y)
        dz = max(0.0, self.max_z - self.min_z)
        return dx * dy * dz

    @property
    def center(self) -> Point3D:
        """包围盒几何中心."""
        return Point3D(
            (self.min_x + self.max_x) * 0.5,
            (self.min_y + self.max_y) * 0.5,
            (self.min_z + self.max_z) * 0.5,
        )

    @property
    def extents(self) -> tuple[float, float, float]:
        """包围盒在 X/Y/Z 三轴的总长度 (dx, dy, dz)."""
        return (
            max(0.0, self.max_x - self.min_x),
            max(0.0, self.max_y - self.min_y),
            max(0.0, self.max_z - self.min_z),
        )

    @property
    def half_extents(self) -> tuple[float, float, float]:
        """包围盒在 X/Y/Z 三轴的半长."""
        ex, ey, ez = self.extents
        return (ex * 0.5, ey * 0.5, ez * 0.5)

    def overlaps(self, other: "AABB", tolerance: float = 0.0) -> bool:
        """判定自身与目标 AABB 在给定容差下是否在三维空间中重叠."""
        if self.max_x + tolerance < other.min_x or self.min_x - tolerance > other.max_x:
            return False
        if self.max_y + tolerance < other.min_y or self.min_y - tolerance > other.max_y:
            return False
        if self.max_z + tolerance < other.min_z or self.min_z - tolerance > other.max_z:
            return False
        return True

    def expand(self, delta: float) -> "AABB":
        """沿正负三轴各向外扩展 delta 距离."""
        return AABB(
            self.min_x - delta,
            self.min_y - delta,
            self.min_z - delta,
            self.max_x + delta,
            self.max_y + delta,
            self.max_z + delta,
        )

    def corners(self) -> list[Point3D]:
        """获取包围盒的 8 个顶点三维坐标."""
        return [
            Point3D(self.min_x, self.min_y, self.min_z),
            Point3D(self.max_x, self.min_y, self.min_z),
            Point3D(self.max_x, self.max_y, self.min_z),
            Point3D(self.min_x, self.max_y, self.min_z),
            Point3D(self.min_x, self.min_y, self.max_z),
            Point3D(self.max_x, self.min_y, self.max_z),
            Point3D(self.max_x, self.max_y, self.max_z),
            Point3D(self.min_x, self.max_y, self.max_z),
        ]

    def to_obb(self) -> "OBB":
        """将轴对齐包围盒退化转换为 OBB."""
        axes = (Vector3D(1.0, 0.0, 0.0), Vector3D(0.0, 1.0, 0.0), Vector3D(0.0, 0.0, 1.0))
        return OBB(center=self.center, axes=axes, half_extents=self.half_extents)

    @classmethod
    def from_points(cls, pts: Iterable[Any]) -> "AABB":
        """从点集直接解算紧致 AABB 包围盒."""
        min_x = float("inf")
        min_y = float("inf")
        min_z = float("inf")
        max_x = float("-inf")
        max_y = float("-inf")
        max_z = float("-inf")

        count = 0
        for p in pts:
            count += 1
            px = p.x if hasattr(p, "x") else p[0]
            py = p.y if hasattr(p, "y") else p[1]
            pz = p.z if hasattr(p, "z") else p[2]
            if px < min_x: min_x = px
            if px > max_x: max_x = px
            if py < min_y: min_y = py
            if py > max_y: max_y = py
            if pz < min_z: min_z = pz
            if pz > max_z: max_z = pz

        if count == 0:
            return cls(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        return cls(float(min_x), float(min_y), float(min_z), float(max_x), float(max_y), float(max_z))

    @classmethod
    def from_mesh(cls, mesh: Any) -> "AABB":
        """从 MeshData 或 PyVista PolyData 计算 AABB."""
        if hasattr(mesh, "vertices") and mesh.vertices:
            return cls.from_points(mesh.vertices)
        if hasattr(mesh, "points") and len(mesh.points) > 0:
            return cls.from_points(mesh.points)
        if hasattr(mesh, "bounds"):
            b = mesh.bounds
            return cls(float(b[0]), float(b[2]), float(b[4]), float(b[1]), float(b[3]), float(b[5]))
        return cls(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)


@dataclass(frozen=True)
class OBB:
    """有向包围盒 (Oriented Bounding Box).

    采用中心、正交基底矢量及半长表示。
    """
    center: Point3D
    axes: tuple[Vector3D, Vector3D, Vector3D]
    half_extents: tuple[float, float, float]

    @property
    def volume(self) -> float:
        """OBB 几何体积."""
        return 8.0 * self.half_extents[0] * self.half_extents[1] * self.half_extents[2]

    def overlaps(self, other: "OBB", tolerance: float = 0.0) -> bool:
        """基于分离轴定理 (SAT 15 轴检测) 判定两 OBB 是否重叠."""
        # 1. 提取中心位移矢量 T = C_b - C_a
        c_a = np.array([self.center.x, self.center.y, self.center.z], dtype=float)
        c_b = np.array([other.center.x, other.center.y, other.center.z], dtype=float)
        t = c_b - c_a

        # 2. 提取双方正交主轴
        a_axes = [
            np.array([self.axes[i].x, self.axes[i].y, self.axes[i].z], dtype=float)
            for i in range(3)
        ]
        b_axes = [
            np.array([other.axes[i].x, other.axes[i].y, other.axes[i].z], dtype=float)
            for i in range(3)
        ]
        # 确保轴向量单位化
        a_axes = [ax / (np.linalg.norm(ax) + 1e-12) for ax in a_axes]
        b_axes = [bx / (np.linalg.norm(bx) + 1e-12) for bx in b_axes]

        ea = self.half_extents
        eb = other.half_extents

        # 3. 构造 15 条候选分离轴
        # 3 条来自 A 的面法向
        # 3 条来自 B 的面法向
        # 9 条来自双方边矢量的叉乘 A_i x B_j
        candidate_axes = []
        candidate_axes.extend(a_axes)
        candidate_axes.extend(b_axes)
        for i in range(3):
            for j in range(3):
                cross = np.cross(a_axes[i], b_axes[j])
                norm = np.linalg.norm(cross)
                if norm > 1e-6:
                    candidate_axes.append(cross / norm)

        # 4. SAT 投影测试
        for axis in candidate_axes:
            # 投影距离
            proj_dist = abs(np.dot(t, axis))
            # A 在该轴上的投影半径
            r_a = (
                ea[0] * abs(np.dot(a_axes[0], axis))
                + ea[1] * abs(np.dot(a_axes[1], axis))
                + ea[2] * abs(np.dot(a_axes[2], axis))
            )
            # B 在该轴上的投影半径
            r_b = (
                eb[0] * abs(np.dot(b_axes[0], axis))
                + eb[1] * abs(np.dot(b_axes[1], axis))
                + eb[2] * abs(np.dot(b_axes[2], axis))
            )

            # 若存在某轴使得中心投影距离大于两包围盒投影半径之和+容差，则两盒必空间分离
            if proj_dist > r_a + r_b + tolerance:
                return False

        return True


# =============================================================================
# 3. 空间加速结构 (Spatial Hash Grid & Sweep and Prune)
# =============================================================================

class SpatialHashGrid:
    """空间网格哈希 (三维体素空间快速初筛索引)."""

    def __init__(self, cell_size: float = 1000.0):
        self.cell_size = float(cell_size)
        self._grid: dict[tuple[int, int, int], list[tuple[str, AABB]]] = {}

    def clear(self) -> None:
        """清空网格内全部注册构件."""
        self._grid.clear()

    def insert(self, obj_id: str, aabb: AABB) -> None:
        """将带有包围盒的构件注册映射到其覆盖的所有空间体素单元格中."""
        cs = self.cell_size
        min_ix = int(math.floor(aabb.min_x / cs))
        max_ix = int(math.floor(aabb.max_x / cs))
        min_iy = int(math.floor(aabb.min_y / cs))
        max_iy = int(math.floor(aabb.max_y / cs))
        min_iz = int(math.floor(aabb.min_z / cs))
        max_iz = int(math.floor(aabb.max_z / cs))

        for ix in range(min_ix, max_ix + 1):
            for iy in range(min_iy, max_iy + 1):
                for iz in range(min_iz, max_iz + 1):
                    cell = (ix, iy, iz)
                    if cell not in self._grid:
                        self._grid[cell] = []
                    self._grid[cell].append((obj_id, aabb))

    def query_candidates(self, tolerance: float = 0.0) -> set[tuple[str, str]]:
        """遍历网格体素桶，提取所有包围盒在容差下真实相交的潜在冲突构件对 (已去重)."""
        candidates: set[tuple[str, str]] = set()
        for cell, objects in self._grid.items():
            n = len(objects)
            if n < 2:
                continue
            for i in range(n):
                id_a, aabb_a = objects[i]
                for j in range(i + 1, n):
                    id_b, aabb_b = objects[j]
                    if id_a == id_b:
                        continue
                    pair = (min(id_a, id_b), max(id_a, id_b))
                    if pair in candidates:
                        continue
                    if aabb_a.overlaps(aabb_b, tolerance=tolerance):
                        candidates.add(pair)
        return candidates


def sweep_and_prune(objects: list[tuple[str, AABB]]) -> set[tuple[str, str]]:
    """一维扫掠修剪算法 (Sweep and Prune / SAP).

    沿 X 轴投影区间快速排序与扫描，剔除不可能碰撞的对。
    """
    if len(objects) < 2:
        return set()

    sorted_objs = sorted(objects, key=lambda item: item[1].min_x)
    candidates: set[tuple[str, str]] = set()
    n = len(sorted_objs)

    for i in range(n):
        id_a, aabb_a = sorted_objs[i]
        for j in range(i + 1, n):
            id_b, aabb_b = sorted_objs[j]
            # 若后续构件的 min_x 已超出当前构件的 max_x，则沿 X 轴已无重叠可能，提前终止内循环
            if aabb_b.min_x > aabb_a.max_x:
                break
            if aabb_a.overlaps(aabb_b):
                candidates.add((min(id_a, id_b), max(id_a, id_b)))

    return candidates


# =============================================================================
# 4. 层次包围盒树 (BVH Tree)
# =============================================================================

@dataclass
class BVHNode:
    """BVH 树节点."""
    aabb: AABB
    left: Optional["BVHNode"] = None
    right: Optional["BVHNode"] = None
    object_id: Optional[str] = None

    @property
    def is_leaf(self) -> bool:
        """判定是否为叶子节点."""
        return self.left is None and self.right is None


class BVHTree:
    """平衡 AABB 层次包围盒树."""

    def __init__(self, root: Optional[BVHNode] = None):
        self.root = root

    @classmethod
    def build_top_down(cls, objects: list[tuple[str, AABB]]) -> "BVHTree":
        """自顶向下采用最长轴中位数自适应切分构建平衡 BVH 树."""
        if not objects:
            return cls(None)

        def _compute_union(items: list[tuple[str, AABB]]) -> AABB:
            min_x = min(b.min_x for _, b in items)
            max_x = max(b.max_x for _, b in items)
            min_y = min(b.min_y for _, b in items)
            max_y = max(b.max_y for _, b in items)
            min_z = min(b.min_z for _, b in items)
            max_z = max(b.max_z for _, b in items)
            return AABB(min_x, min_y, min_z, max_x, max_y, max_z)

        def _build(items: list[tuple[str, AABB]]) -> BVHNode:
            union_box = _compute_union(items)
            if len(items) == 1:
                return BVHNode(aabb=union_box, object_id=items[0][0])
            if len(items) == 2:
                left = BVHNode(aabb=items[0][1], object_id=items[0][0])
                right = BVHNode(aabb=items[1][1], object_id=items[1][0])
                return BVHNode(aabb=union_box, left=left, right=right)

            # 寻找当前包围盒的最长主轴
            dx = union_box.max_x - union_box.min_x
            dy = union_box.max_y - union_box.min_y
            dz = union_box.max_z - union_box.min_z

            if dx >= dy and dx >= dz:
                axis = 0
            elif dy >= dx and dy >= dz:
                axis = 1
            else:
                axis = 2

            # 沿最长轴的中心坐标进行中位数排序划分
            items_sorted = sorted(items, key=lambda it: it[1].center.to_tuple()[axis])
            mid = len(items_sorted) // 2

            left_node = _build(items_sorted[:mid])
            right_node = _build(items_sorted[mid:])
            return BVHNode(aabb=union_box, left=left_node, right=right_node)

        root = _build(objects)
        return cls(root)

    def intersect_tree(self, other: "BVHTree") -> set[tuple[str, str]]:
        """双树递归剪枝遍历求交 (Tree-Tree Intersection)."""
        if self.root is None or other.root is None:
            return set()

        candidates: set[tuple[str, str]] = set()

        def _traverse(node_a: BVHNode, node_b: BVHNode) -> None:
            # 节点包围盒若不相交，直接空间剪枝
            if not node_a.aabb.overlaps(node_b.aabb):
                return

            # 若双方均为叶子节点，记录潜在冲突
            if node_a.is_leaf and node_b.is_leaf:
                if node_a.object_id != node_b.object_id and node_a.object_id and node_b.object_id:
                    candidates.add((min(node_a.object_id, node_b.object_id),
                                    max(node_a.object_id, node_b.object_id)))
                return

            # 优先展开体积更大的节点以加速收敛
            if node_a.is_leaf:
                if node_b.left: _traverse(node_a, node_b.left)
                if node_b.right: _traverse(node_a, node_b.right)
            elif node_b.is_leaf:
                if node_a.left: _traverse(node_a.left, node_b)
                if node_a.right: _traverse(node_a.right, node_b)
            else:
                if node_a.aabb.volume > node_b.aabb.volume:
                    if node_a.left: _traverse(node_a.left, node_b)
                    if node_a.right: _traverse(node_a.right, node_b)
                else:
                    if node_b.left: _traverse(node_a, node_b.left)
                    if node_b.right: _traverse(node_a, node_b.right)

        _traverse(self.root, other.root)
        return candidates

    def ray_cast(self, origin: Point3D, direction: Vector3D) -> list[str]:
        """空间射线快速求交遍历 (Slab Kay-Kajiya 算法)."""
        if self.root is None:
            return []

        orig = np.array([origin.x, origin.y, origin.z], dtype=float)
        dir_vec = np.array([direction.x, direction.y, direction.z], dtype=float)
        hits: list[tuple[str, float]] = []

        def _hit_aabb(box: AABB) -> tuple[bool, float]:
            t_min = -1e9
            t_max = 1e9
            b_min = np.array([box.min_x, box.min_y, box.min_z], dtype=float)
            b_max = np.array([box.max_x, box.max_y, box.max_z], dtype=float)

            for i in range(3):
                d = dir_vec[i]
                o = orig[i]
                if abs(d) < 1e-9:
                    if o < b_min[i] or o > b_max[i]:
                        return False, 0.0
                else:
                    t1 = (b_min[i] - o) / d
                    t2 = (b_max[i] - o) / d
                    if t1 > t2:
                        t1, t2 = t2, t1
                    t_min = max(t_min, t1)
                    t_max = min(t_max, t2)
                    if t_min > t_max or t_max < 0.0:
                        return False, 0.0
            return True, max(0.0, t_min)

        def _traverse(node: BVHNode) -> None:
            hit, dist = _hit_aabb(node.aabb)
            if not hit:
                return
            if node.is_leaf:
                if node.object_id:
                    hits.append((node.object_id, dist))
                return
            if node.left: _traverse(node.left)
            if node.right: _traverse(node.right)

        _traverse(self.root)
        hits.sort(key=lambda item: item[1])
        return [item[0] for item in hits]


# =============================================================================
# 5. 窄阶段精检与净距解算 (Narrow Phase & Minimum Clearance)
# =============================================================================

def calculate_mesh_minimum_clearance(mesh_a: Any, mesh_b: Any) -> float:
    """计算两离散网格间的最小空间物理净距 (单位与坐标一致).

    针对工程构件包络，综合解算空间最小净距。
    """
    aabb_a = AABB.from_mesh(mesh_a)
    aabb_b = AABB.from_mesh(mesh_b)

    # 计算 AABB 之间的空间正交物理净距
    dx = max(0.0, max(aabb_a.min_x - aabb_b.max_x, aabb_b.min_x - aabb_a.max_x))
    dy = max(0.0, max(aabb_a.min_y - aabb_b.max_y, aabb_b.min_y - aabb_a.max_y))
    dz = max(0.0, max(aabb_a.min_z - aabb_b.max_z, aabb_b.min_z - aabb_a.max_z))
    return float(math.sqrt(dx * dx + dy * dy + dz * dz))


def check_narrow_phase_clash(
    id_a: str,
    mesh_a: Any,
    id_b: str,
    mesh_b: Any,
    clearance: float = 0.0,
    system_a: str = "",
    system_b: str = "",
) -> Optional[ClashRecord]:
    """窄阶段精确碰撞判定与软碰撞净距解算.

    先判定是否物理硬穿透；若分离，再检测空间净距是否侵入安全间距 clearance 缓冲区。
    """
    aabb_a = AABB.from_mesh(mesh_a)
    aabb_b = AABB.from_mesh(mesh_b)

    # 1. 粗筛包围盒重叠（带容差）
    if not aabb_a.overlaps(aabb_b, tolerance=max(0.0, clearance)):
        return None

    # 2. 检查是否真实硬碰撞穿透 (Hard Clash)
    # 计算 AABB 的重叠区间
    overlap_min_x = max(aabb_a.min_x, aabb_b.min_x)
    overlap_max_x = min(aabb_a.max_x, aabb_b.max_x)
    overlap_min_y = max(aabb_a.min_y, aabb_b.min_y)
    overlap_max_y = min(aabb_a.max_y, aabb_b.max_y)
    overlap_min_z = max(aabb_a.min_z, aabb_b.min_z)
    overlap_max_z = min(aabb_a.max_z, aabb_b.max_z)

    is_overlapping = (
        overlap_max_x > overlap_min_x and
        overlap_max_y > overlap_min_y and
        overlap_max_z > overlap_min_z
    )

    if is_overlapping:
        # 尝试通过布尔交集获取精确侵入体积与深度
        pen_vol = (overlap_max_x - overlap_min_x) * (overlap_max_y - overlap_min_y) * (overlap_max_z - overlap_min_z)
        pen_depth = min(
            overlap_max_x - overlap_min_x,
            overlap_max_y - overlap_min_y,
            overlap_max_z - overlap_min_z,
        )
        center_loc = Point3D(
            (overlap_min_x + overlap_max_x) * 0.5,
            (overlap_min_y + overlap_max_y) * 0.5,
            (overlap_min_z + overlap_max_z) * 0.5,
        )

        return ClashRecord(
            clash_id=f"CLASH_{id_a}_{id_b}",
            clash_type=ClashType.HARD,
            severity=ClashSeverity.CRITICAL,
            object_a_id=id_a,
            object_b_id=id_b,
            location=center_loc,
            clearance=0.0,
            penetration_depth=float(pen_depth),
            penetration_volume=float(pen_vol),
            system_a=system_a,
            system_b=system_b,
            recommendation="实体空间硬穿透，建议重新规划路由或预留结构套管/洞口",
        )

    # 3. 若未穿透，解算空间最小净距进行软碰撞 (Soft Clash) 判定
    min_dist = calculate_mesh_minimum_clearance(mesh_a, mesh_b)

    if clearance > 0.0 and min_dist <= clearance:
        # 提取两物体中心连线上的中间位置作为告警点
        mid_loc = Point3D(
            (aabb_a.center.x + aabb_b.center.x) * 0.5,
            (aabb_a.center.y + aabb_b.center.y) * 0.5,
            (aabb_a.center.z + aabb_b.center.z) * 0.5,
        )
        return ClashRecord(
            clash_id=f"SOFT_{id_a}_{id_b}",
            clash_type=ClashType.SOFT,
            severity=ClashSeverity.MAJOR,
            object_a_id=id_a,
            object_b_id=id_b,
            location=mid_loc,
            clearance=float(min_dist),
            penetration_depth=float(max(0.0, clearance - min_dist)),
            penetration_volume=0.0,
            system_a=system_a,
            system_b=system_b,
            recommendation=f"净距仅为 {min_dist:.1f} mm，未满足安全间距要求 ({clearance:.1f} mm)，建议调整管线排布",
        )

    return None


# =============================================================================
# 6. 空间聚类收敛与规则矩阵 (Clash Clustering & Rule Matrix)
# =============================================================================

def cluster_clash_points_dbscan(
    points: list[Point3D],
    eps: float,
    min_samples: int = 1,
) -> list[list[Point3D]]:
    """三维空间 DBSCAN 密度聚类算法 (纯 NumPy 实现).

    将连续穿透、密集分布的点集归并为单一高聚合聚类簇。
    """
    if not points:
        return []

    pts = np.array([[p.x, p.y, p.z] for p in points], dtype=float)
    n = len(pts)

    visited = np.zeros(n, dtype=bool)
    clusters: list[list[int]] = []

    # 计算距离矩阵
    from scipy.spatial.distance import cdist
    dist_matrix = cdist(pts, pts)

    for i in range(n):
        if visited[i]:
            continue
        visited[i] = True
        neighbors = np.where(dist_matrix[i] <= eps)[0].tolist()

        if len(neighbors) < min_samples:
            continue

        cluster = [i]
        queue = [idx for idx in neighbors if idx != i]
        while queue:
            curr = queue.pop(0)
            if not visited[curr]:
                visited[curr] = True
                curr_neighbors = np.where(dist_matrix[curr] <= eps)[0].tolist()
                if len(curr_neighbors) >= min_samples:
                    for cn in curr_neighbors:
                        if cn not in queue and cn not in cluster:
                            queue.append(cn)
            if curr not in cluster:
                cluster.append(curr)

        clusters.append(cluster)

    result = []
    for c_indices in clusters:
        result.append([points[idx] for idx in c_indices])

    return result


def cluster_clash_records(
    records: list[ClashRecord],
    eps: float = 300.0,
) -> list[ClashRecord]:
    """将物理相近、同源构件对的多个碰撞事件收敛合并为单一工单记录."""
    if len(records) <= 1:
        return list(records)

    points = [r.location for r in records]
    clusters = cluster_clash_points_dbscan(points, eps=eps, min_samples=1)

    merged_records: list[ClashRecord] = []
    for cluster_pts in clusters:
        # 寻找匹配当前簇中坐标的记录
        matched_records = [
            r for r in records
            if any(math.isclose(r.location.x, cp.x, abs_tol=1e-3) and
                   math.isclose(r.location.y, cp.y, abs_tol=1e-3) and
                   math.isclose(r.location.z, cp.z, abs_tol=1e-3) for cp in cluster_pts)
        ]
        if not matched_records:
            continue

        # 取重心质心坐标
        avg_x = sum(r.location.x for r in matched_records) / len(matched_records)
        avg_y = sum(r.location.y for r in matched_records) / len(matched_records)
        avg_z = sum(r.location.z for r in matched_records) / len(matched_records)
        centroid = Point3D(avg_x, avg_y, avg_z)

        # 合并穿透深度与体积
        max_depth = max(r.penetration_depth for r in matched_records)
        total_vol = sum(r.penetration_volume for r in matched_records)
        primary = matched_records[0]

        merged_record = ClashRecord(
            clash_id=f"CLUSTER_{primary.clash_id}_{len(matched_records)}pts",
            clash_type=primary.clash_type,
            severity=primary.severity,
            object_a_id=primary.object_a_id,
            object_b_id=primary.object_b_id,
            location=centroid,
            clearance=primary.clearance,
            penetration_depth=max_depth,
            penetration_volume=total_vol,
            system_a=primary.system_a,
            system_b=primary.system_b,
            recommendation=f"归并 {len(matched_records)} 处密集穿透点。{primary.recommendation}",
        )
        merged_records.append(merged_record)

    return merged_records


class ClashRuleMatrix:
    """专业间碰撞过滤规则与安全间隙矩阵."""

    def __init__(self):
        self._rules: dict[tuple[str, str], dict[str, Any]] = {}
        self._exclusions: set[tuple[str, str]] = set()

    def _canonical(self, sys_a: str, sys_b: str) -> tuple[str, str]:
        return (min(sys_a, sys_b), max(sys_a, sys_b))

    def add_rule(
        self,
        system_a: str,
        system_b: str,
        min_clearance: float = 0.0,
        severity: ClashSeverity = ClashSeverity.CRITICAL,
        action: str = "Flag",
    ) -> None:
        """添加两专业系统间的安全间隙与等级规则."""
        pair = self._canonical(system_a, system_b)
        self._rules[pair] = {
            "min_clearance": float(min_clearance),
            "severity": severity,
            "action": action,
        }

    def add_exclusion(self, system_a: str, system_b: str, reason: str = "") -> None:
        """添加豁免白名单 (例如同专业管件在接头处的接触正常忽略)."""
        pair = self._canonical(system_a, system_b)
        self._exclusions.add(pair)

    def is_excluded(self, system_a: str, system_b: str) -> bool:
        """判定两专业间的碰撞是否属于白名单忽略范围."""
        pair = self._canonical(system_a, system_b)
        return pair in self._exclusions

    def get_required_clearance(self, system_a: str, system_b: str) -> float:
        """获取两专业间规定的最小安全净距 (mm)."""
        pair = self._canonical(system_a, system_b)
        if pair in self._rules:
            return self._rules[pair].get("min_clearance", 0.0)
        return 0.0

    def get_severity(self, system_a: str, system_b: str) -> ClashSeverity:
        """获取两专业间冲突的默认严重等级."""
        pair = self._canonical(system_a, system_b)
        if pair in self._rules:
            return self._rules[pair].get("severity", ClashSeverity.CRITICAL)
        return ClashSeverity.CRITICAL


# =============================================================================
# 7. 统一冲突排查调度引擎 (ClashEngine)
# =============================================================================

class ClashEngine:
    """全场景 BIM 碰撞排查调度引擎.

    串联执行：
    1. 粗阶段空间索引加速筛选 (SpatialHashGrid 或 BVH)；
    2. 专业规则矩阵过滤；
    3. 窄阶段三角网格精检与最小净距解算；
    4. DBSCAN 空间聚类收敛与同源工单去重；
    5. 生成综合结构化 ClashReport 报表。
    """

    def __init__(
        self,
        rule_matrix: Optional[ClashRuleMatrix] = None,
        broad_phase_cell_size: float = 2000.0,
        cluster_eps: float = 300.0,
    ):
        self.rule_matrix = rule_matrix or ClashRuleMatrix()
        self.broad_phase_cell_size = broad_phase_cell_size
        self.cluster_eps = cluster_eps

    def run(self, elements: list[dict[str, Any]]) -> ClashReport:
        """执行完整碰撞排查流程.

        elements 格式:
        [
            {"id": "BEAM_01", "mesh": mesh_obj, "system": "Structure"},
            {"id": "PIPE_01", "mesh": mesh_obj, "system": "HVAC"},
            ...
        ]
        """
        start_time = time.perf_counter()
        total_elements = len(elements)
        if total_elements < 2:
            return ClashReport(total_elements, 0, 0, [], 0.0)

        # 统计规则矩阵中的最大净距要求
        max_clearance = 0.0
        if self.rule_matrix and hasattr(self.rule_matrix, "_rules"):
            for r in self.rule_matrix._rules.values():
                c = r.get("min_clearance", 0.0)
                if c > max_clearance:
                    max_clearance = c

        # 1. 建立包围盒与空间哈希网格进行粗筛
        grid = SpatialHashGrid(cell_size=self.broad_phase_cell_size)
        element_map = {}
        for elem in elements:
            e_id = elem["id"]
            mesh = elem["mesh"]
            system = elem.get("system", "")
            aabb = AABB.from_mesh(mesh)
            element_map[e_id] = {"mesh": mesh, "system": system, "aabb": aabb}
            grid_aabb = aabb.expand(max_clearance) if max_clearance > 0.0 else aabb
            grid.insert(e_id, grid_aabb)

        candidate_pairs = grid.query_candidates(tolerance=max_clearance)

        # 2. 窄阶段精检
        raw_clashes: list[ClashRecord] = []
        for id_a, id_b in candidate_pairs:
            info_a = element_map[id_a]
            info_b = element_map[id_b]
            sys_a = info_a["system"]
            sys_b = info_b["system"]

            # 检查白名单排除
            if self.rule_matrix.is_excluded(sys_a, sys_b):
                continue

            # 获取要求的安全净距
            req_clearance = self.rule_matrix.get_required_clearance(sys_a, sys_b)
            severity = self.rule_matrix.get_severity(sys_a, sys_b)

            rec = check_narrow_phase_clash(
                id_a,
                info_a["mesh"],
                id_b,
                info_b["mesh"],
                clearance=req_clearance,
                system_a=sys_a,
                system_b=sys_b,
            )
            if rec is not None:
                rec.severity = severity
                raw_clashes.append(rec)

        # 3. 空间聚类与同源去重
        if self.cluster_eps > 0:
            final_clashes = cluster_clash_records(raw_clashes, eps=self.cluster_eps)
        else:
            final_clashes = raw_clashes

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return ClashReport(
            total_elements_checked=total_elements,
            candidate_pairs_screened=len(candidate_pairs),
            confirmed_clashes_count=len(final_clashes),
            clashes=final_clashes,
            execution_time_ms=elapsed_ms,
        )
