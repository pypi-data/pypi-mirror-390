"""Generate the Symbol layer across TailorKey variants."""

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


SYMBOL_SPEC = LayerSpec(
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
        10: KeySpec("&kp", (KeySpec("GRAVE"),)),
        11: KeySpec("&kp", (KeySpec("RBKT"),)),
        12: KeySpec("&kp", (KeySpec("LPAR"),)),
        13: KeySpec("&kp", (KeySpec("RPAR"),)),
        14: KeySpec("&kp", (KeySpec("COMMA"),)),
        15: KeySpec("&kp", (KeySpec("DOT"),)),
        16: KeySpec("&none"),
        17: KeySpec("&none"),
        18: KeySpec("&none"),
        19: KeySpec("&none"),
        20: KeySpec("&none"),
        21: KeySpec("&none"),
        22: KeySpec("&kp", (KeySpec("LBKT"),)),
        23: KeySpec("&kp", (KeySpec("EXCL"),)),
        24: KeySpec("&kp", (KeySpec("LBRC"),)),
        25: KeySpec("&kp", (KeySpec("RBRC"),)),
        26: KeySpec("&kp", (KeySpec("SEMI"),)),
        27: KeySpec("&kp", (KeySpec("QMARK"),)),
        28: KeySpec("&kp", (KeySpec("GRAVE"),)),
        29: KeySpec("&sk", (KeySpec("RSHFT"),)),
        30: KeySpec("&sk", (KeySpec("RCTRL"),)),
        31: KeySpec("&sk", (KeySpec("RALT"),)),
        32: KeySpec("&sk", (KeySpec("RGUI"),)),
        33: KeySpec("&none"),
        34: KeySpec("&kp", (KeySpec("HASH"),)),
        35: KeySpec("&kp", (KeySpec("CARET"),)),
        36: KeySpec("&kp", (KeySpec("EQUAL"),)),
        37: KeySpec("&kp", (KeySpec("UNDER"),)),
        38: KeySpec("&kp", (KeySpec("DLLR"),)),
        39: KeySpec("&kp", (KeySpec("STAR"),)),
        40: KeySpec("&kp", (KeySpec("DQT"),)),
        41: KeySpec("&kp", (KeySpec("BSPC"),)),
        42: KeySpec("&kp", (KeySpec("TAB"),)),
        43: KeySpec("&kp", (KeySpec("SPACE"),)),
        44: KeySpec("&kp", (KeySpec("RET"),)),
        45: KeySpec("&none"),
        46: KeySpec("&kp", (KeySpec("TILDE"),)),
        47: KeySpec("&kp", (KeySpec("LT"),)),
        48: KeySpec("&kp", (KeySpec("PIPE"),)),
        49: KeySpec("&kp", (KeySpec("MINUS"),)),
        50: KeySpec("&kp", (KeySpec("GT"),)),
        51: KeySpec("&kp", (KeySpec("FSLH"),)),
        52: KeySpec("&kp", (KeySpec("BSLH"),)),
        53: KeySpec("&kp", (KeySpec("DOT"),)),
        54: KeySpec("&kp", (KeySpec("STAR"),)),
        55: KeySpec("&none"),
        56: KeySpec("&none"),
        57: KeySpec("&none"),
        58: KeySpec("&kp", (KeySpec("SQT"),)),
        59: KeySpec("&kp", (KeySpec("DEL"),)),
        60: KeySpec("&kp", (KeySpec("LS", (KeySpec("TAB"),)),)),
        61: KeySpec("&kp", (KeySpec("INS"),)),
        62: KeySpec("&kp", (KeySpec("ESC"),)),
        63: KeySpec("&none"),
        64: KeySpec("&symb_dotdot_v1_TKZ"),
        65: KeySpec("&kp", (KeySpec("AMPS"),)),
        66: KeySpec("&kp", (KeySpec("SQT"),)),
        67: KeySpec("&kp", (KeySpec("DQT"),)),
        68: KeySpec("&kp", (KeySpec("PLUS"),)),
        69: KeySpec("&kp", (KeySpec("PRCNT"),)),
        70: KeySpec("&kp", (KeySpec("COLON"),)),
        71: KeySpec("&kp", (KeySpec("AT"),)),
        72: KeySpec("&none"),
        73: KeySpec("&none"),
        74: KeySpec("&none"),
        75: KeySpec("&none"),
        76: KeySpec("&none"),
        77: KeySpec("&none"),
        78: KeySpec("&none"),
        79: KeySpec("&none"),
    }
)

_BASE_SYMBOL_LAYER: Layer = build_layer_from_spec(SYMBOL_SPEC)


_MAC_PATCH: PatchSpec = {
    30: KeySpec("&sk", (KeySpec("RGUI"),)),
    32: KeySpec("&sk", (KeySpec("RCTRL"),)),
}


def build_symbol_layer(variant: str) -> Layer:
    layer = copy_layer(_BASE_SYMBOL_LAYER)
    apply_patch_if(layer, variant in {"mac", "bilateral_mac"}, _MAC_PATCH)
    return layer
