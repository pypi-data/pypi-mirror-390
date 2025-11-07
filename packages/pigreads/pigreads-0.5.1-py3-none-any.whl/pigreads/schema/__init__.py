"""
Schema to define simulations
----------------------------

This submodule provides a Pydantic schema defining a simulation. The schema is
used to read and write simulation configuration files in JSON or YAML format.

See :py:class:`pigreads.schema.simulation.Simulation` for the main schema.
"""

from __future__ import annotations

from pigreads.schema.basic import Slice, Vector3D
from pigreads.schema.diffusivity import Diffusivity, DiffusivityFile, DiffusivityParams
from pigreads.schema.model import ModelDefinition, ModelEntry
from pigreads.schema.setter import Setter, SetterFile
from pigreads.schema.simulation import Simulation
from pigreads.schema.stimulus import SignalStep, Stimulus

__all__ = [
    "Diffusivity",
    "DiffusivityFile",
    "DiffusivityParams",
    "ModelDefinition",
    "ModelEntry",
    "Setter",
    "SetterFile",
    "SignalStep",
    "Simulation",
    "Slice",
    "Stimulus",
    "Vector3D",
]
