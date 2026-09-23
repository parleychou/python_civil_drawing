"""HyperbolicParaboloid — parametric saddle surface."""

from dataclasses import dataclass

from parametric_surface import ParametricSurfaceData
from point3d import Point3D


@dataclass
class HyperbolicParaboloid(ParametricSurfaceData):
    """双曲抛物面 (马鞍面) 参数化曲面。

    土木工程中经典的大跨度空间薄壳与索网屋盖几何形体。
    解析方程：
        x(u, v) = u
        y(u, v) = v
        z(u, v) = c * ((u / a)^2 - (v / b)^2)

    参数说明：
        a: X 轴向主曲率基准 (mm)，默认 1500.0
        b: Y 轴向主曲率基准 (mm)，默认 1500.0
        c: 矢高 (高差缩放系数，mm)，默认 600.0
        u_range: u 参数域范围 (mm)，默认 (-1500.0, 1500.0)
        v_range: v 参数域范围 (mm)，默认 (-1500.0, 1500.0)
        u_resolution: u 方向采样点数，默认 30
        v_resolution: v 方向采样点数，默认 30
    """

    a: float = 1500.0
    b: float = 1500.0
    c: float = 600.0
    u_range: tuple[float, float] = (-1500.0, 1500.0)
    v_range: tuple[float, float] = (-1500.0, 1500.0)
    u_resolution: int = 30
    v_resolution: int = 30
    name: str = "Hyperbolic_Paraboloid"

    def evaluate(self, u: float, v: float) -> "Point3D":
        """根据参数 (u, v) 评估双曲抛物面上的三维空间坐标。"""
        x = float(u)
        y = float(v)
        z = float(self.c * ((u / self.a) ** 2 - (v / self.b) ** 2))
        return Point3D(x, y, z)
