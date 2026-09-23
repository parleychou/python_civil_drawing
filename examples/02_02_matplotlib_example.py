"""
Matplotlib 入门案例 —— 土木工程绘图示例
包含常用函数说明，覆盖折线图、散点图、柱状图、直方图、子图等
"""

import numpy as np
import matplotlib.pyplot as plt

# =============================================
# 1. 基础折线图 —— plt.plot()
# =============================================
# np.linspace(起始, 结束, 数量) 在区间内生成等间距的数值
x = np.linspace(0, 2 * np.pi, 100)          # 0~2π 之间生成 100 个点

# plt.figure() 创建一个新的画布（Figure），figsize 指定宽高（英寸）
plt.figure(figsize=(8, 4))

# plt.plot(x, y, format_string, label) 绘制折线图
# format_string = 'r--' 表示红色(red)虚线(--)，也可写作 color='red', linestyle='--'
plt.plot(x, np.sin(x), 'b-', label='sin(x)')     # 蓝色实线
plt.plot(x, np.cos(x), 'r--', label='cos(x)')    # 红色虚线

# plt.xlabel() / plt.ylabel() 设置 x / y 轴标签
plt.xlabel('x (弧度)')
plt.ylabel('y')

# plt.title() 设置图表标题
plt.title('正弦与余弦曲线')

# plt.legend() 显示图例（需要 plot 时指定了 label）
plt.legend()

# plt.grid() 显示网格线，linestyle / alpha 控制样式和透明度
plt.grid(linestyle=':', alpha=0.6)

# plt.tight_layout() 自动调整子图间距，防止标签被裁剪
plt.tight_layout()

# plt.savefig() 将当前图表保存为图片文件（支持 png / pdf / svg 等）
plt.savefig('sin_cos.png', dpi=150)

# plt.show() 在屏幕上显示图表（交互窗口）
plt.show()


# =============================================
# 2. 散点图 —— plt.scatter()
# =============================================
# np.random.rand(N) 生成 N 个 [0,1) 均匀分布的随机数
n = 50
x_scatter = np.random.rand(n) * 10                # 0~10 随机 x
y_scatter = np.random.rand(n) * 10                # 0~10 随机 y
colors = np.random.rand(n)                        # 每个点的颜色值
sizes = np.random.rand(n) * 500                   # 每个点的大小

plt.figure(figsize=(7, 5))
# plt.scatter(x, y, s=大小, c=颜色, alpha=透明度, cmap=颜色映射)
# cmap='viridis' 使用 Matplotlib 内置色谱
sc = plt.scatter(x_scatter, y_scatter, s=sizes, c=colors,
                 alpha=0.7, cmap='viridis')
# plt.colorbar() 显示颜色条，映射数值到颜色
plt.colorbar(sc, label='颜色值')

plt.xlabel('X 坐标')
plt.ylabel('Y 坐标')
plt.title('散点图示例（大小 + 颜色映射）')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('scatter_demo.png', dpi=150)
plt.show()


# =============================================
# 3. 柱状图 —— plt.bar()
# =============================================
categories = ['混凝土', '钢筋', '砂石', '水泥', '外加剂']
# 各材料用量（kg/m³）
values = [2400, 150, 800, 350, 5]
# 各材料单价（元/kg）
prices = [0.12, 4.50, 0.08, 0.45, 3.00]

plt.figure(figsize=(9, 5))

# plt.bar(x, height, width, color, alpha) 绘制柱状图
bars = plt.bar(categories, values, width=0.6, color='steelblue', alpha=0.85)

# 在每根柱子上方标注数值
# 遍历 bars 容器，用 bar.get_height() 获取柱高
for bar, val in zip(bars, values):
    # plt.text(x, y, text, ha='center', va='bottom') 在指定坐标添加文字
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 15,
             f'{val} kg', ha='center', va='bottom', fontsize=9)

plt.xlabel('材料类型')
plt.ylabel('用量 (kg/m³)')
plt.title('混凝土配合比材料用量')
plt.tight_layout()
plt.savefig('bar_demo.png', dpi=150)
plt.show()


