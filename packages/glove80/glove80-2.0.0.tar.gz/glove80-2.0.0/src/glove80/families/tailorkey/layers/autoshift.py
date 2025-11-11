"""Autoshift layer generation."""

from __future__ import annotations

from glove80.base import KeySpec, Layer, LayerSpec, build_layer_from_spec, copy_layer
from glove80.families.tailorkey.alpha_layouts import needs_alpha_remap, remap_layer_keys

AUTOSHIFT_SPEC = LayerSpec(
    overrides={
        10: KeySpec("&AS_v1_TKZ", (KeySpec("EQUAL"),)),
        11: KeySpec("&AS_v1_TKZ", (KeySpec("N1"),)),
        12: KeySpec("&AS_v1_TKZ", (KeySpec("N2"),)),
        13: KeySpec("&AS_v1_TKZ", (KeySpec("N3"),)),
        14: KeySpec("&AS_v1_TKZ", (KeySpec("N4"),)),
        15: KeySpec("&AS_v1_TKZ", (KeySpec("N5"),)),
        16: KeySpec("&AS_v1_TKZ", (KeySpec("N6"),)),
        17: KeySpec("&AS_v1_TKZ", (KeySpec("N7"),)),
        18: KeySpec("&AS_v1_TKZ", (KeySpec("N8"),)),
        19: KeySpec("&AS_v1_TKZ", (KeySpec("N9"),)),
        20: KeySpec("&AS_v1_TKZ", (KeySpec("N0"),)),
        21: KeySpec("&AS_v1_TKZ", (KeySpec("MINUS"),)),
        23: KeySpec("&AS_v1_TKZ", (KeySpec("Q"),)),
        24: KeySpec("&AS_v1_TKZ", (KeySpec("W"),)),
        25: KeySpec("&AS_v1_TKZ", (KeySpec("E"),)),
        26: KeySpec("&AS_v1_TKZ", (KeySpec("R"),)),
        27: KeySpec("&AS_v1_TKZ", (KeySpec("T"),)),
        28: KeySpec("&AS_v1_TKZ", (KeySpec("Y"),)),
        29: KeySpec("&AS_v1_TKZ", (KeySpec("U"),)),
        30: KeySpec("&AS_v1_TKZ", (KeySpec("I"),)),
        31: KeySpec("&AS_v1_TKZ", (KeySpec("O"),)),
        32: KeySpec("&AS_v1_TKZ", (KeySpec("P"),)),
        33: KeySpec("&AS_v1_TKZ", (KeySpec("BSLH"),)),
        35: KeySpec("&AS_v1_TKZ", (KeySpec("A"),)),
        36: KeySpec("&AS_v1_TKZ", (KeySpec("S"),)),
        37: KeySpec("&AS_v1_TKZ", (KeySpec("D"),)),
        38: KeySpec("&AS_v1_TKZ", (KeySpec("F"),)),
        39: KeySpec("&AS_v1_TKZ", (KeySpec("G"),)),
        40: KeySpec("&AS_v1_TKZ", (KeySpec("H"),)),
        41: KeySpec("&AS_v1_TKZ", (KeySpec("J"),)),
        42: KeySpec("&AS_v1_TKZ", (KeySpec("K"),)),
        43: KeySpec("&AS_v1_TKZ", (KeySpec("L"),)),
        44: KeySpec("&AS_v1_TKZ", (KeySpec("SEMI"),)),
        45: KeySpec("&AS_v1_TKZ", (KeySpec("SQT"),)),
        46: KeySpec("&AS_v1_TKZ", (KeySpec("GRAVE"),)),
        47: KeySpec("&AS_v1_TKZ", (KeySpec("Z"),)),
        48: KeySpec("&AS_v1_TKZ", (KeySpec("X"),)),
        49: KeySpec("&AS_v1_TKZ", (KeySpec("C"),)),
        50: KeySpec("&AS_v1_TKZ", (KeySpec("V"),)),
        51: KeySpec("&AS_v1_TKZ", (KeySpec("B"),)),
        58: KeySpec("&AS_v1_TKZ", (KeySpec("N"),)),
        59: KeySpec("&AS_v1_TKZ", (KeySpec("M"),)),
        60: KeySpec("&AS_v1_TKZ", (KeySpec("COMMA"),)),
        61: KeySpec("&AS_v1_TKZ", (KeySpec("DOT"),)),
        62: KeySpec("&AS_v1_TKZ", (KeySpec("FSLH"),)),
        64: KeySpec("&magic"),
        77: KeySpec("&AS_v1_TKZ", (KeySpec("LBKT"),)),
        78: KeySpec("&AS_v1_TKZ", (KeySpec("RBKT"),)),
    },
)

_BASE_AUTOSHIFT_LAYER: Layer = build_layer_from_spec(AUTOSHIFT_SPEC)


def build_autoshift_layer(variant: str) -> Layer:
    layer = copy_layer(_BASE_AUTOSHIFT_LAYER)
    if needs_alpha_remap(variant):
        remap_layer_keys(layer, variant)
    return layer
