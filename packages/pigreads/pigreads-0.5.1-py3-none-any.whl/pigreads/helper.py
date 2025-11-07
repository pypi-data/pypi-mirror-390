"""
Various functions
-----------------
"""

from __future__ import annotations

from collections.abc import Iterator, MutableMapping
from datetime import datetime
from os import linesep
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np

from pigreads._version import version as __version__

if TYPE_CHECKING:
    from pigreads.models import Models


def get_upper_triangle(
    matrix: np.ndarray[Any, Any],
) -> np.ndarray[Any, Any]:
    """
    Convert a 3x3 matrix to a 6D vector, with the diagonal and upper triangle
    of the matrix as elements in the order xx, yy, zz, yz, xz, xy. Additional
    dimensions are supported, but the last two dimensions must each have size
    3.

    :param matrix: A 3x3 matrix.
    :return: A 6D vector.
    """

    matrix = np.array(matrix)
    assert matrix.ndim >= 2, "matrix must have at least two dimensions"
    assert matrix.shape[-1] == 3, "matrix must be a 3x3 matrix (in the last two axes)"
    assert matrix.shape[-2] == 3, "matrix must be a 3x3 matrix (in the last two axes)"
    assert np.allclose(matrix[..., 1, 2], matrix[..., 2, 1]), (
        "The yz and zy components of matrix need to be the same"
    )
    assert np.allclose(matrix[..., 0, 2], matrix[..., 2, 0]), (
        "The xz and zx components of matrix need to be the same"
    )
    assert np.allclose(matrix[..., 0, 1], matrix[..., 1, 0]), (
        "The xy and yx components of matrix need to be the same"
    )
    triag: np.ndarray[Any, Any] = np.stack(
        (
            matrix[..., 0, 0],  # xx
            matrix[..., 1, 1],  # yy
            matrix[..., 2, 2],  # zz
            matrix[..., 1, 2],  # yz
            matrix[..., 0, 2],  # xz
            matrix[..., 0, 1],  # xy
        ),
        axis=-1,
    )
    return triag


def normalise_vector(
    f: np.ndarray[Any, Any] | list[int] | tuple[int, int, int],
    dtype: type = np.single,
) -> np.ndarray[Any, Any]:
    """
    Normalise a 3D vector to unit length.

    :param f: A 3D vector over space with shape (Nz, Ny, Nx, 3).
    :param dtype: Data type of the arrays, i.e., single or double precision floating point numbers.
    :return: A 5D vector with shape (Nz, Ny, Nx, 3, 1).
    """

    f = np.array(f, dtype=dtype)
    assert isinstance(f, np.ndarray)
    assert f.ndim >= 1, "f must be a 3D vector"
    assert f.ndim <= 4, "too many dimensions for f"
    assert f.shape[-1] == 3, "f must be a 3D vector (in the last axis)"
    while f.ndim < 4:
        f.shape = (1, *f.shape)
    norm = np.linalg.norm(f, axis=-1)
    nonzero = norm > 0
    norm.shape = (*norm.shape, 1)
    f[nonzero] /= norm[nonzero]
    f.shape = (*f.shape, 1)
    assert f.ndim == 5, "f must have 5 dimensions: z, y, x, row, col"
    assert f.shape[-1] == 1, "f must be a 3D column vector"
    assert f.shape[-2] == 3, "f must be a 3D column vector"
    return f


