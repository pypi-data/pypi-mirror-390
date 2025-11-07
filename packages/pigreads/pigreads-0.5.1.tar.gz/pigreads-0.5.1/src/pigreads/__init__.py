# Pigreads: Python-integrated GPU-enabled reaction-diffusion solver
# Copyright (c) 2024 Desmond Kabus. All rights reserved.

"""
Pigreads Python module
----------------------

This Python module is the main interface to set up and run Pigreads simulations
solving the reaction-diffusion equations with OpenCL and NumPy:

.. math::

    \\partial_t \\underline{u}
    =
    \\underline{P} \\nabla \\cdot \\mathbf D \\nabla \\underline{u}
    +
    \\underline{r}(\\underline{u})

for :math:`\\underline{u}(t, \\mathbf x)`, :math:`t\\in[0, T]`, and
:math:`\\mathbf x\\in\\Omega\\subset\\mathbb R^3`, with initial conditions and
no-flux boundary conditions.

The following equations define a simpler example with only two variables,
:math:`\\underline{u} = (u, v)`, with no diffusion in :math:`v`, and
homogeneous and isotropic diffusion:

.. math::

    \\begin{aligned}
    \\partial_t u
    &=
    D \\nabla^2 u
    +
    r_u(u, v)
    \\\\
    \\partial_t v
    &=
    r_v(u, v)
    \\end{aligned}

Pigreads performs the most expensive calculations on graphics cards
using OpenCL, see :py:func:`pigreads.models.Models.run`
and :py:func:`pigreads.models.Models.weights`.
Input and output as well as setting up and interacting with the simulation
should be done in Python, with the exception of adding source terms, so-called
stimulus currents. Pigreads uses the simplistic finite-differences method and
forward-Euler time stepping.

A Pigreads simulation is usually defined in the following steps:
First, define the geometry of the medium. In this example, we use a 2D plane
with 200 points in both x and y::

    import pigreads as pig
    import numpy as np

    R = 10.
    z, y, x = np.mgrid[0:1, -R:R:200j, -R:R:200j]
    dz, dy, dx = pig.deltas(z, y, x)
    r = np.linalg.norm((x, y, z), axis=0)

Pigreads is optimised for three-dimensional space. For
lower-dimensional simulations, set the number of points in additional
dimensions to one, as done above for the z-dimension.

Calculations are performed at all points with periodic boundary conditions.
The integer field ``inhom`` defines which points are inside (1) the medium and outside (0)::

    inhom = np.ones_like(x, dtype=int)
    inhom[r >= R] = 0

Values of inhom larger than zero can be used to select one of multiple models,
i.e., reaction terms :math:`\\underline{r}`. For an ``inhom`` value of 1,
``models[0]`` is used; and ``models[1]`` for a value of 2, etc. One or more of the
available models can be selected using an instance of
the :py:class:`pigreads.models.Models` class::

    models = pig.Models()
    models.add("marcotte2017dynamical", beta=1.389)

This class also has a function to create an array of the same shape as ``inhom``
in space but for a given number of frames in time. The first frame is filled
with the appropriate resting values for each model. Initial conditions can then
be set in the 0th frame::

    states = models.resting_states(inhom, Nframes=100)
    states[0, x < -8, 0] = 1
    states[0, y < 0, 1] = 2

Note that states has five indices, in this order: time, z, y, x, state variable.
This indexing is consistently used in Pigreads and NumPy.

The calculation of the diffusion term :math:`\\underline{P} \\nabla \\cdot
\\mathbf D \\nabla \\underline{u}` is implemented as a weighted sum of neighbouring points.
The weights can be calculated using the function
:py:func:`pigreads.models.Models.weights`, which also requires the
diffusivity_matrix :math:`D` as input, which is set using
:py:func:`pigreads.diffusivity.diffusivity_matrix`::

    diffusivity = pig.diffusivity_matrix(Df=0.03)
    weights = pig.weights(dz, dy, dx, inhom, diffusivity)

Finally, the simulation can be started using :py:func:`pigreads.models.Models.run`,
which does ``Nt`` forward-Euler steps and only returns the final states after those steps::

    Nt = 200
    dt = 0.025
    for it in range(states.shape[0] - 1):
        states[it + 1] = models.run(inhom, weights, states[it], Nt=Nt, dt=dt)

The 5D array states can now be analysed and visualised, for instance with Matplotlib::

    import matplotlib.pyplot as plt
    plt.imshow(states[-1, 0, :, :, 0])
    plt.show()

Full examples with more sophisticated plotting outputting an MP4 movie, a
progress bar, and stability checks can be found in the ``examples`` folder in
the Git repository of this project.
"""

from __future__ import annotations

from pigreads._version import version as __version__
from pigreads.compat import run, weights
from pigreads.diffusivity import diffusivity_matrix
from pigreads.helper import (
    delta,
    deltas,
    get_upper_triangle,
    normalise_vector,
    prepare_array,
    to_ithildin,
)
from pigreads.models import Models
from pigreads.schema.model import ModelDefinition

__all__ = [
    "ModelDefinition",
    "Models",
    "__version__",
    "delta",
    "deltas",
    "diffusivity_matrix",
    "get_upper_triangle",
    "normalise_vector",
    "prepare_array",
    "run",
    "to_ithildin",
    "weights",
]
