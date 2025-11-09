"""Programmatic builders for QuantumTouch finger-training layers."""

from __future__ import annotations

from typing import Callable, Dict, Tuple

from glove80.base import KeySpec, Layer, LayerSpec, build_layer_from_spec
from ..specs.finger_data import FINGER_BY_LABEL, FingerMeta


LEFT_TAP_KEYS: Dict[int, str] = {
    0: "F1",
    1: "F2",
    2: "F3",
    3: "F4",
    4: "F5",
    10: "EQUAL",
    11: "N1",
    12: "N2",
    13: "N3",
    14: "N4",
    15: "N5",
    23: "Q",
    24: "W",
    25: "E",
    26: "R",
    27: "T",
    39: "G",
    47: "Z",
    48: "X",
    49: "C",
    50: "V",
    51: "B",
}

RIGHT_TAP_KEYS: Dict[int, str] = {
    5: "F6",
    6: "F7",
    7: "F8",
    8: "F9",
    9: "F10",
    16: "N6",
    17: "N7",
    18: "N8",
    19: "N9",
    20: "N0",
    21: "MINUS",
    28: "Y",
    29: "U",
    30: "I",
    31: "O",
    32: "P",
    33: "BSLH",
    40: "H",
    45: "SQT",
    58: "N",
    59: "M",
    60: "COMMA",
    61: "DOT",
}

LEFT_KP_KEYS = {41: "J", 42: "K", 43: "L", 44: "SEMI"}
RIGHT_KP_KEYS = {35: "A", 36: "S", 37: "D", 38: "F"}

COMBO_OVERRIDES: Dict[str, Dict[int, Tuple[str | None, Tuple[str, ...]]]] = {
    "LeftIndex": {
        35: ("Pinky", ("LCTRL", "A")),
        36: ("Ring", ("LALT", "S")),
        37: ("Middle", ("LGUI", "D")),
        38: (None, ()),
    },
    "LeftMiddle": {
        35: ("Pinky", ("LCTRL", "A")),
        36: ("Ring", ("LALT", "S")),
        37: (None, ()),
        38: ("Index", ("LSHFT", "F")),
    },
    "LeftRing": {
        35: ("Pinky", ("LCTRL", "A")),
        36: (None, ()),
        37: ("Middle", ("LGUI", "D")),
        38: ("Index", ("LSHFT", "F")),
    },
    "LeftPinky": {
        35: (None, ()),
        36: ("Ring", ("LALT", "S")),
        37: ("Middle", ("LGUI", "D")),
        38: ("Index", ("LSHFT", "F")),
    },
    "RightIndex": {
        41: (None, ()),
        42: ("Middle", ("RGUI", "K")),
        43: ("Ring", ("LALT", "L")),
        44: ("Pinky", ("LCTRL", "SEMI")),
    },
    "RightMiddle": {
        41: ("Index", ("RSHFT", "J")),
        42: (None, ()),
        43: ("Ring", ("LALT", "L")),
        44: ("Pinky", ("RCTRL", "SEMI")),
    },
    "RightRing": {
        41: ("Index", ("RSHFT", "J")),
        42: ("Middle", ("RGUI", "K")),
        43: (None, ()),
        44: ("Pinky", ("RCTRL", "SEMI")),
    },
    "RightPinky": {
        41: ("Index", ("RSHFT", "J")),
        42: ("Middle", ("RGUI", "K")),
        43: ("Ring", ("LALT", "L")),
        44: (None, ()),
    },
}


def _tap_macro(meta: FingerMeta) -> str:
    return f"&BHRM_{meta.hand}_{meta.name}_Tap"


def _partner_macro(meta: FingerMeta, partner: str) -> str:
    return f"&BHRM_{meta.hand}_{meta.name}_{partner}"


def _build_finger_layer(label: str) -> Layer:
    meta = FINGER_BY_LABEL[label]
    tap_keys = LEFT_TAP_KEYS if meta.hand == "L" else RIGHT_TAP_KEYS
    kp_keys = LEFT_KP_KEYS if meta.hand == "L" else RIGHT_KP_KEYS

    overrides: Dict[int, KeySpec] = {}
    tap_macro = _tap_macro(meta)
    for position, key in tap_keys.items():
        overrides[position] = KeySpec(tap_macro, (KeySpec(key),))

    for position, key in kp_keys.items():
        overrides[position] = KeySpec("&kp", (KeySpec(key),))

    for position, (partner, params) in COMBO_OVERRIDES[label].items():
        if partner is None:
            overrides[position] = KeySpec("&none")
            continue
        macro_name = _partner_macro(meta, partner)
        overrides[position] = KeySpec(macro_name, tuple(KeySpec(value) for value in params))

    layer_spec = LayerSpec(overrides=overrides)
    return build_layer_from_spec(layer_spec)


def build_left_index_layer(_variant: str) -> Layer:
    return _build_finger_layer("LeftIndex")


def build_left_middle_layer(_variant: str) -> Layer:
    return _build_finger_layer("LeftMiddle")


def build_left_ring_layer(_variant: str) -> Layer:
    return _build_finger_layer("LeftRing")


def build_left_pinky_layer(_variant: str) -> Layer:
    return _build_finger_layer("LeftPinky")


def build_right_index_layer(_variant: str) -> Layer:
    return _build_finger_layer("RightIndex")


def build_right_middle_layer(_variant: str) -> Layer:
    return _build_finger_layer("RightMiddle")


def build_right_ring_layer(_variant: str) -> Layer:
    return _build_finger_layer("RightRing")


def build_right_pinky_layer(_variant: str) -> Layer:
    return _build_finger_layer("RightPinky")


FINGER_LAYER_BUILDERS: Dict[str, Callable[[str], Layer]] = {
    "LeftIndex": build_left_index_layer,
    "LeftMiddle": build_left_middle_layer,
    "LeftRing": build_left_ring_layer,
    "LeftPinky": build_left_pinky_layer,
    "RightIndex": build_right_index_layer,
    "RightMiddle": build_right_middle_layer,
    "RightRing": build_right_ring_layer,
    "RightPinky": build_right_pinky_layer,
}


__all__ = [
    "build_left_index_layer",
    "build_left_middle_layer",
    "build_left_ring_layer",
    "build_left_pinky_layer",
    "build_right_index_layer",
    "build_right_middle_layer",
    "build_right_ring_layer",
    "build_right_pinky_layer",
    "FINGER_LAYER_BUILDERS",
]
