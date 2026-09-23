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
├── src/         # 纯几何内核与 RenderEngine 基础渲染系统
├── examples/    # 实际对象建模、综合场景渲染与第三方库实操代码
├── test/        # pytest 单元测试目录
├── slides/      # 各章节交互式 HTML 幻灯片课件与三维可视化演示
├── README.md    # 英文文档（默认）
└── README_ZH.md # 中文文档
```

### 1. 纯几何与渲染内核 (`src/`)
高度内聚的纯几何与渲染引擎体系，所有几何对象均继承自 `GeometryData`：
- **基类抽象**：`_base.py` (`GeometryData(ABC)`, `CurveData`, `SurfaceData`)
- **0D-1D 几何图元**：`Point3D`、`Vector3D`、`CoordinateSystem3D`、`Line3D`、`Plane3D`、`Circle3D`、`Arc3D`、`Curve`
- **2D 参数化曲面**：`ParametricSurfaceData`、`HyperbolicParaboloid`（马鞍面）、`SphereSurface`（球面）
- **3D 实体与网格**：`BrepData`（欧拉拓扑边界表示）、`MeshData`（离散多边形网格）、`factories.py`
- **渲染引擎**：`RenderEngine`（基于 PyVista 的多视口调度、相机预设与坐标轴渲染）
- **统一包导出接口**：`__init__.py`（向外统一导出 `src` 命名空间下的所有几何、曲面、实体、网格与渲染核心类）

### 2. 示例与实物建模 (`examples/`)
基于纯几何内核构建实际结构对象与功能验证的脚本：
- **曲面、B-Rep 与网格构建渲染**：`06_01_create_surface_example.py` ~ `06_07_render_surface_brep_mesh_scene.py`
- **图元与点线场景渲染**：`05_07_render_geometry_scene.py`、`04_06_render_points_and_curves.py`
- **梁立方体建模**：`04_02_render_beam_cube.py`、`04_03_pyvista_beam_cube.py`
- **第三方库实操教学**：NumPy、Matplotlib、Pandas、openpyxl、SciPy、build123d、ezdxf、Shapely

### 3. 单元测试 (`test/`)
独立测试目录，使用 `pytest` 运行：
- `test_05_01_geometry_data.py`：第 05 章基础几何类型（点、向量、坐标系、线、面、圆、弧）单元测试。
- `test_06_01_brep_mesh_rendering.py`：第 06 章曲面、B-Rep、Mesh 数据结构与拓扑、PyVista 转换测试。

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
python examples/07_render_surface_brep_mesh_scene.py

# 启动点、向量与三维坐标系渲染演示
python examples/05_render_geometry_scene.py

# 启动双曲抛物面 (马鞍面) 渲染
python examples/02_render_surface_marked.py
```
