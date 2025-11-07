"""
Diffusivity
-----------
"""

from __future__ import annotations

from typing import Any

import numpy as np

from pigreads.helper import get_upper_triangle, normalise_vector


def diffusivity_matrix(
    f: np.ndarray[Any, Any] | list[int] | tuple[int, int, int] | None = None,
    n: np.ndarray[Any, Any] | list[int] | tuple[int, int, int] | None = None,
    Df: np.ndarray[Any, Any] | float = 1.0,  # pylint: disable=invalid-name
    Ds: np.ndarray[Any, Any] | float | None = None,  # pylint: disable=invalid-name
    Dn: np.ndarray[Any, Any] | float | None = None,  # pylint: disable=invalid-name
    dtype: type = np.single,
) -> np.ndarray[Any, Any]:
    """
    Define a diffusivity matrix :math:`\\textbf D` for the reaction-diffusion equation.

    If ``f`` and ``n`` are given, the matrix is defined as:

    .. math::

        \\textbf D = \\textbf D_s \\textbf I + (\\textbf D_f - \\textbf D_s)
        \\textbf f \\textbf f^\\mathrm{T} + (\\textbf D_n - \\textbf D_s)
        \\textbf n \\textbf n^\\mathrm{T}

    :param f: The main direction of diffusion, i.e., the fibre direction. \
            3D vector over space with shape (Nz, Ny, Nx, 3). The last index \
            contains three elements: the x, y, and z component of the vector. \
            Optional if :math:`D_f=D_s=D_n`.
    :param n: The direction of weakest diffusion, i.e., the direction normal to \
            the fibre sheets. A 3D vector over space with shape (Nz, Ny, Nx, 3). The \
            last index contains three elements: the x, y, and z component of the \
            vector. Optional if :math:`D_s=D_n`.
    :param Df: The diffusivity in the direction of the fibres, :math:`\\mathbf{f}`.
    :param Ds: The diffusivity in the fibre sheets, but normal to :math:`\\mathbf{f}`. \
            If ``None``, :math:`D_s` is set to :math:`D_f`.
    :param Dn: The diffusivity in the direction normal to the fibre sheets, \
            i.e., along :math:`\\mathbf{n}`. \
            If ``None``, :math:`D_n` is set to :math:`D_s`.
    :param dtype: Data type of the arrays, i.e., single or double precision floating point numbers.
    :return: A 4D array with shape (Nz, Ny, Nx, 6).

    See also :py:func:`pigreads.helper.get_upper_triangle` for the convention used for the
    last axis of the output array.
    """

    if Ds is None:
        Ds = Df

    if Dn is None:
        Dn = Ds

    if f is None:
        assert np.allclose(Df, Ds), "If Df!=Ds, f must be given"
        f = [0, 0, 0]

    if n is None:
        assert np.allclose(Ds, Dn), "If Ds!=Dn, n must be given"
        n = [0, 0, 0]

    f = normalise_vector(f, dtype=dtype)
    n = normalise_vector(n, dtype=dtype)
    eye: np.ndarray = np.eye(3, dtype=dtype)
    eye.shape = (1, 1, 1, 3, 3)

    D = get_upper_triangle(  # pylint: disable=invalid-name
        np.einsum("...,...ij->...ij", Ds, eye)
        + np.einsum("...,...ij,...ji->...ij", Df - Ds, f, f)
        + np.einsum("...,...ij,...ji->...ij", Dn - Ds, n, n)
    )
    assert D.ndim == 4
    assert D.shape[-1] == 6
    return D


__all__ = [
    "diffusivity_matrix",
]