# =============================================
# 4. 直方图 —— plt.hist()
# =============================================
# 模拟 200 个混凝土试块的抗压强度数据（单位 MPa）
# np.random.normal(均值, 标准差, 数量) 生成正态分布数据
strength = np.random.normal(loc=35, scale=4.0, size=200)

plt.figure(figsize=(8, 5))

# plt.hist(data, bins, edgecolor, alpha) 绘制直方图
# bins=15 将数据分为 15 个区间（组），edgecolor 设置边框色
n, bins, patches = plt.hist(strength, bins=15, edgecolor='white',
                            alpha=0.75, color='coral')

# 添加一条均值线
# plt.axvline(x, color, linestyle, linewidth, label) 绘制垂直参考线
mean_val = np.mean(strength)
plt.axvline(mean_val, color='darkred', linestyle='--',
            linewidth=2, label=f'均值 = {mean_val:.1f} MPa')

plt.xlabel('抗压强度 (MPa)')
plt.ylabel('频数')
plt.title('混凝土试块抗压强度分布')
plt.legend()
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('hist_demo.png', dpi=150)
plt.show()


# =============================================
# 5. 子图布局 —— plt.subplots()
# =============================================
# plt.subplots(nrows, ncols, figsize) 创建多个子图
# 返回 (Figure, axes_array)，axes 是二维数组，可用 ax[row, col] 索引
fig, axes = plt.subplots(2, 2, figsize=(10, 8))

# ------ 子图 (0,0)：折线图 ------
x = np.linspace(0, 10, 50)
axes[0, 0].plot(x, np.sin(x), 'g-', linewidth=1.5)
axes[0, 0].set_title('sin(x)')               # ax.set_title() 设置子图标题
axes[0, 0].set_xlabel('x')
axes[0, 0].set_ylabel('sin(x)')
axes[0, 0].grid(True, alpha=0.3)

# ------ 子图 (0,1)：柱状图 ------
axes[0, 1].bar(['A', 'B', 'C', 'D'], [3, 7, 2, 5], color='teal')
axes[0, 1].set_title('柱状图')

# ------ 子图 (1,0)：散点图 ------
x_r = np.random.rand(30)
y_r = np.random.rand(30)
axes[1, 0].scatter(x_r, y_r, c='orange', s=40, alpha=0.7)
axes[1, 0].set_title('散点图')

# ------ 子图 (1,1)：填充区域图 ax.fill_between() ------
x = np.linspace(0, 5, 100)
y1 = np.sin(x)
y2 = np.sin(x) + 0.3
axes[1, 1].fill_between(x, y1, y2, alpha=0.4, color='skyblue')
axes[1, 1].plot(x, y1, 'b-', label='下界')
axes[1, 1].plot(x, y2, 'r--', label='上界')
axes[1, 1].legend(fontsize=8)
axes[1, 1].set_title('填充区域')

# 整体调整
fig.suptitle('Matplotlib 子图综合示例', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('subplots_demo.png', dpi=150)
plt.show()


# =============================================
print("所有图表已生成并保存。")
print("常用函数速查：")
print("  plt.figure()      —— 创建画布")
print("  plt.plot()        —— 绘制折线图")
print("  plt.scatter()     —— 绘制散点图")
print("  plt.bar()         —— 绘制柱状图")
print("  plt.hist()        —— 绘制直方图")
print("  plt.subplots()    —— 创建多个子图")
print("  plt.xlabel/ylabel —— 设置轴标签")
print("  plt.title()       —— 设置标题")
print("  plt.legend()      —— 显示图例")
print("  plt.grid()        —— 显示网格")
print("  plt.savefig()     —— 保存图片")
print("  plt.show()        —— 显示图表")
print("  plt.text()        —— 在指定坐标添加文字")
print("  plt.axvline()     —— 绘制垂直参考线")
print("  plt.colorbar()    —— 显示颜色条")
