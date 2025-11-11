"""Common helper functions for applying layout patch data."""

from __future__ import annotations

from typing import Mapping

from glove80.base import KeySpec, Layer, apply_patch


def apply_indices_patch(layer: Layer, patch: Mapping[int, KeySpec]) -> None:
    """Apply a sparse override mapping to *layer*."""

    apply_patch(layer, dict(patch))


def apply_mac_morphs(layer: Layer, mapping: Mapping[int, KeySpec]) -> None:
    """Apply Mac-specific overrides derived from shared helper specs."""

    apply_patch(layer, dict(mapping))


def command_binding(key: KeySpec | str) -> KeySpec:
    """Return a KeySpec that triggers ``LG(<key>)`` via ``&kp``."""

    innermost = key if isinstance(key, KeySpec) else KeySpec(key)
    return KeySpec("&kp", (KeySpec("LG", (innermost,)),))


def swap_right_ctrl_to_gui() -> KeySpec:
    """Return the standard Mac swap from Right Ctrl to Right Cmd."""

    return KeySpec("&sk", (KeySpec("RGUI"),))


def swap_right_gui_to_ctrl() -> KeySpec:
    """Return the standard Mac swap from Right Cmd to Right Ctrl."""

    return KeySpec("&sk", (KeySpec("RCTRL"),))


__all__ = [
    "apply_indices_patch",
    "apply_mac_morphs",
    "command_binding",
    "swap_right_ctrl_to_gui",
    "swap_right_gui_to_ctrl",
]
