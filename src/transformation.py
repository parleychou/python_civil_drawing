"""TransformMatrix — 4x4 homogeneous affine transformation matrix."""

from collections.abc import Sequence
from dataclasses import dataclass, field
import math
import numpy as np

from point3d import Point3D
from vector3d import Vector3D


@dataclass
class TransformMatrix:
    """4x4 homogeneous affine transformation matrix for 3D engineering geometries.

    Follows column-vector convention: P' = M @ P, where P = [x, y, z, 1]^T.
    Composite transformation M = T @ R @ S applies Scale first, then Rotation, then Translation.
    """

    matrix: np.ndarray = field(default_factory=lambda: np.eye(4, dtype=np.float64))

    def __post_init__(self) -> None:
        self.matrix = np.asarray(self.matrix, dtype=np.float64)
        if self.matrix.shape != (4, 4):
            raise ValueError(f"TransformMatrix must have shape (4, 4), got {self.matrix.shape}")

    # =========================================================================
    # Factory constructors
    # =========================================================================

    @classmethod
    def identity(cls) -> "TransformMatrix":
        """Return a 4x4 identity matrix (no transformation)."""
        return cls(np.eye(4, dtype=np.float64))

    @classmethod
    def translation(cls, dx: float, dy: float, dz: float) -> "TransformMatrix":
        """Construct a translation matrix along vector (dx, dy, dz)."""
        m = np.eye(4, dtype=np.float64)
        m[0, 3] = float(dx)
        m[1, 3] = float(dy)
        m[2, 3] = float(dz)
        return cls(m)

    @classmethod
    def rotation_x(cls, angle_rad: float) -> "TransformMatrix":
        """Construct a rotation matrix around the X axis by angle_rad (radians)."""
        c = math.cos(angle_rad)
        s = math.sin(angle_rad)
        m = np.array(
            [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, c, -s, 0.0],
                [0.0, s, c, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ],
            dtype=np.float64,
        )
        return cls(m)

    @classmethod
    def rotation_y(cls, angle_rad: float) -> "TransformMatrix":
        """Construct a rotation matrix around the Y axis by angle_rad (radians)."""
        c = math.cos(angle_rad)
        s = math.sin(angle_rad)
        m = np.array(
            [
                [c, 0.0, s, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [-s, 0.0, c, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ],
            dtype=np.float64,
        )
        return cls(m)

    @classmethod
    def rotation_z(cls, angle_rad: float) -> "TransformMatrix":
        """Construct a rotation matrix around the Z axis by angle_rad (radians)."""
        c = math.cos(angle_rad)
        s = math.sin(angle_rad)
        m = np.array(
            [
                [c, -s, 0.0, 0.0],
                [s, c, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ],
            dtype=np.float64,
        )
        return cls(m)

    @classmethod
    def rotation_axis(cls, axis: Vector3D, angle_rad: float) -> "TransformMatrix":
        """Construct a rotation matrix around an arbitrary unit axis using Rodrigues' formula."""
        u = axis.normalized()
        ux, uy, uz = u.x, u.y, u.z
        c = math.cos(angle_rad)
        s = math.sin(angle_rad)
        c1 = 1.0 - c

        # 3x3 Rodrigues rotation matrix components
        r00 = c + ux * ux * c1
        r01 = ux * uy * c1 - uz * s
        r02 = ux * uz * c1 + uy * s

        r10 = uy * ux * c1 + uz * s
        r11 = c + uy * uy * c1
        r12 = uy * uz * c1 - ux * s

        r20 = uz * ux * c1 - uy * s
        r21 = uz * uy * c1 + ux * s
        r22 = c + uz * uz * c1

        m = np.array(
            [
                [r00, r01, r02, 0.0],
                [r10, r11, r12, 0.0],
                [r20, r21, r22, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ],
            dtype=np.float64,
        )
        return cls(m)

    @classmethod
    def scaling(cls, sx: float, sy: float, sz: float) -> "TransformMatrix":
        """Construct a scaling matrix with scale factors (sx, sy, sz)."""
        m = np.diag([float(sx), float(sy), float(sz), 1.0]).astype(np.float64)
        return cls(m)

    @classmethod
    def from_coordinate_systems(
        cls,
        from_cs: "CoordinateSystem3D",
        to_cs: "CoordinateSystem3D | None" = None,
    ) -> "TransformMatrix":
        """Construct a change-of-basis matrix between coordinate systems.

        If `to_cs` is None, it defaults to the standard global World coordinate system.
        """
        # Local to World for from_cs
        u = from_cs.x_axis.normalized()
        v = from_cs.y_axis.normalized()
        w = from_cs.z_axis.normalized()
        o = from_cs.origin

        m_from_to_world = np.array(
            [
                [u.x, v.x, w.x, o.x],
                [u.y, v.y, w.y, o.y],
                [u.z, v.z, w.z, o.z],
                [0.0, 0.0, 0.0, 1.0],
            ],
            dtype=np.float64,
        )

        if to_cs is None:
            return cls(m_from_to_world)

        # Check if to_cs is global world origin and standard axes
        is_standard_world = (
            abs(to_cs.origin.x) < 1e-12
            and abs(to_cs.origin.y) < 1e-12
            and abs(to_cs.origin.z) < 1e-12
            and abs(to_cs.x_axis.x - 1.0) < 1e-12
            and abs(to_cs.y_axis.y - 1.0) < 1e-12
            and abs(to_cs.z_axis.z - 1.0) < 1e-12
        )
        if is_standard_world:
            return cls(m_from_to_world)

        tu = to_cs.x_axis.normalized()
        tv = to_cs.y_axis.normalized()
        tw = to_cs.z_axis.normalized()
        to_pt = to_cs.origin

        m_to_to_world = np.array(
            [
                [tu.x, tv.x, tw.x, to_pt.x],
                [tu.y, tv.y, tw.y, to_pt.y],
                [tu.z, tv.z, tw.z, to_pt.z],
                [0.0, 0.0, 0.0, 1.0],
            ],
            dtype=np.float64,
        )

        # M_{from -> to} = M_{to -> world}^{-1} @ M_{from -> world}
        m_from_to_target = np.linalg.inv(m_to_to_world) @ m_from_to_world
        return cls(m_from_to_target)

    # =========================================================================
    # Matrix operations
    # =========================================================================

    def __matmul__(self, other: "TransformMatrix") -> "TransformMatrix":
        """Chain transformations using the @ operator: M = T @ R @ S."""
        if not isinstance(other, TransformMatrix):
            return NotImplemented
        return TransformMatrix(self.matrix @ other.matrix)

    def inverse(self) -> "TransformMatrix":
        """Compute the inverse transformation matrix."""
        inv_m = np.linalg.inv(self.matrix)
        return TransformMatrix(inv_m)

    # =========================================================================
    # Geometry application
    # =========================================================================

    def apply_to_point(self, pt: Point3D) -> Point3D:
        """Apply transformation to a Point3D (w = 1)."""
        vec4 = np.array([pt.x, pt.y, pt.z, 1.0], dtype=np.float64)
        res = self.matrix @ vec4
        # Perspective divide if necessary (for general projective matrices, typically res[3] == 1.0 for affine)
        w = res[3] if abs(res[3] - 1.0) > 1e-12 and abs(res[3]) > 1e-12 else 1.0
        return Point3D(
            float(res[0] / w),
            float(res[1] / w),
            float(res[2] / w),
            name=pt.name,
        )

    def apply_to_vector(self, vec: Vector3D) -> Vector3D:
        """Apply transformation to a Vector3D (w = 0, unaffected by translation)."""
        vec4 = np.array([vec.x, vec.y, vec.z, 0.0], dtype=np.float64)
        res = self.matrix @ vec4
        return Vector3D(float(res[0]), float(res[1]), float(res[2]), name=vec.name)

    def apply_to_points(self, pts: Sequence[Point3D]) -> tuple[Point3D, ...]:
        """Vectorized batch application of transformation to a sequence of Point3D."""
        if not pts:
            return ()
        arr = np.array([[p.x, p.y, p.z, 1.0] for p in pts], dtype=np.float64).T  # shape (4, N)
        res = self.matrix @ arr  # shape (4, N)
        w = res[3, :]
        mask = (np.abs(w - 1.0) > 1e-12) & (np.abs(w) > 1e-12)
        if np.any(mask):
            res[:3, mask] /= w[mask]
        return tuple(
            Point3D(float(res[0, i]), float(res[1, i]), float(res[2, i]), name=pts[i].name)
            for i in range(len(pts))
        )

    def to_numpy(self) -> np.ndarray:
        """Return a copy of the underlying 4x4 numpy matrix."""
        return self.matrix.copy()

    def __repr__(self) -> str:
        lines = ["TransformMatrix(["]
        for row in self.matrix:
            row_str = ", ".join(f"{v:10.4f}" for v in row)
            lines.append(f"  [{row_str}],")
        lines.append("])")
        return "\n".join(lines)
