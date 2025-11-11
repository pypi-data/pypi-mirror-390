from __future__ import annotations

import copy

from glove80 import build_layout
from glove80.families.tailorkey.alpha_layouts import base_variant_for, needs_alpha_remap, remap_layer_keys


def _layer(layout: dict, name: str) -> list[dict]:
    idx = layout["layer_names"].index(name)
    return layout["layers"][idx]


def test_typing_layer_remap_matches_runtime(tailorkey_variants) -> None:
    for variant in tailorkey_variants:
        if not needs_alpha_remap(variant):
            continue

        base_variant = base_variant_for(variant)
        base_layout = build_layout("tailorkey", base_variant)
        variant_layout = build_layout("tailorkey", variant)

        base_typing = copy.deepcopy(_layer(base_layout, "Typing"))
        remap_layer_keys(base_typing, variant)

        assert base_typing == _layer(variant_layout, "Typing"), f"Remap mismatch for {variant}"
