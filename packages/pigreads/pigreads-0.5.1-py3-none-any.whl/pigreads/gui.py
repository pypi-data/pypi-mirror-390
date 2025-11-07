"""
Interactive simulation
----------------------
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

import matplotlib.pyplot as plt
import numpy as np
import yaml
from matplotlib.colors import Normalize

from pigreads.models import Models
from pigreads.schema.simulation import Simulation

if TYPE_CHECKING:
    import pygame


def get_iz_iv(
    models: Models,
    variable: str | int | None,
    index_z: int | None,
) -> tuple[int, int]:
    """
    Interpret z index and variable index from command line arguments.

    :param models: Models object.
    :param variable: Variable name or index.
    :param index_z: Index in z direction.
    :return: Tuple of z index and variable index.
    """

    iz: int = index_z or 0
    iv: int

    try:
        iv = int(variable or 0)
        assert iv >= 0, "Invalid variable index"
        assert iv < models.Nv, "Invalid variable index"

    except ValueError:
        iv = 0 if variable is None else Simulation.varidx(models)[str(variable)]

    return iz, iv


class LiveView:
    """
    Live view for a simulation.

    Plot a single variable at a fixed z index in an interactive window or save
    it to a file.

    :param models: The models used in the simulation.
    :param variable: Variable name or index.
    :param index_z: Index in z direction.
    :param dx: Grid spacing in x direction.
    :param dy: Grid spacing in y direction.
    :param vmin: Minimum value for colormap normalisation.
    :param vmax: Maximum value for colormap normalisation.
    :param cmap: The colormap to use.
    :param path: Path to save the image to. If None, an interactive window is shown.
    :param click_radius: Radius of click region. If None, clicking is disabled.
    :param click_value: Value to add continuously while clicking. If None, clicking is disabled.

    :ivar models: The models used in the simulation.
    :ivar iv: Index of the variable to plot.
    :ivar iz: Index in z direction.
    :ivar dx: Grid spacing in x direction.
    :ivar dy: Grid spacing in y direction.
    :ivar vmin: Minimum value for colormap normalisation.
    :ivar vmax: Maximum value for colormap normalisation.
    :ivar cmap: The colormap to use.
    :ivar path: Path to save the image to. If None, an interactive window is shown.
    :ivar click_radius: Radius of click region. If None, clicking is disabled.
    :ivar click_value: Value to add continuously while clicking. If None, clicking is disabled
    :ivar click_location: Current mouse click location.
    :ivar click_location_prev: Previous mouse click location.
    :ivar mouse_pressed: Whether the mouse is currently pressed.
    """

    def __init__(
        self,
        models: Models,
        variable: str | int | None = None,
        index_z: int | None = None,
        dx: float = 1.0,
        dy: float = 1.0,
        vmin: float | None = None,
        vmax: float | None = None,
        cmap: str = "viridis",
        path: Path | str | None = None,
        click_radius: float | None = None,
        click_value: float | None = None,
    ) -> None:
        self.models = models
        self.path = path
        self.iz, self.iv = get_iz_iv(models, variable, index_z)
        self.dx = dx
        self.dy = dy
        self.vmin = vmin
        self.vmax = vmax
        self.cmap = plt.get_cmap(cmap)
        self.click_radius = click_radius
        self.click_value = click_value
        self.click_location: tuple[float, float] | None = None
        self.click_location_prev: tuple[float, float] | None = None
        self.mouse_pressed = False
        self._screen: pygame.Surface | None = None
        self._clock: pygame.time.Clock | None = None

    @staticmethod
    def normalise_kwargs(kwargs: int | str | dict[str, Any]) -> dict[str, Any]:
        """
        Normalise command line arguments which can be given in a variety of data types.

        :param kwargs: The command line argument.
        :return: Keyword arguments for the constructor of this class.
        """

        if isinstance(kwargs, str):
            path = Path(kwargs)
            if path.is_file():
                kwargs = yaml.safe_load(path.read_bytes())
        if not isinstance(kwargs, dict):
            kwargs = {"variable": kwargs}
        assert isinstance(kwargs, dict)
        return kwargs

    def draw_thick_line(self, frame: np.ndarray[Any, Any]) -> None:
        """
        Draw a thick line between the previous and new locations with the given radius.

        :param frame: Frame to modify.
        """
        if (
            self.click_radius is None
            or self.click_value is None
            or self.click_location is None
        ):
            return

        x1, y1 = self.click_location
        x2, y2 = self.click_location

        if self.click_location_prev is not None:
            x2, y2 = self.click_location_prev

        dx, dy = x2 - x1, y2 - y1

        y, x = np.meshgrid(
            self.dy * np.arange(frame.shape[-2]),
            self.dx * np.arange(frame.shape[-1]),
            indexing="ij",
        )

        with np.errstate(divide="ignore", invalid="ignore"):
            distance = np.abs(+dy * x - dx * y + x2 * y1 - y2 * x1) / np.linalg.norm(
                (dy, dx), axis=0
            )
            t = ((x - x1) * dx + (y - y1) * dy) / (dx**2 + dy**2)

        mask = (distance <= self.click_radius) & (t >= 0) & (t <= 1)

        for y_, x_ in [(y1, x1), (y2, x2)]:
            mask[np.linalg.norm([y - y_, x - x_], axis=0) <= self.click_radius] = True

        frame[mask] = self.click_value
        self.click_location_prev = self.click_location

    def update(self, states: np.ndarray[Any, Any], time: float) -> None:
        """
        Update the live view.

        :param states: Array of states with shape (Nz, Ny, Nx, Nv).
        :param time: Simulated time.
        """

        frame = states[self.iz % states.shape[0], :, :, self.iv % states.shape[-1]]
        Ny, Nx = frame.shape  # pylint: disable=invalid-name
        norm = Normalize(
            vmin=np.nanmin(frame) if self.vmin is None else self.vmin,
            vmax=np.nanmax(frame) if self.vmax is None else self.vmax,
        )
        frame_rgb = (self.cmap(norm(frame.T))[..., :3] * 255).astype(np.uint8)

        if self.path is not None:
            plt.imsave(self.path, np.transpose(frame_rgb, (1, 0, 2)))

        else:
            import pygame  # pylint: disable=import-outside-toplevel

            if self._screen is None:
                pygame.init()  # pylint: disable=no-member
                self._screen = pygame.display.set_mode(
                    (Nx, Ny),
                    pygame.RESIZABLE,  # pylint: disable=no-member
                    vsync=1,
                )
                self._clock = pygame.time.Clock()
            assert self._screen is not None
            assert self._clock is not None
            pygame.display.set_caption(f"t = {time:.2f} - Pigreads")

            wx, wy = self._screen.get_size()
            scale = min(wx / Nx, wy / Ny)
            sx, sy = scale * Nx, scale * Ny
            ox, oy = int((wx - sx) / 2 + 0.5), int((wy - sy) / 2 + 0.5)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # pylint: disable=no-member
                    pygame.quit()  # pylint: disable=no-member
                    sys.exit(0)

            if pygame.mouse.get_pressed()[0]:
                mx, my = pygame.mouse.get_pos()
                mx = (mx - ox) / sx * Nx * self.dx
                my = (my - oy) / sy * Ny * self.dy
                self.click_location = mx, my
                self.mouse_pressed = True

            else:
                self.mouse_pressed = False
                self.click_location = None
                self.click_location_prev = None

            self.draw_thick_line(frame)

            surface = pygame.surfarray.make_surface(frame_rgb)
            surface = pygame.transform.smoothscale(
                surface, (int(sx + 0.5), int(sy + 0.5))
            )

            self._screen.fill((0, 0, 0))
            self._screen.blit(surface, (ox, oy))
            pygame.display.flip()
            self._clock.tick(120)


__all__ = [
    "LiveView",
]
