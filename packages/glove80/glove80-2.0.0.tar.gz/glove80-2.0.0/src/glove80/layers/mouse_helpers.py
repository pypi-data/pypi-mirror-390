"""Shared helpers for simple mouse layers."""

from __future__ import annotations

from ..base import Layer, LayerSpec, build_layer_from_spec, copy_layer

_TRANSPARENT_MOUSE_LAYER = build_layer_from_spec(LayerSpec(overrides={}))


def build_transparent_mouse_layer(_variant: str) -> Layer:
    """Return a reusable transparent mouse layer."""
    return copy_layer(_TRANSPARENT_MOUSE_LAYER)


__all__ = ["build_transparent_mouse_layer"]
