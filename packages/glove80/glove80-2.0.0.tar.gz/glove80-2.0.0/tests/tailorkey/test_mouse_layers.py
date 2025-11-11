import pytest

from glove80.families.tailorkey.layers.mouse import build_mouse_layers

from .helpers import TAILORKEY_VARIANTS

LAYER_NAMES = ["Mouse", "MouseSlow", "MouseFast", "MouseWarp"]


def _load_canonical_layers(variant: str, loader):
    data = loader(variant)
    layers = {}
    for layer_name in LAYER_NAMES:
        idx = data["layer_names"].index(layer_name)
        layers[layer_name] = data["layers"][idx]
    return layers


@pytest.mark.parametrize("variant", TAILORKEY_VARIANTS)
def test_mouse_layers_match_canonical(variant, load_tailorkey_variant) -> None:
    expected = _load_canonical_layers(variant, load_tailorkey_variant)
    generated = build_mouse_layers(variant)
    assert generated == expected
