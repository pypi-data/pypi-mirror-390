"""Compose full TailorKey layouts from generated layers."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Mapping, Sequence, cast

from glove80.layouts.common import (
    _assemble_layers,
    _attach_variant_metadata,
    _resolve_referenced_fields,
)
from glove80.layouts.family import LayoutFamily, REGISTRY

from .layers import build_all_layers
from .specs import (
    COMBO_DATA,
    COMMON_FIELDS,
    HOLD_TAP_DEFS,
    HOLD_TAP_ORDER,
    INPUT_LISTENER_DATA,
    LAYER_NAME_MAP,
    MACRO_DEFS,
    MACRO_ORDER,
    MACRO_OVERRIDES,
)


def _materialize_named_entry(definitions: Mapping[str, Any], name: str, override: Any | None = None) -> Dict[str, Any]:
    data = override or definitions.get(name)
    if data is None:  # pragma: no cover
        raise KeyError(f"Unknown definition '{name}'")
    if hasattr(data, "to_dict"):
        return data.to_dict()
    return deepcopy(data)


def _get_variant_section(sections: Mapping[str, Sequence[Any]], variant: str, label: str) -> List[Any]:
    try:
        return list(sections[variant])
    except KeyError as exc:  # pragma: no cover
        raise KeyError(f"No {label} for variant '{variant}'") from exc


def _materialize_sequence(items: Sequence[Any]) -> List[Any]:
    result: List[Any] = []
    for item in items:
        if hasattr(item, "to_dict"):
            result.append(item.to_dict())
        else:
            result.append(deepcopy(item))
    return result


def _build_macros(variant: str) -> List[Dict[str, Any]]:
    order = _get_variant_section(MACRO_ORDER, variant, "macro order")
    overrides = MACRO_OVERRIDES.get(variant, {})
    macro_defs = cast(Mapping[str, Any], MACRO_DEFS)
    return [_materialize_named_entry(macro_defs, name, overrides.get(name)) for name in order]


def _build_hold_taps(variant: str) -> List[Dict[str, Any]]:
    order = _get_variant_section(HOLD_TAP_ORDER, variant, "hold-tap order")
    hold_tap_defs = cast(Mapping[str, Any], HOLD_TAP_DEFS)
    return [_materialize_named_entry(hold_tap_defs, name) for name in order]


def _base_layout_payload(variant: str) -> Dict[str, Any]:
    layout = deepcopy(COMMON_FIELDS)
    layout["layer_names"] = deepcopy(_get_variant_section(LAYER_NAME_MAP, variant, "layer names"))
    layout["macros"] = _build_macros(variant)
    layout["holdTaps"] = _build_hold_taps(variant)
    layout["combos"] = _materialize_sequence(_get_variant_section(COMBO_DATA, variant, "combo definitions"))
    layout["inputListeners"] = _materialize_sequence(
        _get_variant_section(INPUT_LISTENER_DATA, variant, "input listeners")
    )
    return layout


class Family(LayoutFamily):
    name = "tailorkey"

    def variants(self) -> Sequence[str]:
        return list(LAYER_NAME_MAP.keys())

    def metadata_key(self) -> str:
        return "tailorkey"

    def build(self, variant: str) -> Dict:
        layout = _base_layout_payload(variant)
        layer_names = layout["layer_names"]
        _resolve_referenced_fields(layout, layer_names=layer_names)
        generated_layers = build_all_layers(variant)
        layout["layers"] = _assemble_layers(layer_names, generated_layers, variant=variant)
        _attach_variant_metadata(layout, variant=variant, layout_key=self.metadata_key())
        return layout


REGISTRY.register(Family())

__all__ = ["Family"]
