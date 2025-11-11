from glove80 import build_layout as build_family_layout
from tests.assertions import assert_layout_equal


def test_quantum_touch_matches_original(load_quantum_touch_variant) -> None:
    expected = load_quantum_touch_variant("default")
    built = build_family_layout("quantum_touch", "default")
    assert_layout_equal(built, expected, label="quantum_touch:default")
