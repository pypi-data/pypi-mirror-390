"""Finger metadata for QuantumTouch HRM helpers."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from glove80.families.shared_finger_specs import (
    FINGER_DEFAULTS,
    LEFT_CANONICAL_HOLD_POSITIONS,
    RIGHT_CANONICAL_HOLD_POSITIONS,
)


class FingerMeta(BaseModel):
    model_config = ConfigDict(frozen=True)

    hand: str  # "L" or "R"
    name: str  # "Pinky", "Ring", ...
    layer: str
    tap_key: str
    tapping_term_ms: int
    quick_tap_ms: int
    require_prior_idle_ms: int
    hold_trigger_positions: tuple[int, ...]


_HAND_CODES = {"left": "L", "right": "R"}
_LAYER_SUFFIXES = {
    "pinky": "Pinky",
    "ring": "Ring",
    "middle": "Middle",
    "index": "Index",
}


def _layer_name(hand: str, finger: str) -> str:
    return ("Left" if hand == "left" else "Right") + _LAYER_SUFFIXES[finger]


FINGERS: tuple[FingerMeta, ...] = tuple(
    FingerMeta(
        hand=_HAND_CODES[defaults.hand],
        name=_LAYER_SUFFIXES[defaults.finger],
        layer=_layer_name(defaults.hand, defaults.finger),
        tap_key=defaults.tap_key,
        tapping_term_ms=defaults.tapping_term_ms,
        quick_tap_ms=defaults.quick_tap_ms,
        require_prior_idle_ms=defaults.require_prior_idle_ms,
        hold_trigger_positions=(
            LEFT_CANONICAL_HOLD_POSITIONS if defaults.hand == "left" else RIGHT_CANONICAL_HOLD_POSITIONS
        ),
    )
    for defaults in FINGER_DEFAULTS
)


FINGER_BY_LABEL: dict[str, FingerMeta] = {
    ("Left" if meta.hand == "L" else "Right") + meta.name: meta for meta in FINGERS
}


__all__ = ["FINGERS", "FINGER_BY_LABEL", "FingerMeta"]
