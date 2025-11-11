from glove80.families.tailorkey.alpha_layouts import remap_layer_keys


def test_remap_layer_keys_is_noop_for_qwerty_variants() -> None:
    layer = [{"value": "&kp", "params": [{"value": "A"}]}]

    remap_layer_keys(layer, "windows")

    assert layer[0]["params"][0]["value"] == "A"
