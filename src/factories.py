"""Factory functions for teaching-example solids."""

from brep_data import BrepData
from mesh_data import MeshData
from point3d import Point3D


def create_cube_brep(width: float, depth: float, height: float) -> BrepData:
    """Manually build a cuboid B-Rep object."""
    vertices = (
        Point3D(0.0, 0.0, 0.0),
        Point3D(width, 0.0, 0.0),
        Point3D(width, depth, 0.0),
        Point3D(0.0, depth, 0.0),
        Point3D(0.0, 0.0, height),
        Point3D(width, 0.0, height),
        Point3D(width, depth, height),
        Point3D(0.0, depth, height),
    )
    edges = (
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7),
    )
    faces = (
        (3, 2, 1, 0),
        (4, 5, 6, 7),
        (0, 1, 5, 4),
        (1, 2, 6, 5),
        (2, 3, 7, 6),
        (3, 0, 4, 7),
    )
    return BrepData(vertices=vertices, edges=edges, faces=faces, name="BRep_Cube")


def create_pyramid_mesh(width: float, depth: float, height: float) -> MeshData:
    """Parametrically construct a pyramid Mesh object."""
    vertices = (
        Point3D(0.0, 0.0, 0.0),
        Point3D(width, 0.0, 0.0),
        Point3D(width, depth, 0.0),
        Point3D(0.0, depth, 0.0),
        Point3D(width / 2.0, depth / 2.0, height),
    )
    faces = (
        (3, 2, 1, 0),
        (0, 1, 4),
        (1, 2, 4),
        (2, 3, 4),
        (3, 0, 4),
    )
    return MeshData(vertices=vertices, faces=faces, name="Mesh_Pyramid")


# 教学别名：课件 Slide 中同时支持 create_box_brep 与 create_cube_brep
create_box_brep = create_cube_brep

