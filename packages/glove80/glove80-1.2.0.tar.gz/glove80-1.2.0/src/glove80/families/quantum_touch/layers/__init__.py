"""QuantumTouch layer registry."""

from typing import Callable, Dict

from glove80.base import Layer, LayerMap
from .base_layer import build_base_layer
from .hrm import build_hrm_layer
from .finger_layers import FINGER_LAYER_BUILDERS
from .lower_layer import build_lower_layer
from .magic_layer import build_magic_layer
from .mouse_layers import MOUSE_LAYER_BUILDERS
from .original_layer import build_original_layer

LayerBuilder = Callable[[str], Layer]


LAYER_BUILDERS: Dict[str, LayerBuilder] = {
    "Base": build_base_layer,
    "HRM": build_hrm_layer,
    "Lower": build_lower_layer,
    "Magic": build_magic_layer,
    "Original": build_original_layer,
}

LAYER_BUILDERS.update(MOUSE_LAYER_BUILDERS)
LAYER_BUILDERS.update(FINGER_LAYER_BUILDERS)


def build_all_layers(variant: str) -> LayerMap:
    """Return every quantum layer currently codified."""

    return {name: builder(variant) for name, builder in LAYER_BUILDERS.items()}
