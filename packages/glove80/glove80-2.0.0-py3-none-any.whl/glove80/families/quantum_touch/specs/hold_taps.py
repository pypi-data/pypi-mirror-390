"""Hold-tap definitions for QuantumTouch (Pydantic models)."""

from __future__ import annotations

from glove80.layouts.schema import HoldTap

from .finger_data import FINGERS, FingerMeta


def _base_name(meta: FingerMeta) -> str:
    return f"&BHRM_{meta.hand}_{meta.name}"


def _hold_macro_name(meta: FingerMeta) -> str:
    return f"&BHRM_{meta.hand}_{meta.name}_Hold"


def _tap_macro_name(meta: FingerMeta) -> str:
    return f"&BHRM_{meta.hand}_{meta.name}_Tap"


LEFT_COMBOS = {
    "Pinky": ("Ring", "Middle", "Index"),
    "Ring": ("Pinky", "Middle", "Index"),
    "Middle": ("Pinky", "Ring", "Index"),
    "Index": ("Pinky", "Ring", "Middle"),
}

RIGHT_COMBOS = {
    "Index": ("Middle", "Ring", "Pinky"),
    "Middle": ("Index", "Ring", "Pinky"),
    "Ring": ("Index", "Middle", "Pinky"),
    "Pinky": ("Index", "Middle", "Ring"),
}


def _combo_order(meta: FingerMeta) -> tuple[str, ...]:
    mapping = LEFT_COMBOS if meta.hand == "L" else RIGHT_COMBOS
    return mapping[meta.name]


REQUIRE_IDLE_OVERRIDES = {
    "&BHRM_L_Ring_Index": 100,
}
POSITION_OVERRIDES = {
    "&BHRM_R_Middle_Pinky": (
        0,
        10,
        22,
        46,
        64,
        65,
        47,
        52,
        51,
        39,
        27,
        15,
        4,
        3,
        2,
        1,
        11,
        23,
        35,
        34,
        48,
        66,
        69,
        70,
        71,
        54,
        53,
        55,
        56,
        57,
        74,
        73,
        72,
        68,
        67,
        49,
        50,
        38,
        26,
        14,
        13,
        25,
        37,
        24,
        12,
        36,
    ),
}

HOLD_TAP_ORDER = []
HOLD_TAP_DEFS = {}

for meta in FINGERS:
    base_name = _base_name(meta)
    HOLD_TAP_ORDER.append(base_name)
    HOLD_TAP_DEFS[base_name] = HoldTap(
        name=base_name,
        description="HRM: tap→key, hold→layer",
        bindings=[_hold_macro_name(meta), "&kp"],
        tappingTermMs=meta.tapping_term_ms,
        flavor="tap-preferred",
        quickTapMs=meta.quick_tap_ms,
        requirePriorIdleMs=meta.require_prior_idle_ms,
        holdTriggerOnRelease=True,
        holdTriggerKeyPositions=list(meta.hold_trigger_positions),
    )

    for partner in _combo_order(meta):
        combo_name = f"{base_name}_{partner}"
        HOLD_TAP_ORDER.append(combo_name)
        HOLD_TAP_DEFS[combo_name] = HoldTap(
            name=combo_name,
            description=f"Combo: {meta.name} + {partner}",
            bindings=["&kp", _tap_macro_name(meta)],
            tappingTermMs=meta.tapping_term_ms,
            flavor="tap-preferred",
            quickTapMs=meta.quick_tap_ms,
            requirePriorIdleMs=REQUIRE_IDLE_OVERRIDES.get(combo_name, meta.require_prior_idle_ms),
            holdTriggerOnRelease=True,
            holdTriggerKeyPositions=list(POSITION_OVERRIDES.get(combo_name, meta.hold_trigger_positions)),
        )


__all__ = ["HOLD_TAP_DEFS", "HOLD_TAP_ORDER"]
