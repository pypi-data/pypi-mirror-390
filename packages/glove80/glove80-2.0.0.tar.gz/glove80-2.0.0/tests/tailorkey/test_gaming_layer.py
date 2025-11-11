import pytest

from glove80.families.tailorkey.layers.gaming import build_gaming_layer

from .helpers import TAILORKEY_VARIANTS


def _canonical_layer(variant: str, loader):
    data = loader(variant)
    idx = data["layer_names"].index("Gaming")
    return data["layers"][idx]


@pytest.mark.parametrize("variant", TAILORKEY_VARIANTS)
def test_gaming_layer(variant, load_tailorkey_variant) -> None:
    assert build_gaming_layer(variant) == _canonical_layer(variant, load_tailorkey_variant)
