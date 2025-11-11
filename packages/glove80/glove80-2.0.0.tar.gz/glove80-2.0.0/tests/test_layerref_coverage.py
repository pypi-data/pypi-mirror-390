from __future__ import annotations

import pytest

from glove80 import build_layout
from glove80.layouts.parse import parse_typed_sections

FAMILY_FIXTURES = (
    ("default", "default_variants"),
    ("tailorkey", "tailorkey_variants"),
    ("quantum_touch", "quantum_touch_variants"),
    ("glorious_engrammer", "glorious_engrammer_variants"),
)


def _assert_indices(indices, limit: int, label: str) -> None:
    for idx in indices:
        assert isinstance(idx, int), f"{label} must contain integer layer indices"
        if idx == -1:  # Sentinel meaning "all layers"
            continue
        assert 0 <= idx < limit, f"Layer index {idx} out of range for {label}"


@pytest.mark.parametrize("family,variant_fixture", FAMILY_FIXTURES)
def test_layer_references_are_in_bounds(request, family: str, variant_fixture: str) -> None:
    variants = request.getfixturevalue(variant_fixture)
    for variant in variants:
        layout = build_layout(family, variant)
        _, _, _, combos, listeners = parse_typed_sections(layout)
        layer_count = len(layout["layer_names"])

        for combo in combos:
            _assert_indices(combo.layers, layer_count, f"combo {combo.name}")

        for listener in listeners:
            for node in listener.nodes:
                _assert_indices(node.layers, layer_count, f"listener {listener.code}")
