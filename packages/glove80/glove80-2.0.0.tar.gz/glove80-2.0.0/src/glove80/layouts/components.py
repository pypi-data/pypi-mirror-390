"""Shared feature component dataclasses used by layout builders."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from glove80.base import LayerMap
    from glove80.layouts.schema import Combo, HoldTap, InputListener, Macro


@dataclass(frozen=True)
class LayoutFeatureComponents:
    """Small bundle of reusable layout pieces (macros, layers, etc.)."""

    macros: Sequence[Macro] = ()
    macro_overrides: Mapping[str, Macro] = field(default_factory=dict)
    # New optional form: direct map by macro name; preferred when provided.
    macros_by_name: Mapping[str, Macro] | None = None
    hold_taps: Sequence[HoldTap] = ()
    combos: Sequence[Combo] = ()
    input_listeners: Sequence[InputListener] = ()
    layers: LayerMap = field(default_factory=dict)


__all__ = ["LayoutFeatureComponents"]
