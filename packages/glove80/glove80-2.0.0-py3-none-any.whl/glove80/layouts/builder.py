"""Declarative builder for assembling Glove80 layout payloads."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal, cast

from .common import compose_layout
from .merge import merge_components

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping, Sequence

    from glove80.base import LayerMap
    from glove80.layouts.components import LayoutFeatureComponents
    from glove80.layouts.schema import Combo, HoldTap, InputListener, Macro


def _unique_sequence(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


@dataclass
class _Sections:
    layer_names: list[str] = field(default_factory=list)
    layers: LayerMap = field(default_factory=dict)
    macros: OrderedDict[str, "Macro"] = field(default_factory=OrderedDict)
    hold_taps: list["HoldTap"] = field(default_factory=list)
    combos: list["Combo"] = field(default_factory=list)
    input_listeners: list["InputListener"] = field(default_factory=list)


class LayoutBuilder:
    """Mutable helper that coordinates every section of a layout payload."""

    def __init__(
        self,
        *,
        metadata_key: str,
        variant: str,
        common_fields: Mapping[str, Any],
        layer_names: Sequence[str] | None = None,
        mouse_layers_provider: Callable[[str], LayerMap] | None = None,
        cursor_layers_provider: Callable[[str], LayerMap] | None = None,
        home_row_provider: Callable[[str], LayoutFeatureComponents] | None = None,
    ) -> None:
        self.metadata_key = metadata_key
        self.variant = variant
        self._common_fields: Mapping[str, Any] = dict(common_fields)
        self._sections = _Sections(layer_names=_unique_sequence(layer_names or ()))
        self._mouse_layers_provider = mouse_layers_provider
        self._cursor_layers_provider = cursor_layers_provider
        self._home_row_provider = home_row_provider

    # ------------------------------------------------------------------
    # Base section wiring
    # ------------------------------------------------------------------
    def set_layer_order(self, layer_names: Sequence[str]) -> LayoutBuilder:
        self._sections.layer_names = _unique_sequence(layer_names)
        return self

    def add_layers(
        self,
        layers: LayerMap,
        *,
        insert_after: str | None = None,
        insert_before: str | None = None,
        explicit_order: Sequence[str] | None = None,
    ) -> LayoutBuilder:
        """Merge *layers* into the builder and update the layer order."""
        if not layers:
            return self

        if insert_after is not None and insert_before is not None:
            msg = "Specify only one of insert_after or insert_before"
            raise ValueError(msg)

        order = list(explicit_order or layers.keys())
        for name in order:
            if name not in layers:
                msg = f"Layer '{name}' missing from provided mapping"
                raise KeyError(msg)
            self._sections.layers[name] = layers[name]
        self._insert_layer_names(order, after=insert_after, before=insert_before)
        return self

    def update_layer(self, name: str, layer_data: Any) -> LayoutBuilder:
        if name not in self._sections.layer_names:
            self._sections.layer_names.append(name)
        self._sections.layers[name] = layer_data
        return self

    def add_macros(
        self,
        macros: Sequence["Macro"],
        *,
        prepend: bool = False,
    ) -> LayoutBuilder:
        if not macros:
            return self

        existing = self._sections.macros
        if prepend:
            # Build a new ordered dict that places the incoming macros up front.
            updated = OrderedDict()
            for macro in macros:
                name = _macro_name(macro)
                updated[name] = macro
            for name, macro in existing.items():
                if name not in updated:
                    updated[name] = macro
            self._sections.macros = updated
            return self

        for macro in macros:
            name = _macro_name(macro)
            existing[name] = macro
        return self

    def add_hold_taps(self, hold_taps: Sequence["HoldTap"]) -> LayoutBuilder:
        self._sections.hold_taps.extend(hold_taps)
        return self

    def add_combos(self, combos: Sequence["Combo"]) -> LayoutBuilder:
        self._sections.combos.extend(combos)
        return self

    def add_input_listeners(self, listeners: Sequence["InputListener"]) -> LayoutBuilder:
        self._sections.input_listeners.extend(listeners)
        return self

    # ------------------------------------------------------------------
    # Feature-oriented helpers
    # ------------------------------------------------------------------
    def set_mouse_layers_provider(self, provider: Callable[[str], LayerMap]) -> LayoutBuilder:
        self._mouse_layers_provider = provider
        return self

    def set_cursor_layers_provider(self, provider: Callable[[str], LayerMap]) -> LayoutBuilder:
        self._cursor_layers_provider = provider
        return self

    def set_home_row_provider(self, provider: Callable[[str], LayoutFeatureComponents]) -> LayoutBuilder:
        self._home_row_provider = provider
        return self

    def add_mouse_layers(self, *, insert_after: str | None = None) -> LayoutBuilder:
        if self._mouse_layers_provider is None:
            msg = "Mouse layer provider is not configured for this builder"
            raise ValueError(msg)
        layers = self._mouse_layers_provider(self.variant)
        return self.add_layers(layers, insert_after=insert_after)

    def add_cursor_layer(self, *, insert_after: str | None = None) -> LayoutBuilder:
        if self._cursor_layers_provider is None:
            msg = "Cursor layer provider is not configured for this builder"
            raise ValueError(msg)
        layers = self._cursor_layers_provider(self.variant)
        return self.add_layers(layers, insert_after=insert_after)

    def add_home_row_mods(
        self,
        *,
        target_layer: str,
        insert_after: str | None = None,
        position: Literal["before", "after"] = "after",
        feature_provider: Callable[[str], LayoutFeatureComponents] | None = None,
    ) -> LayoutBuilder:
        """Attach home-row modifiers and associated macros/combos.

        Parameters
        ----------
        target_layer:
            Layer name that the modifiers conceptually extend. New layers are
            inserted directly after this layer unless *insert_after* overrides
            the placement.
        insert_after:
            Optional explicit anchor at which to append the generated layers.
        feature_provider:
            Optional override for the configured home-row provider. The
            callable must return a :class:`LayoutFeatureComponents` instance.

        """
        provider = feature_provider or self._home_row_provider
        if provider is None:
            msg = "Home-row modifier provider is not configured for this builder"
            raise ValueError(msg)
        if target_layer not in self._sections.layer_names:
            msg = f"Unknown target layer '{target_layer}'"
            raise ValueError(msg)
        components = provider(self.variant)
        anchor = insert_after or target_layer
        if position == "before":
            self._merge_feature_components(components, insert_before=anchor)
        else:
            self._merge_feature_components(components, insert_after=anchor)
        return self

    # ------------------------------------------------------------------
    # Finalization
    # ------------------------------------------------------------------
    def build(self) -> dict[str, Any]:
        missing = [name for name in self._sections.layer_names if name not in self._sections.layers]
        if missing:
            raise KeyError("Cannot build layout; missing layer data for: " + ", ".join(missing))

        return compose_layout(
            self._common_fields,
            layer_names=self._sections.layer_names,
            generated_layers=self._sections.layers,
            metadata_key=self.metadata_key,
            variant=self.variant,
            macros=list(self._sections.macros.values()),
            hold_taps=self._sections.hold_taps,
            combos=self._sections.combos,
            input_listeners=self._sections.input_listeners,
        )

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _insert_layer_names(
        self,
        names: Sequence[str],
        *,
        after: str | None = None,
        before: str | None = None,
    ) -> None:
        if not names:
            return
        if after is not None and before is not None:
            msg = "Specify only one of 'after' or 'before'"
            raise ValueError(msg)

        names = _unique_sequence(names)
        current = self._sections.layer_names

        if after is None and before is None:
            for name in names:
                if name not in current:
                    current.append(name)
            return

        filtered = [name for name in current if name not in names]

        if before is not None:
            try:
                anchor_index = filtered.index(before)
            except ValueError:
                msg = f"Layer '{before}' is not present in the order"
                raise ValueError(msg) from None
            updated = (
                filtered[:anchor_index] + [name for name in names if name not in filtered] + filtered[anchor_index:]
            )
            self._sections.layer_names = updated
            return

        if after is not None:
            try:
                anchor_index = filtered.index(after)
            except ValueError:
                msg = f"Layer '{after}' is not present in the order"
                raise ValueError(msg) from None
            updated = (
                filtered[: anchor_index + 1]
                + [name for name in names if name not in filtered]
                + filtered[anchor_index + 1 :]
            )
            self._sections.layer_names = updated

    def _merge_feature_components(
        self,
        components: LayoutFeatureComponents,
        *,
        insert_after: str | None = None,
        insert_before: str | None = None,
    ) -> None:
        # Delegate merge of non-layer sections to the shared helper to
        # maintain a single behavior surface with runtime feature application.
        shadow_layout: dict[str, Any] = {
            "macros": list(self._sections.macros.values()),
            "holdTaps": list(self._sections.hold_taps),
            "combos": list(self._sections.combos),
            "inputListeners": list(self._sections.input_listeners),
        }
        merge_components(shadow_layout, components)

        # Reconcile back into builder sections, preserving order.
        updated_macros: "OrderedDict[str, Any]" = OrderedDict()
        for macro in shadow_layout["macros"]:
            name = _macro_name(macro)
            updated_macros[name] = macro
        self._sections.macros = updated_macros
        self._sections.hold_taps = list(shadow_layout["holdTaps"])
        self._sections.combos = list(shadow_layout["combos"])
        self._sections.input_listeners = list(shadow_layout["inputListeners"])

        # Layers participate in ordered insertion; use builder's add_layers to
        # honor anchors while still reusing the shared merge for other pieces.
        if components.layers:
            self.add_layers(
                components.layers,
                insert_after=insert_after,
                insert_before=insert_before,
                explicit_order=list(components.layers.keys()),
            )

    # No dict/model coercion helpers in the builder: we carry models through
    # and normalize to dicts in compose_layout just before payload validation.


def _macro_name(macro: Any) -> str:
    # Support pydantic model attribute access or mapping lookup
    if hasattr(macro, "name") and not isinstance(macro, dict):
        name = getattr(macro, "name")
    else:
        try:
            from collections.abc import Mapping

            if isinstance(macro, Mapping):
                name = cast("Mapping[str, Any]", macro)["name"]
            else:
                # Last resort: hope it behaves like a dict
                name = cast("Any", macro)["name"]
        except Exception as exc:  # pragma: no cover - enforced via tests
            msg = "Macro definitions must include a 'name'"
            raise KeyError(msg) from exc
    if not isinstance(name, str):  # pragma: no cover - sanity guard
        msg = "Macro name must be a string"
        raise TypeError(msg)
    return name


__all__ = ["LayoutBuilder"]
