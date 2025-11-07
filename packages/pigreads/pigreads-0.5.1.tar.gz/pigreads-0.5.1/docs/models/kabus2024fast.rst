.. AUTOMATICALLY GENERATED FILE!
.. Edit the templates ``*.jinja``, the header files ``*.cl``, or the model
.. definitions in ``models/`` instead, then run the ``prepare.py``
.. script in the main directory.


Kabus et al. 2024
=================

**Key:** ``kabus2024fast``

This data-driven model was trained on optical voltage mapping data
of human conditionally immortalised atrial myocyte (hiAM) monolayers.
It uses a simple polynomial, a standard-deviation-based approximation for the
gradient, and an exponential moving average to predict the updated value
of the signal. As it can work with much higher time steps, it is computationally
cheaper than the reaction-diffusion based models.

References
----------

1. https://doi.org/10.1016/j.compbiomed.2024.107949

Variables
---------

0. ``u = 0.02``
1. ``a = 0.1``
2. ``g = 0.0``

Parameters
----------

- ``umin = -0.5``
- ``umax = 1.25``
- ``alpha = 0.008``
- ``dist = 8``
- ``wagu = -0.413919278037366``
- ``wgu = 0.193407562922741``
- ``wau = 0.0263083048287399``
- ``wa = 0.00109492883763741``
- ``wag = -0.318420911707539``
- ``wg = 0.153524735108221``
- ``wu = -0.0141740647636319``
- ``w = -0.00448181394403335``

Source code
-----------
.. raw:: html

    <details>
    <summary>OpenCL kernel</summary>

.. code-block:: c

    const Real f = wagu*a*g*u + wag*a*g + wau*a*u + wa*a + wgu*g*u + wg*g + wu*u + w;

    *_new_u = u + dt * f;

    if(*_new_u < umin) { *_new_u = umin; }
    if(*_new_u > umax) { *_new_u = umax; }

    const Real alpha_= alpha/dt;
    *_new_a = alpha_*(*_new_u) + (1 - alpha_)*a;

    const Int dist_ = dist + 0.5;
    Size sum0 = 0;
    Real sum1 = 0;
    Real sum2 = 0;
    for(Int iy=-dist_; iy<=dist_; iy++) {
      for(Int ix=-dist_; ix<=dist_; ix++) {
        if((iy*iy + ix*ix) <= dist*dist) {
          const Real u_ = _r(_x(ix, _y(iy, states_old)));
          if(isfinite(u_)) {
            sum0 += 1;
            sum1 += u_;
            sum2 += u_*u_;
          }
        }
      }
    }
    if(sum0 > 0) {
      const Real avg = sum1/sum0;
      const Real var = sum2/sum0 - avg*avg;
      *_new_g = sqrt(var > 0.0 ? var : 0.0);
    } else {
      *_new_g = 0.0;
    }

.. raw:: html

    </details>

Additional metadata
-------------------

.. code-block:: yaml

    keywords:
    - excitable media
    - electrophysiology
    - heart
    - data-driven
    parameter sets:
      aliev1996simple:
        umin: 0.0
        umax: 1.0
        alpha: 0.03
        dist: 5
        wagu: -0.22407
        wag: -0.82589
        wau: 0.0054601
        wa: 0.021655
        wgu: 0.31082
        wg: 0.23077
        wu: -0.0081478
        w: -0.009711
      optical:
        umin: -0.5
        umax: 1.25
        alpha: 0.008
        dist: 8
        wagu: -0.413919278037366
        wgu: 0.193407562922741
        wau: 0.0263083048287399
        wa: 0.00109492883763741
        wag: -0.318420911707539
        wg: 0.153524735108221
        wu: -0.0141740647636319
        w: -0.00448181394403335
