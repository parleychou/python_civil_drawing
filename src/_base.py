"""Abstract base class and utilities for all geometry data."""

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, fields

import numpy as np
import pyvista as pv

PointTuple = tuple[float, float, float]


@dataclass(kw_only=True)
class GeometryData(ABC):
    """Base type for all geometry data that can interact with RenderEngine."""

    name: str = ""

    @abstractmethod
    def to_pyvista(self) -> "pv.DataSet":
        """Convert this geometry object into a PyVista dataset."""

    def render(self, engine, color: str = "steelblue", show_edges: bool = True) -> None:
        """Render this geometry object with a RenderEngine-like object."""
        engine.add_mesh(self.to_pyvista(), color=color, show_edges=show_edges)

    def data_structure(self) -> dict[str, object]:
        """Return a small teaching summary of this object's data structure."""
        parameters = {
            item.name: _serialize_parameter(getattr(self, item.name))
            for item in fields(self)
            if item.name != "name"
        }
        return {
            "class": type(self).__name__,
            "base_class": "GeometryData",
            "name": self.name,
            "parameters": parameters,
        }

    # =========================================================================
    # 内置几何变换方法 (Built-in Affine Transformation Methods)
    # =========================================================================
    def transform(self, matrix) -> "GeometryData":
        """应用 4x4 仿射变换矩阵，返回变换后的新几何对象。由子类具体实现。"""
        raise NotImplementedError(f"{type(self).__name__} does not implement transform()")

    def translated(self, dx: float = 0.0, dy: float = 0.0, dz: float = 0.0) -> "GeometryData":
        """平移几何体，返回平移后的新几何对象。"""
        from transformation import TransformMatrix
        return self.transform(TransformMatrix.translation(dx, dy, dz))

    def rotated_x(self, angle_rad: float) -> "GeometryData":
        """绕世界 X 轴旋转指定弧度，返回旋转后的新几何对象。"""
        from transformation import TransformMatrix
        return self.transform(TransformMatrix.rotation_x(angle_rad))

    def rotated_y(self, angle_rad: float) -> "GeometryData":
        """绕世界 Y 轴旋转指定弧度，返回旋转后的新几何对象。"""
        from transformation import TransformMatrix
        return self.transform(TransformMatrix.rotation_y(angle_rad))

    def rotated_z(self, angle_rad: float) -> "GeometryData":
        """绕世界 Z 轴旋转指定弧度，返回旋转后的新几何对象。"""
        from transformation import TransformMatrix
        return self.transform(TransformMatrix.rotation_z(angle_rad))

    def rotated(self, axis, angle_rad: float) -> "GeometryData":
        """绕空间任意轴向量旋转指定弧度，返回旋转后的新几何对象。"""
        from transformation import TransformMatrix
        return self.transform(TransformMatrix.rotation_axis(axis, angle_rad))

    def scaled(self, sx: float, sy: float | None = None, sz: float | None = None) -> "GeometryData":
        """沿 X/Y/Z 方向进行缩放。若 sy 或 sz 为 None，则采用 sx 等比例各向同性缩放。"""
        if sy is None:
            sy = sx
        if sz is None:
            sz = sx
        from transformation import TransformMatrix
        return self.transform(TransformMatrix.scaling(sx, sy, sz))

    # =========================================================================
    # 内置空间投影方法 (Built-in Spatial Projection Methods)
    # =========================================================================
    def project_to_plane(self, plane) -> "GeometryData":
        """将几何体正交投影至指定平面 Plane3D，返回降维/压平后的新几何对象。由子类具体实现。"""
        raise NotImplementedError(f"{type(self).__name__} does not implement project_to_plane()")

    def generate_three_views(self, offset: float = 3000.0) -> dict[str, "GeometryData"]:
        """一键生成工程制图标准正交三视图 (俯视图/主视图/侧视图)。

        Args:
            offset: 投影底板距离原点的偏移距离 (默认 3000mm)

        Returns:
            dict[str, GeometryData]: 包含 'top', 'front', 'side' 三个视角的投影几何体。
        """
        from point3d import Point3D
        from vector3d import Vector3D
        from plane3d import Plane3D

        top_plane = Plane3D(center=Point3D(0.0, 0.0, -offset), normal=Vector3D(0.0, 0.0, 1.0))
        front_plane = Plane3D(center=Point3D(0.0, -offset, 0.0), normal=Vector3D(0.0, 1.0, 0.0))
        side_plane = Plane3D(center=Point3D(-offset, 0.0, 0.0), normal=Vector3D(1.0, 0.0, 0.0))

        return {
            "top": self.project_to_plane(top_plane),
            "front": self.project_to_plane(front_plane),
            "side": self.project_to_plane(side_plane),
        }


def _serialize_parameter(value: object) -> object:
    """Recursively convert geometry types to plain Python for display."""
    try:
        from .point3d import Point3D
        from .vector3d import Vector3D
    except (ImportError, ValueError):
        from point3d import Point3D
        from vector3d import Vector3D

    if isinstance(value, (Point3D, Vector3D)):
        return value.to_tuple()
    if isinstance(value, float | int):
        return float(value)
    if isinstance(value, tuple):
        return tuple(_serialize_parameter(item) for item in value)
    if isinstance(value, list):
        return [_serialize_parameter(item) for item in value]
    return value
