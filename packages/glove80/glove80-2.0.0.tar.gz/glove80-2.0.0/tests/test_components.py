from __future__ import annotations

from glove80.features import apply_feature
from glove80.layouts.components import LayoutFeatureComponents


def test_macros_by_name_overrides_and_preserves_order() -> None:
    layout = {
        "macros": [{"name": "foo", "a": 1}],
        "holdTaps": [],
        "combos": [],
        "inputListeners": [],
        "layer_names": [],
        "layers": [],
    }

    components = LayoutFeatureComponents(
        macros_by_name={
            "foo": {"name": "foo", "a": 2},  # override existing
            "bar": {"name": "bar", "b": 3},  # append new
        }
    )

    apply_feature(layout, components)

    names = [m["name"] for m in layout["macros"]]
    assert names == ["foo", "bar"], names
    by_name = {m["name"]: m for m in layout["macros"]}
    assert by_name["foo"]["a"] == 2
    assert by_name["bar"]["b"] == 3
