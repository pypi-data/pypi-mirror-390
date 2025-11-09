from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Sequence

from glove80.base import LayerSpec
from glove80.layouts.common import _build_common_fields
from glove80.specs.primitives import InputListenerNodeSpec, InputListenerSpec, InputProcessorSpec

from .layer_data import BASE_LAYERS, FACTORY_LAYERS, LOWER_LAYERS, MAGIC_LAYERS, MOUSE_EXTRAS


@dataclass(frozen=True)
class VariantSpec:
    common_fields: Dict[str, Any]
    layer_names: Sequence[str]
    layer_specs: Mapping[str, LayerSpec]
    input_listeners: Sequence[InputListenerSpec] = ()


MOUSE_INPUT_LISTENERS: Sequence[InputListenerSpec] = (
    InputListenerSpec(
        code="&mmv_input_listener",
        nodes=(
            InputListenerNodeSpec(
                code="LAYER_MouseSlow",
                description="LAYER_MouseSlow",
                layers=(3,),
                input_processors=(InputProcessorSpec(code="&zip_xy_scaler", params=(1, 9)),),
            ),
            InputListenerNodeSpec(
                code="LAYER_MouseFast",
                description="LAYER_MouseFast",
                layers=(4,),
                input_processors=(InputProcessorSpec(code="&zip_xy_scaler", params=(3, 1)),),
            ),
            InputListenerNodeSpec(
                code="LAYER_MouseWarp",
                description="LAYER_MouseWarp",
                layers=(5,),
                input_processors=(InputProcessorSpec(code="&zip_xy_scaler", params=(12, 1)),),
            ),
        ),
    ),
    InputListenerSpec(
        code="&msc_input_listener",
        nodes=(
            InputListenerNodeSpec(
                code="LAYER_MouseSlow",
                description="LAYER_MouseSlow",
                layers=(3,),
                input_processors=(InputProcessorSpec(code="&zip_scroll_scaler", params=(1, 9)),),
            ),
            InputListenerNodeSpec(
                code="LAYER_MouseFast",
                description="LAYER_MouseFast",
                layers=(4,),
                input_processors=(InputProcessorSpec(code="&zip_scroll_scaler", params=(3, 1)),),
            ),
            InputListenerNodeSpec(
                code="LAYER_MouseWarp",
                description="LAYER_MouseWarp",
                layers=(5,),
                input_processors=(InputProcessorSpec(code="&zip_scroll_scaler", params=(12, 1)),),
            ),
        ),
    ),
)


def _variant_layers(name: str, *, extra_layers: Mapping[str, LayerSpec] | None = None) -> Dict[str, LayerSpec]:
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


VARIANT_SPECS: Dict[str, VariantSpec] = {
    "factory_default": VariantSpec(
        common_fields=_build_common_fields(creator="moergo"),
        layer_names=("Base", "Lower", "Magic", "Factory"),
        layer_specs=_variant_layers("factory_default"),
    ),
    "factory_default_macos": VariantSpec(
        common_fields=_build_common_fields(creator="moergo"),
        layer_names=("Base", "Lower", "Magic", "Factory"),
        layer_specs=_variant_layers("factory_default_macos"),
    ),
    "colemak": VariantSpec(
        common_fields=_build_common_fields(creator="moergo"),
        layer_names=("Base", "Lower", "Magic"),
        layer_specs=_variant_layers("colemak"),
    ),
    "colemak_dh": VariantSpec(
        common_fields=_build_common_fields(creator="moergo"),
        layer_names=("Base", "Lower", "Magic"),
        layer_specs=_variant_layers("colemak_dh"),
    ),
    "dvorak": VariantSpec(
        common_fields=_build_common_fields(creator="moergo"),
        layer_names=("Base", "Lower", "Magic"),
        layer_specs=_variant_layers("dvorak"),
    ),
    "workman": VariantSpec(
        common_fields=_build_common_fields(creator="moergo"),
        layer_names=("Base", "Lower", "Magic"),
        layer_specs=_variant_layers("workman"),
    ),
    "kinesis": VariantSpec(
        common_fields=_build_common_fields(creator="moergo"),
        layer_names=("Base", "Lower", "Magic"),
        layer_specs=_variant_layers("kinesis"),
    ),
    "mouse_emulation": VariantSpec(
        common_fields=_build_common_fields(
            creator="MoErgo",
            config_parameters=[{"paramName": "HID_POINTING", "value": "y"}],
        ),
        layer_names=("Base", "Lower", "Mouse", "MouseSlow", "MouseFast", "MouseWarp", "Magic"),
        layer_specs=_variant_layers("mouse_emulation", extra_layers=MOUSE_EXTRAS["mouse_emulation"]),
        input_listeners=MOUSE_INPUT_LISTENERS,
    ),
}
__all__ = ["VARIANT_SPECS", "VariantSpec"]
