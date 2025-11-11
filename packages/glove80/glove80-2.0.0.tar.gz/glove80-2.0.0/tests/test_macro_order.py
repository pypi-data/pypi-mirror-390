"""Focused macro-order regression tests across layout families."""

from __future__ import annotations

from glove80 import build_layout as build_family_layout


def _macro_names(layout: dict) -> list[str]:
    return [entry["name"] for entry in layout["macros"]]


def test_default_macros_match_release(default_variants, load_default_variant) -> None:
    for variant in default_variants:
        expected = load_default_variant(variant)
        built = build_family_layout("default", variant)
        assert _macro_names(built) == _macro_names(expected), f"default:{variant} macros differ"


def test_tailorkey_macros_match_release(tailorkey_variants, load_tailorkey_variant) -> None:
    for variant in tailorkey_variants:
        expected = load_tailorkey_variant(variant)
        built = build_family_layout("tailorkey", variant)
        assert _macro_names(built) == _macro_names(expected), f"tailorkey:{variant} macros differ"


def test_quantum_touch_macros_match_release(quantum_touch_variants, load_quantum_touch_variant) -> None:
    for variant in quantum_touch_variants:
        expected = load_quantum_touch_variant(variant)
        built = build_family_layout("quantum_touch", variant)
        assert _macro_names(built) == _macro_names(expected), f"quantum_touch:{variant} macros differ"


def test_glorious_engrammer_macros_match_release(
    glorious_engrammer_variants,
    load_glorious_engrammer_variant,
) -> None:
    for variant in glorious_engrammer_variants:
        expected = load_glorious_engrammer_variant(variant)
        built = build_family_layout("glorious_engrammer", variant)
        assert _macro_names(built) == _macro_names(expected), f"glorious_engrammer:{variant} macros differ"
