.. AUTOMATICALLY GENERATED FILE!
.. Edit the templates ``*.jinja``, the header files ``*.cl``, or the model
.. definitions in ``models/`` instead, then run the ``prepare.py``
.. script in the main directory.


Luo & Rudy 1991
===============

**Key:** ``luo1991model``

This model is a significant update of the Beeler-Reuter mammalian ventricular
model (1977), and like the Beeler-Reuter model, the Luo-Rudy I model uses
Hodgkin-Huxley type equations to calculate ionic currents.

References
----------

1. https://doi.org/10.1161/01.res.68.6.1501

Variables
---------

0. ``V = -84.3801107371``
1. ``m = 0.00171338077730188``
2. ``h = 0.982660523699656``
3. ``j = 0.989108212766685``
4. ``d = 0.00302126301779861``
5. ``f = 0.999967936476325``
6. ``X = 0.0417603108167287``
7. ``Cai = 0.00017948816388306``

Parameters
----------

- ``diffusivity_V = 1.0``
- ``background_current_E_b = -59.87``
- ``background_current_g_b = 0.03921``
- ``environment_time = 0.0``
- ``ionic_concentrations_Ki = 145.0``
- ``ionic_concentrations_Ko = 5.4``
- ``ionic_concentrations_Nai = 18.0``
- ``ionic_concentrations_Nao = 140.0``
- ``membrane_C = 1.0``
- ``membrane_F = 96484.6``
- ``membrane_R = 8314.0``
- ``membrane_T = 310.0``
- ``membrane_stim_amplitude = -25.5``
- ``membrane_stim_duration = 2.0``
- ``membrane_stim_end = 9000.0``
- ``membrane_stim_period = 1000.0``
- ``membrane_stim_start = 100.0``
- ``fast_sodium_current_E_Na = 54.79446393509185``
- ``fast_sodium_current_g_Na = 23.0``
- ``time_dependent_potassium_current_PR_NaK = 0.01833``
- ``time_dependent_potassium_current_g_K = 0.282``
- ``time_dependent_potassium_current_E_K = -77.56758438531939``
- ``time_independent_potassium_current_E_K1 = -87.8929017138025``
- ``time_independent_potassium_current_g_K1 = 0.6047``
- ``plateau_potassium_current_E_Kp = -87.8929017138025``
- ``plateau_potassium_current_g_Kp = 0.0183``

Source code
-----------
.. raw:: html

    <details>
    <summary>OpenCL kernel</summary>

