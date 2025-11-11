import pytest

from glove80.families.tailorkey.layers.cursor import build_cursor_layer

from .helpers import TAILORKEY_VARIANTS


def _load_canonical_layer(variant: str, loader):
    data = loader(variant)
    name = "Cursor"
    idx = data["layer_names"].index(name)
    return data["layers"][idx]


@pytest.mark.parametrize("variant", TAILORKEY_VARIANTS)
def test_cursor_layer_matches_canonical(variant, load_tailorkey_variant) -> None:
    assert build_cursor_layer(variant) == _load_canonical_layer(variant, load_tailorkey_variant)
