"""Generate the Lower layer across TailorKey variants."""

from __future__ import annotations

from glove80.base import (
    KeySpec,
    Layer,
    LayerSpec,
    PatchSpec,
    apply_patch_if,
    build_layer_from_spec,
    copy_layer,
)
from glove80.families.tailorkey.alpha_layouts import base_variant_for

LOWER_LAYER_SPEC = LayerSpec(
    overrides={
        0: KeySpec("&kp", (KeySpec("C_BRI_DN"),)),
        1: KeySpec("&kp", (KeySpec("C_BRI_UP"),)),
        2: KeySpec("&kp", (KeySpec("C_PREV"),)),
        3: KeySpec("&kp", (KeySpec("C_NEXT"),)),
        4: KeySpec("&kp", (KeySpec("C_PP"),)),
        5: KeySpec("&kp", (KeySpec("C_MUTE"),)),
        6: KeySpec("&kp", (KeySpec("C_VOL_DN"),)),
        7: KeySpec("&kp", (KeySpec("C_VOL_UP"),)),
        8: KeySpec("&none"),
        9: KeySpec("&kp", (KeySpec("PAUSE_BREAK"),)),
        11: KeySpec("&none"),
        12: KeySpec("&none"),
        13: KeySpec("&none"),
        14: KeySpec("&none"),
        15: KeySpec("&kp", (KeySpec("HOME"),)),
        16: KeySpec("&kp", (KeySpec("LEFT_PARENTHESIS"),)),
        17: KeySpec("&kp", (KeySpec("KP_NUM"),)),
        18: KeySpec("&kp", (KeySpec("EQUAL"),)),
        19: KeySpec("&kp", (KeySpec("KP_SLASH"),)),
        20: KeySpec("&kp", (KeySpec("KP_MULTIPLY"),)),
        21: KeySpec("&kp", (KeySpec("PRINTSCREEN"),)),
        23: KeySpec("&none"),
        24: KeySpec("&none"),
        25: KeySpec("&kp", (KeySpec("UP_ARROW"),)),
        26: KeySpec("&none"),
        27: KeySpec("&kp", (KeySpec("END"),)),
        28: KeySpec("&kp", (KeySpec("RIGHT_PARENTHESIS"),)),
        29: KeySpec("&kp", (KeySpec("KP_N7"),)),
        30: KeySpec("&kp", (KeySpec("KP_N8"),)),
        31: KeySpec("&kp", (KeySpec("KP_N9"),)),
        32: KeySpec("&kp", (KeySpec("KP_MINUS"),)),
        33: KeySpec("&kp", (KeySpec("SCROLLLOCK"),)),
        35: KeySpec("&none"),
        36: KeySpec("&kp", (KeySpec("LEFT_ARROW"),)),
        37: KeySpec("&kp", (KeySpec("DOWN_ARROW"),)),
        38: KeySpec("&kp", (KeySpec("RIGHT_ARROW"),)),
        39: KeySpec("&kp", (KeySpec("PG_UP"),)),
        40: KeySpec("&kp", (KeySpec("PERCENT"),)),
        41: KeySpec("&kp", (KeySpec("KP_N4"),)),
        42: KeySpec("&kp", (KeySpec("KP_N5"),)),
        43: KeySpec("&kp", (KeySpec("KP_N6"),)),
        44: KeySpec("&kp", (KeySpec("KP_PLUS"),)),
        45: KeySpec("&none"),
        47: KeySpec("&kp", (KeySpec("K_APP"),)),
        48: KeySpec("&none"),
        49: KeySpec("&kp", (KeySpec("F11"),)),
        50: KeySpec("&kp", (KeySpec("F12"),)),
        51: KeySpec("&kp", (KeySpec("PG_DN"),)),
        54: KeySpec("&to", (KeySpec(0),)),
        58: KeySpec("&kp", (KeySpec("COMMA"),)),
        59: KeySpec("&kp", (KeySpec("KP_N1"),)),
        60: KeySpec("&kp", (KeySpec("KP_N2"),)),
        61: KeySpec("&kp", (KeySpec("KP_N3"),)),
        62: KeySpec("&kp", (KeySpec("KP_ENTER"),)),
        64: KeySpec("&magic"),
        65: KeySpec("&kp", (KeySpec("CAPS"),)),
        66: KeySpec("&kp", (KeySpec("INS"),)),
        67: KeySpec("&kp", (KeySpec("F11"),)),
        68: KeySpec("&kp", (KeySpec("F12"),)),
        75: KeySpec("&kp", (KeySpec("KP_N0"),)),
        76: KeySpec("&kp", (KeySpec("KP_N0"),)),
        77: KeySpec("&kp", (KeySpec("KP_DOT"),)),
        78: KeySpec("&kp", (KeySpec("KP_ENTER"),)),
    },
)

_BASE_LOWER_LAYER: Layer = build_layer_from_spec(LOWER_LAYER_SPEC)


_DUAL_PATCH: PatchSpec = {
    54: KeySpec("&to", (KeySpec(1),)),
}


def build_lower_layer(variant: str) -> Layer:
    """Return the Lower layer customized for the given variant."""
    layer = copy_layer(_BASE_LOWER_LAYER)
    apply_patch_if(layer, base_variant_for(variant) == "dual", _DUAL_PATCH)
    return layer
