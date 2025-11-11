"""Home-row modifier layers."""

from __future__ import annotations

from glove80.base import (
    KeySpec,
    Layer,
    LayerMap,
    LayerSpec,
    PatchSpec,
    apply_patch,
    build_layer_from_spec,
    copy_layer,
)
from glove80.families.tailorkey.alpha_layouts import base_variant_for, needs_alpha_remap, remap_layer_keys

_BASE_HRM_SPEC = LayerSpec(
    overrides={
        0: KeySpec("&kp", (KeySpec("F1"),)),
        1: KeySpec("&kp", (KeySpec("F2"),)),
        2: KeySpec("&kp", (KeySpec("F3"),)),
        3: KeySpec("&kp", (KeySpec("F4"),)),
        4: KeySpec("&kp", (KeySpec("F5"),)),
        5: KeySpec("&kp", (KeySpec("F6"),)),
        6: KeySpec("&kp", (KeySpec("F7"),)),
        7: KeySpec("&kp", (KeySpec("F8"),)),
        8: KeySpec("&kp", (KeySpec("F9"),)),
        9: KeySpec("&kp", (KeySpec("F10"),)),
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
        22: KeySpec("&kp", (KeySpec("TAB"),)),
        23: KeySpec("&kp", (KeySpec("Q"),)),
        24: KeySpec("&kp", (KeySpec("W"),)),
        25: KeySpec("&kp", (KeySpec("E"),)),
        26: KeySpec("&kp", (KeySpec("R"),)),
        27: KeySpec("&kp", (KeySpec("T"),)),
        28: KeySpec("&kp", (KeySpec("Y"),)),
        29: KeySpec("&kp", (KeySpec("U"),)),
        30: KeySpec("&kp", (KeySpec("I"),)),
        31: KeySpec("&kp", (KeySpec("O"),)),
        32: KeySpec("&kp", (KeySpec("P"),)),
        33: KeySpec("&kp", (KeySpec("BSLH"),)),
        34: KeySpec("&kp", (KeySpec("ESC"),)),
        35: KeySpec("&HRM_left_pinky_v1_TKZ", (KeySpec("LGUI"), KeySpec("A"))),
        36: KeySpec("&HRM_left_ring_v1_TKZ", (KeySpec("LALT"), KeySpec("S"))),
        37: KeySpec("&HRM_left_middy_v1_TKZ", (KeySpec("LCTRL"), KeySpec("D"))),
        38: KeySpec("&HRM_left_index_v1_TKZ", (KeySpec("LSHFT"), KeySpec("F"))),
        39: KeySpec("&kp", (KeySpec("G"),)),
        40: KeySpec("&kp", (KeySpec("H"),)),
        41: KeySpec("&HRM_right_index_v1_TKZ", (KeySpec("RSHFT"), KeySpec("J"))),
        42: KeySpec("&HRM_right_middy_v1_TKZ", (KeySpec("RCTRL"), KeySpec("K"))),
        43: KeySpec("&HRM_right_ring_v1_TKZ", (KeySpec("LALT"), KeySpec("L"))),
        44: KeySpec("&HRM_right_pinky_v1_TKZ", (KeySpec("LGUI"), KeySpec("SEMI"))),
        45: KeySpec("&kp", (KeySpec("SQT"),)),
        46: KeySpec("&kp", (KeySpec("GRAVE"),)),
        47: KeySpec("&kp", (KeySpec("Z"),)),
        48: KeySpec("&kp", (KeySpec("X"),)),
        49: KeySpec("&kp", (KeySpec("C"),)),
        50: KeySpec("&kp", (KeySpec("V"),)),
        51: KeySpec("&kp", (KeySpec("B"),)),
        52: KeySpec("&CAPSWord_v1_TKZ", (KeySpec("LSHFT"),)),
        53: KeySpec("&kp", (KeySpec("LCTRL"),)),
        54: KeySpec("&lower"),
        55: KeySpec("&kp", (KeySpec("LGUI"),)),
        56: KeySpec("&kp", (KeySpec("RCTRL"),)),
        57: KeySpec("&CAPSWord_v1_TKZ", (KeySpec("RSHFT"),)),
        58: KeySpec("&kp", (KeySpec("N"),)),
        59: KeySpec("&kp", (KeySpec("M"),)),
        60: KeySpec("&kp", (KeySpec("COMMA"),)),
        61: KeySpec("&kp", (KeySpec("DOT"),)),
        62: KeySpec("&kp", (KeySpec("FSLH"),)),
        63: KeySpec("&kp", (KeySpec("PG_UP"),)),
        64: KeySpec("&magic"),
        65: KeySpec("&kp", (KeySpec("HOME"),)),
        66: KeySpec("&kp", (KeySpec("END"),)),
        67: KeySpec("&kp", (KeySpec("LEFT"),)),
        68: KeySpec("&kp", (KeySpec("RIGHT"),)),
        69: KeySpec("&thumb_v2_TKZ", (KeySpec(3), KeySpec("BSPC"))),
        70: KeySpec("&kp", (KeySpec("DEL"),)),
        71: KeySpec("&kp", (KeySpec("LALT"),)),
        72: KeySpec("&kp", (KeySpec("RALT"),)),
        73: KeySpec("&thumb_v2_TKZ", (KeySpec(7), KeySpec("RET"))),
        74: KeySpec("&space_v3_TKZ", (KeySpec(4), KeySpec("SPACE"))),
        75: KeySpec("&kp", (KeySpec("UP"),)),
        76: KeySpec("&kp", (KeySpec("DOWN"),)),
        77: KeySpec("&kp", (KeySpec("LBKT"),)),
        78: KeySpec("&kp", (KeySpec("RBKT"),)),
        79: KeySpec("&kp", (KeySpec("PG_DN"),)),
    },
    length=80,
)

