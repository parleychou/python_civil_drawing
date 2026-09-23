"""Reusable PyVista render engine for course examples.

This module wraps the common PyVista viewport setup in a small class so later
lessons can focus on geometry objects instead of repeating rendering setup.
"""

# from __future__ import annotations

from pathlib import Path
from typing import Sequence

import pyvista as pv

PointLike = tuple[float, float, float]


class RenderEngine:
    """Course render engine based on ``pyvista.Plotter``.

    The engine keeps one configured viewport and exposes a small set of methods
    for adding geometry, showing the interactive window, and saving screenshots.
    """

    def __init__(
        self,
        window_size: tuple[int, int] = (1200, 800),
        background: str = "white",
        show_grid: bool = True,
        off_screen: bool = False,
    ) -> None:
        self.plotter = pv.Plotter(window_size=window_size, off_screen=off_screen)
        self.plotter.set_background(background)
        self.plotter.add_axes()
        if show_grid:
            self.plotter.show_grid(
                color="lightgray",
                grid="back",
                location="outer",
            )
        self.plotter.camera_position = "iso"
        self.configure_mouse()

    def configure_mouse(self) -> None:
        """Use trackball camera mouse controls for rotate, pan, and zoom."""
        self.plotter.enable_trackball_style()

    def add_mesh(
        self,
        mesh: pv.DataSet,
        color: str = "tan",
        show_edges: bool = True,
        opacity: float = 1.0,
    ) -> None:
        """Add a mesh-like PyVista dataset to the scene."""
        self.plotter.add_mesh(
            mesh,
            color=color,
            show_edges=show_edges,
            opacity=opacity,
        )

    def render_point(
        self,
        point: PointLike,
        color: str = "coral",
        point_size: float = 14.0,
        label: str | None = None,
    ) -> None:
        """Render one 3D point in the viewport."""
        cloud = pv.PolyData([point])
        self.plotter.add_mesh(
            cloud,
            color=color,
            point_size=point_size,
            render_points_as_spheres=True,
        )
        if label:
            self.plotter.add_point_labels([point], [label], point_size=point_size)

    def render_points(
        self,
        points: Sequence[PointLike],
        color: str = "coral",
        point_size: float = 12.0,
    ) -> None:
        """Render multiple 3D points in the viewport."""
        cloud = pv.PolyData(list(points))
        self.plotter.add_mesh(
            cloud,
            color=color,
            point_size=point_size,
            render_points_as_spheres=True,
        )

    def render_curve(
        self,
        points: Sequence[PointLike],
        color: str = "steelblue",
        line_width: float = 5.0,
    ) -> None:
        """Render a polyline curve through a sequence of 3D points."""
        if len(points) < 2:
            raise ValueError("render_curve() requires at least two points")

        polyline = pv.PolyData(list(points))
        # VTK polyline format: [number_of_points, point_0, point_1, ...].
        polyline.lines = [len(points), *range(len(points))]
        self.plotter.add_mesh(polyline, color=color, line_width=line_width)

    def reset_camera(self) -> None:
        """Reset the camera to frame all visible geometry."""
        self.plotter.reset_camera()

    def show(self) -> None:
        """Open the interactive viewport."""
        self.reset_camera()
        self.plotter.show()

    def save_screenshot(self, filename: str | Path) -> None:
        """Save the current viewport as an image file."""
        self.reset_camera()
        self.plotter.screenshot(str(filename))

    @staticmethod
    def print_mouse_controls() -> None:
        """Print the default mouse controls used by the course viewport."""
        print("Left drag: rotate")
        print("Middle drag or Shift+Left drag: pan")
        print("Mouse wheel or Right drag: zoom")


def demo() -> None:
    """Create a beam-like cube and show it in the course viewport."""
    engine = RenderEngine()
    surface = pv.Plane(
        center=(3000, 0, 0),
        i_size=6000,
        j_size=3000,
    )
    beam = pv.Cube(
        center=(3000, 0, 300),
        x_length=6000,
        y_length=300,
        z_length=600,
    )
    engine.add_mesh(surface, color="lightblue", show_edges=True, opacity=0.35)
    engine.add_mesh(beam, color="tan", show_edges=True)
    engine.render_point((0, 0, 0), label="Origin")

    # render_points 示例：渲染多个点（柱顶节点）
    column_tops = [
        (0, 0, 600),
        (3000, 0, 600),
        (6000, 0, 600),
        (0, 3000, 600),
        (3000, 3000, 600),
        (6000, 3000, 600),
    ]
    engine.render_points(column_tops, color="red", point_size=16.0)

    engine.render_curve(
        [
            (0, 0, 0),
            (3000, 0, 0),
            (6000, 1200, 0),
        ],
        color="steelblue",
    )
    engine.print_mouse_controls()
    engine.show()


if __name__ == "__main__":
    demo()