.. code-block:: c

    // background_current
    const Real background_current_i_b = background_current_g_b * (V - background_current_E_b);

    // fast_sodium_current_h_gate
    const Real fast_sodium_current_h_gate_alpha_h = ((V < -40.0) ? 0.135 * exp((80.0 + V) / -6.8) : 0.0);
    const Real fast_sodium_current_h_gate_beta_h = ((V < -40.0) ? 3.56 * exp(0.079 * V) + 310000.0 * exp(0.35 * V) : 1.0 / ((fabs(0.13 * (1.0 + exp((V + 10.66) / -11.1))) < VERY_SMALL_NUMBER) ? ((0.13 * (1.0 + exp((V + 10.66) / -11.1)) < 0.0) ? -VERY_SMALL_NUMBER : VERY_SMALL_NUMBER) : 0.13 * (1.0 + exp((V + 10.66) / -11.1))));
    *_new_h = h + dt*(fast_sodium_current_h_gate_alpha_h * (1.0 - h) - fast_sodium_current_h_gate_beta_h * h);

    // fast_sodium_current_j_gate
    const Real fast_sodium_current_j_gate_alpha_j = ((V < -40.0) ? (-127140.0 * exp(0.2444 * V) - 3.474e-05 * exp(-0.04391 * V)) * (V + 37.78) / ((fabs(1.0 + exp(0.311 * (V + 79.23))) < VERY_SMALL_NUMBER) ? ((1.0 + exp(0.311 * (V + 79.23)) < 0.0) ? -VERY_SMALL_NUMBER : VERY_SMALL_NUMBER) : 1.0 + exp(0.311 * (V + 79.23))) : 0.0);
    const Real fast_sodium_current_j_gate_beta_j = ((V < -40.0) ? 0.1212 * exp(-0.01052 * V) / ((fabs(1.0 + exp(-0.1378 * (V + 40.14))) < VERY_SMALL_NUMBER) ? ((1.0 + exp(-0.1378 * (V + 40.14)) < 0.0) ? -VERY_SMALL_NUMBER : VERY_SMALL_NUMBER) : 1.0 + exp(-0.1378 * (V + 40.14))) : 0.3 * exp(-2.535e-07 * V) / ((fabs(1.0 + exp(-0.1 * (V + 32.0))) < VERY_SMALL_NUMBER) ? ((1.0 + exp(-0.1 * (V + 32.0)) < 0.0) ? -VERY_SMALL_NUMBER : VERY_SMALL_NUMBER) : 1.0 + exp(-0.1 * (V + 32.0))));
    *_new_j = j + dt*(fast_sodium_current_j_gate_alpha_j * (1.0 - j) - fast_sodium_current_j_gate_beta_j * j);

    // fast_sodium_current_m_gate
    const Real fast_sodium_current_m_gate_alpha_m = 0.32 * (V + 47.13) / ((fabs(1.0 - exp(-0.1 * (V + 47.13))) < VERY_SMALL_NUMBER) ? ((1.0 - exp(-0.1 * (V + 47.13)) < 0.0) ? -VERY_SMALL_NUMBER : VERY_SMALL_NUMBER) : 1.0 - exp(-0.1 * (V + 47.13)));
    const Real fast_sodium_current_m_gate_beta_m = 0.08 * exp(-V / 11.0);
    *_new_m = m + dt*(fast_sodium_current_m_gate_alpha_m * (1.0 - m) - fast_sodium_current_m_gate_beta_m * m);

    // slow_inward_current
    const Real slow_inward_current_E_si = 7.7 - 13.0287 * log(Cai / 1.0);
    const Real slow_inward_current_i_si = 0.09 * d * f * (V - slow_inward_current_E_si);

    // slow_inward_current_d_gate
    const Real slow_inward_current_d_gate_alpha_d = 0.095 * exp(-0.01 * (V - 5.0)) / ((fabs(1.0 + exp(-0.072 * (V - 5.0))) < VERY_SMALL_NUMBER) ? ((1.0 + exp(-0.072 * (V - 5.0)) < 0.0) ? -VERY_SMALL_NUMBER : VERY_SMALL_NUMBER) : 1.0 + exp(-0.072 * (V - 5.0)));
    const Real slow_inward_current_d_gate_beta_d = 0.07 * exp(-0.017 * (V + 44.0)) / ((fabs(1.0 + exp(0.05 * (V + 44.0))) < VERY_SMALL_NUMBER) ? ((1.0 + exp(0.05 * (V + 44.0)) < 0.0) ? -VERY_SMALL_NUMBER : VERY_SMALL_NUMBER) : 1.0 + exp(0.05 * (V + 44.0)));
    *_new_d = d + dt*(slow_inward_current_d_gate_alpha_d * (1.0 - d) - slow_inward_current_d_gate_beta_d * d);

    // slow_inward_current_f_gate
    const Real slow_inward_current_f_gate_alpha_f = 0.012 * exp(-0.008 * (V + 28.0)) / ((fabs(1.0 + exp(0.15 * (V + 28.0))) < VERY_SMALL_NUMBER) ? ((1.0 + exp(0.15 * (V + 28.0)) < 0.0) ? -VERY_SMALL_NUMBER : VERY_SMALL_NUMBER) : 1.0 + exp(0.15 * (V + 28.0)));
    const Real slow_inward_current_f_gate_beta_f = 0.0065 * exp(-0.02 * (V + 30.0)) / ((fabs(1.0 + exp(-0.2 * (V + 30.0))) < VERY_SMALL_NUMBER) ? ((1.0 + exp(-0.2 * (V + 30.0)) < 0.0) ? -VERY_SMALL_NUMBER : VERY_SMALL_NUMBER) : 1.0 + exp(-0.2 * (V + 30.0)));
    *_new_f = f + dt*(slow_inward_current_f_gate_alpha_f * (1.0 - f) - slow_inward_current_f_gate_beta_f * f);

    // time_dependent_potassium_current_X_gate
    const Real time_dependent_potassium_current_X_gate_alpha_X = 0.0005 * exp(0.083 * (V + 50.0)) / ((fabs(1.0 + exp(0.057 * (V + 50.0))) < VERY_SMALL_NUMBER) ? ((1.0 + exp(0.057 * (V + 50.0)) < 0.0) ? -VERY_SMALL_NUMBER : VERY_SMALL_NUMBER) : 1.0 + exp(0.057 * (V + 50.0)));
    const Real time_dependent_potassium_current_X_gate_beta_X = 0.0013 * exp(-0.06 * (V + 20.0)) / ((fabs(1.0 + exp(-0.04 * (V + 20.0))) < VERY_SMALL_NUMBER) ? ((1.0 + exp(-0.04 * (V + 20.0)) < 0.0) ? -VERY_SMALL_NUMBER : VERY_SMALL_NUMBER) : 1.0 + exp(-0.04 * (V + 20.0)));
    *_new_X = X + dt*(time_dependent_potassium_current_X_gate_alpha_X * (1.0 - X) - time_dependent_potassium_current_X_gate_beta_X * X);

    // time_dependent_potassium_current_Xi_gate
    const Real time_dependent_potassium_current_Xi_gate_Xi = ((V > -100.0) ? 2.837 * (exp(0.04 * (V + 77.0)) - 1.0) / ((fabs((V + 77.0) * exp(0.04 * (V + 35.0))) < VERY_SMALL_NUMBER) ? (((V + 77.0) * exp(0.04 * (V + 35.0)) < 0.0) ? -VERY_SMALL_NUMBER : VERY_SMALL_NUMBER) : (V + 77.0) * exp(0.04 * (V + 35.0))) : 1.0);

    // intracellular_calcium_concentration
    *_new_Cai = Cai + dt*(-0.0001 / 1.0 * slow_inward_current_i_si + 0.07 * (0.0001 - Cai));

    // membrane
    const Real membrane_I_stim = ((((environment_time >= membrane_stim_start) && (environment_time <= membrane_stim_end)) && (environment_time - membrane_stim_start - floor((environment_time - membrane_stim_start) / membrane_stim_period) * membrane_stim_period <= membrane_stim_duration)) ? membrane_stim_amplitude : 0.0);

    // fast_sodium_current
    const Real fast_sodium_current_i_Na = fast_sodium_current_g_Na * pow(m, 3.0) * h * j * (V - fast_sodium_current_E_Na);

    // time_dependent_potassium_current
    const Real time_dependent_potassium_current_i_K = time_dependent_potassium_current_g_K * X * time_dependent_potassium_current_Xi_gate_Xi * (V - time_dependent_potassium_current_E_K);

    // time_independent_potassium_current_K1_gate
    const Real time_independent_potassium_current_K1_gate_alpha_K1 = 1.02 / ((fabs(1.0 + exp(0.2385 * (V - time_independent_potassium_current_E_K1 - 59.215))) < VERY_SMALL_NUMBER) ? ((1.0 + exp(0.2385 * (V - time_independent_potassium_current_E_K1 - 59.215)) < 0.0) ? -VERY_SMALL_NUMBER : VERY_SMALL_NUMBER) : 1.0 + exp(0.2385 * (V - time_independent_potassium_current_E_K1 - 59.215)));
    const Real time_independent_potassium_current_K1_gate_beta_K1 = (0.49124 * exp(0.08032 * (V + 5.476 - time_independent_potassium_current_E_K1)) + 1.0 * exp(0.06175 * (V - (time_independent_potassium_current_E_K1 + 594.31)))) / ((fabs(1.0 + exp(-0.5143 * (V - time_independent_potassium_current_E_K1 + 4.753))) < VERY_SMALL_NUMBER) ? ((1.0 + exp(-0.5143 * (V - time_independent_potassium_current_E_K1 + 4.753)) < 0.0) ? -VERY_SMALL_NUMBER : VERY_SMALL_NUMBER) : 1.0 + exp(-0.5143 * (V - time_independent_potassium_current_E_K1 + 4.753)));
    const Real time_independent_potassium_current_K1_gate_K1_infinity = time_independent_potassium_current_K1_gate_alpha_K1 / ((fabs(time_independent_potassium_current_K1_gate_alpha_K1 + time_independent_potassium_current_K1_gate_beta_K1) < VERY_SMALL_NUMBER) ? ((time_independent_potassium_current_K1_gate_alpha_K1 + time_independent_potassium_current_K1_gate_beta_K1 < 0.0) ? -VERY_SMALL_NUMBER : VERY_SMALL_NUMBER) : time_independent_potassium_current_K1_gate_alpha_K1 + time_independent_potassium_current_K1_gate_beta_K1);

    // plateau_potassium_current
    const Real plateau_potassium_current_Kp = 1.0 / ((fabs(1.0 + exp((7.488 - V) / 5.98)) < VERY_SMALL_NUMBER) ? ((1.0 + exp((7.488 - V) / 5.98) < 0.0) ? -VERY_SMALL_NUMBER : VERY_SMALL_NUMBER) : 1.0 + exp((7.488 - V) / 5.98));
    const Real plateau_potassium_current_i_Kp = plateau_potassium_current_g_Kp * plateau_potassium_current_Kp * (V - plateau_potassium_current_E_Kp);

    // *remaining*
    const Real time_independent_potassium_current_i_K1 = time_independent_potassium_current_g_K1 * time_independent_potassium_current_K1_gate_K1_infinity * (V - time_independent_potassium_current_E_K1);
    *_new_V = V + dt*(-1.0 / membrane_C * (membrane_I_stim + fast_sodium_current_i_Na + slow_inward_current_i_si + time_dependent_potassium_current_i_K + time_independent_potassium_current_i_K1 + plateau_potassium_current_i_Kp + background_current_i_b) + _diffuse_V);
.. raw:: html

    </details>

Additional metadata
-------------------

.. code-block:: yaml

    keywords:
    - excitable media
    - electrophysiology
    - heart
    - human
    - ventricle
