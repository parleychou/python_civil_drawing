"""Abstract parametric curve base class."""

import math
from abc import abstractmethod
from dataclasses import dataclass

import numpy as np
import pyvista as pv

from _base import GeometryData


@dataclass(kw_only=True)
class Curve(GeometryData):
    """Abstract parametric curve in 3D space.

    A curve maps a normalized parameter ``t ∈ [0, 1]`` to a 3D point.
    Subclasses implement :meth:`point_at` to define the mapping; the base
    class provides :meth:`sample_points`, :meth:`to_pyvista`, and
    :meth:`render` in terms of it.
    """

    @abstractmethod
    def point_at(self, t: float) -> "Point3D":
        """Return the point on the curve at parameter ``t`` (0 ≤ t ≤ 1)."""

    def sample_points(self, count: int) -> "list[Point3D]":
        """Sample ``count`` evenly-spaced points along the curve."""
        if count < 2:
            raise ValueError("Curve sampling requires at least two points")
        # Avoid circular import: concrete Curve subclasses are imported lazily
        # inside concrete point_at implementations; here we just call them.
        return [self.point_at(float(t)) for t in np.linspace(0.0, 1.0, count)]

    def to_pyvista(self) -> "pv.DataSet":
        """Convert the curve to a PyVista polyline via sampling."""
        pts = [p.to_tuple() for p in self.sample_points()]
        polyline = pv.PolyData(pts)
        polyline.lines = [len(pts), *range(len(pts))]
        return polyline

    def render(self, engine, color: str = "steelblue", show_edges: bool = True) -> None:
        """Render the curve as a polyline."""
        engine.render_curve([p.to_tuple() for p in self.sample_points()], color=color)
