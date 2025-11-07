"""
Schema to define the diffusivity matrix
---------------------------------------
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from pydantic import BaseModel, ConfigDict, Field

from pigreads.schema.basic import Vector3D

# pylint: disable=import-outside-toplevel


class DiffusivityFile(BaseModel):
    """
    Diffusivity matrix read from a file.

    The file should contain a 4D array with the diffusivity values. The array
    should have shape ``(Nz, Ny, Nx, 6)`` where the last dimension corresponds to
    the six independent components of the diffusivity matrix.

    :see: :py:func:`pigreads.diffusivity.diffusivity_matrix`\
          and :py:mod:`numpy.lib.format`
    """

    file: Path = Field(..., examples=[Path("path/to/diffusivity.npy")])
    "Path to the file containing the diffusivity matrix."
    model_config = ConfigDict(extra="forbid", use_attribute_docstrings=True)
    "Configuration for :py:class:`pydantic.BaseModel`."

    def __call__(self) -> np.ndarray[Any, Any]:
        """
        Read the diffusivity matrix from the file.

        :return: Diffusivity matrix.
        """
        array: np.ndarray[Any, Any] = np.load(self.file)
        assert array.ndim == 4, "Diffusivity matrix should be 4D"
        assert array.shape[-1] == 6, "Diffusivity matrix should have 6 components"
        return array


class DiffusivityParams(BaseModel):
    """
    Diffusivity matrix defined by parameters.

    The parameters are passed on to :py:func:`pigreads.diffusivity.diffusivity_matrix`.
    """

    f: Vector3D | None = Field(None, examples=[Vector3D(x=0, y=0, z=0)])
    "Main direction of diffusion."
    n: Vector3D | None = Field(None, examples=[Vector3D(x=0, y=0, z=0)])
    "Direction of weakest diffusion."
    Df: float = Field(..., examples=[1.0, 0.1])
    "Diffusivity in the direction of the fibres."
    Ds: float | None = Field(None, examples=[1.0, 0.1, None])
    "Diffusivity in the fibre sheets."
    Dn: float | None = Field(None, examples=[1.0, 0.1, None])
    "Diffusivity in the direction normal to the fibre sheets."
    model_config = ConfigDict(extra="forbid", use_attribute_docstrings=True)
    "Configuration for :py:class:`pydantic.BaseModel`."

    def __call__(self) -> np.ndarray[Any, Any]:
        """
        Create the diffusivity matrix from the parameters.

        :return: Diffusivity matrix.
        """
        from pigreads import diffusivity_matrix

        kwargs: dict[str, Any] = {"Df": self.Df, "Ds": self.Ds, "Dn": self.Dn}
        if self.f is not None:
            kwargs["f"] = self.f.tuple
        if self.n is not None:
            kwargs["n"] = self.n.tuple
        return diffusivity_matrix(**kwargs)


Diffusivity = DiffusivityFile | DiffusivityParams
"""
The diffusivity matrix is a command to define the diffusivity matrix in the
simulation.

One of:

- :py:class:`DiffusivityFile`
- :py:class:`DiffusivityParams`
"""

__all__ = [
    "Diffusivity",
    "DiffusivityFile",
    "DiffusivityParams",
]
