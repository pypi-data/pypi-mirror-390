import pytest

from glove80.families.tailorkey.layers.cursor import build_cursor_layer


VARIANTS = [
    "windows",
    "mac",
    "dual",
    "bilateral_windows",
    "bilateral_mac",
]


def _load_canonical_layer(variant: str, loader):
    data = loader(variant)
    name = "Cursor"
    idx = data["layer_names"].index(name)
    return data["layers"][idx]


@pytest.mark.parametrize("variant", VARIANTS)
def test_cursor_layer_matches_canonical(variant, load_tailorkey_variant):
    assert build_cursor_layer(variant) == _load_canonical_layer(variant, load_tailorkey_variant)