def to_ithildin(
    framedur: float,
    dt: float,
    dz: float,
    dy: float,
    dx: float,
    models: Models,
    states: np.ndarray[Any, Any],
    inhom: np.ndarray[Any, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, np.ndarray[Any, Any]]]:
    """
    Convert the output of a Pigreads simulation to an Ithildin SimData object.

    While originally designed for a different reaction-diffusion solver,
    the Python module for Ithildin is useful to analyse Pigreads simulations.

    :param framedur: The duration between subsequent frames, usually in milliseconds.
    :param dt: The time step size used in :py:func:`pigreads.models.Models.run`,\
            usually in milliseconds.
    :param dz: The distance between points in the z-dimension,\
            see :py:func:`pigreads.helper.deltas`.
    :param dy: The distance between points in the y-dimension.
    :param dx: The distance between points in the x-dimension.
    :param models: The models used in the simulation,\
            see :py:class:`pigreads.models.Models`.
    :param states: The states of the simulation, a 5D array of shape \
            (Nt, Nz, Ny, Nx, Nv),\
            see :py:func:`pigreads.models.Models.resting_states`\
            and :py:func:`pigreads.models.Models.run`.
    :param inhom: A 3D array with integer values, encoding which model to use at each point. \
            Its value is zero for points outside the medium and one or more for points inside. \
            If ``None``, all points are considered inside the medium.
    :return: Tuple of an Ithildin log file as a string \
            and a dictionary of the variables by variable name.

    Usage::

        import ithildin as ith
        log, variables = pig.to_ithildin(Nt * dt, dt, dz, dy, dx, models, states, inhom)
        sd = ith.SimData(log=ith.Log(data=log))
        sd.vars = variables
    """

    Nt, Nz, Ny, Nx, _ = states.shape  # pylint: disable=invalid-name

    timestamp = datetime.now()

    log = {
        "Ithildin log version": 2,
        "Simulation parameters": {
            "Ithildin library version": f"pigreads {__version__}",
            "Timestep dt": dt,
            "Frame duration": framedur,
            "Number of frames to take": Nt,
            "Serial number": int(timestamp.strftime(r"%Y%m%d%H%M%S")),
            "Name of simulation series": "pigreads",
        },
        "Geometry parameters": {
            "Number of dimensions": 3,
            "Voxel size": [dx, dy, dz],
            "Domain size": [Nx, Ny, Nz],
        },
        "Start date": timestamp.isoformat(),
    }

    for i, model in enumerate(models):
        model_def = models.available[model.key]
        key = "Model parameters"
        if i > 0:
            key += f" {i}"
        log[key] = {
            "Model type": model_def.name,
            "Class": model.key,
            "Citation": linesep.join(model_def.dois),
            "Parameters": model_def(**model.parameters),
            "Initial values": model_def.variables,
            "Variable names": list(model_def.variables.keys()),
            "Number of vars": len(model_def.variables),
        }

    shape = (-1, Nz, Ny, Nx)
    variables: dict[str, np.ndarray[Any, Any]] = {
        v: states[..., iv].reshape(shape)
        for iv, v in enumerate(models.available[models[0].key].variables.keys())
    }
    if inhom is not None:
        variables["inhom"] = inhom.reshape(shape)

    return log, variables


def delta(x: np.ndarray[Any, Any], ax: int = -1) -> float:
    """
    Extract grid spacing from a 3D array.

    :param x: A 3D array.
    :param ax: The axis along which to calculate the distance.
    :return: The distance between the first two points.

    For example, consider this code::

        z, y, x = np.mgrid[0, 0:4:0.2, 0:1:5j]
        dx = pig.delta(z, ax=-1)
        dy = pig.delta(z, ax=-2)
        dz = pig.delta(z, ax=-3)
    """
    assert x.ndim == 3
    diff = np.diff(np.moveaxis(x, ax, -1)[0, 0, :2])
    return 1.0 if diff.shape[0] == 0 else float(diff[0])


def deltas(*x: np.ndarray[Any, Any]) -> list[float]:
    """
    Extract grid spacing from a 3D meshgrid.

    For example, consider this code::

        z, y, x = np.mgrid[0, 0:4:0.2, 0:1:5j]
        dz, dy, dx = pig.deltas(z, y, x)

    :param x: A 3D array.
    :return: A list with the distances between the points.
    """
    return [delta(xi, i) for i, xi in enumerate(x)]


