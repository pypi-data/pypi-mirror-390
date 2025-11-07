"""
Plots and movies
----------------
"""

from __future__ import annotations

import multiprocessing
import subprocess
import time
from os import linesep
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FFMpegWriter
from matplotlib.axes import Axes
from matplotlib.colorbar import Colorbar
from matplotlib.image import AxesImage

from pigreads.progress import PROGRESS_ITERS
from pigreads.schema.simulation import Simulation


def imshow_defaults(
    array: np.ndarray[Any, Any] | None = None,
    sim: Simulation | None = None,
    dx: float | None = None,
    dy: float | None = None,
    Nx: int | None = None,  # pylint: disable=invalid-name
    Ny: int | None = None,  # pylint: disable=invalid-name
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Set default imshow arguments.

    :param array: Array to display.
    :param sim: Simulation object.
    :param dx: Grid spacing in x.
    :param dy: Grid spacing in y.
    :param Nx: Number of grid points in x.
    :param Ny: Number of grid points in y.
    :param kwargs: Additional arguments.
    :return: Dictionary of arguments for
             :py:func:`matplotlib.pyplot.imshow`.
    """

    if "origin" not in kwargs:
        kwargs["origin"] = "lower"

    if "interpolation" not in kwargs:
        kwargs["interpolation"] = "none"

    if array is not None:
        if "vmin" not in kwargs:
            kwargs["vmin"] = np.nanmin(array)

        if "vmax" not in kwargs:
            kwargs["vmax"] = np.nanmax(array)

    if sim is not None:
        dx, dy = sim.dx, sim.dy
        Nx, Ny = sim.Nx, sim.Ny

    if array is not None:
        Ny, Nx = array.shape[-2:]

    if (
        "extent" not in kwargs
        and dx is not None
        and dy is not None
        and Nx is not None
        and Ny is not None
    ):
        kwargs["extent"] = (
            -0.5 * dx,
            (Nx + 0.5) * dx,
            -0.5 * dy,
            (Ny + 0.5) * dy,
        )

    return kwargs


def plot_frame(
    ax: Axes,
    frame: np.ndarray[Any, Any],
    xlabel: str = "x",
    ylabel: str = "y",
    vlabel: str = "",
    title: str = "",
    **kwargs: Any,
) -> tuple[AxesImage, Colorbar]:
    """
    Display a frame as an image.

    :param ax: Axes object.
    :param xlabel: Label for the x-axis.
    :param ylabel: Label for the y-axis.
    :param vlabel: Colorbar label.
    :param title: Title of the plot.
    :param frame: Frame to display.
    :param kwargs: Passed to :py:func:`matplotlib.pyplot.imshow`.

    :return: Image and colorbar objects.
    """
    assert frame.ndim == 2
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    im = ax.imshow(frame, **imshow_defaults(array=frame, **kwargs))
    cbar = plt.colorbar(im)
    cbar.set_label(vlabel)
    return im, cbar


def movie(
    path: str,
    frames: np.ndarray[Any, Any],
    dpi: int = 180,
    fps: int = 15,
    tlables: list[str] | None = None,
    progress: str = "none",
    progress_dict: dict[str, int] | None = None,
    parallel: int = 1,
    **kwargs: Any,
) -> None:
    """
    Render a chunk of frames to a movie file, with optional parallelization.

    :param path: Path to write the movie file to.
    :param frames: Array of frames.
    :param dpi: Dots per inch.
    :param fps: Frames per second.
    :param tlables: List of time labels.
    :param progress: Progress bar type.
    :param progress_dict: Dictionary to store progress.
    :param parallel: Number of processes (default 1, 0 to use all CPUs).
    :param kwargs: Passed to :py:func:`plot_frame`.
    """
    assert frames.ndim == 3

    if parallel == 1:
        fig, ax = plt.subplots(dpi=dpi)
        writer = FFMpegWriter(fps=fps)
        tlables = [f"{i}" for i, _ in enumerate(frames)] if tlables is None else tlables
        im, _ = plot_frame(ax, frames[0], **imshow_defaults(array=frames, **kwargs))

        prog = PROGRESS_ITERS[progress]
        with writer.saving(fig, path, fig.dpi):
            for (i, frame), tlabel in zip(
                enumerate(prog(frames)), tlables, strict=True
            ):
                ax.set_title(tlabel)
                im.set_data(frame)
                writer.grab_frame()
                if progress_dict is not None:
                    progress_dict[path] = i + 1
        return

    Np = multiprocessing.cpu_count() if parallel == 0 else parallel  # pylint: disable=invalid-name
    Nfr = len(frames)  # pylint: disable=invalid-name
    Nfrp = (Nfr + Np - 1) // Np  # pylint: disable=invalid-name
    chunks = [slice(i, min(i + Nfrp, Nfr)) for i in range(0, Nfr, Nfrp)]

    with TemporaryDirectory() as temp:
        paths = [str(Path(temp) / f"{i}.mp4") for i, _ in enumerate(chunks)]

        with multiprocessing.Manager() as manager:
            assert progress_dict is None
            progress_dict_ = manager.dict(dict.fromkeys(paths, 0))
            tasks = [
                [
                    {
                        "path": path,
                        "frames": frames[chunk],
                        "tlables": tlables[chunk] if tlables else None,
                        "progress_dict": progress_dict_,
                        "parallel": 1,
                        "dpi": dpi,
                        "fps": fps,
                        **kwargs,
                    }
                ]
                for path, chunk in zip(paths, chunks, strict=True)
                if chunk.start < chunk.stop
            ]

            progress_proc = multiprocessing.Process(
                target=movie_progress_updater,
                args=(progress, Nfr, progress_dict_),
            )
            progress_proc.start()

            with multiprocessing.Pool(processes=Np) as pool:
                pool.starmap_async(movie_wrapper, tasks).get()

            progress_proc.join()

        pathlist = Path(temp) / "files.txt"
        with pathlist.open("w") as f:
            for p in paths:
                f.write(f"file '{p}'{linesep}")

        proc = subprocess.Popen(  # pylint: disable=consider-using-with
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                pathlist,
                "-c",
                "copy",
                str(path),
            ],
            stderr=subprocess.PIPE,
        )

        _, stderr = proc.communicate()
        assert proc.returncode == 0, stderr.decode()


def movie_wrapper(kwargs: dict[str, Any]) -> None:
    """
    Wrapper for movie to allow for multiprocessing.

    :param kwargs: Keyword arguments for :py:func:`movie`.
    """
    return movie(**kwargs)


def movie_progress_updater(
    progress: str, total: int, progress_dict: dict[str, int]
) -> None:
    """
    Update the progress bar for a movie.

    :param progress: Progress bar type.
    :param total: Total number of frames.
    :param progress_dict: Dictionary to store progress.
    """
    prog = PROGRESS_ITERS[progress]
    for i in prog(range(total)):
        while sum(progress_dict.values()) < i:
            time.sleep(0.1)


__all__ = [
    "imshow_defaults",
    "movie",
    "plot_frame",
]
