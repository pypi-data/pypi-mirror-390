"""Compose MoErgo default layouts from declarative specs."""

from __future__ import annotations

from copy import deepcopy
from typing import Dict

from glove80.base import LayerMap, build_layer_from_spec
from glove80.layouts.common import _assemble_layers, _attach_variant_metadata
from glove80.layouts.family import LayoutFamily, REGISTRY
from glove80.specs.primitives import materialize_sequence

from .specs import VARIANT_SPECS, VariantSpec


def _build_layers_map(spec: VariantSpec) -> LayerMap:
    return {name: build_layer_from_spec(layer_spec) for name, layer_spec in spec.layer_specs.items()}


class Family(LayoutFamily):
    name = "default"

    def variants(self) -> Dict[str, VariantSpec]:
        return dict(VARIANT_SPECS)

    def metadata_key(self) -> str:
        return "default"

    def build(self, variant: str) -> Dict:
        try:
            spec = VARIANT_SPECS[variant]
        except KeyError as exc:  # pragma: no cover
            raise KeyError(f"Unknown default layout '{variant}'. Available: {sorted(VARIANT_SPECS)}") from exc

        layout: Dict = deepcopy(spec.common_fields)
        layout["layer_names"] = list(spec.layer_names)
        layout["macros"] = []
        layout["holdTaps"] = []
        layout["combos"] = []
        layout["inputListeners"] = materialize_sequence(spec.input_listeners)

        layers = _build_layers_map(spec)
        layout["layers"] = _assemble_layers(layout["layer_names"], layers, variant=variant)

        _attach_variant_metadata(layout, variant=variant, layout_key=self.metadata_key())
        return layout


REGISTRY.register(Family())

__all__ = ["Family"]
