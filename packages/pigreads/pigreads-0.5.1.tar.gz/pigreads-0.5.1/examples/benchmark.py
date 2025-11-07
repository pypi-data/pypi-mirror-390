#!/bin/env python3
"""
Run the Niederer benchmark using Pigreads.

https://doi.org/10.1098/rsta.2011.0139
"""

from __future__ import annotations

import warnings

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

import pigreads as pig
from pigreads.plot import movie


def main():
    framedur = 1.0  # ms
    dt = 0.01  # ms {0.005, 0.01, 0.05}
    Nt = int(framedur / dt + 0.5)

    dz = dy = dx = 0.2  # mm {0.1, 0.2, 0.5}
    Lz, Ly, Lx = 3, 7, 20  # mm
    z, y, x = np.meshgrid(
        *[
            d * np.arange(1 + round(L / d))
            for d, L in zip([dz, dy, dx], [Lz, Ly, Lx], strict=True)
        ],
        indexing="ij",
    )
    assert dz == z[1, 0, 0]
    assert dy == y[0, 1, 0]
    assert dx == x[0, 0, 1]
    assert Lz == z[-1, 0, 0]
    assert Ly == y[0, -1, 0]
    assert Lx == x[0, 0, -1]

    inhom = np.ones_like(x, dtype=int)
    inhom[-1] = 0
    inhom[:, -1] = 0
    inhom[:, :, -1] = 0

    # constants
    C_m = 0.01  # µF/mm² (membrane capacitance)
    chi = 140  # 1/mm (surface-to-volume ratio)

    # diffusivities intra/extra longitudinal/transversal
    scale = 1 / (chi * C_m)  # mm³/µF
    Dif = scale * 0.17  # mm²/ms
    Dis = scale * 0.019  # mm²/ms
    Def = scale * 0.62  # mm²/ms
    Des = scale * 0.24  # mm²/ms

    # diffusivities longitudinal/transversal
    Df = Dif * Def / (Dif + Def)  # mm²/ms
    Ds = Dis * Des / (Dis + Des)  # mm²/ms

    # stimulus current
    I_stim = 50.0  # mA/cm³ (stimulus current)
    i_stim = I_stim * scale  # mV/ms

    models = pig.Models()
    models.add("tentusscher2006alternans", diffusivity_V=Df)
    diffusivity = pig.diffusivity_matrix(Df=1, Ds=Ds / Df, f=[1, 0, 0])
    weights = models.weights(dz, dy, dx, inhom, diffusivity)

    states = models.resting_states(inhom, Nframes=100)

    stim_shape = (x < 1.5) & (y < 1.5) & (z < 1.5)
    stim_signal = np.zeros((Nt, states.shape[-1]))
    stim_signal[:, 0] = i_stim

    for ifr in tqdm(range(states.shape[0] - 1)):
        states[ifr + 1] = models.run(
            inhom,
            weights,
            states[ifr],
            stim_signal=stim_signal if ifr <= 2 else None,
            stim_shape=stim_shape if ifr <= 2 else None,
            Nt=Nt,
            dt=dt,
        )

        if ifr > 0 and not np.all(
            np.isfinite(states[ifr + 1][np.isfinite(states[ifr])])
        ):
            with warnings.catch_warnings():
                warnings.simplefilter("always")
                warnings.warn("New NaN values found!", stacklevel=2)

    # plot data with Matplotlib
    plt.imshow(states[-1, states.shape[1] // 2, :, :, 0])
    plt.colorbar()
    plt.show()

    # create a movie using FFmpeg
    movie(
        "benchmark.mp4",
        states[:, states.shape[1] // 2, :-1, :-1, 0],
        progress="bar",
        parallel=1,
        tlables=[f"frame {ifr}" for ifr in range(states.shape[0])],
        extent=(x[0, 0, 0], x[0, 0, -2], y[0, 0, 0], y[0, -2, 0]),
        vmin=-100,
        vmax=30,
    )


if __name__ == "__main__":
    main()
