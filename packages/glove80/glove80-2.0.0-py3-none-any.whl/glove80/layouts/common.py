"""Shared helpers for composing layout payloads."""

from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Any

from glove80.base import Layer, LayerMap, resolve_layer_refs
from glove80.layouts.schema import CommonFields as CommonFieldsModel, LayoutPayload as LayoutPayloadModel
from glove80.metadata import get_variant_metadata

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence
    from glove80.layouts.schema import Macro, HoldTap, Combo, InputListener

META_FIELDS = ("title", "uuid", "parent_uuid", "date", "notes", "tags")
DEFAULT_REF_FIELDS = ("macros", "holdTaps", "combos", "inputListeners")
ALLOW_SERIALIZED_LAYERREF = True

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


def build_layout_payload(
    common_fields: Mapping[str, Any],
    *,
    layer_names: Sequence[str],
    macros: Sequence["Macro"] | None = None,
    hold_taps: Sequence["HoldTap"] | None = None,
    combos: Sequence["Combo"] | None = None,
    input_listeners: Sequence["InputListener"] | None = None,
) -> dict[str, Any]:
    """Create a baseline layout payload from shared metadata and sections."""
    # Validate/normalize common fields via Pydantic, then dump to a plain dict
    # so downstream output remains identical.
    layout: dict[str, Any] = deepcopy(CommonFieldsModel(**dict(common_fields)).model_dump(by_alias=True))
    layout["layer_names"] = list(layer_names)
    layout["macros"] = list(macros or [])
    layout["holdTaps"] = list(hold_taps or [])
    layout["combos"] = list(combos or [])
    layout["inputListeners"] = list(input_listeners or [])
    return layout


def compose_layout(
    common_fields: Mapping[str, Any],
    *,
    layer_names: Sequence[str],
    generated_layers: LayerMap,
    metadata_key: str,
    variant: str,
    macros: Sequence["Macro"] | None = None,
    hold_taps: Sequence["HoldTap"] | None = None,
    combos: Sequence["Combo"] | None = None,
    input_listeners: Sequence["InputListener"] | None = None,
    ref_fields: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Compose a full layout payload given common metadata and generated layers."""
    layout = build_layout_payload(
        common_fields,
        layer_names=layer_names,
        macros=macros,
        hold_taps=hold_taps,
        combos=combos,
        input_listeners=input_listeners,
    )
    # Always normalize section items to dictionaries for JSON stability.
    _normalize_sections_to_dicts(layout, fields=ref_fields or DEFAULT_REF_FIELDS)
    _resolve_referenced_fields(
        layout,
        layer_names=layer_names,
        fields=ref_fields or DEFAULT_REF_FIELDS,
    )
    layout["layers"] = _assemble_layers(layer_names, generated_layers, variant=variant)
    _attach_variant_metadata(layout, variant=variant, layout_key=metadata_key)
    # Validate final payload and normalize away None values.
    validated = LayoutPayloadModel(**layout).model_dump(by_alias=True, exclude_none=True)
    return validated


def build_common_fields(
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


def _normalize_sections_to_dicts(
    layout: dict[str, Any],
    *,
    fields: Iterable[str] = DEFAULT_REF_FIELDS,
) -> None:
    """Coerce any pydantic models within sections to plain dicts."""
    for field in fields:
        items = layout.get(field) or []
        normalized: list[Any] = []
        for item in items:
            if hasattr(item, "model_dump"):
                try:
                    datum = item.model_dump(by_alias=True, exclude_none=True)
                except Exception:
                    datum = item.model_dump()
            else:
                datum = item
            normalized.append(datum)
        layout[field] = normalized


def _resolve_referenced_fields(
    layout: dict[str, Any],
    *,
    layer_names: Sequence[str],
    fields: Iterable[str] = DEFAULT_REF_FIELDS,
) -> None:
    """Resolve layer references for the requested fields after normalization.

    At this point, any pydantic models were converted to dictionaries. Pydantic
    would have serialized LayerRef dataclasses as ``{"name": str}``, so we need
    to map such dicts (and any surviving LayerRef instances) to integer indices.
    """
    layer_indices = {name: idx for idx, name in enumerate(layer_names)}

    def _resolve(obj: Any) -> Any:
        # First, resolve any real LayerRef instances
        obj = resolve_layer_refs(obj, layer_indices)
        # Fallback: resolve serialized LayerRef dicts of shape {"name": str}
        if isinstance(obj, dict):
            if ALLOW_SERIALIZED_LAYERREF and set(obj.keys()) == {"name"} and isinstance(obj.get("name"), str):
                name = obj["name"]
                return layer_indices[name]
            return {k: _resolve(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_resolve(v) for v in obj]
        return obj

    for field in fields:
        layout[field] = _resolve(layout[field])


def _assemble_layers(layer_names: Sequence[str], generated_layers: LayerMap, *, variant: str) -> list[Layer]:
    """Return the ordered list of layers, erroring if any are missing."""
    ordered: list[Layer] = []
    for name in layer_names:
        try:
            ordered.append(generated_layers[name])
        except KeyError as exc:  # pragma: no cover
            msg = f"No generated layer data for '{name}' in variant '{variant}'"
            raise KeyError(msg) from exc
    return ordered


def _attach_variant_metadata(layout: dict[str, Any], *, variant: str, layout_key: str) -> None:
    """Inject metadata fields into the layout payload."""
    meta = get_variant_metadata(variant, layout=layout_key)
    for field in META_FIELDS:
        layout[field] = meta.get(field)
