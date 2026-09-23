# python_civil_drawing

> Python for Civil Engineers: Computational Geometry, 3D Modeling & CAD Engineering Drawing

[English](README.md) | [中文](README_ZH.md)

🌐 **Official Course Website**: [https://drawing.python.venchy.online/](https://drawing.python.venchy.online/)  
📺 **Bilibili Space & Channel**: [parleychou (周文琪)](https://space.bilibili.com/517887865)  
🔴 **Live Sessions & Replays**: [https://drawing.python.venchy.online/live/](https://drawing.python.venchy.online/live/)

This repository contains comprehensive course slides and production-ready source code tailored for civil engineers, structural designers, and AEC professionals looking to master 3D computational geometry, parametric surface generation, boundary representations (B-Rep), and 3D rendering with PyVista and Three.js.

---

## 📺 Live Stream Replays & Video Tutorials (Bilibili)

All video lectures, recordings, and upcoming live session bookings are available on Bilibili:

| Session | Date | Topic | Video Link / Booking |
|---|---|---|---|
| **Session 01** | 2026-06-09 | Introduction & Conda/PyVista Development Environment | [Watch on Bilibili (BV1k8EE6gEdq)](https://www.bilibili.com/video/BV1k8EE6gEdq/) |
| **Session 02** | 2026-06-25 | Geometric Primitives, 3D Engine & Collision Detection | [Watch on Bilibili (BV19kKS6EE9f)](https://www.bilibili.com/video/BV19kKS6EE9f/) |
| **Session 03** | 2026-08-13 | Parametric Geometry, B-Rep & Mesh Generation | [Watch on Bilibili (BV13Ygp6LED6)](https://www.bilibili.com/video/BV13Ygp6LED6/) |
| **Session 04** | 2026-09-24 | Solid & Surface Representations (Surface, B-Rep & Mesh) | [Book Live on Bilibili](http://t.bilibili.com/1251078433829552132?bsource=dynamic_reserve) · [3D Poster](https://drawing.python.venchy.online/posters/06-body-representation/) |

> For the complete live archive and updates, visit the [Live Archives Hub](https://drawing.python.venchy.online/live/).

---

## 🖥️ Interactive Web Slides (Direct Online View)

All slides are built with HTML5, responsive styling, and embedded Three.js 3D interactive graphics. Click below to view them directly in your browser without any setup:

| Chapter | Title | Online Slide Link |
|---|---|---|
| **Chapter 01** | Course Overview & Python in AEC / BIM | 🔗 [01.01-overview-slides.html](https://drawing.python.venchy.online/slides/01.01-overview-slides.html) |
| **Chapter 02** | Python Development Environment Setup | 🔗 [02.01-python-environment-slides.html](https://drawing.python.venchy.online/slides/02.01-python-environment-slides.html) |
| **Chapter 03** | Essential Engineering Libraries | 🔗 [03.01-common-libraries-slides.html](https://drawing.python.venchy.online/slides/03.01-common-libraries-slides.html) |
| **Chapter 04** | Building the 3D PyVista Render Engine | 🔗 [04.01-pyvista-render-engine-slides.html](https://drawing.python.venchy.online/slides/04.01-pyvista-render-engine-slides.html) |
| **Chapter 05.01** | Object-Oriented Geometric Data Structure | 🔗 [05.01-basic-geometry-data-slides.html](https://drawing.python.venchy.online/slides/05.01-basic-geometry-data-slides.html) |
| **Chapter 05.02** | OOP & Parametric Geometric Primitives | 🔗 [05.02-oop-parametric-geometry-slides.html](https://drawing.python.venchy.online/slides/05.02-oop-parametric-geometry-slides.html) |
| **Chapter 06** | Solid & Surface Representations (Surface / B-Rep / Mesh) | 🔗 [06.01-body-representation-slides.html](https://drawing.python.venchy.online/slides/06.01-body-representation-slides.html) |

---

## 📁 Repository Structure

```text
python_civil_drawing/
├── scripts/     # All consolidated Python source code, geometry primitives, and tests
├── slides/      # Interactive HTML5 + Three.js slide presentations
├── README.md    # English documentation (default)
└── README_ZH.md # Chinese documentation
```

### 1. Source Code (`scripts/`)
Organized as a unified, flat directory for ease of learning and execution:
- **03 Essential Libraries**: Vector mathematics (`numpy`), 2D technical plotting (`matplotlib`), tabular quantities (`pandas`), Excel workbook generation (`openpyxl`), spatial distance computation (`scipy`), 3D viewport rendering (`pyvista`), CAD solid modeling (`build123d`), DXF drawing export (`ezdxf`), 2D geometric intersections (`shapely`).
- **04 3D Rendering Engine**: PyVista viewport management, custom camera controls, multi-view layouts, and the reusable `RenderEngine` class.
- **05 Geometric Primitives**: Unified `GeometryData` abstract base class, 3D point (`Point3D`), 3D vector (`Vector3D`), local coordinate system (`CoordinateSystem3D`), line segment (`Line3D`), plane (`Plane3D`), circle (`Circle3D`), and arc (`Arc3D`).
- **06 Surface & Body Representations**:
  - **Parametric Surface**: `ParametricSurfaceData`, hyperbolic paraboloid (saddle roof), and parametric sphere.
  - **Boundary Representation (B-Rep)**: `BrepData` with explicit vertex, edge, and face topological connectivity (box/cube generation).
  - **Polygon Mesh**: `MeshData` with indexed vertices and polygonal faces (pyramid mesh).
  - **Multi-Object Scene**: `07_render_surface_brep_mesh_scene.py` side-by-side interactive 3D comparison.
- **Unit Tests**: Full test suite (`test_geometry_data.py` and `test_brep_mesh_rendering.py`) powered by `pytest`.

---

## 🚀 Quick Start

### Requirements
- Python 3.11+ (Python 3.12 recommended)
- Install required dependencies:
  ```bash
  pip install numpy scipy matplotlib pandas openpyxl pyvista shapely ezdxf build123d pytest
  ```

### Run Unit Tests
```bash
pytest scripts/
```

### Run Demos
```bash
# Launch side-by-side comparison: Surface vs B-Rep vs Mesh
python scripts/07_render_surface_brep_mesh_scene.py

# Launch 3D point, vector, and coordinate system scene
python scripts/05_render_geometry_scene.py

# Launch hyperbolic paraboloid (saddle surface) renderer
python scripts/02_render_surface_marked.py
```
