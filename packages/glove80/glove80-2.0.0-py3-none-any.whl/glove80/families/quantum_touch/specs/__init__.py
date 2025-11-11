"""QuantumTouch declarative specs."""

from .combos import COMBO_DATA
from .common import COMMON_FIELDS, LAYER_NAMES
from .hold_taps import HOLD_TAP_DEFS, HOLD_TAP_ORDER
from .input_listeners import INPUT_LISTENER_DATA
from .macros import MACRO_DEFS, MACRO_ORDER, MACRO_OVERRIDES

__all__ = [
    "COMBO_DATA",
    "COMMON_FIELDS",
    "HOLD_TAP_DEFS",
    "HOLD_TAP_ORDER",
    "INPUT_LISTENER_DATA",
    "LAYER_NAMES",
    "MACRO_DEFS",
    "MACRO_ORDER",
    "MACRO_OVERRIDES",
]
