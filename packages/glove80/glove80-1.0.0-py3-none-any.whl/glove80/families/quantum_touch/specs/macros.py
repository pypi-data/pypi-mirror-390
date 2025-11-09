"""Macro specifications for QuantumTouch."""

from __future__ import annotations

from typing import Dict

from glove80.specs import MacroSpec
from glove80.specs.utils import call, kp, ks, layer_param

from .finger_data import FINGERS


def _hold_macro(meta) -> MacroSpec:
    name = f"&BHRM_{meta.hand}_{meta.name}_Hold"
    hand_label = "Left" if meta.hand == "L" else "Right"
    return MacroSpec(
        name=name,
        description=f"Hold: activate {hand_label} {meta.name} layer",
        bindings=(
            call("&macro_press"),
            call("&macro_param_1to1"),
            kp("A"),
            ks("&mo", layer_param(meta.layer)),
            call("&macro_pause_for_release"),
            call("&macro_release"),
            call("&macro_param_1to1"),
            kp("A"),
            ks("&mo", layer_param(meta.layer)),
        ),
        params=("code",),
        wait_ms=0,
        tap_ms=0,
    )


def _tap_macro(meta) -> MacroSpec:
    name = f"&BHRM_{meta.hand}_{meta.name}_Tap"
    return MacroSpec(
        name=name,
        description="Tap: restore base key",
        bindings=(
            call("&macro_release"),
            kp("LSHFT"),
            kp("RSHFT"),
            kp("LALT"),
            kp("RALT"),
            kp("LCTRL"),
            kp("RCTRL"),
            kp("LGUI"),
            kp("RGUI"),
            call("&macro_tap"),
            kp(meta.tap_key),
            call("&macro_tap"),
            call("&macro_param_1to1"),
            kp("A"),
        ),
        params=("code",),
        wait_ms=0,
        tap_ms=0,
    )


MACRO_DEFS = {}

for meta in FINGERS:
    hold = _hold_macro(meta)
    tap = _tap_macro(meta)
    MACRO_DEFS[hold.name] = hold
    MACRO_DEFS[tap.name] = tap

MACRO_ORDER = tuple(MACRO_DEFS)
MACRO_OVERRIDES: Dict[str, Dict[str, MacroSpec]] = {}

__all__ = ["MACRO_DEFS", "MACRO_ORDER", "MACRO_OVERRIDES"]
