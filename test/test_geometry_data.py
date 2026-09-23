"""Tests for basic geometry data objects."""

import math
import sys
import unittest
from pathlib import Path

# 将 src 目录加入 sys.path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from geometry_primitives import (
    Arc3D,
    Circle3D,
    CoordinateSystem3D,
    GeometryData,
    Line3D,
    Plane3D,
    Point3D,
    Vector3D,
)


class GeometryDataTest(unittest.TestCase):
    def test_all_geometry_objects_share_base_type(self) -> None:
        objects = [
            Point3D(1, 2, 3),
            Vector3D(1, 0, 0),
            CoordinateSystem3D(),
            Line3D(Point3D(0, 0, 0), Point3D(1, 0, 0)),
            Plane3D(Point3D(0, 0, 0), Vector3D(0, 0, 1), size=1),
            Circle3D(Point3D(0, 0, 0), radius=1),
            Arc3D(Point3D(0, 0, 0), radius=1, start_angle=0, end_angle=math.pi / 2),
        ]

        for item in objects:
            self.assertIsInstance(item, GeometryData)
            self.assertTrue(callable(item.to_pyvista))

    def test_point_vector_and_line_calculations(self) -> None:
        start = Point3D(0, 0, 0)
        end = Point3D(3, 4, 0)
        vector = end - start
        line = Line3D(start, end)

        self.assertEqual(vector, Vector3D(3, 4, 0))
        self.assertAlmostEqual(vector.length(), 5.0)
        self.assertAlmostEqual(line.length(), 5.0)

        # Test Vector3D addition and subtraction operator overloading
        v1 = Vector3D(1, 2, 3)
        v2 = Vector3D(4, 5, 6)
        self.assertEqual(v1 + v2, Vector3D(5, 7, 9))
        self.assertEqual(v2 - v1, Vector3D(3, 3, 3))

    def test_arc_sampling_includes_start_and_end_points(self) -> None:
        arc = Arc3D(Point3D(0, 0, 0), radius=2, start_angle=0, end_angle=math.pi / 2)
        points = arc.sample_points(count=5)

        self.assertEqual(points[0], Point3D(2, 0, 0))
        self.assertAlmostEqual(points[-1].x, 0.0, places=9)
        self.assertAlmostEqual(points[-1].y, 2.0, places=9)

    def test_geometry_objects_explain_their_data_structure(self) -> None:
        point = Point3D(1, 2, 3, name="P1")
        line = Line3D(Point3D(0, 0, 0), Point3D(1, 0, 0), name="L1")
        plane = Plane3D(Point3D(0, 0, 0), Vector3D(0, 0, 1), size=2, name="Work plane")

        self.assertEqual(point.data_structure()["class"], "Point3D")
        self.assertEqual(point.data_structure()["base_class"], "GeometryData")
        self.assertEqual(point.data_structure()["parameters"]["x"], 1.0)
        self.assertEqual(line.data_structure()["parameters"]["start"], (0.0, 0.0, 0.0))
        self.assertEqual(line.data_structure()["parameters"]["end"], (1.0, 0.0, 0.0))
        self.assertEqual(plane.data_structure()["parameters"]["normal"], (0.0, 0.0, 1.0))

    def test_vector_dot_and_cross_product(self) -> None:
        v1 = Vector3D(1, 2, 3)
        v2 = Vector3D(4, 5, 6)
        
        self.assertEqual(v1.dot(v2), 1*4 + 2*5 + 3*6)
        self.assertEqual(v1.cross(v2), Vector3D(2*6 - 3*5, 3*4 - 1*6, 1*5 - 2*4))
        
        # Test orthogonal vectors cross product and dot product
        vx = Vector3D(1, 0, 0)
        vy = Vector3D(0, 1, 0)
        self.assertEqual(vx.dot(vy), 0.0)
        self.assertEqual(vx.cross(vy), Vector3D(0, 0, 1))

    def test_coordinate_system_from_origin_and_normal(self) -> None:
        origin = Point3D(1, 2, 3)
        normal = Vector3D(0, 0, 2)
        cs = CoordinateSystem3D.from_origin_and_normal(origin, normal)
        
        self.assertEqual(cs.origin, origin)
        self.assertEqual(cs.z_axis, Vector3D(0, 0, 1))
        # Verify orthonormal basis
        self.assertAlmostEqual(cs.x_axis.length(), 1.0)
        self.assertAlmostEqual(cs.y_axis.length(), 1.0)
        self.assertAlmostEqual(cs.x_axis.dot(cs.y_axis), 0.0)
        self.assertAlmostEqual(cs.x_axis.dot(cs.z_axis), 0.0)
        self.assertAlmostEqual(cs.y_axis.dot(cs.z_axis), 0.0)
        self.assertEqual(cs.x_axis.cross(cs.y_axis), cs.z_axis)

    def test_coordinate_system_from_origin_and_vectors(self) -> None:
        origin = Point3D(1, 2, 3)
        x_dir = Vector3D(2, 0, 0)
        xy_dir = Vector3D(1, 1, 0)
        cs = CoordinateSystem3D.from_origin_and_vectors(origin, x_dir, xy_dir)
        
        self.assertEqual(cs.origin, origin)
        self.assertEqual(cs.x_axis, Vector3D(1, 0, 0))
        self.assertEqual(cs.y_axis, Vector3D(0, 1, 0))
        self.assertEqual(cs.z_axis, Vector3D(0, 0, 1))
        
        # Test collinear error
        with self.assertRaises(ValueError):
            CoordinateSystem3D.from_origin_and_vectors(origin, Vector3D(1, 0, 0), Vector3D(2, 0, 0))

    def test_oriented_circle_and_arc_calculations(self) -> None:
        # Create a circle on a plane with normal (1, 0, 0) (X-plane)
        plane = Plane3D(center=Point3D(1, 2, 3), normal=Vector3D(1, 0, 0))
        circle = Circle3D(plane=plane, radius=5)
        
        # Verify the center was synchronized
        self.assertEqual(circle.center, Point3D(1, 2, 3))
        
        # Sample points on the X-plane circle
        # For normal (1,0,0), our local_axes calculates local X as (0,1,0) and Y as (0,0,1)
        # point_at(0) should be at center + radius * local_x = (1, 2, 3) + 5*(0,1,0) = (1, 7, 3)
        p0 = circle.point_at(0)
        self.assertAlmostEqual(p0.x, 1.0)
        self.assertAlmostEqual(p0.y, 7.0)
        self.assertAlmostEqual(p0.z, 3.0)
        
        # point_at(0.25) should be at center + radius * local_y = (1, 2, 3) + 5*(0,0,1) = (1, 2, 8)
        p25 = circle.point_at(0.25)
        self.assertAlmostEqual(p25.x, 1.0)
        self.assertAlmostEqual(p25.y, 2.0)
        self.assertAlmostEqual(p25.z, 8.0)

    def test_native_pyvista_conversions(self) -> None:
        circle = Circle3D(Point3D(0, 0, 0), radius=5)
        arc = Arc3D(Point3D(0, 0, 0), radius=5, start_angle=0, end_angle=math.pi / 2)
        line = Line3D(Point3D(0, 0, 0), Point3D(10, 10, 10))
        
        # Test PyVista native conversions as reference comparison
        mesh_circle = circle.to_pyvista_native()
        mesh_arc = arc.to_pyvista_native()
        mesh_line = line.to_pyvista_native()
        
        self.assertIsNotNone(mesh_circle)
        self.assertIsNotNone(mesh_arc)
        self.assertIsNotNone(mesh_line)
        # Verify they are PyVista datasets
        import pyvista as pv
        self.assertIsInstance(mesh_circle, pv.DataSet)
        self.assertIsInstance(mesh_arc, pv.DataSet)
        self.assertIsInstance(mesh_line, pv.DataSet)


if __name__ == "__main__":
    unittest.main()