def prepare_array(
    shape: tuple[int, ...],
    path: Path | str | None = None,
    dtype: type = np.single,
) -> np.ndarray[Any, Any]:
    """
    Prepare an array in a given shape.

    Either create a new array or load an existing array from the file with
    the given path as a memory map.

    The shape and dtype of the array are given as arguments. If the path is
    ``None``, a new array is created. If the path is a file, the array is
    loaded from the file. If the array is not of the correct shape or dtype
    or the file does not exist, a new array is created.

    The array is returned as a memory map if a path is given, otherwise as a
    normal numpy array.

    :param shape: Shape of the array.
    :param path: Path to the file to load the array from.
    :param dtype: Data type of the arrays, i.e., single or double precision floating point numbers.
    :return: Resulting array.
    :see: :py:func:`numpy.lib.format.open_memmap`
    """

    if path is None:
        return np.zeros(shape=shape, dtype=dtype)

    path = Path(path)
    if path.is_file():
        arr = np.lib.format.open_memmap(path, "r+")  # type: ignore[no-untyped-call]
        if isinstance(arr, np.ndarray) and arr.shape == shape and arr.dtype == dtype:
            return arr
        del arr

    arr = np.lib.format.open_memmap(  # type: ignore[no-untyped-call]
        path,
        "w+",
        dtype=dtype,
        shape=shape,
    )
    assert isinstance(arr, np.ndarray)
    arr[:] = np.nan
    return arr


class ModelParameters(MutableMapping[str, float]):
    """
    A view into the core implementation of the models
    allowing reading and modifying the parameters of a model.

    :param models: Instance of the models class to link to the core.
    :var models: Instance of the models class to link to the core.
    :vartype models: pigreads.models.Models
    :param imodel: Index of the model.
    :var imodel: Index of the model.
    :vartype imodel: int
    """

    def __init__(self, models: Models, imodel: int) -> None:
        self._models: Models = models
        self._imodel: int = imodel
        self._keys: list[str] = list(
            models.get_definition(imodel).all_parameters.keys()
        )

    def _key_to_index(self, key: str) -> int:
        """
        Get the index of the parameter with the given key.

        :param key: Key of the parameter.
        :return: Index of the parameter.

        .. include in docs
        """
        return next(i for i, k in enumerate(self._keys) if k == key)

    def __getitem__(self, key: str) -> float:
        """
        Get the parameter with the given key.

        :param key: Key of the parameter.
        :return: Parameter value.

        .. include in docs
        """
        return self._models.get_parameter(self._imodel, self._key_to_index(key))

    def __setitem__(self, key: str, value: float) -> None:
        """
        Set the parameter with the given key.

        :param key: Key of the parameter.
        :param value: New value of the parameter.

        .. include in docs
        """
        self._models.set_parameter(self._imodel, self._key_to_index(key), value)

    def __delitem__(self, key: str) -> None:
        """
        Delete the parameter with the given key.

        Note: This operation is not supported in this class.

        :param key: Key of the parameter.

        .. include in docs
        """
        message = "Deleting items is not supported in this class."
        raise NotImplementedError(message)

    def __iter__(self) -> Iterator[str]:
        """
        Get an iterator of the keys of the parameters.

        :return: Iterator of the keys of the parameters.

        .. include in docs
        """
        return iter(self._keys)

    def __len__(self) -> int:
        """
        Get the number of parameters.

        :return: Number of parameters.

        .. include in docs
        """
        return len(self._keys)

    def to_dict(self) -> dict[str, float]:
        """
        Convert the parameters to a dictionary.

        :return: Dictionary of the parameters.
        """
        return {k: self[k] for k in self._keys}

    def __repr__(self) -> str:
        """
        Get the string representation of the parameters.

        :return: String representation of the parameters.

        .. include in docs
        """
        return repr(self.to_dict())

    def __str__(self) -> str:
        """
        Get the string representation of the parameters.

        :return: String representation of the parameters.

        .. include in docs
        """
        return str(self.to_dict())


__all__ = [
    "ModelParameters",
    "delta",
    "deltas",
    "get_upper_triangle",
    "normalise_vector",
    "prepare_array",
    "to_ithildin",
]
