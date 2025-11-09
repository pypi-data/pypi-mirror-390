import pytest

from glove80.families.tailorkey.layers.typing import build_typing_layer


VARIANTS = [
    "windows",
    "mac",
    "dual",
    "bilateral_windows",
    "bilateral_mac",
]


def _load_layer(variant: str, loader):
    data = loader(variant)
    idx = data["layer_names"].index("Typing")
    return data["layers"][idx]


@pytest.mark.parametrize("variant", VARIANTS)
def test_typing_layer(variant, load_tailorkey_variant):
    assert build_typing_layer(variant) == _load_layer(variant, load_tailorkey_variant)
