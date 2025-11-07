.. AUTOMATICALLY GENERATED FILE!
.. Edit the templates ``*.jinja``, the header files ``*.cl``, or the model
.. definitions in ``models/`` instead, then run the ``prepare.py``
.. script in the main directory.


Models
======

A so-called model defines the reaction term of the reaction
diffusion equation. While Pigreads comes with a variety of
pre-defined models, it is also easily possible to define a
model.

Defining a model
----------------

A model can be defined by adding it to the dictionary of available
models::

    import pigreads as pig
    from pigreads.schema.model import ModelDefinition

    pig.Models.available["fitzhugh1961impulses"] = ModelDefinition(
        name="FitzHugh 1961 & Nagumo 1962",
        description="A 2D simplification of the Hodgkin-Huxley model.",
        dois=[
            "https://doi.org/10.1016/S0006-3495(61)86902-6",
            "https://doi.org/10.1109/JRPROC.1962.288235",
        ],
        variables={"u": 1.2, "v": -0.625},
        diffusivity={"u": 1.0},
        parameters={"a": 0.7, "b": 0.8, "c": 3.0, "z": 0.0},
        code="""
            *_new_u = u + dt * (v + u - u*u*u/3 + z + _diffuse_u);
            *_new_v = v + dt * (-(u - a + b*v)/c);
        """,
    )

The definition must adhere to the schema in :py:class:`pigreads.schema.model.ModelDefinition`.

Pre-defined models
------------------

.. toctree::
    :maxdepth: 1
    :hidden:

    aliev1996simple
    barkley1991model
    beeler1977reconstruction
    bueno2008minimal
    courtemanche1998ionic
    fenton1998vortex
    gray1983autocatalytic
    hodgkin1952quantitative
    kabus2024fast
    luo1991model
    luo1994dynamic
    majumder2016mathematical
    maleckar2008mathematical
    marcotte2017dynamical
    mitchell2003two
    nygren1998mathematical
    paci2013computational
    tentusscher2006alternans
    tomek2019development
    trivial

.. csv-table::
    :header: Name, Key, Variables, Parameters

    ":doc:`Aliev & Panfilov 1996 <aliev1996simple>`", "``aliev1996simple``", 2, 5
    ":doc:`Barkley 1991 <barkley1991model>`", "``barkley1991model``", 2, 3
    ":doc:`Beeler & Reuter 1977 <beeler1977reconstruction>`", "``beeler1977reconstruction``", 8, 5
    ":doc:`Bueno-Orovio et al. 2008 <bueno2008minimal>`", "``bueno2008minimal``", 4, 28
    ":doc:`Courtemanche et al. 1998 <courtemanche1998ionic>`", "``courtemanche1998ionic``", 21, 44
    ":doc:`Fenton & Karma 1998 <fenton1998vortex>`", "``fenton1998vortex``", 3, 17
    ":doc:`Gray & Scott 1982 <gray1983autocatalytic>`", "``gray1983autocatalytic``", 2, 2
    ":doc:`Hodgkin & Huxley 1952 <hodgkin1952quantitative>`", "``hodgkin1952quantitative``", 4, 11
    ":doc:`Kabus et al. 2024 <kabus2024fast>`", "``kabus2024fast``", 3, 12
    ":doc:`Luo & Rudy 1991 <luo1991model>`", "``luo1991model``", 8, 25
    ":doc:`Luo & Rudy 1994 <luo1994dynamic>`", "``luo1994dynamic``", 12, 57
    ":doc:`Majumder et al. 2016 <majumder2016mathematical>`", "``majumder2016mathematical``", 27, 76
    ":doc:`Maleckar et al. 2008 <maleckar2008mathematical>`", "``maleckar2008mathematical``", 30, 47
    ":doc:`Marcotte & Grigoriev 2017 <marcotte2017dynamical>`", "``marcotte2017dynamical``", 2, 3
    ":doc:`Mitchell & Schaeffer 2003 <mitchell2003two>`", "``mitchell2003two``", 2, 5
    ":doc:`Nygren et al. 1998 <nygren1998mathematical>`", "``nygren1998mathematical``", 29, 46
    ":doc:`Paci et al. 2013 <paci2013computational>`", "``paci2013computational``", 18, 57
    ":doc:`Ten Tusscher et al. 2006 <tentusscher2006alternans>`", "``tentusscher2006alternans``", 19, 56
    ":doc:`Tomek et al. 2019 <tomek2019development>`", "``tomek2019development``", 43, 158
    ":doc:`Trivial model <trivial>`", "``trivial``", 1, 0