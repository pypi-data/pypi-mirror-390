"""
Schema for stimulation protocols / source terms
-----------------------------------------------
"""

from __future__ import annotations

from typing import Any

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, field_validator

from pigreads.schema.setter import Setter, normalise_list_of_setters


class SignalStep(BaseModel):
    """
    Within a time interval, increase the value of variables by a given amounts.

    The start and duration of the signal are given in time units of the
    simulation. The variables are given as a dictionary with the variable names
    as keys and the amount to increase the variable by as values::

        start: 100 # ms
        duration: 10 # ms
        variables:
          u: 1
          v: 2

    The interval is defined mathematically as
    :math:`t \\in [\\text{start}, \\text{start} + \\text{duration})`.
    """

    start: float = Field(0.0, examples=[123.4, 248.0])
    "Starting time of the signal."
    duration: float = Field(0.0, examples=[1.0, 5.0])
    "Duration of the signal."
    variables: dict[str, float] = Field(
        default_factory=dict, examples=[{"u": 10.0, "v": 0.1}, {"u": 0.1}]
    )
    "Variables to modify and the amount to modify them by."
    model_config = ConfigDict(extra="forbid", use_attribute_docstrings=True)
    "Configuration for :py:class:`pydantic.BaseModel`."

    def __call__(
        self,
        signal: np.ndarray[Any, Any],
        times: np.ndarray[Any, Any],
        varidx: dict[str, int],
    ) -> np.ndarray[Any, Any]:
        """
        Modify the signal array.

        The signal array is modified in place to increase the values of the
        variables by the given amounts within the time interval.

        :param signal: Signal array to modify.
        :param times: Times of the signal steps.
        :param varidx: Mapping of variable names to indices in the signal array,
                       see :py:meth:`pigreads.schema.simulation.Simulation.varidx`.
        :return: Modified signal array.
        """
        mask = (self.start <= times) * (times < self.start + self.duration)
        for varname, value in dict(self.variables).items():
            signal[mask, varidx[varname]] += value
        return signal


class Stimulus(BaseModel):
    """
    A stimulus is a combination of a shape and a signal.

    The shape is defined by a list of :py:class:`pigreads.schema.setter.Setter`
    objects and defines where the stimulus is applied. The signal is defined by
    a list of :py:class:`SignalStep` objects and defines how the stimulus
    changes over time.
    """

    shape: list[Setter] = Field(default_factory=list)
    "Shape of the stimulus."
    signal: list[SignalStep] = Field(default_factory=list)
    "Signal of the stimulus."
    model_config = ConfigDict(extra="forbid", use_attribute_docstrings=True)
    "Configuration for :py:class:`pydantic.BaseModel`."

    @field_validator("shape", mode="before")
    @classmethod
    def normalise_shape(cls, shape: Any) -> Any:
        """
        Normalise the setters in the shape.

        See :py:func:`pigreads.schema.setter.normalise_list_of_setters` for details.

        :param shape: Any data to try to interpret.
        :return: Normalised data.
        """

        return normalise_list_of_setters(shape)


__all__ = [
    "SignalStep",
    "Stimulus",
]
