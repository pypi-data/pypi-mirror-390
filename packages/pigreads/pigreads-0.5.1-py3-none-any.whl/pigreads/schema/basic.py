"""
Schema for some basic data types
--------------------------------
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class Vector3D(BaseModel):
    """
    Vector in three dimensions in space.
    """

    x: float = Field(0, examples=[0.1, 1.0, -0.1])
    "Value in x direction."
    y: float = Field(0, examples=[0.1, 1.0, -0.1])
    "Value in y direction."
    z: float = Field(0, examples=[0.1, 1.0, -0.1])
    "Value in z direction."
    model_config = ConfigDict(extra="forbid", use_attribute_docstrings=True)
    "Configuration for :py:class:`pydantic.BaseModel`."

    @property
    def tuple(self) -> tuple[float, float, float]:
        """
        Representation as a tuple (x, y, z).
        """
        return self.x, self.y, self.z


class Slice(BaseModel):
    """
    Slice of an array.

    :see: :py:class:`slice`
    """

    axis: int = Field(-1, examples=[-1, 0, 3])
    "Axis to slice in."
    start: int | None = Field(None, examples=[4, -1, None])
    "Start index of the slice."
    end: int | None = Field(None, examples=[-2, 4, -1, None])
    "End index of the slice."
    step: int | None = Field(None, examples=[1, 2, -1, None])
    "Index step of the slice."
    model_config = ConfigDict(extra="forbid", use_attribute_docstrings=True)
    "Configuration for :py:class:`pydantic.BaseModel`."

    def __call__(self) -> slice:
        """
        Return a slice object.

        :return: Slice object.
        :see: :py:class:`slice`
        """
        return slice(self.start, self.end, self.step)


__all__ = [
    "Slice",
    "Vector3D",
]
