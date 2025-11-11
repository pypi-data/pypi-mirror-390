"""Helpers for applying reusable layout feature bundles."""

from __future__ import annotations

from typing import TYPE_CHECKING

from glove80.layouts.components import LayoutFeatureComponents
from glove80.layouts.merge import merge_components

if TYPE_CHECKING:
    pass


def apply_feature(layout: dict, components: LayoutFeatureComponents) -> None:
    """Mutate *layout* in-place by appending the provided components."""
    merge_components(layout, components)


__all__ = ["LayoutFeatureComponents", "apply_feature"]
