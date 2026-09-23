"""Matplotlib 基础功能介绍：折线图、柱状图、散点图、多子图、填充图、饼图。

每个函数演示一个主题，用 NumPy 生成数据，Matplotlib 渲染图片。
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

OUTPUT_DIR = Path(__file__).resolve().parent / "output"


# ── 1. 折线图 ──────────────────────────────────────────────


def demo_line_plot() -> None:
    """折线图：sin / cos 曲线。"""
    x = np.linspace(0, 2 * np.pi, 100)

    fig, ax = plt.subplots()
    ax.plot(x, np.sin(x), label="sin(x)")
    ax.plot(x, np.cos(x), label="cos(x)")
    ax.set_title("折线图 - sin / cos")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "01_line_plot.png", dpi=150)
    print("已保存: 01_line_plot.png")
    plt.show()
    # plt.close(fig)


# ── 2. 柱状图 ──────────────────────────────────────────────


def demo_bar_plot() -> None:
    """柱状图：分组柱状。"""
    labels = ["A", "B", "C", "D"]
    x = np.arange(len(labels))
    vals1 = np.array([23, 45, 56, 78])
    vals2 = np.array([12, 30, 40, 55])
    width = 0.35

    fig, ax = plt.subplots()
    ax.bar(x - width / 2, vals1, width, label="Series 1")
    ax.bar(x + width / 2, vals2, width, label="Series 2")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_title("柱状图 - 分组")
    ax.set_ylabel("Value")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "02_bar_plot.png", dpi=150)
    print("已保存: 02_bar_plot.png")
    plt.close(fig)


# ── 3. 散点图 ──────────────────────────────────────────────


def demo_scatter_plot() -> None:
    """散点图：随机点 + 颜色映射。"""
    np.random.seed(0)
    x = np.random.randn(50)
    y = np.random.randn(50)
    colors = np.random.rand(50)
    sizes = 100 * np.random.rand(50)

    fig, ax = plt.subplots()
    sc = ax.scatter(x, y, c=colors, s=sizes, alpha=0.6, cmap="viridis")
    fig.colorbar(sc, ax=ax, label="Color")
    ax.set_title("散点图")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "03_scatter_plot.png", dpi=150)
    print("已保存: 03_scatter_plot.png")
    plt.close(fig)


# ── 4. 多子图 ──────────────────────────────────────────────


def demo_subplots() -> None:
    """多子图：2×2 布局。"""
    x = np.linspace(0, 2 * np.pi, 100)

    fig, axes = plt.subplots(2, 2, figsize=(10, 8))

    axes[0, 0].plot(x, np.sin(x))
    axes[0, 0].set_title("sin(x)")

    axes[0, 1].plot(x, np.cos(x), color="orange")
    axes[0, 1].set_title("cos(x)")

    axes[1, 0].plot(x, np.tan(x), color="green")
    axes[1, 0].set_ylim(-5, 5)
    axes[1, 0].set_title("tan(x)")

    axes[1, 1].plot(x, np.exp(-x), color="red")
    axes[1, 1].set_title("exp(-x)")

    fig.suptitle("多子图 2x2")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "04_subplots.png", dpi=150)
    print("已保存: 04_subplots.png")
    plt.close(fig)


# ── 5. 填充图 ──────────────────────────────────────────────


def demo_fill_plot() -> None:
    """填充图：两条曲线之间的区域。"""
    x = np.linspace(0, 2 * np.pi, 100)
    y1 = np.sin(x)
    y2 = np.sin(x) + 0.5 * np.sin(2 * x)

    fig, ax = plt.subplots()
    ax.plot(x, y1, label="sin(x)")
    ax.plot(x, y2, label="sin(x) + 0.5*sin(2x)")
    ax.fill_between(x, y1, y2, alpha=0.3, color="skyblue")
    ax.set_title("填充图")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "05_fill_plot.png", dpi=150)
    print("已保存: 05_fill_plot.png")
    plt.close(fig)


# ── 6. 饼图 ────────────────────────────────────────────────


def demo_pie_plot() -> None:
    """饼图：简单占比。"""
    labels = ["A", "B", "C", "D"]
    sizes = [30, 25, 20, 25]

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct="%1.0f%%", startangle=90)
    ax.set_title("饼图")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "06_pie_plot.png", dpi=150)
    print("已保存: 06_pie_plot.png")
    plt.close(fig)


# ── 主函数 ──────────────────────────────────────────────────


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("1. 折线图")
    demo_line_plot()

    print("\n2. 柱状图")
    demo_bar_plot()

    print("\n3. 散点图")
    demo_scatter_plot()

    print("\n4. 多子图")
    demo_subplots()

    print("\n5. 填充图")
    demo_fill_plot()

    print("\n6. 饼图")
    demo_pie_plot()

    print(f"\n所有图片已保存至: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
