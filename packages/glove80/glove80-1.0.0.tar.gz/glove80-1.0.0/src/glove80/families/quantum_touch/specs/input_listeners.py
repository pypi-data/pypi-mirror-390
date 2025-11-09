"""Input listener definitions for QuantumTouch."""

from __future__ import annotations

from typing import Tuple

from glove80.base import LayerRef
from glove80.specs import InputListenerNodeSpec, InputListenerSpec, InputProcessorSpec

LAYER_SEQUENCE = ("MouseSlow", "MouseFast", "MouseWarp")


def _node(description: str, layer: str, processor: str, params: Tuple[int, int]) -> InputListenerNodeSpec:
    return InputListenerNodeSpec(
        code=f"LAYER_{layer}",
        description=description,
        layers=(LayerRef(layer),),
        input_processors=(InputProcessorSpec(code=processor, params=params),),
    )


def _listener(code: str, processor: str) -> InputListenerSpec:
    descriptions = ("LAYER_MouseSlow", "LAYER_MouseFast", "LAYER_MouseWarp")
    params = ((1, 9), (3, 1), (12, 1))
    nodes = [_node(desc, layer, processor, param) for desc, layer, param in zip(descriptions, LAYER_SEQUENCE, params)]
    return InputListenerSpec(code=code, nodes=tuple(nodes))


INPUT_LISTENER_DATA = {
    "default": (
        _listener("&mmv_input_listener", "&zip_xy_scaler"),
        _listener("&msc_input_listener", "&zip_scroll_scaler"),
    )
}

__all__ = ["INPUT_LISTENER_DATA"]
