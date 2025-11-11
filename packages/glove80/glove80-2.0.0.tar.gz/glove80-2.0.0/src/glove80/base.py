"""Shared helpers for layer generation."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from pydantic import ConfigDict, field_validator, model_validator
from pydantic.dataclasses import dataclass as pydantic_dataclass

from .keycodes import KnownKeyName, is_known_key_name

Layer = list[dict[str, Any]]
LayerMap = dict[str, Layer]


@pydantic_dataclass(config=ConfigDict(frozen=True))
class LayerRef:
    """Reference to a layer by name (resolved at layout build time)."""

    name: str


KeyParamTuple = tuple["KeySpec", ...]


@pydantic_dataclass(config=ConfigDict(frozen=True))
class KeySpec:
    """Declarative spec for a single key in a layer."""

    value: KnownKeyName | str | int | LayerRef
    params: KeyParamTuple = ()

    @field_validator("value")
    @classmethod
    def _validate_value(cls, value: Any) -> Any:
        if isinstance(value, str) and not value.startswith("&"):
            if not is_known_key_name(value):
                msg = f"Unknown key name '{value}'"
                raise ValueError(msg)
            return value
        return value

    def to_dict(self) -> dict[str, Any]:
        return {
            "value": self.value,
            "params": [_coerce_param(param) for param in self.params],
        }


@pydantic_dataclass(config=ConfigDict(frozen=True))
class LayerSpec:
    """Sparse layer representation."""

    overrides: dict[int, KeySpec]
    length: int = 80
    default: KeySpec = KeySpec("&trans")

    @model_validator(mode="after")
    def _validate_overrides(self) -> LayerSpec:
        if not self.overrides:
            return self
        upper_bound = self.length - 1
        normalized: dict[int, KeySpec] = {}
        for raw_index, spec in self.overrides.items():
            index = self._coerce_override_index(raw_index)
            if index < 0 or index > upper_bound:
                msg = f"Override index {index} is outside the valid range 0-{upper_bound}"
                raise ValueError(msg)
            normalized[index] = spec
        object.__setattr__(self, "overrides", normalized)
        return self

    @staticmethod
    def _coerce_override_index(raw_index: Any) -> int:
        if isinstance(raw_index, bool):
            msg = "Override indices must be integers, not bools"
            raise TypeError(msg)
        if isinstance(raw_index, int):
            return raw_index
        if isinstance(raw_index, str):
            try:
                return int(raw_index, 10)
            except ValueError as exc:  # pragma: no cover
                msg = f"Override index '{raw_index}' is not an integer string"
                raise TypeError(msg) from exc
        if isinstance(raw_index, float):
            if raw_index.is_integer():
                return int(raw_index)
            msg = f"Override index {raw_index} has a fractional component"  # pragma: no cover
            raise TypeError(msg)  # pragma: no cover
        msg = f"Unsupported override index type: {type(raw_index).__name__}"  # pragma: no cover
        raise TypeError(msg)  # pragma: no cover

    def to_layer(self) -> Layer:
        layer = [self.default.to_dict() for _ in range(self.length)]
        for index, spec in self.overrides.items():
            layer[index] = spec.to_dict()
        return layer


def copy_layer(layer: Layer) -> Layer:
    return deepcopy(layer)


def copy_layers_map(layers: LayerMap) -> LayerMap:
    return {name: deepcopy(layer) for name, layer in layers.items()}


def apply_patch(layer: Layer, patch: PatchSpec) -> None:
    for index, spec in patch.items():
        layer[index] = spec.to_dict()


def apply_patch_if(layer: Layer, condition: bool, patch: PatchSpec) -> None:
    if condition:
        apply_patch(layer, patch)


def build_layer_from_spec(spec: LayerSpec) -> Layer:
    return spec.to_layer()


def _coerce_param(param: Any) -> dict[str, Any]:
    if isinstance(param, KeySpec):
        return param.to_dict()
    if isinstance(param, LayerRef):  # pragma: no cover
        msg = "LayerRef must be resolved before serializing"
        raise TypeError(msg)
    if isinstance(param, dict):
        return deepcopy(param)
    if isinstance(param, (str, int)):
        return {"value": param, "params": []}
    msg = f"Unsupported param type: {type(param)!r}"  # pragma: no cover
    raise TypeError(msg)  # pragma: no cover


PatchSpec = dict[int, KeySpec]


def resolve_layer_refs(obj: Any, resolver: dict[str, int]) -> Any:
    """Replace LayerRef placeholders recursively using the provided mapping."""
    if isinstance(obj, LayerRef):
        try:
            return resolver[obj.name]
        except KeyError as exc:  # pragma: no cover
            msg = f"Unknown layer reference '{obj.name}'"
            raise KeyError(msg) from exc
    if isinstance(obj, list):
        return [resolve_layer_refs(item, resolver) for item in obj]
    if isinstance(obj, dict):
        return {key: resolve_layer_refs(value, resolver) for key, value in obj.items()}
    return obj
