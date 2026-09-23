"""ParametricSurfaceData — abstract base for parametric surfaces."""

import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pyvista as pv

from _common import find_chapter_scripts

_ch5 = find_chapter_scripts("05")
if _ch5.exists():
    sys.path.insert(0, str(_ch5))

from _base import GeometryData
from point3d import Point3D


@dataclass
class ParametricSurfaceData(GeometryData, ABC):
    """Abstract parametric surface data structure.

    Provides u, v parameter sampling ranges, resolution, and sampling logic.
    """

    u_range: tuple[float, float] = (0.0, 1.0)
    v_range: tuple[float, float] = (0.0, 1.0)
    u_resolution: int = 20
    v_resolution: int = 20

    @abstractmethod
    def evaluate(self, u: float, v: float) -> "Point3D":
        """Parametric evaluation: (u, v) → Point3D.

        Must be implemented by concrete surface subclasses.
        """

    def to_pyvista(self) -> "pv.StructuredGrid":
        """Uniformly sample the (u, v) domain → PyVista StructuredGrid."""
        u_vals = np.linspace(self.u_range[0], self.u_range[1], self.u_resolution)
        v_vals = np.linspace(self.v_range[0], self.v_range[1], self.v_resolution)

        points = []
        for v in v_vals:
            for u in u_vals:
                pt = self.evaluate(u, v)
                points.append(pt.to_tuple() if hasattr(pt, "to_tuple") else pt)

        grid = pv.StructuredGrid()
        grid.points = np.array(points)
        grid.dimensions = (self.u_resolution, self.v_resolution, 1)
        return grid
