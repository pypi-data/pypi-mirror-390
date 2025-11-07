"""
Backwards compatibility
-----------------------

While these functions are deprecated, they are kept in the API for legacy
reasons.
"""

from __future__ import annotations

from typing import Any
from warnings import warn

import numpy as np

from pigreads.models import Models


def weights(
    dz: float = 1.0,
    dy: float = 1.0,
    dx: float = 1.0,
    inhom: np.ndarray[Any, Any] | None = None,
    diffusivity: np.ndarray[Any, Any] | float = 1.0,
    double_precision: bool = False,
) -> np.ndarray[Any, Any]:
    """
    Calculate the weights for the diffusion term in the reaction-diffusion
    equation.

    .. deprecated:: 0.5.0
       Use :func:`pigreads.models.Models.weights` instead.

    :param dz: The distance between points in the z-dimension,\
            see :py:func:`pigreads.helper.deltas`.
    :param dy: The distance between points in the y-dimension.
    :param dx: The distance between points in the x-dimension.
    :param inhom: A 3D array with integer values, encoding which model to use at each point. \
            Its value is zero for points outside the medium and one or more for points inside. \
            If ``None``, all points are considered inside the medium.
    :param diffusivity: The diffusivity matrix,\
            see :py:func:`pigreads.diffusivity.diffusivity_matrix`. \
            If a scalar is given, the matrix is isotropic with the same value in all directions.
    :param double_precision: If ``True``, use double precision for calculations.
    :return: Weight matrix for the diffusion term, A 5D array of shape (1, Nz, Ny, Nx, 19).
    """
    message: str = (
        "This function is deprecated! Use pigreads.models.Models.weights instead."
    )
    warn(message, DeprecationWarning, stacklevel=2)
    models = Models(double_precision=double_precision)
    return models.weights(dz, dy, dx, inhom=inhom, diffusivity=diffusivity)


def run(
    models: Models,
    inhom: np.ndarray[Any, Any],
    weights: np.ndarray[Any, Any],  # pylint: disable=redefined-outer-name
    states: np.ndarray[Any, Any],
    stim_signal: np.ndarray[Any, Any] | None = None,
    stim_shape: np.ndarray[Any, Any] | None = None,
    Nt: int = 1,  # pylint: disable=invalid-name
    dt: float = 0.001,
    double_precision: bool | None = None,
) -> np.ndarray[Any, Any]:
    """
    Run a Pigreads simulation.

    .. deprecated:: 0.5.0
       Use :func:`pigreads.models.Models.run` instead.

    :param models: The models to be used in the simulation,\
            see :py:class:`pigreads.models.Models`.
    :param inhom: A 3D array with integer values, encoding which model to use at each point. \
            Its value is zero for points outside the medium and one or more for points inside. \
            Values larger than zero are used to select one of multiple models: \
            1 for ``models[0]``, 2 for ``models[1]``, etc.
    :param weights: The weights for the diffusion term, see :py:func:`weights`.
    :param states: The initial states of the simulation, a 4D array of shape \
            (Nz, Ny, Nx, Nv), see :py:func:`pigreads.models.Models.resting_states`.
    :param stim_signal: A 3D array with the stimulus signal at each time point \
            for all variables, with shape (Nt, Ns, Nv). If ``None``, no stimulus is applied.
    :param stim_shape: A 4D array specifying the shape of the stimulus, \
            with shape (Ns, Nz, Ny, Nx). If ``None``, no stimulus is applied
    :param Nt: The number of time steps to run the simulation for.
    :param dt: The time step size.
    :param double_precision: If ``True``, use double precision for calculations.
    :return: The final states of the simulation, a 4D array of shape (Nz, Ny, Nx, Nv).
    """
    message: str = (
        "This function is deprecated! Use pigreads.models.Models.run instead."
    )
    warn(message, DeprecationWarning, stacklevel=2)
    if double_precision is not None:
        assert models.double_precision == double_precision, (
            "Chosen precision must match with instance of Models."
        )
    return models.run(
        inhom=inhom,
        weights=weights,
        states=states,
        stim_signal=stim_signal,
        stim_shape=stim_shape,
        Nt=Nt,
        dt=dt,
    )


__all__ = [
    "run",
    "weights",
]
