"""Combo definitions for QuantumTouch (Pydantic models)."""

from __future__ import annotations

from glove80.layouts.schema import Combo
from glove80.specs.utils import kp

COMBO_DATA = {
    "default": (
        Combo(
            name="combo_enter",
            description="E + D for Enter",
            binding=kp("RET").to_dict(),
            keyPositions=[25, 37],
            timeoutMs=50,
            layers=[-1],
        ),
        Combo(
            name="combo_space",
            description="R + F for Enter",
            binding=kp("SPACE").to_dict(),
            keyPositions=[26, 38],
            timeoutMs=50,
            layers=[-1],
        ),
        Combo(
            name="Hyper",
            description="",
            binding=kp("RGUI").to_dict(),
            keyPositions=[69, 70],
            layers=[-1],
        ),
    ),
}

__all__ = ["COMBO_DATA"]
