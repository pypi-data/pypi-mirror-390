"""Feature components for Bilateral Home Row finger layers."""

from __future__ import annotations

from typing import Literal

from glove80.families.tailorkey.layers.bilateral import assemble_bilateral_layers
from glove80.families.tailorkey.specs.macros import MACRO_DEFS
from glove80.layouts.components import LayoutFeatureComponents

_BILATERAL_MACRO_NAMES = [
    "&HRM_left_index_hold_v1B_TKZ",
    "&HRM_left_index_tap_v1B_TKZ",
    "&HRM_left_middy_hold_v1B_TKZ",
    "&HRM_left_middy_tap_v1B_TKZ",
    "&HRM_left_pinky_hold_v1B_TKZ",
    "&HRM_left_pinky_tap_v1B_TKZ",
    "&HRM_left_ring_hold_v1B_TKZ",
    "&HRM_left_ring_tap_v1B_TKZ",
    "&HRM_right_index_hold_v1B_TKZ",
    "&HRM_right_index_tap_v1B_TKZ",
    "&HRM_right_middy_hold_v1B_TKZ",
    "&HRM_right_middy_tap_v1B_TKZ",
    "&HRM_right_pinky_hold_v1B_TKZ",
    "&HRM_right_pinky_tap_v1B_TKZ",
    "&HRM_right_ring_hold_v1B_TKZ",
    "&HRM_right_ring_tap_v1B_TKZ",
]


def bilateral_home_row_components(
    variant: str,
    *,
    platform: Literal["windows", "mac"] = "windows",
    remap: bool = False,
) -> LayoutFeatureComponents:
    """Return the macros + layers needed for bilateral HRM finger practice.

    Parameters
    ----------
    variant:
        TailorKey variant name whose alpha layout should be used when remapping keys.
    platform:
        Determines whether the mac-specific finger patches are applied.
    remap:
        When True, the layer keys are remapped according to the provided *variant*.

    """
    macros = [MACRO_DEFS[name] for name in _BILATERAL_MACRO_NAMES]
    layers = assemble_bilateral_layers(variant, mac=(platform == "mac"), remap=remap)
    return LayoutFeatureComponents(macros=macros, layers=layers)


__all__ = ["bilateral_home_row_components"]
