import pytest

from glove80.families.tailorkey.layers.symbol import build_symbol_layer

from .helpers import TAILORKEY_VARIANTS


def _load_canonical_layer(variant: str, loader):
    data = loader(variant)
    idx = data["layer_names"].index("Symbol")
    return data["layers"][idx]


@pytest.mark.parametrize("variant", TAILORKEY_VARIANTS)
def test_symbol_layer_matches_canonical(variant, load_tailorkey_variant) -> None:
    assert build_symbol_layer(variant) == _load_canonical_layer(variant, load_tailorkey_variant)
