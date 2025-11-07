.. AUTOMATICALLY GENERATED FILE!
.. Edit the templates ``*.jinja``, the header files ``*.cl``, or the model
.. definitions in ``models/`` instead, then run the ``prepare.py``
.. script in the main directory.


Aliev & Panfilov 1996
=====================

**Key:** ``aliev1996simple``

This simple two-variable model was created by modifying the model by FitzHugh
& Nagumo to describe cardiac excitation waves. It models restitution of
action potential duration, i.e., its dependence on cycle length. It was
originally designed for canine ventricles, but is considered a
phenomenological model.

References
----------

1. https://doi.org/10.1016/0960-0779(95)00089-5

Variables
---------

0. ``u = 0.0``
1. ``v = 0.0``

Parameters
----------

- ``diffusivity_u = 1.0``
- ``eps0 = 0.002``
- ``mu1 = 0.2``
- ``mu2 = 0.3``
- ``a = 0.15``
- ``k = 8.0``

Source code
-----------
.. raw:: html

    <details>
    <summary>OpenCL kernel</summary>

.. code-block:: c

    const Real eps = eps0 + mu1 * v / (u + mu2);
    const Real _react_u = -k * u * (u - a) * (u - 1.0) - u * v;
    const Real _react_v = eps * (-v - k * u * (u - a - 1.0));
    *_new_u = u + dt * (_react_u + _diffuse_u);
    *_new_v = v + dt * _react_v;

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