_BASE_HRM_LAYER: Layer = build_layer_from_spec(_BASE_HRM_SPEC)


_MAC_PATCH: PatchSpec = {
    35: KeySpec("&HRM_left_pinky_v1_TKZ", (KeySpec("LCTRL"), KeySpec("A"))),
    37: KeySpec("&HRM_left_middy_v1_TKZ", (KeySpec("LGUI"), KeySpec("D"))),
    42: KeySpec("&HRM_right_middy_v1_TKZ", (KeySpec("RGUI"), KeySpec("K"))),
    44: KeySpec("&HRM_right_pinky_v1_TKZ", (KeySpec("RCTRL"), KeySpec("SEMI"))),
    53: KeySpec("&kp", (KeySpec("LGUI"),)),
    55: KeySpec("&kp", (KeySpec("LCTRL"),)),
    56: KeySpec("&kp", (KeySpec("RGUI"),)),
}

_DUAL_PATCH: PatchSpec = {
    69: KeySpec("&thumb_v2_TKZ", (KeySpec(5), KeySpec("BSPC"))),
    74: KeySpec("&space_v3_TKZ", (KeySpec(6), KeySpec("SPACE"))),
}

_DUAL_MAC_PATCH: PatchSpec = {
    69: KeySpec("&thumb_v2_TKZ", (KeySpec(4), KeySpec("BSPC"))),
    74: KeySpec("&space_v3_TKZ", (KeySpec(6), KeySpec("SPACE"))),
}

_BILATERAL_WIN_PATCH: PatchSpec = {
    35: KeySpec("&HRM_left_pinky_v1B_TKZ", (KeySpec("LGUI"), KeySpec("A"))),
    36: KeySpec("&HRM_left_ring_v1B_TKZ", (KeySpec("LALT"), KeySpec("S"))),
    37: KeySpec("&HRM_left_middy_v1B_TKZ", (KeySpec("LCTRL"), KeySpec("D"))),
    38: KeySpec("&HRM_left_index_v1B_TKZ", (KeySpec("LSHFT"), KeySpec("F"))),
    41: KeySpec("&HRM_right_index_v1B_TKZ", (KeySpec("RSHFT"), KeySpec("J"))),
    42: KeySpec("&HRM_right_middy_v1B_TKZ", (KeySpec("RCTRL"), KeySpec("K"))),
    43: KeySpec("&HRM_right_ring_v1B_TKZ", (KeySpec("LALT"), KeySpec("L"))),
    44: KeySpec("&HRM_right_pinky_v1B_TKZ", (KeySpec("RGUI"), KeySpec("SEMI"))),
    73: KeySpec("&thumb_v2_TKZ", (KeySpec(15), KeySpec("RET"))),
}

