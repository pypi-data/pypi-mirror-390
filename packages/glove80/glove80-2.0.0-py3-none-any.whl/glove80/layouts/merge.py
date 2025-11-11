"""Shared logic for merging feature components into a layout dict.

This centralizes the behavior used by both the builder and the runtime
``features.apply_feature`` helper so they cannot drift.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from .components import LayoutFeatureComponents

if TYPE_CHECKING:
    from collections.abc import MutableSequence


def _ensure_section(layout: dict[str, Any], key: str) -> MutableSequence[Any]:
    section = layout.get(key)
    if section is None:
        msg = f"Layout is missing '{key}' section"
        raise KeyError(msg)
    return cast("MutableSequence[Any]", section)


def _to_dict(obj: Any) -> Any:
    if hasattr(obj, "model_dump"):
        try:
            return obj.model_dump(by_alias=True, exclude_none=True)
        except Exception:
            return obj.model_dump()
    return obj


def merge_components(layout: dict[str, Any], components: LayoutFeatureComponents) -> None:
    """Mutate ``layout`` in-place by appending/overriding ``components``.

    The function expects standard Glove80 layout sections. If the ``layers``
    fields (``layer_names`` and ``layers``) are present, they will be updated;
    otherwise, layer merging is skipped.
    """

    # ------------------------- macros (ordered by name) -------------------------
    existing_macros = [_to_dict(macro) for macro in list(_ensure_section(layout, "macros"))]
    macros_by_name = {
        macro.get("name"): macro for macro in existing_macros if isinstance(macro, dict) and "name" in macro
    }
    macro_order = [macro.get("name") for macro in existing_macros if isinstance(macro, dict) and "name" in macro]

    def _set_macro(macro_obj: Any) -> None:
        macro_dict = _to_dict(macro_obj)
        name = macro_dict.get("name")
        if not isinstance(name, str):
            msg = "Feature macros must include a 'name'"
            raise KeyError(msg)
        macros_by_name[name] = macro_dict
        if name not in macro_order:
            macro_order.append(name)

    for macro in components.macros:
        _set_macro(macro)
    for macro in components.macro_overrides.values():
        _set_macro(macro)
    if components.macros_by_name:
        for name, macro in components.macros_by_name.items():
            # Ensure name coherence even if caller omitted 'name' inside dict
            macro_dict = _to_dict(macro)
            if isinstance(macro_dict, dict):
                macro_dict.setdefault("name", name)
            macros_by_name[name] = macro_dict  # override wins
            if name not in macro_order:
                macro_order.append(name)

    layout["macros"] = [macros_by_name[name] for name in macro_order]

    # ---------------- holdTaps / combos / inputListeners ----------------
    _ensure_section(layout, "holdTaps").extend(_to_dict(x) for x in components.hold_taps)
    _ensure_section(layout, "combos").extend(_to_dict(x) for x in components.combos)
    _ensure_section(layout, "inputListeners").extend(_to_dict(x) for x in components.input_listeners)

    # --------------------------------- layers ----------------------------------
    if "layer_names" in layout and "layers" in layout:
        layer_names = cast("MutableSequence[str]", layout["layer_names"])
        ordered_layers = cast("MutableSequence[Any]", layout["layers"])
        layers_by_name: dict[str, Any] = dict(zip(layer_names, ordered_layers, strict=False))

        for name, layer in components.layers.items():
            if name not in layers_by_name:
                layer_names.append(name)
            layers_by_name[name] = _to_dict(layer)

        layout["layers"] = [layers_by_name[name] for name in layer_names]


__all__ = ["merge_components"]
