import pytest

from glove80.families.tailorkey.layers.typing import build_typing_layer

from .helpers import TAILORKEY_VARIANTS


def _load_layer(variant: str, loader):
    data = loader(variant)
    idx = data["layer_names"].index("Typing")
    return data["layers"][idx]


@pytest.mark.parametrize("variant", TAILORKEY_VARIANTS)
def test_typing_layer(variant, load_tailorkey_variant) -> None:
    assert build_typing_layer(variant) == _load_layer(variant, load_tailorkey_variant)
