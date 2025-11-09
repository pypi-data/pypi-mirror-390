"""Layer construction helpers and registry."""

from typing import Callable, Iterable

from .autoshift import build_autoshift_layer
from .bilateral import build_bilateral_training_layers
from .cursor import build_cursor_layer
from .gaming import build_gaming_layer
from .hrm import build_hrm_layers
from .lower import build_lower_layer
from .magic import build_magic_layer
from .mouse import build_mouse_layers
from .symbol import build_symbol_layer
from .typing import build_typing_layer

from glove80.base import Layer, LayerMap

LayerProvider = Callable[[str], LayerMap]


def _single_layer(name: str, builder: Callable[[str], Layer]) -> LayerProvider:
    def provider(variant: str) -> LayerMap:
        return {name: builder(variant)}

    return provider


def _cursor_provider(variant: str) -> LayerMap:
    layers = {"Cursor": build_cursor_layer(variant)}
    if variant == "dual":
        layers["Cursor_macOS"] = build_cursor_layer("mac")
    return layers


LAYER_PROVIDERS: Iterable[LayerProvider] = [
    build_hrm_layers,
    _single_layer("Typing", build_typing_layer),
    _single_layer("Autoshift", build_autoshift_layer),
    _cursor_provider,
    _single_layer("Symbol", build_symbol_layer),
    _single_layer("Gaming", build_gaming_layer),
    _single_layer("Lower", build_lower_layer),
    build_mouse_layers,
    _single_layer("Magic", build_magic_layer),
    build_bilateral_training_layers,
]


def build_all_layers(variant: str) -> LayerMap:
    """Return every layer needed for the given variant."""

    layers: LayerMap = {}
    for provider in LAYER_PROVIDERS:
        layers.update(provider(variant))
    return layers


__all__ = [
    "Layer",
    "LayerMap",
    "build_all_layers",
    "build_autoshift_layer",
    "build_bilateral_training_layers",
    "build_cursor_layer",
    "build_gaming_layer",
    "build_hrm_layers",
    "build_lower_layer",
    "build_magic_layer",
    "build_mouse_layers",
    "build_symbol_layer",
    "build_typing_layer",
]
