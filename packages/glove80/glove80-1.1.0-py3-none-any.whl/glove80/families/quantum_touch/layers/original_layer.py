"""QuantumTouch Original layer."""

from __future__ import annotations

from glove80.base import KeySpec, Layer, LayerSpec, build_layer_from_spec


ORIGINAL_LAYER_SPEC = LayerSpec(
    overrides={
        10: KeySpec("&kp", (KeySpec("EQUAL"),)),
        11: KeySpec("&kp", (KeySpec("N1"),)),
        12: KeySpec("&kp", (KeySpec("N2"),)),
        13: KeySpec("&kp", (KeySpec("N3"),)),
        14: KeySpec("&kp", (KeySpec("N4"),)),
        15: KeySpec("&kp", (KeySpec("N5"),)),
        16: KeySpec("&kp", (KeySpec("N6"),)),
        17: KeySpec("&kp", (KeySpec("N7"),)),
        18: KeySpec("&kp", (KeySpec("N8"),)),
        19: KeySpec("&kp", (KeySpec("N9"),)),
        20: KeySpec("&kp", (KeySpec("N0"),)),
        21: KeySpec("&kp", (KeySpec("MINUS"),)),
        33: KeySpec("&kp", (KeySpec("BSLH"),)),
        35: KeySpec("&kp", (KeySpec("A"),)),
        36: KeySpec("&kp", (KeySpec("S"),)),
        37: KeySpec("&kp", (KeySpec("D"),)),
        38: KeySpec("&kp", (KeySpec("F"),)),
        41: KeySpec("&kp", (KeySpec("J"),)),
        42: KeySpec("&kp", (KeySpec("K"),)),
        43: KeySpec("&kp", (KeySpec("L"),)),
        44: KeySpec("&kp", (KeySpec("SEMI"),)),
        45: KeySpec("&kp", (KeySpec("SQT"),)),
        46: KeySpec("&kp", (KeySpec("GRAVE"),)),
        52: KeySpec("&kp", (KeySpec("LSHFT"),)),
        53: KeySpec("&kp", (KeySpec("LCTRL"),)),
        55: KeySpec("&kp", (KeySpec("RGUI"),)),
        56: KeySpec("&kp", (KeySpec("RCTRL"),)),
        57: KeySpec("&kp", (KeySpec("RSHFT"),)),
        60: KeySpec("&kp", (KeySpec("COMMA"),)),
        61: KeySpec("&kp", (KeySpec("DOT"),)),
        62: KeySpec("&kp", (KeySpec("FSLH"),)),
        64: KeySpec("&magic"),
        65: KeySpec("&kp", (KeySpec("HOME"),)),
        66: KeySpec("&kp", (KeySpec("END"),)),
        70: KeySpec("&kp", (KeySpec("LGUI"),)),
        71: KeySpec("&kp", (KeySpec("LALT"),)),
        72: KeySpec("&kp", (KeySpec("RALT"),)),
        73: KeySpec("&kp", (KeySpec("RET"),)),
        77: KeySpec("&kp", (KeySpec("LBKT"),)),
        78: KeySpec("&kp", (KeySpec("RBKT"),)),
    }
)


def build_original_layer(_variant: str) -> Layer:
    return build_layer_from_spec(ORIGINAL_LAYER_SPEC)
