"""Compose full TailorKey layouts from generated layers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from glove80.layouts import LayoutBuilder
from glove80.layouts.schema import HoldTap, Macro
from glove80.layouts.components import LayoutFeatureComponents
from glove80.layouts.family import REGISTRY, LayoutFamily
# Build ordered sequences of models without legacy helpers.

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

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence


def _get_variant_section(sections: Mapping[str, Sequence[Any]], variant: str, label: str) -> list[Any]:
    try:
        return list(sections[variant])
    except KeyError as exc:  # pragma: no cover
        msg = f"No {label} for variant '{variant}'"
        raise KeyError(msg) from exc


def _build_macros(variant: str) -> list[Macro]:
    order = _get_variant_section(MACRO_ORDER, variant, "macro order")
    overrides = MACRO_OVERRIDES.get(variant, {}) or {}
    result: list[Macro] = []
    for name in order:
        value = overrides.get(name, MACRO_DEFS.get(name))
        if value is None:
            raise KeyError(f"Unknown definition '{name}'")
        result.append(value)
    return result


def _build_hold_taps(variant: str) -> list[HoldTap]:
    order = _get_variant_section(HOLD_TAP_ORDER, variant, "hold-tap order")
    result: list[HoldTap] = []
    for name in order:
        value = HOLD_TAP_DEFS.get(name)
        if value is None:
            raise KeyError(f"Unknown definition '{name}'")
        result.append(value)
    return result


def _layer_names(variant: str) -> list[str]:
    return list(_get_variant_section(LAYER_NAME_MAP, variant, "layer names"))


class Family(LayoutFamily):
    name = "tailorkey"

    def variants(self) -> Sequence[str]:
        return list(LAYER_NAME_MAP.keys())

    def metadata_key(self) -> str:
        return "tailorkey"

    def build(self, variant: str) -> dict:
        combos = _get_variant_section(COMBO_DATA, variant, "combo definitions")
        listeners = _get_variant_section(INPUT_LISTENER_DATA, variant, "input listeners")
        generated_layers = build_all_layers(variant)
        layer_names = _layer_names(variant)

        hrm_names = [name for name in layer_names if name.startswith("HRM_")]
        cursor_names = [name for name in layer_names if name.startswith("Cursor")]
        mouse_names = [name for name in layer_names if name.startswith("Mouse")]

        builder = LayoutBuilder(
            metadata_key=self.metadata_key(),
            variant=variant,
            common_fields=COMMON_FIELDS,
            layer_names=layer_names,
            mouse_layers_provider=_subset_layer_provider(mouse_names, generated_layers),
            cursor_layers_provider=_subset_layer_provider(cursor_names, generated_layers),
            home_row_provider=_home_row_provider(hrm_names, generated_layers),
        )
        builder.add_layers({name: generated_layers[name] for name in layer_names})
        builder.add_macros(_build_macros(variant))
        builder.add_hold_taps(_build_hold_taps(variant))
        builder.add_combos(combos)
        builder.add_input_listeners(listeners)

        if hrm_names:
            before, after = _group_anchor(layer_names, hrm_names)
            anchor = after if before is None else before
            if anchor is None:
                msg = "TailorKey layout requires at least one non-HRM layer"
                raise ValueError(msg)
            builder.add_home_row_mods(
                target_layer=anchor,
                insert_after=anchor,
                position="before" if before is None else "after",
            )

        if cursor_names:
            before, _ = _group_anchor(layer_names, cursor_names)
            if before:
                builder.add_cursor_layer(insert_after=before)

        if mouse_names:
            before, _ = _group_anchor(layer_names, mouse_names)
            if before:
                builder.add_mouse_layers(insert_after=before)

        return builder.build()


def _subset_layer_provider(names: Sequence[str], layers: Mapping[str, Any]):
    if not names:
        return None

    def provider(_variant: str) -> dict[str, Any]:
        return {name: layers[name] for name in names}

    return provider


def _home_row_provider(names: Sequence[str], layers: Mapping[str, Any]):
    if not names:
        return None

    def provider(_variant: str) -> LayoutFeatureComponents:
        return LayoutFeatureComponents(layers={name: layers[name] for name in names})

    return provider


def _group_anchor(layer_names: Sequence[str], group_names: Sequence[str]) -> tuple[str | None, str | None]:
    if not group_names:
        return None, None

    indices = [idx for idx, name in enumerate(layer_names) if name in group_names]
    if not indices:
        return None, None

    first = min(indices)
    last = max(indices)

    before = None
    for idx in range(first - 1, -1, -1):
        candidate = layer_names[idx]
        if candidate not in group_names:
            before = candidate
            break

    after = None
    for idx in range(last + 1, len(layer_names)):
        candidate = layer_names[idx]
        if candidate not in group_names:
            after = candidate
            break

    return before, after


REGISTRY.register(Family())

__all__ = ["Family"]
