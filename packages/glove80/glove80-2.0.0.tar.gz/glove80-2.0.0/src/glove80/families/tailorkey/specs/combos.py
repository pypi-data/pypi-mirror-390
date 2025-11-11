"""Combo definitions for TailorKey variants (Pydantic models)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from glove80.base import LayerRef
from glove80.families.tailorkey.alpha_layouts import TAILORKEY_VARIANTS, base_variant_for
from glove80.layouts.schema import Combo
from glove80.specs.utils import kp, ks, layer_param, mod

if TYPE_CHECKING:
    from collections.abc import Iterable

ORDER = (
    "capslock_v1_TKZ",
    "F11_v1_TKZ",
    "F12_v1_TKZ",
    "sticky_hyp_rght_v1_TKZ",
    "sticky_meh_rght_v1_TKZ",
    "gaming_layer_v1_TKZ",
)


BASE_COMBOS = {
    "capslock_v1_TKZ": Combo(
        name="capslock_v1_TKZ",
        description="capslock when pressing both T1's - TailorKey",
        binding=kp("CAPS").to_dict(),
        keyPositions=[52, 57],
        timeoutMs=50,
        layers=[LayerRef("HRM_WinLinx"), LayerRef("Autoshift")],
    ),
    "F11_v1_TKZ": Combo(
        name="F11_v1_TKZ",
        description="F11 on RH_C5 and RH_R1+R2 - TailorKey",
        binding=kp("F11").to_dict(),
        keyPositions=[8, 20],
        timeoutMs=50,
        layers=[LayerRef("HRM_WinLinx"), LayerRef("Autoshift")],
    ),
    "F12_v1_TKZ": Combo(
        name="F12_v1_TKZ",
        description="F12 on RH_C6 and RH_R1+R2 - TailorKey",
        binding=kp("F12").to_dict(),
        keyPositions=[9, 21],
        timeoutMs=50,
        layers=[LayerRef("HRM_WinLinx"), LayerRef("Autoshift")],
    ),
    "sticky_hyp_rght_v1_TKZ": Combo(
        name="sticky_hyp_rght_v1_TKZ",
        description='sticky "hyper" modifiers (Win + Alt + Ctrl + Shift) - TailorKey',
        binding=ks("&sk", mod("LG", mod("LA", mod("LC", "LSHFT")))).to_dict(),
        keyPositions=[74, 57],
        timeoutMs=50,
        layers=[LayerRef("HRM_WinLinx"), LayerRef("Autoshift")],
    ),
    "sticky_meh_rght_v1_TKZ": Combo(
        name="sticky_meh_rght_v1_TKZ",
        description='sticky "meh" modifiers (Alt + Ctrl + Shift) - TailorKey',
        binding=ks("&sk", mod("LA", mod("LC", "LSHFT"))).to_dict(),
        keyPositions=[73, 74],
        timeoutMs=50,
        layers=[LayerRef("HRM_WinLinx"), LayerRef("Autoshift")],
    ),
    "gaming_layer_v1_TKZ": Combo(
        name="gaming_layer_v1_TKZ",
        description="toggle gaming layer - TailorKey",
        binding=ks("&tog", layer_param("Gaming")).to_dict(),
        keyPositions=[51, 68],
        timeoutMs=50,
        layers=[-1],
    ),
}


def _with_layers(combo: Combo, layers: Iterable[LayerRef | int]) -> Combo:
    return Combo(
        name=combo.name,
        description=combo.description,
        binding=combo.binding,
        keyPositions=combo.keyPositions,
        timeoutMs=combo.timeoutMs,
        layers=list(layers),
    )


def _with_description(combo: Combo, description: str) -> Combo:
    return Combo(
        name=combo.name,
        description=description,
        binding=combo.binding,
        keyPositions=combo.keyPositions,
        timeoutMs=combo.timeoutMs,
        layers=combo.layers,
    )


def _layers(*names: str) -> tuple[LayerRef, ...]:
    return tuple(LayerRef(name) for name in names)


WINDOWS_STICKY_DESC = 'sticky "hyper" modifiers (Win + Alt + Ctrl + Shift) - Use with Tab - TailorKey'
WINDOWS_MEH_DESC = 'sticky "meh" modifiers (Alt + Ctrl + Shift) - Use with Tab - TailorKey'

COMBO_DATA: dict[str, list[Combo]] = {
    "windows": [
        BASE_COMBOS["capslock_v1_TKZ"],
        BASE_COMBOS["F11_v1_TKZ"],
        BASE_COMBOS["F12_v1_TKZ"],
        _with_description(BASE_COMBOS["sticky_hyp_rght_v1_TKZ"], WINDOWS_STICKY_DESC),
        _with_description(BASE_COMBOS["sticky_meh_rght_v1_TKZ"], WINDOWS_MEH_DESC),
        BASE_COMBOS["gaming_layer_v1_TKZ"],
    ],
}


def _variant_list(layer_names: tuple[str, ...]) -> list[Combo]:
    combos: list[Combo] = []
    for name in ORDER:
        combo = BASE_COMBOS[name]
        if combo.layers == [-1]:
            combos.append(combo)
        else:
            combos.append(_with_layers(combo, _layers(*layer_names)))
    return combos


COMBO_DATA["mac"] = [
    _with_layers(BASE_COMBOS["F11_v1_TKZ"], _layers("HRM_macOS", "Autoshift")),
    _with_layers(BASE_COMBOS["F12_v1_TKZ"], _layers("HRM_macOS", "Autoshift")),
    _with_layers(BASE_COMBOS["sticky_hyp_rght_v1_TKZ"], _layers("HRM_macOS", "Autoshift")),
    _with_layers(BASE_COMBOS["capslock_v1_TKZ"], _layers("HRM_macOS", "Autoshift")),
    _with_layers(BASE_COMBOS["sticky_meh_rght_v1_TKZ"], _layers("HRM_macOS", "Autoshift")),
    BASE_COMBOS["gaming_layer_v1_TKZ"],
]

COMBO_DATA["dual"] = _variant_list(("HRM_macOS", "HRM_WinLinx", "Autoshift"))

COMBO_DATA["bilateral_windows"] = [
    BASE_COMBOS["capslock_v1_TKZ"],
    BASE_COMBOS["F11_v1_TKZ"],
    BASE_COMBOS["F12_v1_TKZ"],
    BASE_COMBOS["sticky_hyp_rght_v1_TKZ"],
    BASE_COMBOS["sticky_meh_rght_v1_TKZ"],
    BASE_COMBOS["gaming_layer_v1_TKZ"],
]

COMBO_DATA["bilateral_mac"] = [
    BASE_COMBOS["gaming_layer_v1_TKZ"],
    _with_layers(BASE_COMBOS["F12_v1_TKZ"], _layers("Autoshift", "HRM_macOS")),
    _with_layers(BASE_COMBOS["sticky_hyp_rght_v1_TKZ"], _layers("Autoshift", "HRM_macOS")),
    _with_layers(BASE_COMBOS["F11_v1_TKZ"], _layers("Autoshift", "HRM_macOS")),
    _with_layers(BASE_COMBOS["sticky_meh_rght_v1_TKZ"], _layers("Autoshift", "HRM_macOS")),
    _with_layers(BASE_COMBOS["capslock_v1_TKZ"], _layers("HRM_macOS", "Autoshift")),
]


for _variant in TAILORKEY_VARIANTS:
    if _variant not in COMBO_DATA:
        template = base_variant_for(_variant)
        COMBO_DATA[_variant] = list(COMBO_DATA[template])


__all__ = ["COMBO_DATA"]
