"""Shared TailorKey finger metadata for HRM-related specs."""

from __future__ import annotations

from dataclasses import dataclass

from glove80.families.shared_finger_specs import (
    FINGER_DEFAULTS_BY_KEY,
    LEFT_CANONICAL_HOLD_POSITIONS,
    RIGHT_CANONICAL_HOLD_POSITIONS,
    Finger,
    Hand,
)


@dataclass(frozen=True)
class FingerMeta:
    hand: Hand
    finger: str
    layer: str
    tap_key: str
    tapping_term_ms: int
    quick_tap_ms: int
    require_prior_idle_ms: int
    hold_trigger_positions: tuple[int, ...]
    bilateral_positions: tuple[int, ...] | None = None


@dataclass(frozen=True)
class _FingerConfig:
    hand: Hand
    canonical_finger: Finger
    layer: str
    finger_label: str
    hold_positions: tuple[int, ...]
    bilateral_positions: tuple[int, ...] | None


def _ascending_tail_variant(positions: tuple[int, ...]) -> tuple[int, ...]:
    """Ensure the last three indices are sorted ascending."""

    return positions[:-3] + tuple(sorted(positions[-3:]))


_LEFT_COMMON_HOLD = LEFT_CANONICAL_HOLD_POSITIONS
_LEFT_ASCENDING_TAIL = _ascending_tail_variant(LEFT_CANONICAL_HOLD_POSITIONS)
_LEFT_PINKY_HOLD: tuple[int, ...] = (
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
    9,
    16,
    17,
    18,
    19,
    20,
    21,
    29,
    30,
    31,
    32,
    33,
    42,
    43,
    44,
    45,
    60,
    61,
    62,
    63,
    28,
    40,
    41,
    58,
    59,
    75,
    76,
    77,
    79,
    78,
    52,
    53,
    54,
    69,
    70,
    71,
)
_RIGHT_PRIORITY_HOLD: tuple[int, ...] = (
    52,
    53,
    54,
    71,
    70,
    69,
    0,
    1,
    10,
    11,
    12,
    13,
    14,
    22,
    23,
    24,
    25,
    26,
    27,
    34,
    35,
    36,
    37,
    38,
    39,
    46,
    47,
    48,
    49,
    50,
    51,
    64,
    65,
    66,
    67,
    68,
    15,
    4,
    2,
    3,
    55,
    56,
    57,
    72,
    73,
    74,
)

_LEFT_BILATERAL = LEFT_CANONICAL_HOLD_POSITIONS
_RIGHT_BILATERAL = RIGHT_CANONICAL_HOLD_POSITIONS

TAILORKEY_FINGER_CONFIGS: tuple[_FingerConfig, ...] = (
    _FingerConfig(
        hand="left",
        canonical_finger="index",
        finger_label="index",
        layer="LeftIndex",
        hold_positions=_LEFT_COMMON_HOLD,
        bilateral_positions=_LEFT_BILATERAL,
    ),
    _FingerConfig(
        hand="left",
        canonical_finger="middle",
        finger_label="middy",
        layer="LeftMiddy",
        hold_positions=_LEFT_ASCENDING_TAIL,
        bilateral_positions=_LEFT_BILATERAL,
    ),
    _FingerConfig(
        hand="left",
        canonical_finger="ring",
        finger_label="ring",
        layer="LeftRingy",
        hold_positions=_LEFT_ASCENDING_TAIL,
        bilateral_positions=_LEFT_BILATERAL,
    ),
    _FingerConfig(
        hand="left",
        canonical_finger="pinky",
        finger_label="pinky",
        layer="LeftPinky",
        hold_positions=_LEFT_PINKY_HOLD,
        bilateral_positions=_LEFT_BILATERAL,
    ),
    _FingerConfig(
        hand="right",
        canonical_finger="index",
        finger_label="index",
        layer="RightIndex",
        hold_positions=_RIGHT_PRIORITY_HOLD,
        bilateral_positions=_RIGHT_BILATERAL,
    ),
    _FingerConfig(
        hand="right",
        canonical_finger="middle",
        finger_label="middy",
        layer="RightMiddy",
        hold_positions=_RIGHT_PRIORITY_HOLD,
        bilateral_positions=_RIGHT_BILATERAL,
    ),
    _FingerConfig(
        hand="right",
        canonical_finger="ring",
        finger_label="ring",
        layer="RightRingy",
        hold_positions=_RIGHT_PRIORITY_HOLD,
        bilateral_positions=_RIGHT_BILATERAL,
    ),
    _FingerConfig(
        hand="right",
        canonical_finger="pinky",
        finger_label="pinky",
        layer="RightPinky",
        hold_positions=_RIGHT_PRIORITY_HOLD,
        bilateral_positions=_RIGHT_BILATERAL,
    ),
)


def _build_meta(config: _FingerConfig) -> FingerMeta:
    defaults = FINGER_DEFAULTS_BY_KEY[(config.hand, config.canonical_finger)]
    return FingerMeta(
        hand=config.hand,
        finger=config.finger_label,
        layer=config.layer,
        tap_key=defaults.tap_key,
        tapping_term_ms=defaults.tapping_term_ms,
        quick_tap_ms=defaults.quick_tap_ms,
        require_prior_idle_ms=defaults.require_prior_idle_ms,
        hold_trigger_positions=config.hold_positions,
        bilateral_positions=config.bilateral_positions,
    )


FINGERS: tuple[FingerMeta, ...] = tuple(_build_meta(config) for config in TAILORKEY_FINGER_CONFIGS)


__all__ = ["FINGERS", "FingerMeta"]
