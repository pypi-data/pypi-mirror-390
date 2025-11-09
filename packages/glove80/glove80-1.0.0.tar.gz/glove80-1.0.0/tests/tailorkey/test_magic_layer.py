import pytest

from glove80.families.tailorkey.layers.magic import build_magic_layer


VARIANTS = [
    "windows",
    "mac",
    "dual",
    "bilateral_windows",
    "bilateral_mac",
]


def _canonical_layer(variant: str, loader):
    data = loader(variant)
    idx = data["layer_names"].index("Magic")
    return data["layers"][idx]


@pytest.mark.parametrize("variant", VARIANTS)
def test_magic_layer(variant, load_tailorkey_variant):
    assert build_magic_layer(variant) == _canonical_layer(variant, load_tailorkey_variant)
