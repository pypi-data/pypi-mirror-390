"""Combo specifications for TailorKey variants."""

from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

from glove80.base import LayerRef
from glove80.specs import ComboSpec
from glove80.specs.utils import kp, ks, mod, layer_param


ORDER = (
    "capslock_v1_TKZ",
    "F11_v1_TKZ",
    "F12_v1_TKZ",
    "sticky_hyp_rght_v1_TKZ",
    "sticky_meh_rght_v1_TKZ",
    "gaming_layer_v1_TKZ",
)


BASE_COMBOS = {
    "capslock_v1_TKZ": ComboSpec(
        name="capslock_v1_TKZ",
        description="capslock when pressing both T1's - TailorKey",
        binding=kp("CAPS"),
        key_positions=(52, 57),
        timeout_ms=50,
        layers=(LayerRef("HRM_WinLinx"), LayerRef("Autoshift")),
    ),
    "F11_v1_TKZ": ComboSpec(
        name="F11_v1_TKZ",
        description="F11 on RH_C5 and RH_R1+R2 - TailorKey",
        binding=kp("F11"),
        key_positions=(8, 20),
        timeout_ms=50,
        layers=(LayerRef("HRM_WinLinx"), LayerRef("Autoshift")),
    ),
    "F12_v1_TKZ": ComboSpec(
        name="F12_v1_TKZ",
        description="F12 on RH_C6 and RH_R1+R2 - TailorKey",
        binding=kp("F12"),
        key_positions=(9, 21),
        timeout_ms=50,
        layers=(LayerRef("HRM_WinLinx"), LayerRef("Autoshift")),
    ),
    "sticky_hyp_rght_v1_TKZ": ComboSpec(
        name="sticky_hyp_rght_v1_TKZ",
        description='sticky "hyper" modifiers (Win + Alt + Ctrl + Shift) - TailorKey',
        binding=ks("&sk", mod("LG", mod("LA", mod("LC", "LSHFT")))),
        key_positions=(74, 57),
        timeout_ms=50,
        layers=(LayerRef("HRM_WinLinx"), LayerRef("Autoshift")),
    ),
    "sticky_meh_rght_v1_TKZ": ComboSpec(
        name="sticky_meh_rght_v1_TKZ",
        description='sticky "meh" modifiers (Alt + Ctrl + Shift) - TailorKey',
        binding=ks("&sk", mod("LA", mod("LC", "LSHFT"))),
        key_positions=(73, 74),
        timeout_ms=50,
        layers=(LayerRef("HRM_WinLinx"), LayerRef("Autoshift")),
    ),
    "gaming_layer_v1_TKZ": ComboSpec(
        name="gaming_layer_v1_TKZ",
        description="toggle gaming layer - TailorKey",
        binding=ks("&tog", layer_param("Gaming")),
        key_positions=(51, 68),
        timeout_ms=50,
        layers=(-1,),
    ),
}


def _with_layers(combo: ComboSpec, layers: Iterable[LayerRef | int]) -> ComboSpec:
    return ComboSpec(
        name=combo.name,
        description=combo.description,
        binding=combo.binding,
        key_positions=combo.key_positions,
        timeout_ms=combo.timeout_ms,
        layers=tuple(layers),
    )


def _with_description(combo: ComboSpec, description: str) -> ComboSpec:
    return ComboSpec(
        name=combo.name,
        description=description,
        binding=combo.binding,
        key_positions=combo.key_positions,
        timeout_ms=combo.timeout_ms,
        layers=combo.layers,
    )


def _layers(*names: str) -> Tuple[LayerRef, ...]:
    return tuple(LayerRef(name) for name in names)


WINDOWS_STICKY_DESC = 'sticky "hyper" modifiers (Win + Alt + Ctrl + Shift) - Use with Tab - TailorKey'
WINDOWS_MEH_DESC = 'sticky "meh" modifiers (Alt + Ctrl + Shift) - Use with Tab - TailorKey'

COMBO_DATA: Dict[str, List[ComboSpec]] = {
    "windows": [
        BASE_COMBOS["capslock_v1_TKZ"],
        BASE_COMBOS["F11_v1_TKZ"],
        BASE_COMBOS["F12_v1_TKZ"],
        _with_description(BASE_COMBOS["sticky_hyp_rght_v1_TKZ"], WINDOWS_STICKY_DESC),
        _with_description(BASE_COMBOS["sticky_meh_rght_v1_TKZ"], WINDOWS_MEH_DESC),
        BASE_COMBOS["gaming_layer_v1_TKZ"],
    ],
}


def _variant_list(layer_names: Tuple[str, ...]) -> List[ComboSpec]:
    combos: List[ComboSpec] = []
    for name in ORDER:
        combo = BASE_COMBOS[name]
        if combo.layers == (-1,):
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


__all__ = ["COMBO_DATA"]
