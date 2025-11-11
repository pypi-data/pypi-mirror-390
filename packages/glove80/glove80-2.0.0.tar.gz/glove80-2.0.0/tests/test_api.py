from __future__ import annotations

from glove80 import (
    apply_feature,
    bilateral_home_row_components,
    build_layout,
    list_families,
)


def test_top_level_api_is_importable_and_works() -> None:
    families = list_families()
    assert "tailorkey" in families

    layout = build_layout("tailorkey", "windows")
    before = len(layout["macros"]) if "macros" in layout else 0
    components = bilateral_home_row_components("windows")
    apply_feature(layout, components)
    assert len(layout["macros"]) >= before
