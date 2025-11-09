"""Input listener specifications for TailorKey variants."""

from __future__ import annotations

from typing import Dict, Sequence, Tuple

from glove80.base import LayerRef
from glove80.specs import InputListenerNodeSpec, InputListenerSpec, InputProcessorSpec

LAYER_SEQUENCE = ("MouseSlow", "MouseFast", "MouseWarp")


def _node(description: str, layer: str, processor: str, params: Sequence[int]) -> InputListenerNodeSpec:
    return InputListenerNodeSpec(
        code=f"LAYER_{layer}",
        description=description,
        layers=(LayerRef(layer),),
        input_processors=(InputProcessorSpec(code=processor, params=params),),
    )


def _listeners(
    slow_xy_desc: str,
    slow_scroll_desc: str,
    warp_desc_xy: str,
    warp_desc_scroll: str,
) -> Tuple[InputListenerSpec, InputListenerSpec]:
    xy_nodes = [
        _node(slow_xy_desc, "MouseSlow", "&zip_xy_scaler", (1, 9)),
        _node("LAYER_MouseFast", "MouseFast", "&zip_xy_scaler", (3, 1)),
        _node(warp_desc_xy, "MouseWarp", "&zip_xy_scaler", (12, 1)),
    ]
    scroll_nodes = [
        _node(slow_scroll_desc, "MouseSlow", "&zip_scroll_scaler", (1, 9)),
        _node("LAYER_MouseFast", "MouseFast", "&zip_scroll_scaler", (3, 1)),
        _node(warp_desc_scroll, "MouseWarp", "&zip_scroll_scaler", (12, 1)),
    ]
    return (
        InputListenerSpec(code="&mmv_input_listener", nodes=tuple(xy_nodes)),
        InputListenerSpec(code="&msc_input_listener", nodes=tuple(scroll_nodes)),
    )


INPUT_LISTENER_DATA: Dict[str, list[InputListenerSpec]] = {
    "windows": list(_listeners("LAYER_MouseSlow", "LAYER_MouseSlow", "LAYER_MouseFast", "LAYER_MouseWarp")),
    "mac": list(_listeners("LAYER_MouseSlow\n", "LAYER_MouseSlow\n", "LAYER_MouseWarp", "LAYER_MouseWarp")),
    "dual": list(_listeners("LAYER_MouseSlow", "LAYER_MouseSlow\n", "LAYER_MouseWarp", "LAYER_MouseWarp")),
    "bilateral_windows": list(_listeners("LAYER_MouseSlow", "LAYER_MouseSlow", "LAYER_MouseWarp", "LAYER_MouseWarp")),
    "bilateral_mac": list(_listeners("LAYER_MouseSlow\n", "LAYER_MouseSlow\n", "LAYER_MouseWarp", "LAYER_MouseWarp")),
}


__all__ = ["INPUT_LISTENER_DATA"]
