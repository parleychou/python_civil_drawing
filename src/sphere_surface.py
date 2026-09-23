"""SphereSurface — parametric sphere via longitude/latitude mapping."""

from dataclasses import dataclass

import numpy as np

from parametric_surface import ParametricSurfaceData
from point3d import Point3D


@dataclass
class SphereSurface(ParametricSurfaceData):
    """Parametric sphere surface.

    Analytic formula:
        x = R * cos(u) * cos(v)
        y = R * sin(u) * cos(v)
        z = R * sin(v)

    u = longitude  [0, 2π]
    v = latitude   [-π/2, π/2]
    """

    radius: float = 1000.0

    def evaluate(self, u: float, v: float) -> "Point3D":
        """Evaluate a 3D point on the sphere from (longitude, latitude)."""
        x = self.radius * np.cos(u) * np.cos(v)
        y = self.radius * np.sin(u) * np.cos(v)
        z = self.radius * np.sin(v)
        return Point3D(float(x), float(y), float(z))
