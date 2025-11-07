#!/bin/env python3
"""
Define a model and run a simulation.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

import pigreads as pig
from pigreads.schema.model import ModelDefinition

pig.Models.available["fitzhugh1961impulses"] = ModelDefinition(
    name="FitzHugh 1961 & Nagumo 1962",
    description="A 2D simplification of the Hodgkin-Huxley model.",
    dois=[
        "https://doi.org/10.1016/S0006-3495(61)86902-6",
        "https://doi.org/10.1109/JRPROC.1962.288235",
    ],
    variables={"u": 1.2, "v": -0.625},
    diffusivity={"u": 1.0},
    parameters={"a": 0.7, "b": 0.8, "c": 3.0, "z": 0.0},
    code="""
        *_new_u = u + dt * (v + u - u*u*u/3 + z + _diffuse_u);
        *_new_v = v + dt * (-(u - a + b*v)/c);
    """,
)


def main():
    R = 10
    z, y, x = np.mgrid[0:1, 0:1, -R:R:200j]
    dz, dy, dx = pig.deltas(z, y, x)
    r = np.linalg.norm((x, y, z), axis=0)

    inhom = np.ones_like(x, dtype=int)
    inhom[r >= R] = 0

    models = pig.Models()
    models.add("fitzhugh1961impulses", z=-0.4)

    states = models.resting_states(inhom, Nframes=100)
    states[0, x < -8, 0] = -1

    diffusivity = pig.diffusivity_matrix(Df=1.0)

    weights = pig.weights(dz, dy, dx, inhom, diffusivity)

    Nt = 100
    dt = 0.004
    for it in tqdm(range(states.shape[0] - 1)):
        states[it + 1] = pig.run(models, inhom, weights, states[it], Nt=Nt, dt=dt)

        if it > 0:
            assert np.all(np.isfinite(states[it + 1][np.isfinite(states[it])])), (
                "New NaN values found!"
            )

    plt.imshow(
        states[:, 0, 0, :, 0].T,
        extent=(0, (states.shape[0] - 1) * Nt * dt, x[0, 0, 0], x[0, 0, -1]),
        origin="lower",
    )
    plt.colorbar()
    plt.show()


if __name__ == "__main__":
    main()
