"""
Low-level implementation
------------------------
"""

from __future__ import annotations

import os
from logging import warning
from typing import Any

import numpy as np
import pyopencl as cl

from pigreads import kernels

Size = np.uint64
"""
The unsigned integer type used for sizes and indices.
"""
Int = np.int32
"""
The signed integer type used for integer arrays.
"""

StatesIdx = np.dtype(
    [
        ("Ns", Size),
        ("Nt", Size),
        ("Nz", Size),
        ("Ny", Size),
        ("Nx", Size),
        ("Nv", Size),
        ("it", Size),
        ("iz", Size),
        ("iy", Size),
        ("ix", Size),
        ("iv", Size),
    ]
)
"""
The struct used to pass array shape and indices to OpenCL kernels.
"""


def idx(
    s: Any, it: int = 0, iz: int = 0, iy: int = 0, ix: int = 0, iv: int = 0
) -> np.ndarray:
    """
    Create a ``StatesIdx`` struct to pass to OpenCL kernels.

    :param s: The array for which to create the index struct.
    :param it: Index in time.
    :param iz: Index in the z-dimension.
    :param iy: Index in the y-dimension.
    :param ix: Index in the x-dimension.
    :param iv: Index in the variable dimension.
    :return: The ``StatesIdx`` struct as a numpy array.
    """
    shape = np.ones(5, dtype=np.int64)
    shape[-len(s.shape) :] = s.shape
    return np.array(
        (
            s.dtype.itemsize,
            *shape,
            it % shape[0],
            iz % shape[1],
            iy % shape[2],
            ix % shape[3],
            iv % shape[4],
        ),
        dtype=StatesIdx,
    )


_context: cl.Context | None = None
"""
The OpenCL context used for computations.
"""
_queue: cl.CommandQueue | None = None
"""
The OpenCL command queue used for computations.
"""


