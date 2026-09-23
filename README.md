# python_civil_drawing

> Python for Civil Engineers: Computational Geometry, 3D Modeling & CAD Engineering Drawing

[English](README.md) | [中文](README_ZH.md)

🌐 **Official Course Website**: [https://drawing.python.venchy.online/](https://drawing.python.venchy.online/)  
📺 **Bilibili Space & Channel**: [非解构](https://space.bilibili.com/517887865)  
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
├── src/         # Pure geometry data classes & RenderEngine core system
├── examples/    # Real-world object creation, scenes, and library practices
├── test/        # Unit test suite powered by pytest
├── slides/      # Interactive HTML5 + Three.js slide presentations
├── README.md    # English documentation (default)
└── README_ZH.md # Chinese documentation
```

### 1. Pure Geometry & Render Core (`src/`)
A pure, self-contained geometry and rendering kernel where all geometric types inherit from `GeometryData`:
- **Base Abstraction**: `_base.py` (`GeometryData(ABC)`, `CurveData`, `SurfaceData`)
- **0D-1D Geometric Primitives**: `Point3D`, `Vector3D`, `CoordinateSystem3D`, `Line3D`, `Plane3D`, `Circle3D`, `Arc3D`, `Curve`
- **2D Parametric Surfaces**: `ParametricSurfaceData`, `HyperbolicParaboloid` (saddle surface), `SphereSurface`
- **3D Topologies (B-Rep & Mesh)**: `BrepData` (Euler topological connectivity), `MeshData` (indexed vertex buffer & polygon faces), `factories.py`
- **Rendering Engine**: `RenderEngine` (PyVista-based multi-viewport rendering, camera management, coordinate axes)
- **Unified Package Entry**: `__init__.py` (re-exports all geometry, surface, brep, mesh, and rendering classes under `src`)

### 2. Examples & Real Object Creation (`examples/`)
Runnable demonstration scripts that use the core geometry system or third-party tools:
- **Surface, B-Rep & Mesh Demonstrations**: `06_01_create_surface_example.py` ~ `06_07_render_surface_brep_mesh_scene.py`
- **Primitive Scene Rendering**: `05_07_render_geometry_scene.py`, `04_06_render_points_and_curves.py`
- **Structural Object Modeling**: `04_02_render_beam_cube.py`, `04_03_pyvista_beam_cube.py`
- **Essential Library Tutorials**: NumPy, Matplotlib, Pandas, openpyxl, SciPy, build123d, ezdxf, Shapely

### 3. Unit Tests (`test/`)
Dedicated test directory powered by `pytest`:
- `test_05_01_geometry_data.py`: Unit tests for Chapter 05 geometric primitives.
- `test_06_01_brep_mesh_rendering.py`: Unit tests for Chapter 06 Surface, B-Rep, and Mesh structures and rendering.

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
pytest test/
```

### Run Demos
```bash
# Launch side-by-side comparison: Surface vs B-Rep vs Mesh
python examples/07_render_surface_brep_mesh_scene.py

# Launch 3D point, vector, and coordinate system scene
python examples/05_render_geometry_scene.py

# Launch hyperbolic paraboloid (saddle surface) renderer
python examples/02_render_surface_marked.py
```
