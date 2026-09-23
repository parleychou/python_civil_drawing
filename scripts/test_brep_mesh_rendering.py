"""验证 B-Rep、Mesh 和 Surface 数据结构及其继承关系的单元测试。"""

import sys
import unittest
import math
from pathlib import Path

# 将当前 scripts 目录加入 sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from brep_primitives import (
    BrepData,
    MeshData,
    ParametricSurfaceData,
    SphereSurface,
    HyperbolicParaboloid,
    create_cube_brep,
    create_box_brep,
    create_pyramid_mesh,
    Point3D,
    GeometryData,
)


class TestBrepMeshSurfaceRendering(unittest.TestCase):
    def test_inheritance_and_base_type(self) -> None:
        """测试所有自定义几何表达都继承自统一基类 GeometryData。"""
        cube = create_cube_brep(1000.0, 1000.0, 1000.0)
        pyramid = create_pyramid_mesh(1000.0, 1000.0, 1000.0)
        sphere = SphereSurface(radius=1000.0, u_range=(0.0, 2.0*math.pi), v_range=(-math.pi/2.0, math.pi/2.0), u_resolution=10, v_resolution=10)
        saddle = HyperbolicParaboloid(a=1500.0, b=1500.0, c=600.0)

        self.assertIsInstance(cube, GeometryData)
        self.assertIsInstance(pyramid, GeometryData)
        self.assertIsInstance(sphere, GeometryData)
        self.assertIsInstance(saddle, GeometryData)
        self.assertIsInstance(saddle, ParametricSurfaceData)


    def test_brep_cube_structure(self) -> None:
        """测试 B-Rep 立方体是否包含正确的顶点数、棱边数和面数拓扑。"""
        cube = create_cube_brep(2000.0, 1500.0, 3000.0)
        
        # 8个顶点，12条边，6个面
        self.assertEqual(len(cube.vertices), 8)
        self.assertEqual(len(cube.edges), 12)
        self.assertEqual(len(cube.faces), 6)

        # 检查特征顶角坐标
        self.assertAlmostEqual(cube.vertices[6].x, 2000.0)
        self.assertAlmostEqual(cube.vertices[6].y, 1500.0)
        self.assertAlmostEqual(cube.vertices[6].z, 3000.0)

        # 检查边线拓扑
        self.assertIn((0, 1), cube.edges)
        self.assertIn((6, 7), cube.edges)

        # 检查 PyVista 转换
        poly = cube.to_pyvista()
        self.assertEqual(poly.n_points, 8)
        self.assertEqual(poly.n_cells, 6)

    def test_mesh_pyramid_structure(self) -> None:
        """测试 Mesh 四棱锥网格顶点的索引结构是否正确。"""
        pyramid = create_pyramid_mesh(2000.0, 1500.0, 3000.0)
        
        # 5个顶点，5个面片 (1底面 + 4侧面)
        self.assertEqual(len(pyramid.vertices), 5)
        self.assertEqual(len(pyramid.faces), 5)

        # 验证尖端最高点
        self.assertAlmostEqual(pyramid.vertices[4].x, 1000.0)
        self.assertAlmostEqual(pyramid.vertices[4].y, 750.0)
        self.assertAlmostEqual(pyramid.vertices[4].z, 3000.0)

        # 检查 PyVista 转换
        poly = pyramid.to_pyvista()
        self.assertEqual(poly.n_points, 5)
        self.assertEqual(poly.n_cells, 5)

    def test_parametric_surface_evaluate(self) -> None:
        """测试参数化球面的解析计算结果是否符合数学公式。"""
        # x = R * cos(u) * cos(v), y = R * sin(u) * cos(v), z = R * sin(v)
        # 若 R=1000.0, u=0, v=0 -> x=1000.0, y=0.0, z=0.0
        sphere = SphereSurface(
            radius=1000.0,
            u_range=(0.0, 2.0 * math.pi), v_range=(-math.pi / 2.0, math.pi / 2.0),
            u_resolution=10, v_resolution=10
        )
        
        pt = sphere.evaluate(0.0, 0.0)
        self.assertAlmostEqual(pt.x, 1000.0)
        self.assertAlmostEqual(pt.y, 0.0)
        self.assertAlmostEqual(pt.z, 0.0)

        # 测试 StructuredGrid 采样点数
        grid = sphere.to_pyvista()
        self.assertEqual(grid.n_points, 100)  # 10x10 = 100
        self.assertEqual(grid.dimensions, (10, 10, 1))

    def test_hyperbolic_paraboloid_evaluate(self) -> None:
        """测试课件主讲双曲抛物面 (马鞍面) 的解析计算与网格采样。"""
        # z = c * (u^2/a^2 - v^2/b^2)
        saddle = HyperbolicParaboloid(
            a=1500.0,
            b=1500.0,
            c=600.0,
            u_range=(-1500.0, 1500.0),
            v_range=(-1500.0, 1500.0),
            u_resolution=12,
            v_resolution=12,
        )

        # 1. 中心鞍点 (0, 0) -> z = 0
        p_center = saddle.evaluate(0.0, 0.0)
        self.assertAlmostEqual(p_center.x, 0.0)
        self.assertAlmostEqual(p_center.y, 0.0)
        self.assertAlmostEqual(p_center.z, 0.0)

        # 2. 拱顶最大值点 (1500, 0) -> z = +600.0
        p_arch = saddle.evaluate(1500.0, 0.0)
        self.assertAlmostEqual(p_arch.x, 1500.0)
        self.assertAlmostEqual(p_arch.y, 0.0)
        self.assertAlmostEqual(p_arch.z, 600.0)

        # 3. 悬链下凹点 (0, 1500) -> z = -600.0
        p_sag = saddle.evaluate(0.0, 1500.0)
        self.assertAlmostEqual(p_sag.x, 0.0)
        self.assertAlmostEqual(p_sag.y, 1500.0)
        self.assertAlmostEqual(p_sag.z, -600.0)

        # 4. 角点 (1500, 1500) -> z = 0
        p_corner = saddle.evaluate(1500.0, 1500.0)
        self.assertAlmostEqual(p_corner.x, 1500.0)
        self.assertAlmostEqual(p_corner.y, 1500.0)
        self.assertAlmostEqual(p_corner.z, 0.0)

        # 5. 测试 StructuredGrid 网格采样
        grid = saddle.to_pyvista()
        self.assertEqual(grid.n_points, 144)  # 12x12 = 144
        self.assertEqual(grid.dimensions, (12, 12, 1))

    def test_create_box_brep_alias(self) -> None:
        """测试 create_box_brep 别名与 create_cube_brep 具有相同的功能。"""
        box = create_box_brep(1000.0, 800.0, 600.0)
        self.assertEqual(len(box.vertices), 8)
        self.assertEqual(len(box.edges), 12)
        self.assertEqual(len(box.faces), 6)
        self.assertEqual(box.to_pyvista().n_points, 8)
        self.assertEqual(box.to_pyvista().n_cells, 6)


if __name__ == "__main__":
    unittest.main()

