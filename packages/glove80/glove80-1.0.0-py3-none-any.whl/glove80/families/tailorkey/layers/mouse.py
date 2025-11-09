"""Generate the TailorKey mouse-oriented layers."""

from __future__ import annotations

from typing import Dict

from glove80.base import (
    KeySpec,
    Layer,
    LayerSpec,
    PatchSpec,
    apply_patch,
    build_layer_from_spec,
    copy_layers_map,
)
from glove80.layers.mouse_helpers import build_transparent_mouse_layer

MOUSE_LAYER_SPECS: Dict[str, LayerSpec] = {
    "Mouse": LayerSpec(
        overrides={
            0: KeySpec("&none"),
            1: KeySpec("&none"),
            2: KeySpec("&none"),
            3: KeySpec("&none"),
            4: KeySpec("&none"),
            5: KeySpec("&none"),
            6: KeySpec("&none"),
            7: KeySpec("&none"),
            8: KeySpec("&none"),
            9: KeySpec("&none"),
            10: KeySpec("&none"),
            11: KeySpec("&none"),
            12: KeySpec("&none"),
            13: KeySpec("&none"),
            14: KeySpec("&none"),
            15: KeySpec("&none"),
            16: KeySpec("&none"),
            17: KeySpec("&none"),
            18: KeySpec("&none"),
            19: KeySpec("&none"),
            20: KeySpec("&none"),
            21: KeySpec("&none"),
            22: KeySpec("&none"),
            23: KeySpec("&none"),
            24: KeySpec("&msc", (KeySpec("SCRL_LEFT"),)),
            25: KeySpec("&mmv", (KeySpec("MOVE_UP"),)),
            26: KeySpec("&msc", (KeySpec("SCRL_RIGHT"),)),
            27: KeySpec("&none"),
            28: KeySpec("&none"),
            29: KeySpec("&sk", (KeySpec("RSHFT"),)),
            30: KeySpec("&sk", (KeySpec("RCTRL"),)),
            31: KeySpec("&sk", (KeySpec("RALT"),)),
            32: KeySpec("&sk", (KeySpec("RGUI"),)),
            33: KeySpec("&none"),
            34: KeySpec("&none"),
            35: KeySpec("&msc", (KeySpec("SCRL_UP"),)),
            36: KeySpec("&mmv", (KeySpec("MOVE_LEFT"),)),
            37: KeySpec("&mmv", (KeySpec("MOVE_DOWN"),)),
            38: KeySpec("&mmv", (KeySpec("MOVE_RIGHT"),)),
            39: KeySpec("&msc", (KeySpec("SCRL_UP"),)),
            40: KeySpec("&msc", (KeySpec("SCRL_UP"),)),
            41: KeySpec("&mo", (KeySpec(9),)),
            42: KeySpec("&mo", (KeySpec(10),)),
            43: KeySpec("&mo", (KeySpec(8),)),
            44: KeySpec("&mkp", (KeySpec("LCLK"),)),
            45: KeySpec("&mkp", (KeySpec("MB4"),)),
            46: KeySpec("&none"),
            47: KeySpec("&msc", (KeySpec("SCRL_DOWN"),)),
            48: KeySpec("&mo", (KeySpec(8),)),
            49: KeySpec("&mo", (KeySpec(10),)),
            50: KeySpec("&mo", (KeySpec(9),)),
            51: KeySpec("&msc", (KeySpec("SCRL_DOWN"),)),
            52: KeySpec("&mkp", (KeySpec("MCLK"),)),
            53: KeySpec("&kp", (KeySpec("K_APP"),)),
            54: KeySpec("&mkp", (KeySpec("MB5"),)),
            55: KeySpec("&kp", (KeySpec("LC", (KeySpec("X"),)),)),
            56: KeySpec("&kp", (KeySpec("LC", (KeySpec("C"),)),)),
            57: KeySpec("&kp", (KeySpec("LC", (KeySpec("LC", (KeySpec("V"),)),)),)),
            58: KeySpec("&msc", (KeySpec("SCRL_DOWN"),)),
            59: KeySpec("&msc", (KeySpec("SCRL_LEFT"),)),
            60: KeySpec("&mmv", (KeySpec("MOVE_UP"),)),
            61: KeySpec("&msc", (KeySpec("SCRL_RIGHT"),)),
            62: KeySpec("&mkp", (KeySpec("RCLK"),)),
            63: KeySpec("&mkp", (KeySpec("MB5"),)),
            64: KeySpec("&none"),
            65: KeySpec("&none"),
            66: KeySpec("&none"),
            67: KeySpec("&none"),
            68: KeySpec("&none"),
            69: KeySpec("&mkp", (KeySpec("LCLK"),)),
            70: KeySpec("&mkp", (KeySpec("RCLK"),)),
            71: KeySpec("&mkp", (KeySpec("MB4"),)),
            72: KeySpec("&none"),
            73: KeySpec("&none"),
            74: KeySpec("&none"),
            75: KeySpec("&mmv", (KeySpec("MOVE_LEFT"),)),
            76: KeySpec("&mmv", (KeySpec("MOVE_DOWN"),)),
            77: KeySpec("&mmv", (KeySpec("MOVE_RIGHT"),)),
            78: KeySpec("&mkp", (KeySpec("MCLK"),)),
            79: KeySpec("&kp", (KeySpec("K_APP"),)),
        }
    ),
}


_BASE_MOUSE_LAYERS = {"Mouse": build_layer_from_spec(MOUSE_LAYER_SPECS["Mouse"])}
for transparent in ("MouseSlow", "MouseFast", "MouseWarp"):
    _BASE_MOUSE_LAYERS[transparent] = build_transparent_mouse_layer(transparent)


_MAC_MOUSE_PATCH: PatchSpec = {
    30: KeySpec("&sk", (KeySpec("RGUI"),)),
    32: KeySpec("&sk", (KeySpec("RCTRL"),)),
    55: KeySpec("&kp", (KeySpec("LG", (KeySpec("X"),)),)),
    56: KeySpec("&kp", (KeySpec("LG", (KeySpec("C"),)),)),
    57: KeySpec("&kp", (KeySpec("LG", (KeySpec("V"),)),)),
}

_DUAL_MOUSE_PATCH: PatchSpec = {
    55: KeySpec("&none"),
    56: KeySpec("&none"),
    57: KeySpec("&none"),
}

_BILATERAL_MOUSE_PATCH: PatchSpec = {
    41: KeySpec("&mo", (KeySpec(17),)),
    42: KeySpec("&mo", (KeySpec(18),)),
    43: KeySpec("&mo", (KeySpec(16),)),
    48: KeySpec("&mo", (KeySpec(16),)),
    49: KeySpec("&mo", (KeySpec(18),)),
    50: KeySpec("&mo", (KeySpec(17),)),
}


def build_mouse_layers(variant: str) -> Dict[str, Layer]:
    """Return the four mouse-related layers for the requested variant."""
    layers = copy_layers_map(_BASE_MOUSE_LAYERS)
    mouse = layers["Mouse"]

    if variant in {"mac", "bilateral_mac"}:
        apply_patch(mouse, _MAC_MOUSE_PATCH)

    if variant == "dual":
        apply_patch(mouse, _DUAL_MOUSE_PATCH)

    if variant in {"bilateral_windows", "bilateral_mac"}:
        apply_patch(mouse, _BILATERAL_MOUSE_PATCH)

    return layers
