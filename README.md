# python_civil_drawing

> Python for Civil Engineers: Computational Geometry, 3D Modeling & CAD Engineering Drawing

[English](README.md) | [中文](README_ZH.md)

This repository contains comprehensive course slides and production-ready source code tailored for civil engineers, structural designers, and AEC professionals looking to master 3D computational geometry, parametric surface generation, boundary representations (B-Rep), and 3D rendering with PyVista and Three.js.

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

### 2. Interactive Slides (`slides/`)
Modern HTML5 web slides featuring live embedded Three.js 3D viewers:
- `01.01-overview-slides.html`: Course Overview & Python in AEC/BIM
- `02.01-python-environment-slides.html`: Python Development Environment Setup
- `03.01-common-libraries-slides.html`: Essential Engineering Libraries
- `04.01-pyvista-render-engine-slides.html`: Building the 3D PyVista Render Engine
- `05.01-basic-geometry-data-slides.html`: Object-Oriented Geometric Data
- `05.02-oop-parametric-geometry-slides.html`: Parametric Geometric Primitives
- `06.01-body-representation-slides.html`: Solid & Surface Representations (Surface / B-Rep / Mesh)

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
