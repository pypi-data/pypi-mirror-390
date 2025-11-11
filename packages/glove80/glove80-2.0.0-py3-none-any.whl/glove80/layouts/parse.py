"""Helpers for parsing existing layout JSON into typed models."""

from __future__ import annotations

from typing import Any, Mapping

from .schema import Combo, HoldTap, InputListener, LayoutPayload, Macro


def parse_typed_sections(
    json_data: Mapping[str, Any],
) -> tuple[LayoutPayload, list[Macro], list[HoldTap], list[Combo], list[InputListener]]:
    """Parse an existing layout JSON into typed models.

    Returns a tuple of the full, validated :class:`LayoutPayload` and the
    section lists as strongly-typed Pydantic models.
    """
    payload = LayoutPayload.model_validate(dict(json_data))
    macros: list[Macro] = [m if isinstance(m, Macro) else Macro.model_validate(m) for m in payload.macros]
    hold_taps: list[HoldTap] = [h if isinstance(h, HoldTap) else HoldTap.model_validate(h) for h in payload.holdTaps]
    combos: list[Combo] = [c if isinstance(c, Combo) else Combo.model_validate(c) for c in payload.combos]
    listeners: list[InputListener] = [
        item if isinstance(item, InputListener) else InputListener.model_validate(item)
        for item in payload.inputListeners
    ]
    return (payload, macros, hold_taps, combos, listeners)


__all__ = ["parse_typed_sections"]
