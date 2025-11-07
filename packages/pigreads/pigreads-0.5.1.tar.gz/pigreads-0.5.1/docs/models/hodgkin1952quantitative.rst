.. AUTOMATICALLY GENERATED FILE!
.. Edit the templates ``*.jinja``, the header files ``*.cl``, or the model
.. definitions in ``models/`` instead, then run the ``prepare.py``
.. script in the main directory.


Hodgkin & Huxley 1952
=====================

**Key:** ``hodgkin1952quantitative``

This model describes the electrical conduction in giant nerve fibre of
squids. It is one of the first mathematical models of electrophysiology.

References
----------

1. https://doi.org/10.1113/jphysiol.1952.sp004764

Variables
---------

0. ``V = -75.0``
1. ``n = 0.317``
2. ``m = 0.05``
3. ``h = 0.595``

Parameters
----------

- ``diffusivity_V = 1.0``
- ``engine_pace = 0.0``
- ``engine_time = 0.0``
- ``leak_Eleak = -64.387``
- ``leak_g_max = 0.3``
- ``potassium_Ek = -87.0``
- ``potassium_g_max = 36.0``
- ``sodium_ENa = 40.0``
- ``sodium_g_max = 120.0``
- ``membrane_A = 100.0``
- ``membrane_C = 1.0``
- ``membrane_Vhold = -60.0``

Source code
-----------
.. raw:: html

    <details>
    <summary>OpenCL kernel</summary>

.. code-block:: c

    // leak
    const Real leak_i = leak_g_max * (V - leak_Eleak);

    // potassium
    const Real potassium_n_a = 0.01 * (-V - 65.0) / ((fabs(exp((-V - 65.0) / 10.0) - 1.0) < VERY_SMALL_NUMBER) ? ((exp((-V - 65.0) / 10.0) - 1.0 < 0.0) ? -VERY_SMALL_NUMBER : VERY_SMALL_NUMBER) : exp((-V - 65.0) / 10.0) - 1.0);
    const Real potassium_n_b = 0.125 * exp((-V - 75.0) / 80.0);
    *_new_n = n + dt*(potassium_n_a * (1.0 - n) - potassium_n_b * n);
    const Real potassium_i = potassium_g_max * pow(n, 4.0) * (V - potassium_Ek);

    // sodium
    const Real sodium_h_a = 0.07 * exp((-V - 75.0) / 20.0);
    const Real sodium_h_b = 1.0 / ((fabs(exp((-V - 45.0) / 10.0) + 1.0) < VERY_SMALL_NUMBER) ? ((exp((-V - 45.0) / 10.0) + 1.0 < 0.0) ? -VERY_SMALL_NUMBER : VERY_SMALL_NUMBER) : exp((-V - 45.0) / 10.0) + 1.0);
    *_new_h = h + dt*(sodium_h_a * (1.0 - h) - sodium_h_b * h);
    const Real sodium_m_a = 0.1 * (-V - 50.0) / ((fabs(exp((-V - 50.0) / 10.0) - 1.0) < VERY_SMALL_NUMBER) ? ((exp((-V - 50.0) / 10.0) - 1.0 < 0.0) ? -VERY_SMALL_NUMBER : VERY_SMALL_NUMBER) : exp((-V - 50.0) / 10.0) - 1.0);
    const Real sodium_m_b = 4.0 * exp((-V - 75.0) / 18.0);
    *_new_m = m + dt*(sodium_m_a * (1.0 - m) - sodium_m_b * m);
    const Real sodium_i = sodium_g_max * pow(m, 3.0) * h * (V - sodium_ENa);

    // membrane
    const Real membrane_i_stim = (V - membrane_Vhold) * membrane_A * engine_pace;
    *_new_V = V + dt*(-(1.0 / membrane_C) * (sodium_i + potassium_i + leak_i + membrane_i_stim) + _diffuse_V);
.. raw:: html

    </details>

Additional metadata
-------------------

.. code-block:: yaml

    keywords:
    - excitable media
    - electrophysiology
    - squid
