.. AUTOMATICALLY GENERATED FILE!
.. Edit the templates ``*.jinja``, the header files ``*.cl``, or the model
.. definitions in ``models/`` instead, then run the ``prepare.py``
.. script in the main directory.


Marcotte & Grigoriev 2017
=========================

**Key:** ``marcotte2017dynamical``

Smoothed version of the Karma model as published by Marcotte & Grigoriev in 2017.
In it, a single spiral wave breaks up into spiral wave chaos due to amplification
of the alternans instability. It can be used as a model of the transition from
tachycardia to fibrillation.

References
----------

1. https://doi.org/10.1063/1.5003259
2. https://doi.org/10.1063/1.4915143
3. https://doi.org/10.1103/PhysRevLett.71.1103
4. https://doi.org/10.1063/1.166024

Variables
---------

0. ``u = 0.0``
1. ``v = 0.0``

Parameters
----------

- ``diffusivity_u = 1.0``
- ``diffusivity_v = 0.05``
- ``beta = 1.389``
- ``eps = 0.01``
- ``ustar = 1.5415``

Source code
-----------
.. raw:: html

    <details>
    <summary>OpenCL kernel</summary>

.. code-block:: c

    const Real e = exp(2. * (1.2571 * (u - 1.)));
    const Real V = eps * (beta * ((1. + (e - 1.) / (e + 1.)) / 2.) + (1. + (exp(2. * (1.2571 * (v - 1.))) - 1.) / (exp(2. * (1.2571 * (v - 1.))) + 1.)) / 2. * (v - 1.) - v);
    const Real U = (ustar - v * v * v * v) * (1. - (exp(2. * (u - 3.)) - 1.) / (exp(2. * (u - 3.)) + 1.)) * u * u / 2. - u;
    *_new_u = u + dt * (U + _diffuse_u);
    *_new_v = v + dt * (V + _diffuse_v);

.. raw:: html

    </details>

Additional metadata
-------------------

.. code-block:: yaml

    keywords:
    - excitable media
    - electrophysiology
    - heart
    - phenomenological
