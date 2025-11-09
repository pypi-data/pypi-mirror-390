"""Shared helpers for composing layout payloads."""

from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence

from ..base import Layer, LayerMap, resolve_layer_refs
from ..metadata import get_variant_metadata

META_FIELDS = ("title", "uuid", "parent_uuid", "date", "notes", "tags")
DEFAULT_REF_FIELDS = ("macros", "holdTaps", "combos", "inputListeners")

BASE_COMMON_FIELDS = {
    "keyboard": "glove80",
    "firmware_api_version": "1",
    "locale": "en-US",
    "unlisted": False,
    "custom_defined_behaviors": "",
    "custom_devicetree": "",
    "config_parameters": [],
    "layout_parameters": {},
}


def _build_common_fields(
    *,
    creator: str,
    locale: str = "en-US",
    custom_defined_behaviors: str = "",
    custom_devicetree: str = "",
    config_parameters: Sequence[Mapping[str, Any]] | None = None,
    layout_parameters: Mapping[str, Any] | None = None,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the shared metadata dict populated for a layout family."""

    fields: dict[str, Any] = dict(BASE_COMMON_FIELDS)
    fields["creator"] = creator
    fields["locale"] = locale
    fields["custom_defined_behaviors"] = custom_defined_behaviors
    fields["custom_devicetree"] = custom_devicetree
    fields["config_parameters"] = list(config_parameters or [])
    fields["layout_parameters"] = dict(layout_parameters or {})
    if extra:
        fields.update(extra)
    return fields


def _resolve_referenced_fields(
    layout: dict,
    *,
    layer_names: Sequence[str],
    fields: Iterable[str] = DEFAULT_REF_FIELDS,
) -> None:
    """Resolve LayerRef placeholders for the requested fields."""

    layer_indices = {name: idx for idx, name in enumerate(layer_names)}
    for field in fields:
        layout[field] = resolve_layer_refs(layout[field], layer_indices)


def _assemble_layers(layer_names: Sequence[str], generated_layers: LayerMap, *, variant: str) -> list[Layer]:
    """Return the ordered list of layers, erroring if any are missing."""

    ordered: list[Layer] = []
    for name in layer_names:
        try:
            ordered.append(generated_layers[name])
        except KeyError as exc:  # pragma: no cover
            raise KeyError(f"No generated layer data for '{name}' in variant '{variant}'") from exc
    return ordered


def _attach_variant_metadata(layout: dict, *, variant: str, layout_key: str) -> None:
    """Inject metadata fields into the layout payload."""

    meta = get_variant_metadata(variant, layout=layout_key)
    for field in META_FIELDS:
        layout[field] = meta.get(field)
