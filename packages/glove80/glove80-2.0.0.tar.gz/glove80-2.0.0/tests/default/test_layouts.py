import pytest

from glove80 import build_layout as build_family_layout
from tests.assertions import assert_layout_equal


@pytest.mark.parametrize(
    "variant",
    [
        "factory_default",
        "factory_default_macos",
        "mouse_emulation",
        "colemak",
        "colemak_dh",
        "dvorak",
        "workman",
        "kinesis",
    ],
)
def test_default_layout_matches_release(variant, load_default_variant) -> None:
    expected = load_default_variant(variant)
    built = build_family_layout("default", variant)
    assert_layout_equal(built, expected, label=f"default:{variant}")
