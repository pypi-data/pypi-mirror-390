"""Layer specs for Glorious Engrammer."""

from __future__ import annotations

from glove80.base import LayerMap, LayerSpec, build_layer_from_spec

from .alpha_layers import ALPHA_LAYER_SPECS
from .finger_layers import FINGER_LAYER_SPECS
from .utility_layers import UTILITY_LAYER_SPECS
from .mouse_layers import MOUSE_LAYER_SPECS

LAYER_SPEC_GROUPS = (
    ALPHA_LAYER_SPECS,
    FINGER_LAYER_SPECS,
    UTILITY_LAYER_SPECS,
    MOUSE_LAYER_SPECS,
)


def _merge_specs() -> dict[str, LayerSpec]:
    specs: dict[str, LayerSpec] = {}
    for group in LAYER_SPEC_GROUPS:
        overlap = set(specs).intersection(group)
        if overlap:  # pragma: no cover
            raise ValueError(f"Duplicate layer specs: {sorted(overlap)}")
        specs.update(group)
    return specs


LAYER_SPECS = _merge_specs()


def build_all_layers(variant: str) -> LayerMap:  # noqa: ARG001
    return {name: build_layer_from_spec(spec) for name, spec in LAYER_SPECS.items()}


__all__ = ["LAYER_SPECS", "build_all_layers"]
