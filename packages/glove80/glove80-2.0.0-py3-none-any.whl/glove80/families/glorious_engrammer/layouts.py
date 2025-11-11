"""Compose the Glorious Engrammer layout."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from glove80.layouts import LayoutBuilder
from glove80.layouts.family import REGISTRY, LayoutFamily

from .layers import build_all_layers
from .specs import VARIANT_SPECS

if TYPE_CHECKING:
    from collections.abc import Sequence

FIELD_ORDER: Sequence[str] = (
    "keyboard",
    "firmware_api_version",
    "locale",
    "uuid",
    "parent_uuid",
    "unlisted",
    "date",
    "creator",
    "title",
    "notes",
    "tags",
    "custom_defined_behaviors",
    "custom_devicetree",
    "config_parameters",
    "layout_parameters",
    "layer_names",
    "layers",
    "macros",
    "inputListeners",
    "holdTaps",
    "combos",
)


def _order_layout_fields(layout: dict[str, Any]) -> dict[str, Any]:
    layout_keys = set(layout)
    field_set = set(FIELD_ORDER)
    unexpected = sorted(layout_keys - field_set)
    if unexpected:
        msg = f"Unexpected layout fields: {unexpected}"
        raise KeyError(msg)
    missing = sorted(field_set - layout_keys)
    if missing:
        msg = f"Layout is missing fields: {missing}"
        raise KeyError(msg)

    ordered: dict[str, Any] = {}
    for field in FIELD_ORDER:
        ordered[field] = layout[field]
    return ordered


class Family(LayoutFamily):
    name = "glorious_engrammer"

    def variants(self) -> Sequence[str]:
        return tuple(VARIANT_SPECS.keys())

    def metadata_key(self) -> str:
        return "glorious_engrammer"

    def build(self, variant: str) -> dict:
        try:
            spec = VARIANT_SPECS[variant]
        except KeyError as exc:
            msg = f"Unknown Glorious Engrammer variant '{variant}'. Available: {sorted(VARIANT_SPECS)}"
            raise KeyError(
                msg,
            ) from exc

        generated_layers = build_all_layers(variant)
        builder = LayoutBuilder(
            metadata_key=self.metadata_key(),
            variant=variant,
            common_fields=spec.common_fields,
            layer_names=spec.layer_names,
        )
        builder.add_layers({name: generated_layers[name] for name in spec.layer_names})
        layout = builder.build()
        return _order_layout_fields(layout)


REGISTRY.register(Family())

__all__ = ["Family"]
