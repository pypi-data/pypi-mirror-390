"""TailorKey declarative specifications."""

from .combos import COMBO_DATA
from .common import COMMON_FIELDS, LAYER_NAME_MAP
from .hold_taps import HOLD_TAP_DEFS, HOLD_TAP_ORDER
from .input_listeners import INPUT_LISTENER_DATA
from .macros import MACRO_DEFS, MACRO_ORDER, MACRO_OVERRIDES

__all__ = [
    "COMBO_DATA",
    "COMMON_FIELDS",
    "HOLD_TAP_DEFS",
    "HOLD_TAP_ORDER",
    "INPUT_LISTENER_DATA",
    "LAYER_NAME_MAP",
    "MACRO_DEFS",
    "MACRO_ORDER",
    "MACRO_OVERRIDES",
]