class Models:
    """
    Core implementation of the ``Models`` class.

    :see: :py:class:`pigreads.models.Models` for the main interface to the models.

    :param double_precision: If ``True``, use double precision for calculations.
    :param context: OpenCL context to use for computations.
    """

    def __init__(
        self, double_precision: bool = False, context: cl.Context | None = None
    ) -> None:
        self._double_precision: bool = double_precision
        self._Nv: int = 0  # pylint: disable=invalid-name
        self._model_keys: list[str] = []
        self._model_ids: list[int] = []
        self._model_offsets: list[int] = [0]
        self._model_params: list[float] = []
        self._context: cl.Context | None = context
        self._queue: cl.CommandQueue | None = None
        self._kernels: dict[str, cl.Kernel] = {}
        self._block_size: tuple[int, int, int] = (1, 8, 8)
        self.compile(kernels.CORE)

    def prepare_context(self) -> None:
        """
        Make sure there is a context and a queue.
        """
        if self._context is None:
            global _context  # noqa: PLW0603  # pylint: disable=global-statement
            if _context is None:
                _context = cl.create_some_context()
            self._context = _context

        if self._queue is None:
            global _queue  # noqa: PLW0603  # pylint: disable=global-statement
            if _queue is None:
                _queue = cl.CommandQueue(self._context)
            self._queue = _queue

    @property
    def context(self) -> cl.Context:
        """
        The OpenCL context used for computations.
        """
        self.prepare_context()
        assert self._context is not None
        return self._context

    @property
    def queue(self) -> cl.CommandQueue:
        """
        The OpenCL command queue used for computations.
        """
        self.prepare_context()
        assert self._queue is not None
        return self._queue

    def compile(self, code: str) -> None:
        """
        Compile the given OpenCL code.

        :param code: OpenCL code to compile.
        """
        program = cl.Program(self.context, kernels.HEADER + code)

        if self.double_precision:
            for device in self.context.devices:
                assert "cl_khr_fp64" in device.extensions.split(), (
                    "The selected device does not support double precision."
                )

        cokey = "PYOPENCL_COMPILER_OUTPUT"
        coval = os.environ.get(cokey)
        os.environ[cokey] = "1"

        try:
            program.build(
                options=["-D", "DOUBLE_PRECISION"] if self.double_precision else []
            )

        except cl.CompilerWarning as e:
            warning(str(e))

        if coval is not None:
            os.environ[cokey] = coval
        else:
            del os.environ[cokey]

        for kernel in program.all_kernels():
            self._kernels[kernel.function_name] = kernel

    @property
    def double_precision(self) -> bool:
        """
        Whether double precision is used.
        """
        return self._double_precision

    @property
    def real(self) -> type:
        """
        The floating-point type used, i.e., ``np.float32`` or ``np.float64``.
        """
        return np.float64 if self.double_precision else np.float32

    @property
    def Nv(self) -> int:  # pylint: disable=invalid-name
        """
        Maximum number of state variables in the models.
        """
        return self._Nv

    def __len__(self) -> int:
        """
        Number of models.

        :return: Number of models.

        .. include in docs
        """
        return len(self._model_ids)

    def get_number_definitions(self) -> int:
        """
        Get the number of model definitions.

        :return: Number of model definitions
        """
        return len(self._model_keys)

    def get_key(self, imodel: int) -> str:
        """
        Get the key of the model with the given index.

        :param imodel: Index of the model.
        :return: Key of the model with the given index.
        """
        return self._model_keys[self._model_ids[imodel]]

    def get_parameter(self, imodel: int, iparam: int) -> float:
        """
        Get the parameter with the given indices.

        :param imodel: Index of the model.
        :param iparam: Index of the parameter.
        :return: Parameter value.
        """
        return float(self._model_params[self._model_offsets[imodel] + iparam])

    def set_parameter(self, imodel: int, iparam: int, value: float) -> None:
        """
        Set the parameter with the given indices.

        :param imodel: Index of the model.
        :param iparam: Index of the parameter.
        :param value: New parameter value.
        """
        self._model_params[self._model_offsets[imodel] + iparam] = value

    def get_block_size(self) -> tuple[int, int, int]:
        """
        Get the local work size for running OpenCL kernels.

        :return: Local work size.
        """
        return self._block_size

    def set_block_size(self, block_size: tuple[int, int, int]) -> None:
        """
        Set the local work size for running OpenCL kernels.

        :param block_size: Local work size.
        """
        assert len(block_size) == 3
        self._block_size = (int(block_size[0]), int(block_size[1]), int(block_size[2]))

    @property
    def block_size(self) -> tuple[int, int, int]:
        """
        Local work size for running OpenCL kernels.
        """
        return self.get_block_size()

    @block_size.setter
    def block_size(self, block_size: tuple[int, int, int]) -> None:
        self.set_block_size(block_size)

    def adjust_work_size(self, Nz: int, Ny: int, Nx: int) -> tuple[int, int, int]:  # pylint: disable=invalid-name
        """
        Slightly increase the global work size to be a multiple of the local
        work size.

        :param Nz: Number of points in the z-dimension.
        :param Ny: Number of points in the y-dimension.
        :param Nx: Number of points in the x-dimension.
        :return: Adjusted global work size.
        """
        bz, by, bx = self.block_size
        return (
            (Nz + bz - 1) // bz * bz,
            (Ny + by - 1) // by * by,
            (Nx + bx - 1) // bx * bx,
        )

    def add(self, key: str, code: str, Nv: int, params: np.ndarray[Any, Any]) -> None:  # pylint: disable=invalid-name
        """
        Select and enable a model with given parameters.

        :param key: The key of the model to be added.
        :param code: OpenCL code for the model.
        :param Nv: Number of variables.
        :param params: Parameter values.
        """
        if key in self._model_keys:
            self._model_ids.append(self._model_keys.index(key))

        else:
            self._model_ids.append(len(self._model_keys))
            self.compile(code)
            self._model_keys.append(key)

        self._model_offsets.append(self._model_offsets[-1] + params.size)
        self._model_params.extend(params.tolist())

        self._Nv = max(self._Nv, Nv)

    def weights(
        self,
        dz: Any,
        dy: Any,
        dx: Any,
        mask: np.ndarray[Any, Any],
        diffusivity: np.ndarray[Any, Any],
    ) -> np.ndarray[Any, Any]:
        """
        Calculate the weights for the diffusion term in the reaction-diffusion
        equation.

        :param dz: The distance between points in the z-dimension.
        :param dy: The distance between points in the y-dimension.
        :param dx: The distance between points in the x-dimension.
        :param mask: 3D boolean array encoding which points are inside the medium.
        :param diffusivity: The diffusivity matrix.
        :return: Weight matrix for the diffusion term, A 5D array of shape (1, Nz, Ny, Nx, 19).
        """

        assert mask.ndim == 5
        assert mask.shape[0] == 1
        assert mask.shape[-1] == 1
        mask_np: np.ndarray[Any, Any] = np.ascontiguousarray(mask, dtype=Int)
        _, Nz, Ny, Nx, _ = mask_np.shape  # pylint: disable=invalid-name
        mask_cl = cl.Buffer(
            self.context,
            cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR,
            hostbuf=mask_np,
        )

        while diffusivity.ndim < 5:
            diffusivity = diffusivity[np.newaxis, ...]
        assert diffusivity.ndim == 5
        assert diffusivity.shape[0] == 1
        assert diffusivity.shape[-1] == 6
        diffusivity_np: np.ndarray[Any, Any] = np.ascontiguousarray(
            diffusivity, dtype=self.real
        )
        diffusivity_cl = cl.Buffer(
            self.context,
            cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR,
            hostbuf=diffusivity_np,
        )

        weights_np: np.ndarray[Any, Any] = np.zeros(
            (1, Nz, Ny, Nx, 19), dtype=self.real
        )
        weights_cl = cl.Buffer(
            self.context,
            cl.mem_flags.WRITE_ONLY,
            weights_np.nbytes,
        )

        self._kernels["calculate_weights"](
            self.queue,
            self.adjust_work_size(Nz, Ny, Nx),
            self.block_size,
            self.real(dz),
            self.real(dy),
            self.real(dx),
            mask_cl,
            idx(mask_np),
            diffusivity_cl,
            idx(diffusivity_np),
            weights_cl,
            idx(weights_np),
        )
        cl.enqueue_copy(self.queue, weights_np, weights_cl)

        self.queue.finish()

        return weights_np

    def run(
        self,
        inhom: np.ndarray[Any, Any],
        weights: np.ndarray[Any, Any],
        states: np.ndarray[Any, Any],
        stim_signal: np.ndarray[Any, Any],
        stim_shape: np.ndarray[Any, Any],
        Nt: Any,  # pylint: disable=invalid-name
        dt: Any,
    ) -> None:
        """
        Run a Pigreads simulation.

        :param inhom: A 3D array with integer values, encoding which model to use at each point. \
                Its value is zero for points outside the medium and one or more for points inside. \
                Values larger than zero are used to select one of multiple models: \
                1 for ``models[0]``, 2 for ``models[1]``, etc.
        :param weights: The weights for the diffusion term, see :py:func:`weights`.
        :param states: The initial states of the simulation, a 4D array of shape \
                (Nz, Ny, Nx, Nv).
        :param stim_signal: A 3D array with the stimulus signal at each time point \
                for all variables, with shape (Nt, Ns, Nv).
        :param stim_shape: A 4D array specifying the shape of the stimulus, \
                with shape (Ns, Nz, Ny, Nx).
        :param Nt: The number of time steps to run the simulation for.
        :param dt: The time step size.
        """

        assert dt > 0
        assert Nt > 0

        model_ids_np: np.ndarray[Any, Any] = np.array(self._model_ids, dtype=Size)
        model_ids_cl = cl.Buffer(
            self.context,
            cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR,
            hostbuf=model_ids_np,
        )

        model_offsets_np: np.ndarray[Any, Any] = np.array(
            self._model_offsets, dtype=Size
        )
        model_offsets_cl = cl.Buffer(
            self.context,
            cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR,
            hostbuf=model_offsets_np,
        )

        model_params_np: np.ndarray[Any, Any] = np.array(
            self._model_params, dtype=self.real
        )
        model_params_cl = cl.Buffer(
            self.context,
            cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR,
            hostbuf=model_params_np,
        )

        # in/output frame
        assert states.ndim == 4
        Nz, Ny, Nx, Nv = states.shape  # pylint: disable=invalid-name
        assert Nv == self.Nv

        # even and odd frames
        states_np: np.ndarray[Any, Any] = np.full(
            (2, *states.shape), np.nan, dtype=self.real
        )
        states_np[0, ...] = states
        states_cl = cl.Buffer(
            self.context,
            cl.mem_flags.READ_WRITE | cl.mem_flags.COPY_HOST_PTR,
            hostbuf=states_np,
        )

        weights_np: np.ndarray[Any, Any] = np.ascontiguousarray(
            weights, dtype=self.real
        )
        assert weights_np.ndim == 5
        assert weights_np.shape[0] == 1
        assert weights_np.shape[-1] == 19
        weights_cl = cl.Buffer(
            self.context,
            cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR,
            hostbuf=weights_np,
        )

        inhom_np: np.ndarray[Any, Any] = np.ascontiguousarray(inhom, dtype=Int)
        assert inhom_np.ndim == 4
        assert inhom_np.shape[-1] == 1
        inhom_cl = cl.Buffer(
            self.context,
            cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR,
            hostbuf=inhom_np,
        )

        stim_signal_np: np.ndarray[Any, Any] = np.ascontiguousarray(
            stim_signal, dtype=self.real
        )
        stim_shape_np: np.ndarray[Any, Any] = np.ascontiguousarray(
            stim_shape, dtype=self.real
        )

        if stim_signal_np.size > 0 and stim_shape_np.size > 0:
            assert stim_signal_np.ndim == 5
            assert stim_signal_np.shape[2] == 1
            assert stim_signal_np.shape[3] == 1
            assert stim_signal_np.shape[-1] == Nv

            assert stim_shape_np.ndim == 5
            assert stim_shape_np.shape[0] == stim_signal_np.shape[1]
            assert stim_shape_np.shape[-1] == 1

        if stim_shape_np.size == 0:
            stim_shape_np = np.ones(1, dtype=self.real).reshape((1, 1, 1, 1, 1))

        stim_shape_cl = cl.Buffer(
            self.context,
            cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR,
            hostbuf=stim_shape_np,
        )

        work_size = self.adjust_work_size(Nz, Ny, Nx)
        set_of_model_ids = set(self._model_ids)

        self._kernels["set_outside"](
            self.queue,
            work_size,
            self.block_size,
            self.real(np.nan),
            inhom_cl,
            idx(inhom_np),
            states_cl,
            idx(states_np),
        )

        for it in range(Nt):
            idx_old = idx(states_np, it=it)
            idx_new = idx(states_np, it=it + 1)

            for mid in set_of_model_ids:
                self._kernels[f"Model_{self._model_keys[mid]}_kernel"](
                    self.queue,
                    work_size,
                    self.block_size,
                    Size(len(self)),
                    model_ids_cl,
                    model_offsets_cl,
                    model_params_cl,
                    inhom_cl,
                    idx(inhom_np),
                    weights_cl,
                    idx(weights_np),
                    states_cl,
                    idx_old,
                    states_cl,
                    idx_new,
                    self.real(dt),
                )

            if stim_signal_np.size > 0 and stim_shape_np.size > 0:
                for istim in range(stim_signal_np.shape[1]):
                    stim_shape_idx = idx(stim_shape_np, it=istim)
                    for iv in range(Nv):
                        stim_amplitude = stim_signal_np[
                            it % stim_signal_np.shape[0], istim, 0, 0, iv
                        ]
                        if abs(stim_amplitude) > 1e-10:
                            idx_stim = idx(states_np, it=it + 1, iv=iv)
                            self._kernels["add_stimulus"](
                                self.queue,
                                work_size,
                                self.block_size,
                                self.real(dt * stim_amplitude),
                                stim_shape_cl,
                                stim_shape_idx,
                                states_cl,
                                idx_stim,
                            )

        for it in range(states_np.shape[0]):
            self._kernels["set_outside"](
                self.queue,
                work_size,
                self.block_size,
                self.real(np.nan),
                inhom_cl,
                idx(inhom_np),
                states_cl,
                idx(states_np, it=it),
            )

        cl.enqueue_copy(self.queue, states_np, states_cl)

        self.queue.finish()

        states[...] = states_np[Nt % states_np.shape[0], ...]


__all__ = ["Models"]
