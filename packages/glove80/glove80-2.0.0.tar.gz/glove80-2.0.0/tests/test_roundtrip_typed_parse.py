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


def _dump(section):
    return [item.model_dump(by_alias=True, exclude_none=True) for item in section]


@pytest.mark.parametrize("family,variant_fixture", FAMILY_FIXTURES)
def test_roundtrip_parse_matches_payload(request, family: str, variant_fixture: str) -> None:
    variants = request.getfixturevalue(variant_fixture)
    for variant in variants:
        layout = build_layout(family, variant)
        payload, macros, hold_taps, combos, listeners = parse_typed_sections(layout)

        assert payload.model_dump(by_alias=True, exclude_none=True) == layout
        assert _dump(macros) == layout["macros"]
        assert _dump(hold_taps) == layout["holdTaps"]
        assert _dump(combos) == layout["combos"]
        assert _dump(listeners) == layout["inputListeners"]
