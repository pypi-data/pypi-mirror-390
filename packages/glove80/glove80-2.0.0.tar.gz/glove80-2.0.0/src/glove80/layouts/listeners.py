"""Shared input-listener factories for layout families."""

from __future__ import annotations

from typing import Sequence

from glove80.base import LayerRef
from glove80.layouts.schema import InputListener, InputProcessor, ListenerNode


def make_mouse_listeners(
    *,
    slow_xy_description: str = "LAYER_MouseSlow",
    slow_scroll_description: str = "LAYER_MouseSlow",
    warp_xy_description: str = "LAYER_MouseWarp",
    warp_scroll_description: str = "LAYER_MouseWarp",
) -> tuple[InputListener, InputListener]:
    """Return standard XY + scroll listeners for Mouse layers.

    Parameters
    ----------
    slow_xy_description, slow_scroll_description
        Textual labels for the slow-speed nodes in the XY and scroll stacks.
    warp_xy_description, warp_scroll_description
        Textual labels for the warp nodes in the XY and scroll stacks.
    """

    sequence: Sequence[tuple[str, tuple[int, int]]] = (
        ("MouseSlow", (1, 9)),
        ("MouseFast", (3, 1)),
        ("MouseWarp", (12, 1)),
    )

    def _nodes(processor: str, descriptions: tuple[str, str, str]) -> list[ListenerNode]:
        nodes: list[ListenerNode] = []
        for (layer, params), description in zip(sequence, descriptions, strict=False):
            nodes.append(
                ListenerNode(
                    code=f"LAYER_{layer}",
                    description=description,
                    layers=[LayerRef(layer)],
                    inputProcessors=[InputProcessor(code=processor, params=list(params))],
                )
            )
        return nodes

    xy_descriptions = (slow_xy_description, "LAYER_MouseFast", warp_xy_description)
    scroll_descriptions = (slow_scroll_description, "LAYER_MouseFast", warp_scroll_description)

    xy_listener = InputListener(
        code="&mmv_input_listener",
        nodes=_nodes("&zip_xy_scaler", xy_descriptions),
    )
    scroll_listener = InputListener(
        code="&msc_input_listener",
        nodes=_nodes("&zip_scroll_scaler", scroll_descriptions),
    )
    return xy_listener, scroll_listener


__all__ = ["make_mouse_listeners"]
