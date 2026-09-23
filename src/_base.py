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


def _serialize_parameter(value: object) -> object:
    """Recursively convert geometry types to plain Python for display."""
    # Avoid circular import: GeometryData.data_structure() calls this at
    # runtime, by which time all modules are already loaded.
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
