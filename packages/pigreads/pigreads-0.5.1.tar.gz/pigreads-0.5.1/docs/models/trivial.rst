.. AUTOMATICALLY GENERATED FILE!
.. Edit the templates ``*.jinja``, the header files ``*.cl``, or the model
.. definitions in ``models/`` instead, then run the ``prepare.py``
.. script in the main directory.


Trivial model
=============

**Key:** ``trivial``

This model encodes only diffusion, with a zero reaction term.



Variables
---------

0. ``u = 0.0``

Parameters
----------

- ``diffusivity_u = 1.0``

Source code
-----------
.. raw:: html

    <details>
    <summary>OpenCL kernel</summary>

.. code-block:: c

    *_new_u = u + dt * _diffuse_u;

.. raw:: html

    </details>

Additional metadata
-------------------

.. code-block:: yaml

    keywords:
    - diffusion
