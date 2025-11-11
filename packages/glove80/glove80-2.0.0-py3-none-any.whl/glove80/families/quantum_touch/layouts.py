"""Compose QuantumTouch layouts from declarative layer specs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from glove80.layouts import LayoutBuilder
from glove80.layouts.family import REGISTRY, LayoutFamily

from .layers import build_all_layers
from .specs import (
    COMBO_DATA,
    COMMON_FIELDS,
    HOLD_TAP_DEFS,
    HOLD_TAP_ORDER,
    INPUT_LISTENER_DATA,
    LAYER_NAMES,
    MACRO_DEFS,
    MACRO_ORDER,
)

if TYPE_CHECKING:
    from collections.abc import Sequence


class Family(LayoutFamily):
    name = "quantum_touch"

    def variants(self) -> Sequence[str]:
        return ["default"]

    def metadata_key(self) -> str:
        return "quantum_touch"

    def build(self, variant: str = "default") -> dict:
        combos = list(COMBO_DATA["default"])  # already Pydantic models
        listeners = list(INPUT_LISTENER_DATA["default"])  # already models
        macros = [MACRO_DEFS[name] for name in MACRO_ORDER]
        hold_taps = [HOLD_TAP_DEFS[name] for name in HOLD_TAP_ORDER]
        generated_layers = build_all_layers(variant)

        builder = LayoutBuilder(
            metadata_key=self.metadata_key(),
            variant=variant,
            common_fields=COMMON_FIELDS,
            layer_names=LAYER_NAMES,
        )
        builder.add_layers(generated_layers)
        builder.add_macros(macros)
        builder.add_hold_taps(hold_taps)
        builder.add_combos(combos)
        builder.add_input_listeners(listeners)
        return builder.build()


REGISTRY.register(Family())

__all__ = ["Family"]
