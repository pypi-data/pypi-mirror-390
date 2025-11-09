import pytest

from glove80.families.tailorkey.layers.symbol import build_symbol_layer


VARIANTS = [
    "windows",
    "mac",
    "dual",
    "bilateral_windows",
    "bilateral_mac",
]


def _load_canonical_layer(variant: str, loader):
    data = loader(variant)
    idx = data["layer_names"].index("Symbol")
    return data["layers"][idx]


@pytest.mark.parametrize("variant", VARIANTS)
def test_symbol_layer_matches_canonical(variant, load_tailorkey_variant):
    assert build_symbol_layer(variant) == _load_canonical_layer(variant, load_tailorkey_variant)
