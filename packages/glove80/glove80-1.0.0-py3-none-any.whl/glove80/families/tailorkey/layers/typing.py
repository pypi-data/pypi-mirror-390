"""Typing layer generation."""

from __future__ import annotations

from glove80.base import KeySpec, Layer, LayerSpec, build_layer_from_spec, copy_layer


TYPING_LAYER_SPEC = LayerSpec(
    overrides={
        35: KeySpec("&kp", (KeySpec("A"),)),
        36: KeySpec("&kp", (KeySpec("S"),)),
        37: KeySpec("&kp", (KeySpec("D"),)),
        38: KeySpec("&kp", (KeySpec("F"),)),
        41: KeySpec("&kp", (KeySpec("J"),)),
        42: KeySpec("&kp", (KeySpec("K"),)),
        43: KeySpec("&kp", (KeySpec("L"),)),
        44: KeySpec("&kp", (KeySpec("SEMI"),)),
    }
)

_BASE_TYPING_LAYER: Layer = build_layer_from_spec(TYPING_LAYER_SPEC)


def build_typing_layer(_variant: str) -> Layer:
    """The Typing layer is identical across all variants."""

    return copy_layer(_BASE_TYPING_LAYER)
