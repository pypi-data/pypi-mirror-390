.. AUTOMATICALLY GENERATED FILE!
.. Edit the templates ``*.jinja``, the header files ``*.cl``, or the model
.. definitions in ``models/`` instead, then run the ``prepare.py``
.. script in the main directory.


Barkley 1991
============

**Key:** ``barkley1991model``

This early phenomenological model of excitable media is one of the
simplest models describing both excitation and recovery enabling
spiral waves.

References
----------

1. https://doi.org/10.1016/0167-2789(91)90194-E

Variables
---------

0. ``u = 0.0``
1. ``v = 0.0``

Parameters
----------

- ``diffusivity_u = 1.0``
- ``diffusivity_v = 0.0``
- ``a = 0.75``
- ``b = 0.02``
- ``eps = 0.02``

Source code
-----------
.. raw:: html

    <details>
    <summary>OpenCL kernel</summary>

.. code-block:: c

    const Real _react_u = u*(1 - u)*(u - (v + b)/a)/eps;
    const Real _react_v = u - v;
    *_new_u = u + dt * (_react_u + _diffuse_u);
    *_new_v = v + dt * (_react_v + _diffuse_v);

.. raw:: html

    </details>

Additional metadata
-------------------

.. code-block:: yaml

    keywords:
    - excitable media
    - phenomenological
