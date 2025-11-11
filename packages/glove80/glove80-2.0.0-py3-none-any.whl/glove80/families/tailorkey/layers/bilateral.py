"""Bilateral-specific finger layers."""

from __future__ import annotations

from glove80.base import (
    KeySpec,
    LayerMap,
    LayerSpec,
    PatchSpec,
    apply_patch,
    build_layer_from_spec,
)
from glove80.families.tailorkey.alpha_layouts import base_variant_for, needs_alpha_remap, remap_layer_keys

_LEFT_TAP_KEYS: dict[int, str] = {
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

_RIGHT_TAP_KEYS: dict[int, str] = {
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

_LEFT_KP_OVERRIDES: dict[int, KeySpec] = {
    41: KeySpec("&kp", (KeySpec("J"),)),
    42: KeySpec("&kp", (KeySpec("K"),)),
    43: KeySpec("&kp", (KeySpec("L"),)),
    44: KeySpec("&kp", (KeySpec("SEMI"),)),
}

_RIGHT_KP_OVERRIDES: dict[int, KeySpec] = {
    35: KeySpec("&kp", (KeySpec("A"),)),
    36: KeySpec("&kp", (KeySpec("S"),)),
    37: KeySpec("&kp", (KeySpec("D"),)),
    38: KeySpec("&kp", (KeySpec("F"),)),
}

_LEFT_FINGER_SPECS = {
    "LeftIndex": (
        "&HRM_left_index_tap_v1B_TKZ",
        {
            35: KeySpec("&HRM_left_index_pinky_v1B_TKZ", (KeySpec("LGUI"), KeySpec("A"))),
            36: KeySpec("&HRM_left_index_ringv1_TKZ", (KeySpec("LALT"), KeySpec("S"))),
            37: KeySpec("&HRM_left_index_middy_v1B_TKZ", (KeySpec("LCTRL"), KeySpec("D"))),
            38: KeySpec("&none"),
        },
    ),
    "LeftMiddy": (
        "&HRM_left_middy_tap_v1B_TKZ",
        {
            35: KeySpec("&HRM_left_middy_pinky_v1B_TKZ", (KeySpec("LGUI"), KeySpec("A"))),
            36: KeySpec("&HRM_left_middy_ring_v1B_TKZ", (KeySpec("LALT"), KeySpec("S"))),
            37: KeySpec("&none"),
            38: KeySpec("&HRM_left_middy_index_v1B_TKZ", (KeySpec("LSHFT"), KeySpec("F"))),
        },
    ),
    "LeftRingy": (
        "&HRM_left_ring_tap_v1B_TKZ",
        {
            35: KeySpec("&HRM_left_ring_pinky_v1B_TKZ", (KeySpec("LGUI"), KeySpec("A"))),
            36: KeySpec("&none"),
            37: KeySpec("&HRM_left_ring_middy_v1B_TKZ", (KeySpec("LCTRL"), KeySpec("D"))),
            38: KeySpec("&HRM_left_ring_index_v1B_TKZ", (KeySpec("LSHFT"), KeySpec("F"))),
        },
    ),
    "LeftPinky": (
        "&HRM_left_pinky_tap_v1B_TKZ",
        {
            35: KeySpec("&none"),
            36: KeySpec("&HRM_left_pinky_ring_v1B_TKZ", (KeySpec("LALT"), KeySpec("S"))),
            37: KeySpec("&HRM_left_pinky_middy_v1B_TKZ", (KeySpec("LCTRL"), KeySpec("D"))),
            38: KeySpec("&HRM_left_pinky_index_v1B_TKZ", (KeySpec("LSHFT"), KeySpec("F"))),
        },
    ),
}

_RIGHT_FINGER_SPECS = {
    "RightIndex": (
        "&HRM_right_index_tap_v1B_TKZ",
        {
            41: KeySpec("&none"),
            42: KeySpec("&HRM_right_index_middy_v1B_TKZ", (KeySpec("RCTRL"), KeySpec("K"))),
            43: KeySpec("&HRM_right_index_ring_v1B_TKZ", (KeySpec("LALT"), KeySpec("L"))),
            44: KeySpec("&HRM_right_index_pinky_v1B_TKZ", (KeySpec("RGUI"), KeySpec("SEMI"))),
        },
    ),
    "RightMiddy": (
        "&HRM_right_middy_tap_v1B_TKZ",
        {
            41: KeySpec("&HRM_right_middy_index_v1B_TKZ", (KeySpec("RSHFT"), KeySpec("J"))),
            42: KeySpec("&none"),
            43: KeySpec("&HRM_right_middy_ring_v1B_TKZ", (KeySpec("LALT"), KeySpec("L"))),
            44: KeySpec("&HRM_right_middy_pinky_v1B_TKZ", (KeySpec("RGUI"), KeySpec("SEMI"))),
        },
    ),
    "RightRingy": (
        "&HRM_right_ring_tap_v1B_TKZ",
        {
            41: KeySpec("&HRM_right_ring_index_v1B_TKZ", (KeySpec("RSHFT"), KeySpec("J"))),
            42: KeySpec("&HRM_right_ring_middy_v1B_TKZ", (KeySpec("RCTRL"), KeySpec("K"))),
            43: KeySpec("&none"),
            44: KeySpec("&HRM_right_ring_pinky_v1B_TKZ", (KeySpec("RGUI"), KeySpec("SEMI"))),
        },
    ),
    "RightPinky": (
        "&HRM_right_pinky_tap_v1B_TKZ",
        {
            41: KeySpec("&HRM_right_pinky_index_v1B_TKZ", (KeySpec("RSHFT"), KeySpec("J"))),
            42: KeySpec("&HRM_right_pinky_middy_v1B_TKZ", (KeySpec("RCTRL"), KeySpec("K"))),
            43: KeySpec("&HRM_right_pinky_ring_v1B_TKZ", (KeySpec("LALT"), KeySpec("L"))),
            44: KeySpec("&none"),
        },
    ),
}


def _build_left_layer_spec(tap_macro: str, extras: dict[int, KeySpec]) -> LayerSpec:
    overrides = {index: KeySpec(tap_macro, (KeySpec(code),)) for index, code in _LEFT_TAP_KEYS.items()}
    overrides.update(_LEFT_KP_OVERRIDES)
    overrides.update(extras)
    return LayerSpec(overrides=overrides, length=80)


def _build_right_layer_spec(tap_macro: str, extras: dict[int, KeySpec]) -> LayerSpec:
    overrides = {index: KeySpec(tap_macro, (KeySpec(code),)) for index, code in _RIGHT_TAP_KEYS.items()}
    overrides.update(_RIGHT_KP_OVERRIDES)
    overrides.update(extras)
    return LayerSpec(overrides=overrides, length=80)


_BILATERAL_LAYER_SPECS: dict[str, LayerSpec] = {
    name: _build_left_layer_spec(tap_macro, extras) for name, (tap_macro, extras) in _LEFT_FINGER_SPECS.items()
}
_BILATERAL_LAYER_SPECS.update(
    {name: _build_right_layer_spec(tap_macro, extras) for name, (tap_macro, extras) in _RIGHT_FINGER_SPECS.items()},
)


def _build_bilateral_layers() -> LayerMap:
    return {name: build_layer_from_spec(spec) for name, spec in _BILATERAL_LAYER_SPECS.items()}


_MAC_PATCHES: dict[str, PatchSpec] = {
    "LeftIndex": {
        35: KeySpec("&HRM_left_index_pinky_v1B_TKZ", (KeySpec("LCTRL"), KeySpec("A"))),
        37: KeySpec("&HRM_left_index_middy_v1B_TKZ", (KeySpec("LGUI"), KeySpec("D"))),
    },
    "LeftMiddy": {
        35: KeySpec("&HRM_left_middy_pinky_v1B_TKZ", (KeySpec("LCTRL"), KeySpec("A"))),
    },
    "LeftRingy": {
        35: KeySpec("&HRM_left_ring_pinky_v1B_TKZ", (KeySpec("LCTRL"), KeySpec("A"))),
        37: KeySpec("&HRM_left_ring_middy_v1B_TKZ", (KeySpec("LGUI"), KeySpec("D"))),
    },
    "LeftPinky": {
        37: KeySpec("&HRM_left_pinky_middy_v1B_TKZ", (KeySpec("LGUI"), KeySpec("D"))),
    },
    "RightIndex": {
        42: KeySpec("&HRM_right_index_middy_v1B_TKZ", (KeySpec("RGUI"), KeySpec("K"))),
        44: KeySpec("&HRM_right_index_pinky_v1B_TKZ", (KeySpec("LCTRL"), KeySpec("SEMI"))),
    },
    "RightMiddy": {
        44: KeySpec("&HRM_right_middy_pinky_v1B_TKZ", (KeySpec("RCTRL"), KeySpec("SEMI"))),
    },
    "RightRingy": {
        42: KeySpec("&HRM_right_ring_middy_v1B_TKZ", (KeySpec("RGUI"), KeySpec("K"))),
        44: KeySpec("&HRM_right_ring_pinky_v1B_TKZ", (KeySpec("RCTRL"), KeySpec("SEMI"))),
    },
    "RightPinky": {
        42: KeySpec("&HRM_right_pinky_middy_v1B_TKZ", (KeySpec("RGUI"), KeySpec("K"))),
    },
}


def assemble_bilateral_layers(variant: str, *, mac: bool = False, remap: bool = True) -> LayerMap:
    """Return bilateral layers tailored for the requested platform/variant."""
    layers = _build_bilateral_layers()
    if mac:
        for name, patch in _MAC_PATCHES.items():
            apply_patch(layers[name], patch)

    if remap and needs_alpha_remap(variant):
        for layer in layers.values():
            remap_layer_keys(layer, variant)

    return layers


def build_bilateral_finger_layers(variant: str) -> LayerMap:
    """Return the eight bilateral finger layers if needed."""
    base_variant = base_variant_for(variant)
    if base_variant not in {"bilateral_windows", "bilateral_mac"}:
        return {}

    return assemble_bilateral_layers(variant, mac=(base_variant == "bilateral_mac"))
