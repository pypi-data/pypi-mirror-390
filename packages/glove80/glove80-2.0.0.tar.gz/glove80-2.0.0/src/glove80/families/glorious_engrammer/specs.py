from __future__ import annotations

from importlib import resources
from typing import Any
from collections.abc import Mapping, Sequence

from pydantic import BaseModel, ConfigDict
from glove80.layouts.common import build_common_fields

from .layers import LAYER_SPECS

from glove80.base import LayerSpec


def _load_text(name: str) -> str:
    return resources.files(__package__).joinpath(name).read_text(encoding="utf-8")


CUSTOM_DEFINED_BEHAVIORS = _load_text("custom_behaviors.txt")
CUSTOM_DEVICE_TREE = _load_text("custom_devicetree.dtsi")

LAYER_ORDER: Sequence[str] = (
    "Enthium",
    "Engrammer",
    "Engram",
    "Dvorak",
    "Colemak",
    "QWERTY",
    "ColemakDH",
    "Typing",
    "LeftPinky",
    "LeftRingy",
    "LeftMiddy",
    "LeftIndex",
    "RightPinky",
    "RightRingy",
    "RightMiddy",
    "RightIndex",
    "Cursor",
    "Number",
    "Function",
    "Emoji",
    "World",
    "Symbol",
    "System",
    "Mouse",
    "MouseFine",
    "MouseSlow",
    "MouseFast",
    "MouseWarp",
    "Gaming",
    "Factory",
    "Lower",
    "Magic",
)


class VariantSpec(BaseModel):
    model_config = ConfigDict(frozen=True)

    common_fields: dict[str, Any]
    layer_names: Sequence[str]
    layer_specs: Mapping[str, LayerSpec]


VARIANT_SPECS: dict[str, VariantSpec] = {
    "v42_rc6_preview": VariantSpec(
        common_fields=build_common_fields(
            creator="sunaku",
            custom_defined_behaviors=CUSTOM_DEFINED_BEHAVIORS,
            custom_devicetree=CUSTOM_DEVICE_TREE,
        ),
        layer_names=LAYER_ORDER,
        layer_specs={
            "Enthium": LAYER_SPECS["Enthium"],
            "Engrammer": LAYER_SPECS["Engrammer"],
            "Engram": LAYER_SPECS["Engram"],
            "Dvorak": LAYER_SPECS["Dvorak"],
            "Colemak": LAYER_SPECS["Colemak"],
            "QWERTY": LAYER_SPECS["QWERTY"],
            "ColemakDH": LAYER_SPECS["ColemakDH"],
            "Typing": LAYER_SPECS["Typing"],
            "LeftPinky": LAYER_SPECS["LeftPinky"],
            "LeftRingy": LAYER_SPECS["LeftRingy"],
            "LeftMiddy": LAYER_SPECS["LeftMiddy"],
            "LeftIndex": LAYER_SPECS["LeftIndex"],
            "RightPinky": LAYER_SPECS["RightPinky"],
            "RightRingy": LAYER_SPECS["RightRingy"],
            "RightMiddy": LAYER_SPECS["RightMiddy"],
            "RightIndex": LAYER_SPECS["RightIndex"],
            "Cursor": LAYER_SPECS["Cursor"],
            "Number": LAYER_SPECS["Number"],
            "Function": LAYER_SPECS["Function"],
            "Emoji": LAYER_SPECS["Emoji"],
            "World": LAYER_SPECS["World"],
            "Symbol": LAYER_SPECS["Symbol"],
            "System": LAYER_SPECS["System"],
            "Mouse": LAYER_SPECS["Mouse"],
            "MouseFine": LAYER_SPECS["MouseFine"],
            "MouseSlow": LAYER_SPECS["MouseSlow"],
            "MouseFast": LAYER_SPECS["MouseFast"],
            "MouseWarp": LAYER_SPECS["MouseWarp"],
            "Gaming": LAYER_SPECS["Gaming"],
            "Factory": LAYER_SPECS["Factory"],
            "Lower": LAYER_SPECS["Lower"],
            "Magic": LAYER_SPECS["Magic"],
        },
    ),
}

__all__ = ["LAYER_ORDER", "VARIANT_SPECS", "VariantSpec"]
