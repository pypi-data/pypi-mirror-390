"""Shared helper functions for building spec dataclasses."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from glove80.base import KeySpec, LayerRef

if TYPE_CHECKING:
    from collections.abc import Sequence


def ks(value: Any, *params: Any) -> KeySpec:
    """Construct a KeySpec, coercing nested params automatically."""
    return KeySpec(value, tuple(_ensure_key_spec(param) for param in params))


def kp(code: Any) -> KeySpec:
    """Shortcut for `&kp <code>` bindings."""
    return KeySpec("&kp", (_ensure_key_spec(code),))


def call(name: str) -> KeySpec:
    """Shortcut for macro helper behaviors without params."""
    return KeySpec(name)


def mod(wrapper: str, inner: Any) -> KeySpec:
    """Wrap a binding in another modifier (e.g., LC(LS(RIGHT)))."""
    return ks(wrapper, inner)


def layer_param(name: str) -> KeySpec:
    """Represent a LayerRef as a KeySpec parameter."""
    return KeySpec(LayerRef(name))


def key_sequence(values: Sequence[Any]) -> Sequence[KeySpec]:
    """Convert a sequence of values into KeySpecs."""
    return tuple(_ensure_key_spec(value) for value in values)


def _ensure_key_spec(value: Any) -> KeySpec:
    if isinstance(value, KeySpec):
        return value
    return KeySpec(value)
