"""
Schema for model definitions
----------------------------
"""

from __future__ import annotations

from collections.abc import MutableMapping
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ModelEntry(BaseModel):
    """
    A model entry chooses a model by its key and which parameters to use.

    :see: :py:class:`pigreads.models.Models` and :py:class:`ModelDefinition`
    """

    key: str = Field(..., examples=["author2025title", "aliev1996simple", "trivial"])
    "The key of the model."
    parameters: MutableMapping[str, float] = Field(
        default_factory=dict, examples=[{"a": 0.2, "diffusivity_u": 1.2}, {}]
    )
    "The parameters of the model."
    model_config = ConfigDict(extra="forbid", use_attribute_docstrings=True)
    "Configuration for :py:class:`pydantic.BaseModel`."

    @model_validator(mode="before")
    @classmethod
    def normalise(cls, values: Any) -> Any:
        """
        Normalise the model entry.

        If the entry is a string, it is converted to a dictionary with an empty
        parameter set. If the entry is a dictionary with a single key, the key
        is used as the model key.

        :param values: Any data to try to interpret.
        :return: Normalised data.
        """

        assert isinstance(values, dict)

        key = values.get("key")
        if "key" in values:
            del values["key"]

        parameters = values.get("parameters", {})
        if "parameters" in values:
            del values["parameters"]

        if key is None:
            assert len(values) == 1

            key, parameters = next(iter(values.items()))
            return {"key": key, "parameters": parameters or {}}

        parameters = {**parameters, **values}

        return {"key": key, "parameters": parameters or {}}


class ModelDefinition(BaseModel):
    """
    Definition of a so-called model, i.e., the reaction-term.

    Note: Additional fields are allowed stored in :py:attr:`meta`.

    :see: :py:class:`pigreads.models.Models` and :py:class:`ModelEntry`
    """

    name: str = Field(..., examples=["author2025title", "aliev1996simple", "trivial"])
    "Human readable name of the model, usually the authors and the year."
    description: str = Field(
        ..., examples=["This two-variable model was created by modifying the model..."]
    )
    "A simple description of the model, what it was designed for, and its unique features."
    dois: list[str] = Field(
        default_factory=list,
        examples=[
            ["https://doi.org/10.0000/foobar0123"],
            [
                "https://doi.org/10.1016/j.jtbi.2008.03.029",
                "https://doi.org/10.1063/1.166311",
                "https://doi.org/10.1161/01.RES.82.11.1206",
                "https://doi.org/10.1152/ajpheart.00794.2003",
            ],
        ],
    )
    "List of digital object identifiers in URL form, i.e., starting with ``https://doi.org/10``."
    variables: dict[str, float] = Field(
        default_factory=dict, examples=[{"u": 0.0, "v": 1.0}]
    )
    "Model variable names and their resting/initial values."
    diffusivity: dict[str, float] = Field(default_factory=dict, examples=[{"u": 1.0}])
    "Dictionary that maps the names of variables to diffuse to their diffusivity."
    parameters: dict[str, float] = Field(
        default_factory=dict,
        examples=[{"eps0": 0.002, "mu1": 0.2, "mu2": 0.3, "a": 0.15, "k": 8.0}],
    )
    "Model parameter names and their default values."
    code: str = Field(..., examples=["*_new_u = u + dt * _diffuse_u;"])
    "Source code of the forward Euler step in OpenCL."
    model_config = ConfigDict(extra="allow", use_attribute_docstrings=True)
    "Configuration for :py:class:`pydantic.BaseModel`."

    @property
    def meta(self) -> dict[str, Any] | None:
        """
        Read-only view of additional fields, i.e., metadata.
        """
        return self.model_extra

    @property
    def all_parameters(self) -> dict[str, float]:
        "Dictionary of parameters including the diffusivities."
        return {
            **{
                "diffusivity_" + varname: value
                for varname, value in self.diffusivity.items()
            },
            **self.parameters,
        }

    def __call__(self, **parameters: float) -> dict[str, float]:
        """
        Merge diffusivities, default parameters, and given parameters.

        :param parameters: Additional parameters.
        :return: Merged parameter dictionary.
        """
        return {**self.all_parameters, **parameters}


__all__ = [
    "ModelDefinition",
    "ModelEntry",
]
