"""Compose the Glorious Engrammer layout."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Sequence

from glove80.layouts.common import _assemble_layers, _attach_variant_metadata
from glove80.layouts.family import LayoutFamily, REGISTRY

from .layers import build_all_layers
from .specs import VARIANT_SPECS

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


def _order_layout_fields(layout: Dict[str, Any]) -> Dict[str, Any]:
    ordered: Dict[str, Any] = {}
    for field in FIELD_ORDER:
        ordered[field] = layout[field]
    return ordered


class Family(LayoutFamily):
    name = "glorious_engrammer"

    def variants(self) -> Sequence[str]:
        return tuple(VARIANT_SPECS.keys())

    def metadata_key(self) -> str:
        return "glorious_engrammer"

    def build(self, variant: str) -> Dict:
        try:
            spec = VARIANT_SPECS[variant]
        except KeyError as exc:
            raise KeyError(
                f"Unknown Glorious Engrammer variant '{variant}'. Available: {sorted(VARIANT_SPECS)}"
            ) from exc

        layout: Dict = deepcopy(spec.common_fields)
        layout["layer_names"] = list(spec.layer_names)
        layout["macros"] = []
        layout["holdTaps"] = []
        layout["combos"] = []
        layout["inputListeners"] = []

        generated_layers = build_all_layers(variant)
        layout["layers"] = _assemble_layers(layout["layer_names"], generated_layers, variant=variant)
        _attach_variant_metadata(layout, variant=variant, layout_key=self.metadata_key())
        return _order_layout_fields(layout)


REGISTRY.register(Family())

__all__ = ["Family"]
