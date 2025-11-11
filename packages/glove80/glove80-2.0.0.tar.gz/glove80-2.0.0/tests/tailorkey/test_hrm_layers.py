import pytest

from glove80.families.tailorkey.layers.hrm import build_hrm_layers

from .helpers import TAILORKEY_VARIANTS


def _canonical_layers(variant: str, loader):
    data = loader(variant)
    layer_map = {}
    for idx, name in enumerate(data["layer_names"]):
        if name.startswith("HRM"):
            layer_map[name] = data["layers"][idx]
    return layer_map


@pytest.mark.parametrize("variant", TAILORKEY_VARIANTS)
def test_hrm_layers(variant, load_tailorkey_variant) -> None:
    expected = _canonical_layers(variant, load_tailorkey_variant)
    actual = build_hrm_layers(variant)
    assert actual.keys() == expected.keys()
    for name, layer in expected.items():
        assert actual[name] == layer
