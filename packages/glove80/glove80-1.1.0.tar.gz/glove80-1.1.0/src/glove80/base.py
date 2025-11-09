"""Shared helpers for layer generation."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, List, Sequence

Layer = List[Dict[str, Any]]
LayerMap = Dict[str, Layer]


@dataclass(frozen=True)
class LayerRef:
    """Reference to a layer by name (resolved at layout build time)."""

    name: str


@dataclass(frozen=True)
class KeySpec:
    """Declarative spec for a single key in a layer."""

    value: Any
    params: Sequence[Any] = ()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "params": [_coerce_param(param) for param in self.params],
        }


@dataclass(frozen=True)
class LayerSpec:
    """Sparse layer representation."""

    overrides: Dict[int, KeySpec]
    length: int = 80
    default: KeySpec = KeySpec("&trans")

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


def _coerce_param(param: Any) -> Dict[str, Any]:
    if isinstance(param, KeySpec):
        return param.to_dict()
    if isinstance(param, LayerRef):
        raise TypeError("LayerRef must be resolved before serializing")
    if isinstance(param, dict):
        return deepcopy(param)
    if isinstance(param, (str, int)):
        return {"value": param, "params": []}
    raise TypeError(f"Unsupported param type: {type(param)!r}")  # pragma: no cover


PatchSpec = Dict[int, KeySpec]


def resolve_layer_refs(obj: Any, resolver: Dict[str, int]) -> Any:
    """Replace LayerRef placeholders recursively using the provided mapping."""

    if isinstance(obj, LayerRef):
        try:
            return resolver[obj.name]
        except KeyError as exc:  # pragma: no cover
            raise KeyError(f"Unknown layer reference '{obj.name}'") from exc
    if isinstance(obj, list):
        return [resolve_layer_refs(item, resolver) for item in obj]
    if isinstance(obj, dict):
        return {key: resolve_layer_refs(value, resolver) for key, value in obj.items()}
    return obj
