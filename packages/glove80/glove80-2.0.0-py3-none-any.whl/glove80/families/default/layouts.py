"""Compose MoErgo default layouts from declarative specs."""

from __future__ import annotations

from glove80.base import LayerMap, build_layer_from_spec
from glove80.layouts import LayoutBuilder
from glove80.layouts.family import REGISTRY, LayoutFamily

from .specs import VARIANT_SPECS, VariantSpec


def _build_layers_map(spec: VariantSpec) -> LayerMap:
    return {name: build_layer_from_spec(layer_spec) for name, layer_spec in spec.layer_specs.items()}


class Family(LayoutFamily):
    name = "default"

    def variants(self) -> dict[str, VariantSpec]:
        return dict(VARIANT_SPECS)

    def metadata_key(self) -> str:
        return "default"

    def build(self, variant: str) -> dict:
        try:
            spec = VARIANT_SPECS[variant]
        except KeyError as exc:  # pragma: no cover
            msg = f"Unknown default layout '{variant}'. Available: {sorted(VARIANT_SPECS)}"
            raise KeyError(msg) from exc

        layers = _build_layers_map(spec)
        builder = LayoutBuilder(
            metadata_key=self.metadata_key(),
            variant=variant,
            common_fields=spec.common_fields,
            layer_names=spec.layer_names,
        )
        builder.add_layers(layers)
        builder.add_input_listeners(list(spec.input_listeners))
        return builder.build()


REGISTRY.register(Family())

__all__ = ["Family"]
