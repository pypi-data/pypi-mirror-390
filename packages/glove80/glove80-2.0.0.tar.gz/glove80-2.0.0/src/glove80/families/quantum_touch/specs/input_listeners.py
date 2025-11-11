"""Input listener definitions for QuantumTouch (Pydantic models)."""

from __future__ import annotations

from glove80.layouts.listeners import make_mouse_listeners


INPUT_LISTENER_DATA = {
    "default": make_mouse_listeners(),
}

__all__ = ["INPUT_LISTENER_DATA"]
