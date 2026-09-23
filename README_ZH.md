# python_civil_drawing

> 土木人的 Python 课 —— 工程制图、计算几何与三维建模核心实战

[English](README.md) | [中文](README_ZH.md)

本项目包含专为土木与工程设计人员打造的 Python 计算几何、三维实体表达与三维渲染全套课件与源码。

---

## 📁 目录结构

```text
python_civil_drawing/
├── scripts/     # 全部工程源码与核心几何库（单一目录扁平化组织）
├── slides/      # 各章节交互式 HTML 幻灯片课件与三维可视化演示
├── README.md    # 英文文档（默认）
└── README_ZH.md # 中文文档
```

### 1. 核心代码 (`scripts/`)
涵盖从基础工程计算库到参数化几何体与拓扑表达：
- **03 常用库入门**：Numpy 向量计算、Matplotlib 二维图、Pandas 表格、OpenPyxl 数据导出、SciPy 距离矩阵、PyVista 视口、build123d 实体、ezdxf 制图、Shapely 几何相交。
- **04 渲染引擎封装**：PyVista 多视口初始化、坐标系、光照背景配置与 `RenderEngine` 交互类。
- **05 基础几何表达**：`GeometryData` 统一抽象基类，点 (`Point3D`)、向量 (`Vector3D`)、坐标系 (`CoordinateSystem3D`)、线段 (`Line3D`)、平面 (`Plane3D`)、圆 (`Circle3D`) 与圆弧 (`Arc3D`)。
- **06 面和体的表达方式**：
  - 参数化曲面 (`ParametricSurfaceData`, 双曲抛物面/马鞍面、球面)
  - 边界表示法 (`BrepData`, 长方体/立方体精确拓扑)
  - 多边形网格 (`MeshData`, 四棱锥网格)
  - 对比渲染场景 (`07_render_surface_brep_mesh_scene.py`)
- **单元测试**：`test_geometry_data.py` 和 `test_brep_mesh_rendering.py`（使用 `pytest` 运行）。

### 2. 在线课件 (`slides/`)
基于 HTML5 + Three.js 构建的现代交互式工程幻灯片：
- `01.01-overview-slides.html`：土木人的 Python 课综述
- `02.01-python-environment-slides.html`：Python 开发环境配置
- `03.01-common-libraries-slides.html`：常用工程计算库
- `04.01-pyvista-render-engine-slides.html`：接入三维渲染引擎
- `05.01-basic-geometry-data-slides.html`：基本几何数据与面向对象
- `05.02-oop-parametric-geometry-slides.html`：面向对象与几何参数化表达
- `06.01-body-representation-slides.html`：面和体的表达方式（Surface / B-Rep / Mesh）

---

## 🚀 快速开始

### 运行环境
- Python 3.11+ (推荐 Python 3.12)
- 依赖库：
  ```bash
  pip install numpy scipy matplotlib pandas openpyxl pyvista shapely ezdxf build123d pytest
  ```

### 运行单元测试
```bash
pytest scripts/
```

### 运行示例脚本
```bash
# 启动曲面、B-Rep、Mesh 三合一三维对比渲染视口
python scripts/07_render_surface_brep_mesh_scene.py

# 启动点、向量与三维坐标系渲染演示
python scripts/05_render_geometry_scene.py
```
