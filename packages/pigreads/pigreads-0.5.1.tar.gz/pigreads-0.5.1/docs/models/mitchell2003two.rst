.. AUTOMATICALLY GENERATED FILE!
.. Edit the templates ``*.jinja``, the header files ``*.cl``, or the model
.. definitions in ``models/`` instead, then run the ``prepare.py``
.. script in the main directory.


Mitchell & Schaeffer 2003
=========================

**Key:** ``mitchell2003two``

A model for electrical activity of cardiac membrane which incorporates only
an inward and an outward current. This model is useful for three reasons: (1)
Its simplicity, comparable to the FitzHugh-Nagumo model, makes it useful in
numerical simulations, especially in two or three spatial dimensions where
numerical efficiency is so important. (2) It can be understood analytically
without recourse to numerical simulations. This allows us to determine rather
completely how the parameters in the model affect its behavior which in turn
provides insight into the effects of the many parameters in more realistic
models. (3) It naturally gives rise to a one-dimensional map which specifies
the action potential duration as a function of the previous diastolic interval.
For certain parameter values, this map exhibits a new phenomenon--subcritical
alternans--that does not occur for the commonly used exponential map.

References
----------

1. https://doi.org/10.1016/S0092-8240(03)00041-7

Variables
---------

0. ``V = 0.0``
1. ``h = 0.9``

Parameters
----------

- ``diffusivity_V = 1.0``
- ``V_gate = 0.13``
- ``tau_in = 0.3``
- ``tau_out = 6.0``
- ``tau_open = 120.0``
- ``tau_close = 150.0``

Source code
-----------
.. raw:: html

    <details>
    <summary>OpenCL kernel</summary>

.. code-block:: c

    const Real J_in = h * (V*V * (1.0 - V)) / tau_in;
    const Real J_out = -V / tau_out;
    *_new_h = h + dt*(((V < V_gate) ? (1.0 - h) / tau_open : -h / tau_close));
    *_new_V = V + dt*(J_in + J_out + _diffuse_V);

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
