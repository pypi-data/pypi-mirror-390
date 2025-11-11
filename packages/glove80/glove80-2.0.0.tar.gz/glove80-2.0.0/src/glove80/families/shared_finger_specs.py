"""Shared finger metadata defaults used by multiple Glove80 families."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal

Hand = Literal["left", "right"]
Finger = Literal["pinky", "ring", "middle", "index"]


@dataclass(frozen=True)
class FingerDefaults:
    """Family-agnostic timing defaults for a single finger."""

    hand: Hand
    finger: Finger
    tap_key: str
    tapping_term_ms: int
    quick_tap_ms: int
    require_prior_idle_ms: int


LEFT_CANONICAL_HOLD_POSITIONS: Final[tuple[int, ...]] = (
    57,
    56,
    55,
    72,
    73,
    74,
    5,
    6,
    7,
    8,
    16,
    17,
    18,
    19,
    20,
    28,
    29,
    30,
    31,
    32,
    40,
    41,
    42,
    43,
    44,
    58,
    59,
    60,
    61,
    62,
    75,
    76,
    77,
    78,
    9,
    21,
    33,
    45,
    63,
    79,
    52,
    53,
    54,
    70,
    71,
    69,
)

RIGHT_CANONICAL_HOLD_POSITIONS: Final[tuple[int, ...]] = (
    0,
    10,
    22,
    34,
    46,
    64,
    65,
    47,
    35,
    23,
    1,
    2,
    12,
    11,
    24,
    36,
    48,
    66,
    67,
    49,
    37,
    25,
    13,
    3,
    4,
    14,
    15,
    27,
    26,
    38,
    39,
    51,
    50,
    68,
    52,
    53,
    54,
    71,
    70,
    69,
    55,
    56,
    57,
    74,
    73,
    72,
)

FINGER_DEFAULTS: Final[tuple[FingerDefaults, ...]] = (
    FingerDefaults(
        hand="left",
        finger="pinky",
        tap_key="A",
        tapping_term_ms=280,
        quick_tap_ms=300,
        require_prior_idle_ms=150,
    ),
    FingerDefaults(
        hand="left",
        finger="ring",
        tap_key="S",
        tapping_term_ms=240,
        quick_tap_ms=300,
        require_prior_idle_ms=150,
    ),
    FingerDefaults(
        hand="left",
        finger="middle",
        tap_key="D",
        tapping_term_ms=210,
        quick_tap_ms=300,
        require_prior_idle_ms=150,
    ),
    FingerDefaults(
        hand="left",
        finger="index",
        tap_key="F",
        tapping_term_ms=190,
        quick_tap_ms=300,
        require_prior_idle_ms=100,
    ),
    FingerDefaults(
        hand="right",
        finger="index",
        tap_key="J",
        tapping_term_ms=190,
        quick_tap_ms=300,
        require_prior_idle_ms=100,
    ),
    FingerDefaults(
        hand="right",
        finger="middle",
        tap_key="K",
        tapping_term_ms=210,
        quick_tap_ms=300,
        require_prior_idle_ms=150,
    ),
    FingerDefaults(
        hand="right",
        finger="ring",
        tap_key="L",
        tapping_term_ms=240,
        quick_tap_ms=300,
        require_prior_idle_ms=150,
    ),
    FingerDefaults(
        hand="right",
        finger="pinky",
        tap_key="SEMI",
        tapping_term_ms=280,
        quick_tap_ms=300,
        require_prior_idle_ms=150,
    ),
)

FINGER_DEFAULTS_BY_KEY: Final[dict[tuple[Hand, Finger], FingerDefaults]] = {
    (defaults.hand, defaults.finger): defaults for defaults in FINGER_DEFAULTS
}


__all__ = [
    "FingerDefaults",
    "FINGER_DEFAULTS",
    "FINGER_DEFAULTS_BY_KEY",
    "LEFT_CANONICAL_HOLD_POSITIONS",
    "RIGHT_CANONICAL_HOLD_POSITIONS",
    "Hand",
    "Finger",
]