_BILATERAL_MAC_PATCH: PatchSpec = {
    35: KeySpec("&HRM_left_pinky_v1B_TKZ", (KeySpec("LCTRL"), KeySpec("A"))),
    36: KeySpec("&HRM_left_ring_v1B_TKZ", (KeySpec("LALT"), KeySpec("S"))),
    37: KeySpec("&HRM_left_middy_v1B_TKZ", (KeySpec("LGUI"), KeySpec("D"))),
    38: KeySpec("&HRM_left_index_v1B_TKZ", (KeySpec("LSHFT"), KeySpec("F"))),
    41: KeySpec("&HRM_right_index_v1B_TKZ", (KeySpec("RSHFT"), KeySpec("J"))),
    42: KeySpec("&HRM_right_middy_v1B_TKZ", (KeySpec("RGUI"), KeySpec("K"))),
    43: KeySpec("&HRM_right_ring_v1B_TKZ", (KeySpec("LALT"), KeySpec("L"))),
    44: KeySpec("&HRM_right_pinky_v1B_TKZ", (KeySpec("RCTRL"), KeySpec("SEMI"))),
    73: KeySpec("&thumb_v2_TKZ", (KeySpec(15), KeySpec("RET"))),
}


def _maybe_remap(layer: Layer, variant: str, remap_required: bool) -> None:
    if remap_required:
        remap_layer_keys(layer, variant)


def build_hrm_layers(variant: str) -> LayerMap:
    """Return the HRM layers needed for the variant."""
    layers: LayerMap = {}
    remap_required = needs_alpha_remap(variant)
    base_variant = base_variant_for(variant)

    if base_variant == "windows":
        layer = copy_layer(_BASE_HRM_LAYER)
        _maybe_remap(layer, variant, remap_required)
        layers["HRM_WinLinx"] = layer
    elif base_variant == "mac":
        layer = copy_layer(_BASE_HRM_LAYER)
        apply_patch(layer, _MAC_PATCH)
        _maybe_remap(layer, variant, remap_required)
        layers["HRM_macOS"] = layer
    elif base_variant == "dual":
        win_layer = copy_layer(_BASE_HRM_LAYER)
        apply_patch(win_layer, _DUAL_PATCH)
        _maybe_remap(win_layer, variant, remap_required)
        layers["HRM_WinLinx"] = win_layer

        mac_layer = copy_layer(_BASE_HRM_LAYER)
        apply_patch(mac_layer, _MAC_PATCH)
        apply_patch(mac_layer, _DUAL_MAC_PATCH)
        _maybe_remap(mac_layer, variant, remap_required)
        layers["HRM_macOS"] = mac_layer
    elif base_variant == "bilateral_windows":
        layer = copy_layer(_BASE_HRM_LAYER)
        apply_patch(layer, _BILATERAL_WIN_PATCH)
        _maybe_remap(layer, variant, remap_required)
        layers["HRM_WinLinx"] = layer
    elif base_variant == "bilateral_mac":
        layer = copy_layer(_BASE_HRM_LAYER)
        apply_patch(layer, _MAC_PATCH)
        apply_patch(layer, _BILATERAL_MAC_PATCH)
        _maybe_remap(layer, variant, remap_required)
        layers["HRM_macOS"] = layer
    else:  # pragma: no cover
        msg = f"Unsupported variant: {variant}"
        raise ValueError(msg)

    return layers
