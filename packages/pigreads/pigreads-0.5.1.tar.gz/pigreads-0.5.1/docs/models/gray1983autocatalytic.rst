.. AUTOMATICALLY GENERATED FILE!
.. Edit the templates ``*.jinja``, the header files ``*.cl``, or the model
.. definitions in ``models/`` instead, then run the ``prepare.py``
.. script in the main directory.


Gray & Scott 1982
=================

**Key:** ``gray1983autocatalytic``

One of the two variable reaction-diffusion models presented in the article
"Autocatalytic reactions in the isothermal, continuous stirred tank
reactor: isolas and other forms of multistability". Depending on the
parameters, different patterns can be seen to form in its solutions.

It describes the chemical reactions:

.. math::

  U + 2V &\to 3V
  \\
  V &\to P

- ``u``, ``v``: concentrations of :math:`U`, :math:`V`.
- ``k``: rate of conversion of :math:`V` to :math:`P`.
- ``f``: rate of the process that feeds :math:`U` and
  drains :math:`U`, :math:`V`, and :math:`P`.

References
----------

1. https://doi.org/10.1016/0009-2509(83)80132-8

Variables
---------

0. ``u = 1.0``
1. ``v = 0.0``

Parameters
----------

- ``diffusivity_u = 1``
- ``diffusivity_v = 0.5``
- ``f = 0.055``
- ``k = 0.062``

Source code
-----------
.. raw:: html

    <details>
    <summary>OpenCL kernel</summary>

.. code-block:: c

    const Real uvv = u * v * v;
    const Real U = -uvv + f * (1 - u);
    const Real V = uvv - (f + k) * v;

    *_new_u = u + dt * (U + _diffuse_u);
    *_new_v = v + dt * (V + _diffuse_v);

.. raw:: html

    </details>

Additional metadata
-------------------

.. code-block:: yaml

    keywords:
    - pattern formation
