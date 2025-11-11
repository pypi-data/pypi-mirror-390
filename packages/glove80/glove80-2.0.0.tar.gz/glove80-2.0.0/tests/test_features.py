from glove80.families.tailorkey.layouts import Family as TailorKeyFamily
from glove80.features import apply_feature, bilateral_home_row_components


def test_bilateral_feature_adds_macros_and_layers() -> None:
    family = TailorKeyFamily()
    layout = family.build("windows")
    base_macro_count = len(layout["macros"])

    components = bilateral_home_row_components("windows")
    apply_feature(layout, components)

    assert len(layout["macros"]) == base_macro_count + len(components.macros)
    for layer_name in components.layers:
        assert layer_name in layout["layer_names"]
