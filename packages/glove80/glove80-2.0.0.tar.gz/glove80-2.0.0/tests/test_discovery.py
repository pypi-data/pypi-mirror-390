from __future__ import annotations

import pytest

from glove80.layouts.generator import available_layouts
from glove80 import metadata


def test_generator_imports_all_metadata_packages() -> None:
    """Discovery derives from LAYOUT_METADATA_PACKAGES values."""
    discovered = set(available_layouts())
    expected = set(metadata.layout_metadata_packages().keys())
    assert expected.issubset(discovered)


def test_layout_metadata_packages_include_entry_points(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_iter() -> list[tuple[str, str]]:
        return [("custom", "custom_pkg.families.custom")]

    monkeypatch.setattr(metadata, "_iter_entry_point_layouts", fake_iter)
    metadata._refresh_layout_metadata_packages_for_tests()
    try:
        packages = metadata.layout_metadata_packages()
        assert packages["custom"] == "custom_pkg.families.custom"
    finally:
        metadata._refresh_layout_metadata_packages_for_tests()
