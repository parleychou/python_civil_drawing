"""NumPy 基础功能介绍：数组创建、向量运算、矩阵变换、统计与网格生成。

本脚本涵盖土木工程计算中常用的 NumPy 功能，
每个函数演示一个主题，可在 main() 中依次运行。
"""

import numpy as np


# ── 1. 数组创建 ──────────────────────────────────────────────


def demo_array_creation() -> None:
    """演示 NumPy 数组的多种创建方式。"""
    # 从列表创建
    coords = np.array([3000.0, 1500.0, 0.0])
    print("[创建] 从列表:", coords, "  类型:", coords.dtype)

    # 指定 dtype
    ids = np.array([1, 2, 3], dtype=np.int32)
    print("[创建] 指定 int32:", ids, "  类型:", ids.dtype)

    # 全零 / 全一 / 填充
    zeros = np.zeros(3)
    ones = np.ones((2, 3))
    filled = np.full((2, 2), 6.0)  # 6 米层高
    print("[创建] np.zeros(3):", zeros)
    print("[创建] np.ones((2,3)):\n", ones)
    print("[创建] np.full((2,2), 6.0):\n", filled)

    # 等差序列
    floors = np.arange(0, 30, 3)  # 0, 3, 6, ..., 27 米
    print("[创建] np.arange(0, 30, 3):", floors)

    # 等间距采样
    span = np.linspace(0, 6000, 5)  # 6 米跨度，5 个等分点
    print("[创建] np.linspace(0, 6000, 5):", span)


# ── 2. 向量运算 ──────────────────────────────────────────────


def demo_vector_ops() -> None:
    """演示向量加减、模长、点积、叉积。"""
    a = np.array([3.0, 0.0, 0.0])
    b = np.array([0.0, 4.0, 0.0])

    # 加减与数乘
    print("[向量] a + b =", a + b)
    print("[向量] 2 * a =", 2 * a)

    # 模长（norm）
    print("[向量] |a| =", np.linalg.norm(a))
    print("[向量] |b| =", np.linalg.norm(b))

    # 点积 → 判断垂直 / 求投影
    dot = np.dot(a, b)
    print("[向量] a · b =", dot, "(0 表示垂直)")

    # 叉积 → 求法向量
    cross = np.cross(a, b)
    print("[向量] a × b =", cross, "(垂直于 a、b 所在平面)")

    # 归一化
    c = np.array([3.0, 4.0, 0.0])
    unit = c / np.linalg.norm(c)
    print("[向量] 归一化:", unit, "  模长:", np.linalg.norm(unit))


# ── 3. 矩阵与变换 ──────────────────────────────────────────


def demo_matrix_transform() -> None:
    """演示 4×4 齐次变换矩阵的基本用法。"""
    # 单位矩阵
    I = np.eye(4)
    print("[矩阵] 单位矩阵 (4×4):\n", I)

    # 平移矩阵
    T = np.eye(4)
    T[0, 3] = 6000.0  # X 方向平移 6 m
    T[1, 3] = 3000.0  # Y 方向平移 3 m
    print("[矩阵] 平移矩阵:\n", T)

    # 用矩阵变换一个点
    p = np.array([0.0, 0.0, 0.0, 1.0])  # 齐次坐标
    p_new = T @ p
    print("[矩阵] 原始点:", p[:3], " → 变换后:", p_new[:3])

    # 矩阵乘法：组合两次平移
    T2 = np.eye(4)
    T2[2, 3] = 500.0  # Z 方向平移 0.5 m
    combined = T2 @ T
    print("[矩阵] 组合平移 (6m, 3m, 0.5m):", combined[:3, 3])


# ── 4. 数组索引与统计 ──────────────────────────────────────


def demo_indexing_stats() -> None:
    """演示索引、切片、条件筛选与统计函数。"""
    # 梁截面高度数据 (mm)
    heights = np.array([300, 400, 500, 600, 800, 1000])

    # 索引与切片
    print("[索引] 第 1 根:", heights[0])
    print("[索引] 前 3 根:", heights[:3])
    print("[索引] 最后 2 根:", heights[-2:])

    # 条件筛选（布尔索引）
    tall = heights[heights > 500]
    print("[筛选] 高度 > 500 mm:", tall)

    # 统计
    print("[统计] 最大值:", heights.max(), "  位置:", heights.argmax())
    print("[统计] 最小值:", heights.min(), "  位置:", heights.argmin())
    print("[统计] 均值:", heights.mean(), "  标准差:", heights.std())
    print("[统计] 总和:", heights.sum())

    # where 条件
    safe = np.where(heights >= 500, "合规", "偏小")
    print("[条件] 合规性:", safe)


# ── 5. 形状变换与堆叠 ──────────────────────────────────────


def demo_reshape_stack() -> None:
    """演示 reshape、vstack、hstack。"""
    # reshape: 将一维数组变为二维
    data = np.arange(1, 7)  # [1, 2, 3, 4, 5, 6]
    matrix = data.reshape(2, 3)
    print("[形状] reshape(2,3):\n", matrix)
    print("[形状] shape:", matrix.shape)

    # 垂直堆叠：上下拼
    a = np.array([[1, 2], [3, 4]])
    b = np.array([[5, 6]])
    v = np.vstack([a, b])
    print("[堆叠] vstack:\n", v)

    # 水平堆叠：左右拼
    c = np.array([[7], [8]])
    h = np.hstack([a, c])
    print("[堆叠] hstack:\n", h)


# ── 6. 网格生成（曲面与地形基础） ──────────────────────────


def demo_meshgrid() -> None:
    """演示 linspace + meshgrid 生成结构化网格。"""
    x = np.linspace(0, 12, 5)  # X 方向 12m
    y = np.linspace(0, 8, 4)   # Y 方向 8m
    xx, yy = np.meshgrid(x, y)
    print("[网格] X 坐标:\n", xx)
    print("[网格] Y 坐标:\n", yy)

    # 用向量化的数学运算生成屋面高度
    zz = 0.5 * np.sin(xx / 12 * np.pi) * np.sin(yy / 8 * np.pi)
    print("[网格] 屋面高度 Z (m):\n", np.round(zz, 3))


# ── 主函数 ──────────────────────────────────────────────────


def main() -> None:
    """依次运行所有演示。"""
    print("=" * 50)
    print("1. 数组创建")
    print("=" * 50)
    demo_array_creation()

    print("\n" + "=" * 50)
    print("2. 向量运算")
    print("=" * 50)
    demo_vector_ops()

    print("\n" + "=" * 50)
    print("3. 矩阵与变换")
    print("=" * 50)
    demo_matrix_transform()

    print("\n" + "=" * 50)
    print("4. 索引与统计")
    print("=" * 50)
    demo_indexing_stats()

    print("\n" + "=" * 50)
    print("5. 形状变换与堆叠")
    print("=" * 50)
    demo_reshape_stack()

    print("\n" + "=" * 50)
    print("6. 网格生成")
    print("=" * 50)
    demo_meshgrid()


if __name__ == "__main__":
    main()
