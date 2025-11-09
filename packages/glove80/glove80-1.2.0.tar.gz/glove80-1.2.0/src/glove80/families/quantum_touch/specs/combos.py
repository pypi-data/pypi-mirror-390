"""Combo specifications for QuantumTouch."""

from __future__ import annotations

from glove80.specs import ComboSpec
from glove80.specs.utils import kp

COMBO_DATA = {
    "default": (
        ComboSpec(
            name="combo_enter",
            description="E + D for Enter",
            binding=kp("RET"),
            key_positions=(25, 37),
            timeout_ms=50,
            layers=(-1,),
        ),
        ComboSpec(
            name="combo_space",
            description="R + F for Enter",
            binding=kp("SPACE"),
            key_positions=(26, 38),
            timeout_ms=50,
            layers=(-1,),
        ),
        ComboSpec(
            name="Hyper",
            description="",
            binding=kp("RGUI"),
            key_positions=(69, 70),
            layers=(-1,),
        ),
    )
}

__all__ = ["COMBO_DATA"]
