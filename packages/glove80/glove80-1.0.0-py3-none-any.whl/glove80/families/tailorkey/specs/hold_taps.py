"""Hold-tap specifications for TailorKey variants."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from glove80.specs import HoldTapSpec

from .finger_data import FINGERS

FINGER_MAP = {f"{meta.hand}_{meta.finger}": meta for meta in FINGERS}
INDEX_IDLE_MS = FINGER_MAP["left_index"].require_prior_idle_ms


BASE_DESCRIPTIONS = {
    "left_index": "Homerow Mod for the left index finger - TailorKey.\nFor advanced tuning of HRM values, see: https://docs.google.com/spreadsheets/d/1ESgObQelyz4lnKlfwLYsmofLJulOMK5RdGBsopLe2o8",
    "left_middy": "Homerow Mod for the left middle finger - TailorKey",
    "left_ring": "Homerow Mod for the left ring finger 1 - TailorKey",
    "left_pinky": "Homerow Mod for the left pinky - TailorKey",
    "right_index": "Homerow Mod for the right index finger - TailorKey",
    "right_middy": "Homerow Mod for the right middle finger - TailorKey",
    "right_ring": "Homerow Mod for the right ring 1 - TailorKey\n",
    "right_pinky": "Homerow Mod for the right pinky - TailorKey",
}


HOLD_TAP_DEFS: Dict[str, HoldTapSpec] = {
    "&AS_HT_v2_TKZ": HoldTapSpec(
        name="&AS_HT_v2_TKZ",
        description="AutoShift Helper - &AS main macro is chained to &AS_HT hold tap and &AS_Shifted macro. For faster typists, it is recommended to decrease the tapping-term-ms value. A suggested value is 135 ms.\nMore: https://github.com/nickcoutsos/keymap-editor/wiki/Autoshift-using-ZMK-behaviors",
        bindings=("&AS_Shifted_v1_TKZ", "&kp"),
        tapping_term_ms=190,
        flavor="tap-preferred",
    ),
    "&CAPSWord_v1_TKZ": HoldTapSpec(
        name="&CAPSWord_v1_TKZ",
        description="Capsword helper - tap for caps_word - hold for key press",
        bindings=("&kp", "&caps_word"),
        tapping_term_ms=200,
    ),
    "&space_v3_TKZ": HoldTapSpec(
        name="&space_v3_TKZ",
        description="space_layer_access - TailorKey",
        bindings=("&mo", "&kp"),
        tapping_term_ms=200,
        flavor="balanced",
        quick_tap_ms=150,
    ),
    "&thumb_v2_TKZ": HoldTapSpec(
        name="&thumb_v2_TKZ",
        description="thumb_layer_access - TailorKey",
        bindings=("&mo", "&kp"),
        tapping_term_ms=200,
        flavor="balanced",
        quick_tap_ms=300,
    ),
}

for key, description in BASE_DESCRIPTIONS.items():
    meta = FINGER_MAP[key]
    name = f"&HRM_{meta.hand}_{meta.finger}_v1_TKZ"
    HOLD_TAP_DEFS[name] = HoldTapSpec(
        name=name,
        description=description,
        bindings=("&kp", "&kp"),
        tapping_term_ms=meta.tapping_term_ms,
        flavor="tap-preferred",
        quick_tap_ms=meta.quick_tap_ms,
        require_prior_idle_ms=meta.require_prior_idle_ms,
        hold_trigger_on_release=True,
        hold_trigger_key_positions=meta.hold_trigger_positions,
    )


@dataclass(frozen=True)
class BilateralTemplate:
    name: str
    finger_key: str
    description: str
    binding_kind: str  # "hold" or "tap"


BILATERAL_TEMPLATES: Tuple[BilateralTemplate, ...] = (
    BilateralTemplate(
        name="&HRM_left_index_middy_v1B_TKZ",
        finger_key="left_index",
        description="HRM_left_index_middy_bilateral -> &kp - &HRM_left_index_tap - TailorKey",
        binding_kind="tap",
    ),
    BilateralTemplate(
        name="&HRM_left_index_pinky_v1B_TKZ",
        finger_key="left_index",
        description="HRM_left_index_pinky_bilateral -> &kp - &HRM_left_index_tap - TailorKey",
        binding_kind="tap",
    ),
    BilateralTemplate(
        name="&HRM_left_index_ringv1_TKZ",
        finger_key="left_index",
        description="HRM_left_index_ring_bilateral -> &kp - &HRM_left_index_tap - TailorKey",
        binding_kind="tap",
    ),
    BilateralTemplate(
        name="&HRM_left_index_v1B_TKZ",
        finger_key="left_index",
        description="HRM_left_index_bilateral -> &HRM_left_index_hold -> &kp - TailorKey",
        binding_kind="hold",
    ),
    BilateralTemplate(
        name="&HRM_left_middy_index_v1B_TKZ",
        finger_key="left_middy",
        description="HRM_left_middy_index_bilateral  -> &kp ->&HRM_left_middy_tap - TailorKey",
        binding_kind="tap",
    ),
    BilateralTemplate(
        name="&HRM_left_middy_pinky_v1B_TKZ",
        finger_key="left_middy",
        description="HRM_left_middy_pinky_bilateral -> &kp - &HRM_left_pinky_tap - TailorKey",
        binding_kind="tap",
    ),
    BilateralTemplate(
        name="&HRM_left_middy_ring_v1B_TKZ",
        finger_key="left_middy",
        description="HRM_left_middy_ring_bilateral -> &kp - &HRM_left_middy_tap - TailorKey",
        binding_kind="tap",
    ),
    BilateralTemplate(
        name="&HRM_left_middy_v1B_TKZ",
        finger_key="left_middy",
        description="HRM_left_middy_bilateral -> &HRM_left_index_hold -> &kp - TailorKey",
        binding_kind="hold",
    ),
    BilateralTemplate(
        name="&HRM_left_pinky_index_v1B_TKZ",
        finger_key="left_pinky",
        description="HRM_left_pinky_index_bilateral  -> &kp ->&HRM_left_pinky_tap - TailorKey",
        binding_kind="tap",
    ),
    BilateralTemplate(
        name="&HRM_left_pinky_middy_v1B_TKZ",
        finger_key="left_pinky",
        description="HRM_left_pinky_middy_bilateral -> &kp - &HRM_left_pinky_tap - TailorKey",
        binding_kind="tap",
    ),
    BilateralTemplate(
        name="&HRM_left_pinky_ring_v1B_TKZ",
        finger_key="left_pinky",
        description="HRM_left_pinky_ring_bilateral -> &kp - &HRM_left_pinky_tap - TailorKey",
        binding_kind="tap",
    ),
    BilateralTemplate(
        name="&HRM_left_pinky_v1B_TKZ",
        finger_key="left_pinky",
        description="HRM_left_pinky_bilateral  - &HRM_left_pinky_hold -> &kp - TailorKey",
        binding_kind="hold",
    ),
    BilateralTemplate(
        name="&HRM_left_ring_index_v1B_TKZ",
        finger_key="left_ring",
        description="HRM_left_ring_index_bilateral  -> &kp ->&HRM_left_ring_tap - TailorKey",
        binding_kind="tap",
    ),
    BilateralTemplate(
        name="&HRM_left_ring_middy_v1B_TKZ",
        finger_key="left_ring",
        description="HRM_left_ring_middy_bilateral -> &kp - &HRM_left_ring_tap - TailorKey",
        binding_kind="tap",
    ),
    BilateralTemplate(
        name="&HRM_left_ring_pinky_v1B_TKZ",
        finger_key="left_ring",
        description="HRM_left_ring_pinky_bilateral -> &kp - &HRM_left_ring_tap - TailorKey",
        binding_kind="tap",
    ),
    BilateralTemplate(
        name="&HRM_left_ring_v1B_TKZ",
        finger_key="left_ring",
        description="HRM_left_ring_bilateral  - &HRM_left_ring_hold -> &kp - TailorKey",
        binding_kind="hold",
    ),
    BilateralTemplate(
        name="&HRM_right_index_middy_v1B_TKZ",
        finger_key="right_index",
        description="HRM_right_index_middy_bilateral -> &kp - &HRM_right_index_tap - TailorKey",
        binding_kind="tap",
    ),
    BilateralTemplate(
        name="&HRM_right_index_pinky_v1B_TKZ",
        finger_key="right_index",
        description="HRM_right_index_pinky_bilateral -> &kp - &HRM_right_index_tap - TailorKey",
        binding_kind="tap",
    ),
    BilateralTemplate(
        name="&HRM_right_index_ring_v1B_TKZ",
        finger_key="right_index",
        description="HRM_right_index_ring_bilateral -> &kp - &HRM_right_index_tap - TailorKey",
        binding_kind="tap",
    ),
    BilateralTemplate(
        name="&HRM_right_index_v1B_TKZ",
        finger_key="right_index",
        description="HRM_right_index_bilateral -> &HRM_right_index_hold -> &kp - TailorKey",
        binding_kind="hold",
    ),
    BilateralTemplate(
        name="&HRM_right_middy_index_v1B_TKZ",
        finger_key="right_middy",
        description="HRM_right_middy_index_bilateral  -> &kp ->&HRM_right_middy_tap - TailorKey",
        binding_kind="tap",
    ),
    BilateralTemplate(
        name="&HRM_right_middy_pinky_v1B_TKZ",
        finger_key="right_middy",
        description="HRM_right_middy_pinky_bilateral -> &kp - &HRM_right_pinky_tap - TailorKey",
        binding_kind="tap",
    ),
    BilateralTemplate(
        name="&HRM_right_middy_ring_v1B_TKZ",
        finger_key="right_middy",
        description="HRM_right_middy_ring_bilateral -> &kp - &HRM_right_middy_tap - TailorKey",
        binding_kind="tap",
    ),
    BilateralTemplate(
        name="&HRM_right_middy_v1B_TKZ",
        finger_key="right_middy",
        description="HRM_right_middy_bilateral -> &HRM_right_index_hold -> &kp - TailorKey",
        binding_kind="hold",
    ),
    BilateralTemplate(
        name="&HRM_right_pinky_index_v1B_TKZ",
        finger_key="right_pinky",
        description="HRM_right_pinky_index_bilateral  -> &kp ->&HRM_right_pinky_tap - TailorKey",
        binding_kind="tap",
    ),
    BilateralTemplate(
        name="&HRM_right_pinky_middy_v1B_TKZ",
        finger_key="right_pinky",
        description="HRM_right_pinky_middy_bilateral -> &kp - &HRM_right_pinky_tap - TailorKey",
        binding_kind="tap",
    ),
    BilateralTemplate(
        name="&HRM_right_pinky_ring_v1B_TKZ",
        finger_key="right_pinky",
        description="HRM_right_pinky_ring_bilateral -> &kp - &HRM_right_pinky_tap - TailorKey",
        binding_kind="tap",
    ),
    BilateralTemplate(
        name="&HRM_right_pinky_v1B_TKZ",
        finger_key="right_pinky",
        description="HRM_right_pinky_bilateral  - &HRM_right_pinky_hold -> &kp - TailorKey",
        binding_kind="hold",
    ),
    BilateralTemplate(
        name="&HRM_right_ring_index_v1B_TKZ",
        finger_key="right_ring",
        description="HRM_right_ring_index_bilateral  -> &kp ->&HRM_right_ring_tap - TailorKey",
        binding_kind="tap",
    ),
    BilateralTemplate(
        name="&HRM_right_ring_middy_v1B_TKZ",
        finger_key="right_ring",
        description="HRM_right_ring_middy_bilateral -> &kp - &HRM_right_ring_tap - TailorKey",
        binding_kind="tap",
    ),
    BilateralTemplate(
        name="&HRM_right_ring_pinky_v1B_TKZ",
        finger_key="right_ring",
        description="HRM_right_ring_pinky_bilateral -> &kp - &HRM_right_ring_tap - TailorKey",
        binding_kind="tap",
    ),
    BilateralTemplate(
        name="&HRM_right_ring_v1B_TKZ",
        finger_key="right_ring",
        description="HRM_right_ring_bilateral  - &HRM_right_ring_hold -> &kp - TailorKey",
        binding_kind="hold",
    ),
)


POSITION_OVERRIDES = {
    "&HRM_right_middy_pinky_v1B_TKZ": (
        0,
        10,
        22,
        46,
        64,
        65,
        47,
        52,
        51,
        39,
        27,
        15,
        4,
        3,
        2,
        1,
        11,
        23,
        35,
        34,
        48,
        66,
        69,
        70,
        71,
        54,
        53,
        55,
        56,
        57,
        74,
        73,
        72,
        68,
        67,
        49,
        50,
        38,
        26,
        14,
        13,
        25,
        37,
        24,
        12,
        36,
    )
}


def _build_bilateral_spec(template: BilateralTemplate) -> HoldTapSpec:
    meta = FINGER_MAP[template.finger_key]
    if template.binding_kind == "hold":
        bindings = (f"&HRM_{meta.hand}_{meta.finger}_hold_v1B_TKZ", "&kp")
    else:
        bindings = ("&kp", f"&HRM_{meta.hand}_{meta.finger}_tap_v1B_TKZ")
    require_idle_ms = INDEX_IDLE_MS if template.name == "&HRM_left_ring_index_v1B_TKZ" else meta.require_prior_idle_ms
    positions = POSITION_OVERRIDES.get(template.name, meta.bilateral_positions or meta.hold_trigger_positions)
    return HoldTapSpec(
        name=template.name,
        description=template.description,
        bindings=bindings,
        tapping_term_ms=meta.tapping_term_ms,
        flavor="tap-preferred",
        quick_tap_ms=meta.quick_tap_ms,
        require_prior_idle_ms=require_idle_ms,
        hold_trigger_on_release=True,
        hold_trigger_key_positions=positions,
    )


for template in BILATERAL_TEMPLATES:
    HOLD_TAP_DEFS[template.name] = _build_bilateral_spec(template)


HOLD_TAP_ORDER = {
    "windows": [
        "&AS_HT_v2_TKZ",
        "&CAPSWord_v1_TKZ",
        "&HRM_left_index_v1_TKZ",
        "&HRM_left_middy_v1_TKZ",
        "&HRM_left_pinky_v1_TKZ",
        "&HRM_left_ring_v1_TKZ",
        "&HRM_right_index_v1_TKZ",
        "&HRM_right_middy_v1_TKZ",
        "&HRM_right_pinky_v1_TKZ",
        "&HRM_right_ring_v1_TKZ",
        "&space_v3_TKZ",
        "&thumb_v2_TKZ",
    ],
    "mac": [
        "&AS_HT_v2_TKZ",
        "&CAPSWord_v1_TKZ",
        "&HRM_left_index_v1_TKZ",
        "&HRM_left_middy_v1_TKZ",
        "&HRM_left_pinky_v1_TKZ",
        "&HRM_left_ring_v1_TKZ",
        "&HRM_right_index_v1_TKZ",
        "&HRM_right_middy_v1_TKZ",
        "&HRM_right_pinky_v1_TKZ",
        "&HRM_right_ring_v1_TKZ",
        "&space_v3_TKZ",
        "&thumb_v2_TKZ",
    ],
    "dual": [
        "&AS_HT_v2_TKZ",
        "&CAPSWord_v1_TKZ",
        "&HRM_left_index_v1_TKZ",
        "&HRM_left_middy_v1_TKZ",
        "&HRM_left_pinky_v1_TKZ",
        "&HRM_left_ring_v1_TKZ",
        "&HRM_right_index_v1_TKZ",
        "&HRM_right_middy_v1_TKZ",
        "&HRM_right_pinky_v1_TKZ",
        "&HRM_right_ring_v1_TKZ",
        "&space_v3_TKZ",
        "&thumb_v2_TKZ",
    ],
    "bilateral_windows": [
        "&AS_HT_v2_TKZ",
        "&CAPSWord_v1_TKZ",
        "&HRM_left_index_middy_v1B_TKZ",
        "&HRM_left_index_pinky_v1B_TKZ",
        "&HRM_left_index_ringv1_TKZ",
        "&HRM_left_index_v1B_TKZ",
        "&HRM_left_middy_index_v1B_TKZ",
        "&HRM_left_middy_pinky_v1B_TKZ",
        "&HRM_left_middy_ring_v1B_TKZ",
        "&HRM_left_middy_v1B_TKZ",
        "&HRM_left_pinky_index_v1B_TKZ",
        "&HRM_left_pinky_middy_v1B_TKZ",
        "&HRM_left_pinky_ring_v1B_TKZ",
        "&HRM_left_pinky_v1B_TKZ",
        "&HRM_left_ring_index_v1B_TKZ",
        "&HRM_left_ring_middy_v1B_TKZ",
        "&HRM_left_ring_pinky_v1B_TKZ",
        "&HRM_left_ring_v1B_TKZ",
        "&HRM_right_index_middy_v1B_TKZ",
        "&HRM_right_index_pinky_v1B_TKZ",
        "&HRM_right_index_ring_v1B_TKZ",
        "&HRM_right_index_v1B_TKZ",
        "&HRM_right_middy_index_v1B_TKZ",
        "&HRM_right_middy_pinky_v1B_TKZ",
        "&HRM_right_middy_ring_v1B_TKZ",
        "&HRM_right_middy_v1B_TKZ",
        "&HRM_right_pinky_index_v1B_TKZ",
        "&HRM_right_pinky_middy_v1B_TKZ",
        "&HRM_right_pinky_ring_v1B_TKZ",
        "&HRM_right_pinky_v1B_TKZ",
        "&HRM_right_ring_index_v1B_TKZ",
        "&HRM_right_ring_middy_v1B_TKZ",
        "&HRM_right_ring_pinky_v1B_TKZ",
        "&HRM_right_ring_v1B_TKZ",
        "&space_v3_TKZ",
        "&thumb_v2_TKZ",
    ],
    "bilateral_mac": [
        "&AS_HT_v2_TKZ",
        "&CAPSWord_v1_TKZ",
        "&HRM_left_index_middy_v1B_TKZ",
        "&HRM_left_index_pinky_v1B_TKZ",
        "&HRM_left_index_ringv1_TKZ",
        "&HRM_left_index_v1B_TKZ",
        "&HRM_left_middy_index_v1B_TKZ",
        "&HRM_left_middy_pinky_v1B_TKZ",
        "&HRM_left_middy_ring_v1B_TKZ",
        "&HRM_left_middy_v1B_TKZ",
        "&HRM_left_pinky_index_v1B_TKZ",
        "&HRM_left_pinky_middy_v1B_TKZ",
        "&HRM_left_pinky_ring_v1B_TKZ",
        "&HRM_left_pinky_v1B_TKZ",
        "&HRM_left_ring_index_v1B_TKZ",
        "&HRM_left_ring_middy_v1B_TKZ",
        "&HRM_left_ring_pinky_v1B_TKZ",
        "&HRM_left_ring_v1B_TKZ",
        "&HRM_right_index_middy_v1B_TKZ",
        "&HRM_right_index_pinky_v1B_TKZ",
        "&HRM_right_index_ring_v1B_TKZ",
        "&HRM_right_index_v1B_TKZ",
        "&HRM_right_middy_index_v1B_TKZ",
        "&HRM_right_middy_pinky_v1B_TKZ",
        "&HRM_right_middy_ring_v1B_TKZ",
        "&HRM_right_middy_v1B_TKZ",
        "&HRM_right_pinky_index_v1B_TKZ",
        "&HRM_right_pinky_middy_v1B_TKZ",
        "&HRM_right_pinky_ring_v1B_TKZ",
        "&HRM_right_pinky_v1B_TKZ",
        "&HRM_right_ring_index_v1B_TKZ",
        "&HRM_right_ring_middy_v1B_TKZ",
        "&HRM_right_ring_pinky_v1B_TKZ",
        "&HRM_right_ring_v1B_TKZ",
        "&space_v3_TKZ",
        "&thumb_v2_TKZ",
    ],
}


__all__ = ["HOLD_TAP_DEFS", "HOLD_TAP_ORDER"]
