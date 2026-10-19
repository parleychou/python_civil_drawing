"""Factory functions for teaching-example solids and civil engineering components."""

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


def create_i_beam_brep(
    length: float = 2000.0,
    width: float = 300.0,
    height: float = 500.0,
    flange_thickness: float = 20.0,
    web_thickness: float = 15.0,
) -> BrepData:
    """Construct an engineering standard I-beam (工字钢梁) B-Rep solid."""
    w2 = width / 2.0
    h2 = height / 2.0
    tw2 = web_thickness / 2.0
    tf = flange_thickness

    # 12 2D cross-section contour vertices in XY plane
    sec2d = [
        (-w2, -h2),
        (w2, -h2),
        (w2, -h2 + tf),
        (tw2, -h2 + tf),
        (tw2, h2 - tf),
        (w2, h2 - tf),
        (w2, h2),
        (-w2, h2),
        (-w2, h2 - tf),
        (-tw2, h2 - tf),
        (-tw2, -h2 + tf),
        (-w2, -h2 + tf),
    ]

    # Extrude along Z: bottom cap at z=0, top cap at z=length
    vertices = []
    for x, y in sec2d:
        vertices.append(Point3D(x, y, 0.0))
    for x, y in sec2d:
        vertices.append(Point3D(x, y, length))

    # Edges
    edges = []
    # Bottom perimeter
    for i in range(12):
        edges.append((i, (i + 1) % 12))
    # Top perimeter
    for i in range(12):
        edges.append((12 + i, 12 + (i + 1) % 12))
    # Longitudinal edges
    for i in range(12):
        edges.append((i, 12 + i))

    # Faces: 12 side faces + 2 end caps
    faces = []
    for i in range(12):
        next_i = (i + 1) % 12
        faces.append((i, next_i, 12 + next_i, 12 + i))

    # Bottom end cap (normal pointing -Z)
    faces.append(tuple(range(11, -1, -1)))
    # Top end cap (normal pointing +Z)
    faces.append(tuple(range(12, 24)))

    return BrepData(
        vertices=tuple(vertices),
        edges=tuple(edges),
        faces=tuple(faces),
        name="BRep_IBeam",
    )


def create_bridge_pier_brep(
    height: float = 4000.0,
    top_width: float = 1200.0,
    top_depth: float = 800.0,
    bottom_width: float = 1800.0,
    bottom_depth: float = 1200.0,
) -> BrepData:
    """Construct a tapered bridge pier (变截面桥墩) B-Rep solid."""
    bw2 = bottom_width / 2.0
    bd2 = bottom_depth / 2.0
    tw2 = top_width / 2.0
    td2 = top_depth / 2.0

    vertices = (
        Point3D(-bw2, -bd2, 0.0),
        Point3D(bw2, -bd2, 0.0),
        Point3D(bw2, bd2, 0.0),
        Point3D(-bw2, bd2, 0.0),
        Point3D(-tw2, -td2, height),
        Point3D(tw2, -td2, height),
        Point3D(tw2, td2, height),
        Point3D(-tw2, td2, height),
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
    return BrepData(
        vertices=vertices,
        edges=edges,
        faces=faces,
        name="BRep_BridgePier",
    )


def create_box_mesh(origin: Point3D, width: float, depth: float, height: float) -> MeshData:
    """Construct a triangulated box MeshData solid."""
    ox, oy, oz = origin.x, origin.y, origin.z
    vertices = (
        Point3D(ox, oy, oz),
        Point3D(ox + width, oy, oz),
        Point3D(ox + width, oy + depth, oz),
        Point3D(ox, oy + depth, oz),
        Point3D(ox, oy, oz + height),
        Point3D(ox + width, oy, oz + height),
        Point3D(ox + width, oy + depth, oz + height),
        Point3D(ox, oy + depth, oz + height),
    )
    # 6 quad faces, triangulated into 12 triangles
    faces = (
        # Bottom (Z = oz)
        (0, 2, 1), (0, 3, 2),
        # Top (Z = oz + height)
        (4, 5, 6), (4, 6, 7),
        # Front (Y = oy)
        (0, 1, 5), (0, 5, 4),
        # Right (X = ox + width)
        (1, 2, 6), (1, 6, 5),
        # Back (Y = oy + depth)
        (2, 3, 7), (2, 7, 6),
        # Left (X = ox)
        (3, 0, 4), (3, 4, 7),
    )
    return MeshData(vertices=vertices, faces=faces, name="Mesh_Box")
