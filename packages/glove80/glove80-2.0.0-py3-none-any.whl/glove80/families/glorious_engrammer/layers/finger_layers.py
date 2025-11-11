"""Finger Layers rows for Glorious Engrammer."""

from __future__ import annotations

from typing import TYPE_CHECKING

from glove80.layouts.layers import Token, rows_to_layer_spec

if TYPE_CHECKING:
    from collections.abc import Sequence

    from glove80.base import LayerSpec

LayerRows = tuple[tuple[Token, ...], ...]


def _custom(code: str) -> Token:
    return ("Custom", code)


def _repeat(token: Token, count: int) -> tuple[Token, ...]:
    return tuple(token for _ in range(count))


def _taps(macro: str, coords: Sequence[str]) -> tuple[Token, ...]:
    return tuple(("Custom", f"&{macro}_tap {coord}") for coord in coords)


def _lh(*coords: str) -> tuple[str, ...]:
    return tuple(f"KEY_LH_{coord}" for coord in coords)


def _rh(*coords: str) -> tuple[str, ...]:
    return tuple(f"KEY_RH_{coord}" for coord in coords)


FINGER_LAYER_SPECS: dict[str, LayerSpec] = {
    "LeftPinky": rows_to_layer_spec(
        (
            (
                *_taps("left_pinky", _lh("C6R1", "C5R1", "C4R1", "C3R1", "C2R1")),
                *_repeat("&trans", 5),
            ),
            (
                *_taps("left_pinky", _lh("C6R2", "C5R2", "C4R2", "C3R2", "C2R2", "C1R2")),
                *_repeat("&trans", 4),
            ),
            (
                *_repeat("&trans", 2),
                *_taps("left_pinky", _lh("C6R3", "C5R3", "C4R3", "C3R3", "C2R3", "C1R3")),
                *_repeat("&trans", 2),
            ),
            (
                *_repeat("&trans", 4),
                *_taps("left_pinky", _lh("C6R4")),
                *_repeat("&none", 1),
                _custom("&LeftPinkyRingy"),
                _custom("&LeftPinkyMiddy"),
                _custom("&LeftPinkyIndex"),
                *_taps("left_pinky", _lh("C1R4")),
            ),
            (
                *_repeat("&trans", 1),
                _custom("&kp RIGHT_INDEX_KEY"),
                _custom("&kp RIGHT_MIDDY_KEY"),
                _custom("&kp RIGHT_RINGY_KEY"),
                _custom("&kp RIGHT_PINKY_KEY"),
                *_repeat("&trans", 2),
                *_taps("left_pinky", _lh("C5R5", "C4R5", "C3R5")),
            ),
            (
                *_taps("left_pinky", _lh("C2R5", "C1R5")),
                _custom("&mo LAY_LH_T1"),
                *_taps("left_pinky", _lh("T2", "T3")),
                *_repeat("&trans", 5),
            ),
            (
                *_repeat("&trans", 5),
                *_taps("left_pinky", _lh("C5R6", "C4R6", "C3R6")),
                _custom("&mo LAY_LH_C2R6"),
                _custom("&mo LAY_LH_T4"),
            ),
            (
                _custom("&mo LAY_LH_T5"),
                _custom("&mo LAY_LH_T6"),
                *_repeat("&trans", 8),
            ),
        ),
    ),
    "LeftRingy": rows_to_layer_spec(
        (
            (
                *_taps("left_ringy", _lh("C6R1", "C5R1", "C4R1", "C3R1", "C2R1")),
                *_repeat("&trans", 5),
            ),
            (
                *_taps("left_ringy", _lh("C6R2", "C5R2", "C4R2", "C3R2", "C2R2", "C1R2")),
                *_repeat("&trans", 4),
            ),
            (
                *_repeat("&trans", 2),
                *_taps("left_ringy", _lh("C6R3", "C5R3", "C4R3", "C3R3", "C2R3", "C1R3")),
                *_repeat("&trans", 2),
            ),
            (
                *_repeat("&trans", 4),
                *_taps("left_ringy", _lh("C6R4")),
                _custom("&LeftRingyPinky"),
                *_repeat("&none", 1),
                _custom("&LeftRingyMiddy"),
                _custom("&LeftRingyIndex"),
                *_taps("left_ringy", _lh("C1R4")),
            ),
            (
                *_repeat("&trans", 1),
                _custom("&kp RIGHT_INDEX_KEY"),
                _custom("&kp RIGHT_MIDDY_KEY"),
                _custom("&kp RIGHT_RINGY_KEY"),
                _custom("&kp RIGHT_PINKY_KEY"),
                *_repeat("&trans", 2),
                *_taps("left_ringy", _lh("C5R5", "C4R5", "C3R5")),
            ),
            (
                *_taps("left_ringy", _lh("C2R5", "C1R5")),
                _custom("&mo LAY_LH_T1"),
                *_taps("left_ringy", _lh("T2", "T3")),
                *_repeat("&trans", 5),
            ),
            (
                *_repeat("&trans", 5),
                *_taps("left_ringy", _lh("C5R6", "C4R6", "C3R6")),
                _custom("&mo LAY_LH_C2R6"),
                _custom("&mo LAY_LH_T4"),
            ),
            (
                _custom("&mo LAY_LH_T5"),
                _custom("&mo LAY_LH_T6"),
                *_repeat("&trans", 8),
            ),
        ),
    ),
    "LeftMiddy": rows_to_layer_spec(
        (
            (
                *_taps("left_middy", _lh("C6R1", "C5R1", "C4R1", "C3R1", "C2R1")),
                *_repeat("&trans", 5),
            ),
            (
                *_taps("left_middy", _lh("C6R2", "C5R2", "C4R2", "C3R2", "C2R2", "C1R2")),
                *_repeat("&trans", 4),
            ),
            (
                *_repeat("&trans", 2),
                *_taps("left_middy", _lh("C6R3", "C5R3", "C4R3", "C3R3", "C2R3", "C1R3")),
                *_repeat("&trans", 2),
            ),
            (
                *_repeat("&trans", 4),
                *_taps("left_middy", _lh("C6R4")),
                _custom("&LeftMiddyPinky"),
                _custom("&LeftMiddyRingy"),
                *_repeat("&none", 1),
                _custom("&LeftMiddyIndex"),
                *_taps("left_middy", _lh("C1R4")),
            ),
            (
                *_repeat("&trans", 1),
                _custom("&kp RIGHT_INDEX_KEY"),
                _custom("&kp RIGHT_MIDDY_KEY"),
                _custom("&kp RIGHT_RINGY_KEY"),
                _custom("&kp RIGHT_PINKY_KEY"),
                *_repeat("&trans", 2),
                *_taps("left_middy", _lh("C5R5", "C4R5", "C3R5")),
            ),
            (
                *_taps("left_middy", _lh("C2R5", "C1R5")),
                _custom("&mo LAY_LH_T1"),
                *_taps("left_middy", _lh("T2", "T3")),
                *_repeat("&trans", 5),
            ),
            (
                *_repeat("&trans", 5),
                *_taps("left_middy", _lh("C5R6", "C4R6", "C3R6")),
                _custom("&mo LAY_LH_C2R6"),
                _custom("&mo LAY_LH_T4"),
            ),
            (
                _custom("&mo LAY_LH_T5"),
                _custom("&mo LAY_LH_T6"),
                *_repeat("&trans", 8),
            ),
        ),
    ),
    "LeftIndex": rows_to_layer_spec(
        (
            (
                *_taps("left_index", _lh("C6R1", "C5R1", "C4R1", "C3R1", "C2R1")),
                *_repeat("&trans", 5),
            ),
            (
                *_taps("left_index", _lh("C6R2", "C5R2", "C4R2", "C3R2", "C2R2", "C1R2")),
                *_repeat("&trans", 4),
            ),
            (
                *_repeat("&trans", 2),
                *_taps("left_index", _lh("C6R3", "C5R3", "C4R3", "C3R3", "C2R3", "C1R3")),
                *_repeat("&trans", 2),
            ),
            (
                *_repeat("&trans", 4),
                *_taps("left_index", _lh("C6R4")),
                _custom("&LeftIndexPinky"),
                _custom("&LeftIndexRingy"),
                _custom("&LeftIndexMiddy"),
                *_repeat("&none", 1),
                *_taps("left_index", _lh("C1R4")),
            ),
            (
                *_repeat("&trans", 1),
                _custom("&kp RIGHT_INDEX_KEY"),
                _custom("&kp RIGHT_MIDDY_KEY"),
                _custom("&kp RIGHT_RINGY_KEY"),
                _custom("&kp RIGHT_PINKY_KEY"),
                *_repeat("&trans", 2),
                *_taps("left_index", _lh("C5R5", "C4R5", "C3R5")),
            ),
            (
                *_taps("left_index", _lh("C2R5", "C1R5")),
                _custom("&mo LAY_LH_T1"),
                *_taps("left_index", _lh("T2", "T3")),
                *_repeat("&trans", 5),
            ),
            (
                *_repeat("&trans", 5),
                *_taps("left_index", _lh("C5R6", "C4R6", "C3R6")),
                _custom("&mo LAY_LH_C2R6"),
                _custom("&mo LAY_LH_T4"),
            ),
            (
                _custom("&mo LAY_LH_T5"),
                _custom("&mo LAY_LH_T6"),
                *_repeat("&trans", 8),
            ),
        ),
    ),
    "RightPinky": rows_to_layer_spec(
        (
            (
                *_repeat("&trans", 5),
                *_taps("right_pinky", _rh("C2R1", "C3R1", "C4R1", "C5R1", "C6R1")),
            ),
            (
                *_repeat("&trans", 6),
                *_taps("right_pinky", _rh("C1R2", "C2R2", "C3R2", "C4R2")),
            ),
            (
                *_taps("right_pinky", _rh("C5R2", "C6R2")),
                *_repeat("&trans", 6),
                *_taps("right_pinky", _rh("C1R3", "C2R3")),
            ),
            (
                *_taps("right_pinky", _rh("C3R3", "C4R3", "C5R3", "C6R3")),
                *_repeat("&trans", 1),
                _custom("&kp LEFT_PINKY_KEY"),
                _custom("&kp LEFT_RINGY_KEY"),
                _custom("&kp LEFT_MIDDY_KEY"),
                _custom("&kp LEFT_INDEX_KEY"),
                *_repeat("&trans", 1),
            ),
            (
                *_taps("right_pinky", _rh("C1R4")),
                _custom("&RightPinkyIndex"),
                _custom("&RightPinkyMiddy"),
                _custom("&RightPinkyRingy"),
                *_repeat("&none", 1),
                *_taps("right_pinky", _rh("C6R4")),
                *_repeat("&trans", 4),
            ),
            (
                *_repeat("&trans", 5),
                *_taps("right_pinky", _rh("T3", "T2")),
                _custom("&mo LAY_RH_T1"),
                *_taps("right_pinky", _rh("C1R5", "C2R5")),
            ),
            (
                *_taps("right_pinky", _rh("C3R5", "C4R5", "C5R5")),
                *_repeat("&trans", 7),
            ),
            (
                *_repeat("&trans", 2),
                _custom("&mo LAY_RH_T6"),
                _custom("&mo LAY_RH_T5"),
                _custom("&mo LAY_RH_T4"),
                _custom("&mo LAY_RH_C2R6"),
                *_taps("right_pinky", _rh("C3R6", "C4R6", "C5R6")),
                *_repeat("&trans", 1),
            ),
        ),
    ),
    "RightRingy": rows_to_layer_spec(
        (
            (
                *_repeat("&trans", 5),
                *_taps("right_ringy", _rh("C2R1", "C3R1", "C4R1", "C5R1", "C6R1")),
            ),
            (
                *_repeat("&trans", 6),
                *_taps("right_ringy", _rh("C1R2", "C2R2", "C3R2", "C4R2")),
            ),
            (
                *_taps("right_ringy", _rh("C5R2", "C6R2")),
                *_repeat("&trans", 6),
                *_taps("right_ringy", _rh("C1R3", "C2R3")),
            ),
            (
                *_taps("right_ringy", _rh("C3R3", "C4R3", "C5R3", "C6R3")),
                *_repeat("&trans", 1),
                _custom("&kp LEFT_PINKY_KEY"),
                _custom("&kp LEFT_RINGY_KEY"),
                _custom("&kp LEFT_MIDDY_KEY"),
                _custom("&kp LEFT_INDEX_KEY"),
                *_repeat("&trans", 1),
            ),
            (
                *_taps("right_ringy", _rh("C1R4")),
                _custom("&RightRingyIndex"),
                _custom("&RightRingyMiddy"),
                *_repeat("&none", 1),
                _custom("&RightRingyPinky"),
                *_taps("right_ringy", _rh("C6R4")),
                *_repeat("&trans", 4),
            ),
            (
                *_repeat("&trans", 5),
                *_taps("right_ringy", _rh("T3", "T2")),
                _custom("&mo LAY_RH_T1"),
                *_taps("right_ringy", _rh("C1R5", "C2R5")),
            ),
            (
                *_taps("right_ringy", _rh("C3R5", "C4R5", "C5R5")),
                *_repeat("&trans", 7),
            ),
            (
                *_repeat("&trans", 2),
                _custom("&mo LAY_RH_T6"),
                _custom("&mo LAY_RH_T5"),
                _custom("&mo LAY_RH_T4"),
                _custom("&mo LAY_RH_C2R6"),
                *_taps("right_ringy", _rh("C3R6", "C4R6", "C5R6")),
                *_repeat("&trans", 1),
            ),
        ),
    ),
    "RightMiddy": rows_to_layer_spec(
        (
            (
                *_repeat("&trans", 5),
                *_taps("right_middy", _rh("C2R1", "C3R1", "C4R1", "C5R1", "C6R1")),
            ),
            (
                *_repeat("&trans", 6),
                *_taps("right_middy", _rh("C1R2", "C2R2", "C3R2", "C4R2")),
            ),
            (
                *_taps("right_middy", _rh("C5R2", "C6R2")),
                *_repeat("&trans", 6),
                *_taps("right_middy", _rh("C1R3", "C2R3")),
            ),
            (
                *_taps("right_middy", _rh("C3R3", "C4R3", "C5R3", "C6R3")),
                *_repeat("&trans", 1),
                _custom("&kp LEFT_PINKY_KEY"),
                _custom("&kp LEFT_RINGY_KEY"),
                _custom("&kp LEFT_MIDDY_KEY"),
                _custom("&kp LEFT_INDEX_KEY"),
                *_repeat("&trans", 1),
            ),
            (
                *_taps("right_middy", _rh("C1R4")),
                _custom("&RightMiddyIndex"),
                *_repeat("&none", 1),
                _custom("&RightMiddyRingy"),
                _custom("&RightMiddyPinky"),
                *_taps("right_middy", _rh("C6R4")),
                *_repeat("&trans", 4),
            ),
            (
                *_repeat("&trans", 5),
                *_taps("right_middy", _rh("T3", "T2")),
                _custom("&mo LAY_RH_T1"),
                *_taps("right_middy", _rh("C1R5", "C2R5")),
            ),
            (
                *_taps("right_middy", _rh("C3R5", "C4R5", "C5R5")),
                *_repeat("&trans", 7),
            ),
            (
                *_repeat("&trans", 2),
                _custom("&mo LAY_RH_T6"),
                _custom("&mo LAY_RH_T5"),
                _custom("&mo LAY_RH_T4"),
                _custom("&mo LAY_RH_C2R6"),
                *_taps("right_middy", _rh("C3R6", "C4R6", "C5R6")),
                *_repeat("&trans", 1),
            ),
        ),
    ),
    "RightIndex": rows_to_layer_spec(
        (
            (
                *_repeat("&trans", 5),
                *_taps("right_index", _rh("C2R1", "C3R1", "C4R1", "C5R1", "C6R1")),
            ),
            (
                *_repeat("&trans", 6),
                *_taps("right_index", _rh("C1R2", "C2R2", "C3R2", "C4R2")),
            ),
            (
                *_taps("right_index", _rh("C5R2", "C6R2")),
                *_repeat("&trans", 6),
                *_taps("right_index", _rh("C1R3", "C2R3")),
            ),
            (
                *_taps("right_index", _rh("C3R3", "C4R3", "C5R3", "C6R3")),
                *_repeat("&trans", 1),
                _custom("&kp LEFT_PINKY_KEY"),
                _custom("&kp LEFT_RINGY_KEY"),
                _custom("&kp LEFT_MIDDY_KEY"),
                _custom("&kp LEFT_INDEX_KEY"),
                *_repeat("&trans", 1),
            ),
            (
                *_taps("right_index", _rh("C1R4")),
                *_repeat("&none", 1),
                _custom("&RightIndexMiddy"),
                _custom("&RightIndexRingy"),
                _custom("&RightIndexPinky"),
                *_taps("right_index", _rh("C6R4")),
                *_repeat("&trans", 4),
            ),
            (
                *_repeat("&trans", 5),
                *_taps("right_index", _rh("T3", "T2")),
                _custom("&mo LAY_RH_T1"),
                *_taps("right_index", _rh("C1R5", "C2R5")),
            ),
            (
                *_taps("right_index", _rh("C3R5", "C4R5", "C5R5")),
                *_repeat("&trans", 7),
            ),
            (
                *_repeat("&trans", 2),
                _custom("&mo LAY_RH_T6"),
                _custom("&mo LAY_RH_T5"),
                _custom("&mo LAY_RH_T4"),
                _custom("&mo LAY_RH_C2R6"),
                *_taps("right_index", _rh("C3R6", "C4R6", "C5R6")),
                *_repeat("&trans", 1),
            ),
        ),
    ),
}
