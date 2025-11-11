from __future__ import annotations

from glove80.layouts.builder import LayoutBuilder
from glove80.layouts.common import BASE_COMMON_FIELDS, compose_layout
from glove80.layouts.components import LayoutFeatureComponents
from glove80.layouts.schema import Combo, Macro


def _mock_layer(token: str) -> list[dict[str, object]]:
    return [{"value": token, "params": []} for _ in range(4)]


def _mock_feature_components(name: str) -> LayoutFeatureComponents:
    macro = Macro(
        name=name,
        description=None,
        bindings=[{"value": "&kp", "params": [{"value": "A", "params": []}]}],
    )
    return LayoutFeatureComponents(macros=[macro], layers={f"{name}_layer": _mock_layer(name)})


def test_builder_matches_compose_layout() -> None:
    layers = {
        "Typing": _mock_layer("&kp_A"),
        "Symbol": _mock_layer("&kp_HASH"),
    }
    macros = [
        Macro(
            name="&macro_demo",
            description=None,
            bindings=[{"value": "&kp", "params": [{"value": "A", "params": []}]}],
        )
    ]
    combos = [
        Combo(
            name="combo_demo",
            description=None,
            binding={"value": "&kp", "params": [{"value": "A", "params": []}]},
            keyPositions=[0, 1],
            layers=[0, 1],
        )
    ]

    builder = LayoutBuilder(
        metadata_key="default",
        variant="factory_default",
        common_fields=BASE_COMMON_FIELDS,
        layer_names=["Typing", "Symbol"],
    )
    builder.add_layers(layers)
    builder.add_macros(macros)
    builder.add_combos(combos)

    built = builder.build()
    expected = compose_layout(
        BASE_COMMON_FIELDS,
        layer_names=["Typing", "Symbol"],
        macros=macros,
        combos=combos,
        hold_taps=[],
        input_listeners=[],
        generated_layers=layers,
        metadata_key="default",
        variant="factory_default",
    )

    assert built == expected


def test_add_home_row_mods_inserts_layers_and_sections() -> None:
    base_layers = {
        "Typing": _mock_layer("&kp_A"),
        "Symbol": _mock_layer("&kp_HASH"),
    }
    builder = LayoutBuilder(
        metadata_key="tailorkey",
        variant="windows",
        common_fields=BASE_COMMON_FIELDS,
        layer_names=["Typing", "Symbol"],
        home_row_provider=lambda _: _mock_feature_components("&hrm_macro"),
    )
    builder.add_layers(base_layers)

    builder.add_home_row_mods(target_layer="Typing")

    layout = builder.build()
    assert layout["macros"][0]["name"] == "&hrm_macro"
    assert layout["layer_names"][1] == "&hrm_macro_layer"


def test_add_mouse_layers_respects_order() -> None:
    builder = LayoutBuilder(
        metadata_key="tailorkey",
        variant="windows",
        common_fields=BASE_COMMON_FIELDS,
        layer_names=["Typing"],
        mouse_layers_provider=lambda _: {"Mouse": _mock_layer("&mouse")},
    )
    builder.add_layers({"Typing": _mock_layer("&kp_A")})
    builder.add_mouse_layers(insert_after="Typing")

    layout = builder.build()
    assert layout["layer_names"][1] == "Mouse"


def test_high_level_feature_methods_use_providers() -> None:
    builder = LayoutBuilder(
        metadata_key="tailorkey",
        variant="windows",
        common_fields=BASE_COMMON_FIELDS,
        layer_names=["Typing"],
        mouse_layers_provider=lambda _: {"Mouse": _mock_layer("&mouse")},
        cursor_layers_provider=lambda _: {"Cursor": _mock_layer("&cursor")},
        home_row_provider=lambda _: _mock_feature_components("&hrm_macro"),
    )
    builder.add_layers({"Typing": _mock_layer("&kp_A")})

    builder.add_mouse_layers(insert_after="Typing")
    builder.add_cursor_layer(insert_after="Mouse")
    builder.add_home_row_mods(target_layer="Typing", insert_after="Cursor")

    layout = builder.build()
    assert layout["layer_names"][1] == "Mouse"
    assert layout["layer_names"][2] == "Cursor"
    assert layout["layer_names"][3] == "&hrm_macro_layer"
    assert any(macro["name"] == "&hrm_macro" for macro in layout["macros"])
