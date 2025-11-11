from __future__ import annotations

from typing import Any
from collections.abc import Mapping, Sequence

from pydantic import BaseModel, ConfigDict

from glove80.layouts.common import build_common_fields
from glove80.layouts.schema import InputListener, InputProcessor, ListenerNode

from .layer_data import BASE_LAYERS, FACTORY_LAYERS, LOWER_LAYERS, MAGIC_LAYERS, MOUSE_EXTRAS

from glove80.base import LayerSpec


class VariantSpec(BaseModel):
    model_config = ConfigDict(frozen=True)

    common_fields: dict[str, Any]
    layer_names: Sequence[str]
    layer_specs: Mapping[str, LayerSpec]
    input_listeners: Sequence[InputListener] = ()


MOUSE_INPUT_LISTENERS: Sequence[InputListener] = (
    InputListener(
        code="&mmv_input_listener",
        nodes=[
            ListenerNode(
                code="LAYER_MouseSlow",
                description="LAYER_MouseSlow",
                layers=[3],
                inputProcessors=[InputProcessor(code="&zip_xy_scaler", params=[1, 9])],
            ),
            ListenerNode(
                code="LAYER_MouseFast",
                description="LAYER_MouseFast",
                layers=[4],
                inputProcessors=[InputProcessor(code="&zip_xy_scaler", params=[3, 1])],
            ),
            ListenerNode(
                code="LAYER_MouseWarp",
                description="LAYER_MouseWarp",
                layers=[5],
                inputProcessors=[InputProcessor(code="&zip_xy_scaler", params=[12, 1])],
            ),
        ],
    ),
    InputListener(
        code="&msc_input_listener",
        nodes=[
            ListenerNode(
                code="LAYER_MouseSlow",
                description="LAYER_MouseSlow",
                layers=[3],
                inputProcessors=[InputProcessor(code="&zip_scroll_scaler", params=[1, 9])],
            ),
            ListenerNode(
                code="LAYER_MouseFast",
                description="LAYER_MouseFast",
                layers=[4],
                inputProcessors=[InputProcessor(code="&zip_scroll_scaler", params=[3, 1])],
            ),
            ListenerNode(
                code="LAYER_MouseWarp",
                description="LAYER_MouseWarp",
                layers=[5],
                inputProcessors=[InputProcessor(code="&zip_scroll_scaler", params=[12, 1])],
            ),
        ],
    ),
)


def _variant_layers(name: str, *, extra_layers: Mapping[str, LayerSpec] | None = None) -> dict[str, LayerSpec]:
    layers = {
        "Base": BASE_LAYERS[name],
        "Lower": LOWER_LAYERS[name],
        "Magic": MAGIC_LAYERS[name],
    }
    if name in FACTORY_LAYERS:
        layers["Factory"] = FACTORY_LAYERS[name]
    if extra_layers:
        layers.update(extra_layers)
    return layers


VARIANT_SPECS: dict[str, VariantSpec] = {
    "factory_default": VariantSpec(
        common_fields=build_common_fields(creator="moergo"),
        layer_names=("Base", "Lower", "Magic", "Factory"),
        layer_specs=_variant_layers("factory_default"),
    ),
    "factory_default_macos": VariantSpec(
        common_fields=build_common_fields(creator="moergo"),
        layer_names=("Base", "Lower", "Magic", "Factory"),
        layer_specs=_variant_layers("factory_default_macos"),
    ),
    "colemak": VariantSpec(
        common_fields=build_common_fields(creator="moergo"),
        layer_names=("Base", "Lower", "Magic"),
        layer_specs=_variant_layers("colemak"),
    ),
    "colemak_dh": VariantSpec(
        common_fields=build_common_fields(creator="moergo"),
        layer_names=("Base", "Lower", "Magic"),
        layer_specs=_variant_layers("colemak_dh"),
    ),
    "dvorak": VariantSpec(
        common_fields=build_common_fields(creator="moergo"),
        layer_names=("Base", "Lower", "Magic"),
        layer_specs=_variant_layers("dvorak"),
    ),
    "workman": VariantSpec(
        common_fields=build_common_fields(creator="moergo"),
        layer_names=("Base", "Lower", "Magic"),
        layer_specs=_variant_layers("workman"),
    ),
    "kinesis": VariantSpec(
        common_fields=build_common_fields(creator="moergo"),
        layer_names=("Base", "Lower", "Magic"),
        layer_specs=_variant_layers("kinesis"),
    ),
    "mouse_emulation": VariantSpec(
        common_fields=build_common_fields(
            creator="MoErgo",
            config_parameters=[{"paramName": "HID_POINTING", "value": "y"}],
        ),
        layer_names=("Base", "Lower", "Mouse", "MouseSlow", "MouseFast", "MouseWarp", "Magic"),
        layer_specs=_variant_layers("mouse_emulation", extra_layers=MOUSE_EXTRAS["mouse_emulation"]),
        input_listeners=MOUSE_INPUT_LISTENERS,
    ),
}
__all__ = ["VARIANT_SPECS", "VariantSpec"]
