from glove80 import build_layout as build_family_layout


def test_glorious_engrammer_matches_release(load_glorious_engrammer_variant):
    expected = load_glorious_engrammer_variant("v42_rc6_preview")
    built = build_family_layout("glorious_engrammer", "v42_rc6_preview")
    assert built == expected
