"""
Classes to manage models
------------------------
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from typing import Any, ClassVar

import numpy as np

from pigreads import core as _core
from pigreads.diffusivity import diffusivity_matrix
from pigreads.helper import ModelParameters
from pigreads.kernels import PREDEFINED_MODELS, TEMPLATE
from pigreads.schema.model import ModelDefinition, ModelEntry


class Models:
    """
    This class stores the models to be used in a Pigreads simulation. The
    models are defined by OpenCL code. The class variable :py:attr:`available`
    is a dictionary of all available models.

    Models are added to an instance of this class using the :py:meth:`add`
    method, or as a list of tuples in the constructor. The order of the models
    is the order in which they are used in the simulation. ``models[0]`` is used
    at ``inhom`` values of 1, ``models[1]`` at 2, etc.

    :param tuples_key_kwargs: A list of tuples with the model key and keyword \
    arguments encoding parameter names and values to be passed to the \
    :py:meth:`add` method. If a string is given, it is treated the name of the \
    first model to be added with no keyword arguments. If ``None``, no \
    models are added.

    :param double_precision: If ``True``, use double precision for calculations.
    :var double_precision: If ``True``, use double precision for calculations.
    :vartype double_precision: bool
    """

    available: ClassVar[dict[str, ModelDefinition]] = {
        k: ModelDefinition(**v) for k, v in PREDEFINED_MODELS.items()
    }
    """
    Dictionary of all available models.
    """

    def __init__(
        self,
        tuples_key_kwargs: list[tuple[str, dict[str, float]]] | str | None = None,
        double_precision: bool = False,
    ):
        self.double_precision: bool = double_precision
        self._core: _core.Models | None = None

        if tuples_key_kwargs is None:
            tuples_key_kwargs = []
        elif isinstance(tuples_key_kwargs, str):
            tuples_key_kwargs = [(tuples_key_kwargs, {})]
        for key, kwargs in tuples_key_kwargs:
            self.add(key, **kwargs)

    @property
    def core(self) -> _core.Models:
        """
        Get the link to the core implementation of this class.
        """
        if not isinstance(self._core, _core.Models):
            self._core = _core.Models(double_precision=self.double_precision)
        return self._core

    def __len__(self) -> int:
        """
        The number of models added to the list of models.

        .. include in docs
        """
        return len(self.core)

    def get_key(self, imodel: int) -> str:
        """
        Get the key of the model with the given index.

        :param imodel: Index of the model.
        """
        return self.core.get_key(imodel)

    def get_definition(self, imodel: int) -> ModelDefinition:
        """
        Get the definition of the model with the given index.

        :param imodel: Index of the model.
        """
        return self.available[self.get_key(imodel)]

    def get_parameter(self, imodel: int, iparam: int) -> float:
        """
        Get the parameter with the given indices.

        :param imodel: Index of the model.
        :param iparam: Index of the parameter.
        :return: Parameter value.
        """
        return self.core.get_parameter(imodel, iparam)

    def set_parameter(self, imodel: int, iparam: int, value: float) -> None:
        """
        Set the parameter with the given indices.

        :param imodel: Index of the model.
        :param iparam: Index of the parameter.
        :param value: New parameter value.
        """
        self.core.set_parameter(imodel, iparam, value)

    def get_entry(self, imodel: int) -> ModelEntry:
        """
        Get the model entry with the given index linked to the core
        implementation to read and change model parameters.

        :param imodel: Index of the model.
        :return: Model entry with a :py:class:`pigreads.helper.ModelParameters` view.
        """
        model = ModelEntry(key=self.get_key(imodel))
        model.parameters = ModelParameters(models=self, imodel=imodel)
        return model

    def __getitem__(self, imodel: int) -> ModelEntry:
        """
        Get the model entry with the given index linked to the core
        implementation to read and change model parameters.

        :param imodel: Index of the model.
        :return: Model entry with a :py:class:`pigreads.helper.ModelParameters` view.

        .. include in docs
        """
        return self.get_entry(imodel)

    def __iter__(self) -> Iterator[ModelEntry]:
        """
        Get an iterator of model entries linked to the core
        implementation to read and change model parameters.

        :return: Iterator of model entries.

        .. include in docs
        """
        for imodel in range(len(self)):
            yield self.get_entry(imodel)

    @property
    def block_size(self) -> tuple[int, int, int]:
        """
        Local work size for running OpenCL kernels.

        The ``block_size`` parameter corresponds to OpenCL's ``localWorkSize`` and
        defines the size of a small block of the domain that is processed together by
        the OpenCL platform (typically the GPU).

        If chosen too small, the performance will be suboptimal. If chosen too
        large, the OpenCL kernel will not run. The default value is ``(1, 8, 8)``,
        i.e., a block of unit width in z, and ``8x8`` in the y and x
        dimensions. This is a good compromise for most applications.

        Tweaking this value can lead to significant performance improvements.
        """
        return self.core.get_block_size()

    @block_size.setter
    def block_size(self, block_size: tuple[int, int, int]) -> None:
        """
        Set the local work size for running OpenCL kernels.

        :param block_size: Local work size.
        """
        self.core.set_block_size(block_size)

    def add(self, key: str, **parameters: Any) -> None:
        """
        Select and enable a model with given parameters.

        :param key: The key of the model to be added.
        :param parameters: Parameter names and their values to be passed to the model.
        """
        model_id = self.core.get_number_definitions()
        model_def = self.available[key]
        self.core.add(
            key,
            self.code(key, model_id),
            len(model_def.variables),
            np.array(list(model_def(**parameters).values())),
        )

    def code(self, key: str, model_id: int) -> str:
        """
        OpenCL kernel source code defining a model.

        :param key: The key of the model.
        :param model_id: An integer identifying the model.
        """
        code = TEMPLATE.render(
            model_def=self.available[key],
            key=key,
            model_id=model_id,
        )

        if self.double_precision:
            return code
        return re.sub(
            r"""
            (?<![\w.])
            (
                (?:\d+\.\d*|\.\d+|\d+\.)
                (?:[eE][+-]?\d+)?
                |
                \d+[eE][+-]?\d+
            )
            (?![fFdD\w])
        """,
            r"\1f",
            code,
            flags=re.VERBOSE,
        )

    @property
    def Nv(self) -> int:  # pylint: disable=invalid-name
        """
        Maximum number of state variables in the models.
        """
        return self.core.Nv

    @property
    def dtype(self) -> type:
        """
        Data type to use for calculations,
        i.e., single or double precision floating point numbers.
        """
        dtype: type = np.double if self.double_precision else np.single
        return dtype

    def resting_states(
        self,
        inhom: np.ndarray[Any, Any],
        Nframes: int = 1,  # pylint: disable=invalid-name
        dtype: type | None = None,
    ) -> np.ndarray[Any, Any]:
        """
        Create an array of states and fill the first frame with the resting
        values of the models depending on the ``inhom`` values.

        :param inhom: A 3D array with integer values, encoding which model to use at each point. \
                Its value is zero for points outside the medium and one or more for points inside. \
                Values larger than zero are used to select one of multiple models: \
                1 for ``models[0]``, 2 for ``models[1]``, etc.
        :param Nframes: The number of frames in time.
        :param dtype: Data type of the arrays, \
                i.e., single or double precision floating point numbers.
        :return: A 5D array of shape (Nframes, Nz, Ny, Nx, Nv).
        """

        if dtype is None:
            dtype = self.dtype

        model_count = len(self)
        assert model_count > 0, "must add at least one model"
        assert inhom.ndim == 3
        inhom = inhom.astype(int)
        mask = inhom > 0
        states: np.ndarray[Any, Any] = np.full(
            (Nframes, *inhom.shape, self.Nv), np.nan, dtype=dtype
        )
        for imodel in range(len(self)):
            model_def = self.get_definition(imodel)
            for iv, resting in enumerate(model_def.variables.values()):
                states[0, mask * ((inhom - 1) % model_count == imodel), iv] = resting
        states[:, ~mask, :] = np.nan
        return states

    def weights(
        self,
        dz: float = 1.0,
        dy: float = 1.0,
        dx: float = 1.0,
        inhom: np.ndarray[Any, Any] | None = None,
        diffusivity: np.ndarray[Any, Any] | float = 1.0,
    ) -> np.ndarray[Any, Any]:
        """
        Calculate the weights for the diffusion term in the reaction-diffusion
        equation.

        :param dz: The distance between points in the z-dimension,\
                see :py:func:`pigreads.helper.deltas`.
        :param dy: The distance between points in the y-dimension.
        :param dx: The distance between points in the x-dimension.
        :param inhom: A 3D array with integer values, encoding which model to use at each point. \
                Its value is zero for points outside the medium and one or more for points inside. \
                If ``None``, all points are considered inside the medium.
        :param diffusivity: The diffusivity matrix, \
                see :py:func:`pigreads.diffusivity.diffusivity_matrix`. \
                If a scalar is given, the matrix is isotropic with the same value in all directions.
        :return: Weight matrix for the diffusion term, A 5D array of shape (1, Nz, Ny, Nx, 19).
        """

        assert dz > 0
        assert dy > 0
        assert dx > 0

        if inhom is None:
            inhom = np.ones(shape=(1, 1, 1), dtype=self.dtype)
        assert inhom.ndim == 3

        mask = np.ascontiguousarray(inhom, dtype=np.int32) > 0
        mask.shape = (1, *mask.shape, 1)

        diffusivity = np.ascontiguousarray(diffusivity, dtype=self.dtype)
        assert isinstance(diffusivity, np.ndarray)
        if diffusivity.ndim == 1:
            diffusivity = diffusivity_matrix(
                Df=float(diffusivity.item()), dtype=self.dtype
            )
        assert diffusivity.ndim == 4
        assert diffusivity.shape[-1] == 6

        return self.core.weights(dz, dy, dx, mask, diffusivity)

    def run(
        self,
        inhom: np.ndarray[Any, Any],
        weights: np.ndarray[Any, Any],
        states: np.ndarray[Any, Any],
        stim_signal: np.ndarray[Any, Any] | None = None,
        stim_shape: np.ndarray[Any, Any] | None = None,
        Nt: int = 1,  # pylint: disable=invalid-name
        dt: float = 0.001,
    ) -> np.ndarray[Any, Any]:
        """
        Run a Pigreads simulation.

        :param inhom: A 3D array with integer values, encoding which model to use at each point. \
                Its value is zero for points outside the medium and one or more for points inside. \
                Values larger than zero are used to select one of multiple models: \
                1 for ``models[0]``, 2 for ``models[1]``, etc.
        :param weights: The weights for the diffusion term, see :py:func:`weights`.
        :param states: The initial states of the simulation, a 4D array of shape \
                (Nz, Ny, Nx, Nv), see :py:func:`Models.resting_states`.
        :param stim_signal: A 3D array with the stimulus signal at each time point \
                for all variables, with shape (Nt, Ns, Nv). If ``None``, no stimulus is applied.
        :param stim_shape: A 4D array specifying the shape of the stimulus, \
                with shape (Ns, Nz, Ny, Nx). If ``None``, no stimulus is applied
        :param Nt: The number of time steps to run the simulation for.
        :param dt: The time step size.
        :return: The final states of the simulation, a 4D array of shape (Nz, Ny, Nx, Nv).
        """
        assert Nt > 0
        assert dt > 0
        assert len(self) > 0, "must add at least one model"
        assert inhom.ndim == 3

        if stim_signal is None or getattr(stim_signal, "size", 0) == 0:
            stim_signal = np.zeros((0, 0, 0, 0, 0), dtype=self.dtype)
        else:  # np.ndarray
            assert stim_signal.ndim in [2, 3]
            stim_signal = np.reshape(
                stim_signal, (stim_signal.shape[0], -1, 1, 1, self.Nv)
            )

        assert isinstance(stim_signal, np.ndarray)
        Ns = stim_signal.shape[1]  # pylint: disable=invalid-name

        if stim_shape is None or getattr(stim_shape, "size", 0) == 0:
            stim_shape = np.zeros((0, 0, 0, 0, 0), dtype=self.dtype)
        else:  # np.ndarray
            assert stim_shape.ndim in [3, 4]
            stim_shape = np.where(inhom > 0, stim_shape, 0)
            stim_shape.shape = (Ns, *stim_shape.shape[-3:], 1)

        assert isinstance(stim_shape, np.ndarray)
        assert stim_shape.shape[0] == stim_signal.shape[1]

        states = states.astype(self.dtype).copy(order="C")
        self.core.run(
            np.ascontiguousarray(np.reshape(inhom, (*inhom.shape, 1)), dtype=np.int32),
            np.ascontiguousarray(weights, dtype=self.dtype),
            states,
            np.ascontiguousarray(stim_signal, dtype=self.dtype),
            np.ascontiguousarray(stim_shape, dtype=self.dtype),
            Nt,
            dt,
        )
        return states


__all__ = [
    "Models",
]
