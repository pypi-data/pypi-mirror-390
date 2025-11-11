"""Common metadata for TailorKey specs."""

from glove80.families.tailorkey.alpha_layouts import TAILORKEY_VARIANTS, base_variant_for
from glove80.layouts.common import build_common_fields

COMMON_FIELDS = build_common_fields(creator="moosy")

LAYER_NAME_MAP = {
    "windows": [
        "HRM_WinLinx",
        "Typing",
        "Autoshift",
        "Cursor",
        "Symbol",
        "Gaming",
        "Lower",
        "Mouse",
        "MouseSlow",
        "MouseFast",
        "MouseWarp",
        "Magic",
    ],
    "mac": [
        "HRM_macOS",
        "Typing",
        "Autoshift",
        "Cursor",
        "Symbol",
        "Gaming",
        "Lower",
        "Mouse",
        "MouseSlow",
        "MouseFast",
        "MouseWarp",
        "Magic",
    ],
    "dual": [
        "HRM_macOS",
        "HRM_WinLinx",
        "Typing",
        "Autoshift",
        "Cursor_macOS",
        "Cursor",
        "Symbol",
        "Mouse",
        "MouseSlow",
        "MouseFast",
        "MouseWarp",
        "Gaming",
        "Lower",
        "Magic",
    ],
    "bilateral_windows": [
        "HRM_WinLinx",
        "Typing",
        "Autoshift",
        "Cursor",
        "Symbol",
        "Gaming",
        "Lower",
        "LeftIndex",
        "LeftMiddy",
        "LeftRingy",
        "LeftPinky",
        "RightIndex",
        "RightMiddy",
        "RightRingy",
        "RightPinky",
        "Mouse",
        "MouseSlow",
        "MouseFast",
        "MouseWarp",
        "Magic",
    ],
    "bilateral_mac": [
        "HRM_macOS",
        "Typing",
        "Autoshift",
        "Cursor",
        "Symbol",
        "Gaming",
        "Lower",
        "LeftIndex",
        "LeftMiddy",
        "LeftRingy",
        "LeftPinky",
        "RightIndex",
        "RightMiddy",
        "RightRingy",
        "RightPinky",
        "Mouse",
        "MouseSlow",
        "MouseFast",
        "MouseWarp",
        "Magic",
    ],
}

for variant in TAILORKEY_VARIANTS:
    if variant not in LAYER_NAME_MAP:
        base = base_variant_for(variant)
        LAYER_NAME_MAP[variant] = list(LAYER_NAME_MAP[base])


__all__ = ["COMMON_FIELDS", "LAYER_NAME_MAP"]
