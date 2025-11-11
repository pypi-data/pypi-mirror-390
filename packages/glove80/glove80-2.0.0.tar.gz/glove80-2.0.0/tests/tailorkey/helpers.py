"""Shared TailorKey test helpers."""

from __future__ import annotations

from glove80.families.tailorkey.alpha_layouts import base_variant_for
from glove80.metadata import load_metadata

TAILORKEY_VARIANTS = tuple(sorted(load_metadata(layout="tailorkey").keys()))


def variants_for_base(*bases: str) -> list[str]:
    base_set = set(bases)
    return [variant for variant in TAILORKEY_VARIANTS if base_variant_for(variant) in base_set]


def non_bilateral_variants() -> list[str]:
    return variants_for_base("windows", "mac", "dual")


__all__ = ["TAILORKEY_VARIANTS", "non_bilateral_variants", "variants_for_base"]
