"""QuantumTouch HRM layer."""

from __future__ import annotations

from glove80.base import KeySpec, Layer, LayerSpec, build_layer_from_spec


HRM_LAYER_SPEC = LayerSpec(
    overrides={
        35: KeySpec("&BHRM_L_Pinky", (KeySpec("LCTRL"), KeySpec("A"))),
        36: KeySpec("&BHRM_L_Ring", (KeySpec("LALT"), KeySpec("S"))),
        37: KeySpec("&BHRM_L_Middle", (KeySpec("LGUI"), KeySpec("D"))),
        38: KeySpec("&BHRM_L_Index", (KeySpec("LSHFT"), KeySpec("F"))),
        41: KeySpec("&BHRM_R_Index", (KeySpec("RSHFT"), KeySpec("J"))),
        42: KeySpec("&BHRM_R_Middle", (KeySpec("RGUI"), KeySpec("K"))),
        43: KeySpec("&BHRM_R_Ring", (KeySpec("LALT"), KeySpec("L"))),
        44: KeySpec("&BHRM_R_Pinky", (KeySpec("RCTRL"), KeySpec("SEMI"))),
    }
)


def build_hrm_layer(_variant: str) -> Layer:
    return build_layer_from_spec(HRM_LAYER_SPEC)
