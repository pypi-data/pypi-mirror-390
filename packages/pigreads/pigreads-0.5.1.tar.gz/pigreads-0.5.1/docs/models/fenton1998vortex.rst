.. AUTOMATICALLY GENERATED FILE!
.. Edit the templates ``*.jinja``, the header files ``*.cl``, or the model
.. definitions in ``models/`` instead, then run the ``prepare.py``
.. script in the main directory.


Fenton & Karma 1998
===================

**Key:** ``fenton1998vortex``

A simplified ionic model with three membrane currents that approximates well
the restitution properties and spiral wave behavior of more complex ionic
models of cardiac action potential (Beeler-Reuter and others)

The transmembrane potential can be found using the relation:
``Vm = V_0 + u * (V_fi - V_0)``.

References
----------

1. https://doi.org/10.1063/1.166311

Variables
---------

0. ``u = 0.0``
1. ``v = 1.0``
2. ``w = 1.0``

Parameters
----------

- ``diffusivity_u = 1.0``
- ``Cm = 1.0``
- ``V_0 = -85.0``
- ``V_fi = 15.0``
- ``g_fi_max = 4.0``
- ``k = 10.0``
- ``tau_0 = 12.5``
- ``tau_d = 0.25``
- ``tau_r = 33.33``
- ``tau_si = 29.0``
- ``tau_v1m = 1250.0``
- ``tau_v2m = 19.6``
- ``tau_vp = 3.33``
- ``tau_wm = 41.0``
- ``tau_wp = 870.0``
- ``u_c = 0.13``
- ``u_csi = 0.85``
- ``u_v = 0.04``

Source code
-----------
.. raw:: html

    <details>
    <summary>OpenCL kernel</summary>

.. code-block:: c

    const Real p = u >= u_c;
    const Real q = u >= u_v;
    const Real tau_vm = q * tau_v1m + (1.0 - q) * tau_v2m;
    const Real J_fi = -v * p * (1.0 - u) * (u - u_c) / tau_d;
    const Real J_si = -w * (1.0 + (exp(2.0 * k * (u - u_csi)) - 1.0) / (exp(2.0 * k * (u - u_csi)) + 1.0)) / (2.0 * tau_si);
    const Real J_so = u * (1.0 - p) / tau_0 + p / tau_r;
    *_new_u = u + dt*(_diffuse_u - (J_fi + J_so + J_si));
    *_new_v = v + dt*((1.0 - p) * (1.0 - v) / tau_vm - p * v / tau_vp);
    *_new_w = w + dt*((1.0 - p) * (1.0 - w) / tau_wm - p * w / tau_wp);

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
    parameter sets:
      Beeler Reuter:
        Cm: 1.0
        V_0: -85.0
        V_fi: 15.0
        g_fi_max: 4.0
        k: 10.0
        tau_0: 12.5
        tau_d: 0.25
        tau_r: 33.33
        tau_si: 29.0
        tau_v1m: 1250.0
        tau_v2m: 19.6
        tau_vp: 3.33
        tau_wm: 41.0
        tau_wp: 870.0
        u_c: 0.13
        u_csi: 0.85
        u_v: 0.04
      Modified Beeler Reuter:
        Cm: 1.0
        V_0: -85.0
        V_fi: 15.0
        g_fi_max: 4.0
        k: 10.0
        tau_0: 8.3
        tau_d: 0.25
        tau_r: 50.0
        tau_si: 44.84
        tau_v1m: 1000.0
        tau_v2m: 19.2
        tau_vp: 3.33
        tau_wm: 11.0
        tau_wp: 667.0
        u_c: 0.13
        u_csi: 0.85
        u_v: 0.055
      Girouard:
        Cm: 1.0
        V_0: -85.0
        V_fi: 15.0
        g_fi_max: 8.7
        k: 10.0
        tau_0: 12.5
        tau_d: 0.1149425287356322
        tau_r: 25.0
        tau_si: 22.22
        tau_v1m: 333.0
        tau_v2m: 40.0
        tau_vp: 10.0
        tau_wm: 65.0
        tau_wp: 1000.0
        u_c: 0.13
        u_csi: 0.85
        u_v: 0.025
      Luo Rudy:
        Cm: 1.0
        V_0: -85.0
        V_fi: 15.0
        g_fi_max: 5.8
        k: 10.0
        tau_0: 12.5
        tau_d: 0.1724137931034483
        tau_r: 130.0
        tau_si: 127.0
        tau_v1m: 18.2
        tau_v2m: 18.2
        tau_vp: 10.0
        tau_wm: 80.0
        tau_wp: 1020.0
        u_c: 0.13
        u_csi: 0.85
        u_v: 0.0
