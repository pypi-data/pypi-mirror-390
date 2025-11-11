import pytest

from glove80.families.tailorkey.layers.autoshift import build_autoshift_layer

from .helpers import TAILORKEY_VARIANTS


def _canonical_layer(variant: str, loader):
    data = loader(variant)
    idx = data["layer_names"].index("Autoshift")
    return data["layers"][idx]


@pytest.mark.parametrize("variant", TAILORKEY_VARIANTS)
def test_autoshift_layer(variant, load_tailorkey_variant) -> None:
    assert build_autoshift_layer(variant) == _canonical_layer(variant, load_tailorkey_variant)
