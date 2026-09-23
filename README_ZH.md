# python_civil_drawing

> 土木人的 Python 课 —— 工程制图、计算几何与三维建模核心实战

[English](README.md) | [中文](README_ZH.md)

🌐 **官方课程主页**：[https://drawing.python.venchy.online/](https://drawing.python.venchy.online/)  
📺 **B 站个人空间**：[非解构](https://space.bilibili.com/517887865)  
🔴 **历次直播与录屏回放**：[https://drawing.python.venchy.online/live/](https://drawing.python.venchy.online/live/)

本项目包含专为土木与工程设计人员打造的 Python 计算几何、三维实体表达与三维渲染全套课件与源码。

---

## 📺 直播回放与实战演示 (B 站)

所有课程录屏、直播回放与预约均已同步上线 B 站：

| 期数 | 直播日期 | 课程主题 | B 站视频 / 直播预约 |
|---|---|---|---|
| **第一期** | 2026-06-09 | 导论与开发环境配置 (Conda / PyVista) | [在 B 站观看 (BV1k8EE6gEdq)](https://www.bilibili.com/video/BV1k8EE6gEdq/) |
| **第二期** | 2026-06-25 | 几何对象构建、三维渲染引擎接入与碰撞检测 | [在 B 站观看 (BV19kKS6EE9f)](https://www.bilibili.com/video/BV19kKS6EE9f/) |
| **第三期** | 2026-08-13 | 手搓三维几何与画法几何（参数曲面 / B-Rep / Mesh） | [在 B 站观看 (BV13Ygp6LED6)](https://www.bilibili.com/video/BV13Ygp6LED6/) |
| **第四期** | 2026-09-24 | 面和体的表达（马鞍面、拓扑边界与三角网格） | [前往 B 站预约直播](http://t.bilibili.com/1251078433829552132?bsource=dynamic_reserve) · [3D 动态海报](https://drawing.python.venchy.online/posters/06-body-representation/) |

> 更多直播排期与历史记录可查看 [直播记录总览](https://drawing.python.venchy.online/live/)。

---

## 🖥️ 在线课件浏览 (直接点击在浏览器中查看)

全部课件采用 HTML5 + 响应式排版制作，并内置 Three.js 实时 3D 几何互动视口。点击链接即可在线浏览：

| 章节 | 课件主题 | 在线课件直达链接 |
|---|---|---|
| **第 01 章** | 土木人的 Python 课综述 | 🔗 [01.01-overview-slides.html](https://drawing.python.venchy.online/slides/01.01-overview-slides.html) |
| **第 02 章** | Python 开发环境配置 | 🔗 [02.01-python-environment-slides.html](https://drawing.python.venchy.online/slides/02.01-python-environment-slides.html) |
| **第 03 章** | 常用工程计算库简介 | 🔗 [03.01-common-libraries-slides.html](https://drawing.python.venchy.online/slides/03.01-common-libraries-slides.html) |
| **第 04 章** | 接入 PyVista 三维渲染引擎 | 🔗 [04.01-pyvista-render-engine-slides.html](https://drawing.python.venchy.online/slides/04.01-pyvista-render-engine-slides.html) |
| **第 05.01 章** | 基本几何数据与面向对象设计 | 🔗 [05.01-basic-geometry-data-slides.html](https://drawing.python.venchy.online/slides/05.01-basic-geometry-data-slides.html) |
| **第 05.02 章** | 面向对象与几何参数化表达 | 🔗 [05.02-oop-parametric-geometry-slides.html](https://drawing.python.venchy.online/slides/05.02-oop-parametric-geometry-slides.html) |
| **第 06 章** | 面和体的表达方式 (Surface / B-Rep / Mesh) | 🔗 [06.01-body-representation-slides.html](https://drawing.python.venchy.online/slides/06.01-body-representation-slides.html) |

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
### 2. 单元测试 (`test/`)
独立测试目录，使用 `pytest` 运行：
- `test_geometry_data.py`：第 05 章基础几何类型（点、向量、坐标系、线、面、圆、弧）单元测试。
- `test_brep_mesh_rendering.py`：第 06 章曲面、B-Rep、Mesh 数据结构与拓扑、PyVista 转换测试。

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
pytest test/
```

### 运行示例脚本
```bash
# 启动曲面、B-Rep、Mesh 三合一三维对比渲染视口
python scripts/07_render_surface_brep_mesh_scene.py

# 启动点、向量与三维坐标系渲染演示
python scripts/05_render_geometry_scene.py

# 启动双曲抛物面 (马鞍面) 渲染
python scripts/02_render_surface_marked.py
```
