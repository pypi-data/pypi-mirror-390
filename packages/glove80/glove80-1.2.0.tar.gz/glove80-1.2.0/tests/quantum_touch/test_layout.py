from glove80 import build_layout as build_family_layout


def test_quantum_touch_matches_original(load_quantum_touch_variant):
    expected = load_quantum_touch_variant("default")
    built = build_family_layout("quantum_touch", "default")
    assert built == expected
