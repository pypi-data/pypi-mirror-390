"""Declarative macro specs for TailorKey variants."""

from __future__ import annotations

from typing import Dict

from glove80.specs import MacroSpec
from glove80.specs.utils import call, kp, ks, layer_param, mod

from .finger_data import FINGERS


def _cursor_macro(name: str, description: str, *bindings) -> MacroSpec:
    return MacroSpec(
        name=name,
        description=description,
        bindings=bindings,
        wait_ms=1,
        tap_ms=1,
    )


AS_SHIFTED = MacroSpec(
    name="&AS_Shifted_v1_TKZ",
    description="AutoShift Helper- &AS main macro is chained to &AS_HT hold tap and &AS_Shifted macro - TailorKey",
    bindings=(
        call("&macro_press"),
        kp("LSHFT"),
        call("&macro_tap"),
        call("&macro_param_1to1"),
        kp("N1"),
        call("&macro_release"),
        kp("LSHFT"),
    ),
    params=("code",),
)


AS_ASSIGN = MacroSpec(
    name="&AS_v1_TKZ",
    description="AutoShift (Assign &AS to a Key) - &AS main macro is chained to &AS_HT hold tap and &AS_Shifted macro - TailorKey",
    bindings=(
        call("&macro_press"),
        call("&macro_param_1to1"),
        call("&macro_param_1to2"),
        ks("&AS_HT_v2_TKZ", "A", "A"),
        call("&macro_pause_for_release"),
        call("&macro_release"),
        call("&macro_param_1to1"),
        call("&macro_param_1to2"),
        ks("&AS_HT_v2_TKZ", "A", "A"),
    ),
    params=("code",),
    wait_ms=10,
    tap_ms=10,
)


CURSOR_MACROS = [
    _cursor_macro(
        "&cur_EXTEND_LINE_v1_TKZ",
        "Cursor Layer - Extent Line (seq) - TailorKey",
        kp(mod("LS", "END")),
    ),
    _cursor_macro(
        "&cur_EXTEND_WORD_v1_TKZ",
        "Cursor Layer - Extend Word (seq) - TailorKey",
        kp(mod("LC", mod("LS", "RIGHT"))),
    ),
    _cursor_macro(
        "&cur_SELECT_LINE_v1_TKZ",
        "Cursor Layer - Select Line (seq) - TailorKey",
        kp("HOME"),
        kp(mod("LS", "END")),
    ),
    _cursor_macro(
        "&cur_SELECT_NONE_v1_TKZ",
        "Cursor Layer - Select None (seq) - TailorKey",
        kp("DOWN"),
        kp("UP"),
        kp("RIGHT"),
        kp("LEFT"),
    ),
    _cursor_macro(
        "&cur_SELECT_WORD_v1_TKZ",
        "Cursor Layer - Select Word (seq) - TailorKey",
        kp(mod("LC", "LEFT")),
        kp(mod("LC", mod("LS", "RIGHT"))),
    ),
]


CURSOR_MACROS_MAC = [
    _cursor_macro(
        "&cur_EXTEND_LINE_macos_v1_TKZ",
        "Cursor Layer - Extent Line (seq) - TailorKey",
        kp(mod("LG", mod("LS", "RIGHT"))),
    ),
    _cursor_macro(
        "&cur_EXTEND_WORD_macos_v1_TKZ",
        "Cursor Layer - Extend Word (seq) - TailorKey",
        kp(mod("LA", mod("LS", "RIGHT"))),
    ),
    _cursor_macro(
        "&cur_SELECT_LINE_macos_v1_TKZ",
        "Cursor Layer macos - Select Line (seq) - TailorKey",
        kp(mod("LG", "LEFT")),
        kp(mod("LG", mod("LS", "RIGHT"))),
    ),
    _cursor_macro(
        "&cur_SELECT_WORD_macos_v1_TKZ",
        "Cursor Layer - Select Word (seq) - TailorKey",
        kp(mod("LA", "LEFT")),
        kp(mod("LA", mod("LS", "RIGHT"))),
    ),
]


MOD_TAB_CHORD = MacroSpec(
    name="&mod_tab_chord_v2_TKZ",
    description="mod_tab_switcher_chord -  TailorKey",
    bindings=(
        call("&macro_press"),
        call("&macro_param_2to1"),
        ks("&mo", "MACRO_PLACEHOLDER"),
        call("&macro_press"),
        call("&macro_param_1to1"),
        ks("&mod_tab_v2_TKZ", "MACRO_PLACEHOLDER"),
        call("&macro_pause_for_release"),
        call("&macro_release"),
        call("&macro_param_1to1"),
        ks("&mod_tab_v2_TKZ", "MACRO_PLACEHOLDER"),
        call("&macro_release"),
        call("&macro_param_2to1"),
        ks("&mo", "MACRO_PLACEHOLDER"),
    ),
    params=("code", "layer"),
    wait_ms=0,
    tap_ms=0,
)


MOD_TAB = MacroSpec(
    name="&mod_tab_v2_TKZ",
    description="mod_tab_switcher - TailorKey\n\n",
    bindings=(
        call("&macro_press"),
        call("&macro_param_1to1"),
        kp("MACRO_PLACEHOLDER"),
        call("&macro_tap"),
        kp("TAB"),
        call("&macro_pause_for_release"),
        call("&macro_release"),
        call("&macro_param_1to1"),
        kp("MACRO_PLACEHOLDER"),
    ),
    params=("code",),
    wait_ms=0,
    tap_ms=0,
)


MOD_TAB_V1 = MacroSpec(
    name="&mod_tab_v1_TKZ",
    description="mod_tab_switcher - TailorKey\n\n",
    bindings=(
        call("&macro_press"),
        call("&macro_param_1to1"),
        kp("MACRO_PLACEHOLDER"),
        call("&macro_tap"),
        kp("TAB"),
        call("&macro_pause_for_release"),
        call("&macro_release"),
        call("&macro_param_1to1"),
        kp("MACRO_PLACEHOLDER"),
    ),
    params=("code",),
    wait_ms=0,
    tap_ms=0,
)


MSTR1 = MacroSpec(
    name="&mstr1_v1_TKZ",
    description='macro string1 sample - Magic Layer F1 - Text output sample macro 1 "¡Hola!" - TailorKey',
    bindings=(
        call("&macro_press"),
        kp("RALT"),
        call("&macro_tap"),
        kp("KP_N0"),
        kp("KP_N1"),
        kp("KP_N6"),
        kp("KP_N1"),
        call("&macro_release"),
        kp("RALT"),
        call("&macro_press"),
        kp("LSHFT"),
        call("&macro_tap"),
        kp("H"),
        call("&macro_release"),
        kp("LSHFT"),
        call("&macro_tap"),
        kp("O"),
        kp("L"),
        kp("A"),
        kp("EXCL"),
        kp("SPACE"),
        kp("RET"),
    ),
)


MSTR2 = MacroSpec(
    name="&mstr2_v1_TKZ",
    description='macro string2 sample - Magic Layer F2 - Text output sample macro 2 "grammar check: <paste>" - TailorKey',
    bindings=(
        call("&macro_tap"),
        kp("G"),
        kp("R"),
        kp("A"),
        kp("M"),
        kp("M"),
        kp("A"),
        kp("R"),
        kp("SPACE"),
        kp("C"),
        kp("H"),
        kp("E"),
        kp("C"),
        kp("K"),
        kp("COLON"),
        kp(mod("LC", "V")),
        kp("RET"),
    ),
)


SYMB_DOTDOT = MacroSpec(
    name="&symb_dotdot_v1_TKZ",
    description="Symbol layer dot dot",
    bindings=(
        call("&macro_tap"),
        kp("DOT"),
        kp("DOT"),
    ),
    wait_ms=0,
    tap_ms=0,
)


MACRO_BASE = [
    AS_SHIFTED,
    AS_ASSIGN,
    *CURSOR_MACROS,
    MOD_TAB_CHORD,
    MOD_TAB,
    MSTR1,
    MSTR2,
    SYMB_DOTDOT,
]


MACRO_DEFS = {macro.name: macro for macro in MACRO_BASE}

for macro in CURSOR_MACROS_MAC:
    MACRO_DEFS[macro.name] = macro

MACRO_DEFS[MOD_TAB_V1.name] = MOD_TAB_V1


MOD_CLEAR_SEQUENCE = (
    kp("LSHFT"),
    kp("RSHFT"),
    kp("LALT"),
    kp("RALT"),
    kp("LCTRL"),
    kp("RCTRL"),
    kp("LGUI"),
    kp("RGUI"),
)


def _hold_description(hand: str, finger: str) -> str:
    desc = f"HRM_{hand}_{finger}_hold -> swich layer - TailorKey"
    if hand == "left" and finger == "index":
        desc = "HRM_left_index_hold -> swich layer  - TailorKey"
    return desc


for meta in FINGERS:
    hand = meta.hand
    finger = meta.finger
    hold_name = f"&HRM_{hand}_{finger}_hold_v1B_TKZ"
    tap_name = f"&HRM_{hand}_{finger}_tap_v1B_TKZ"
    MACRO_DEFS[hold_name] = MacroSpec(
        name=hold_name,
        description=_hold_description(hand, finger),
        bindings=(
            call("&macro_press"),
            call("&macro_param_1to1"),
            kp("A"),
            ks("&mo", layer_param(meta.layer)),
            call("&macro_pause_for_release"),
            call("&macro_release"),
            call("&macro_param_1to1"),
            kp("A"),
            ks("&mo", layer_param(meta.layer)),
        ),
        params=("code",),
        wait_ms=0,
        tap_ms=0,
    )
    MACRO_DEFS[tap_name] = MacroSpec(
        name=tap_name,
        description=f"HRM_{hand}_{finger}_tap - incl. QWERTY alpha character - TailorKey",
        bindings=(
            call("&macro_release"),
            *MOD_CLEAR_SEQUENCE,
            call("&macro_tap"),
            kp(meta.tap_key),
            call("&macro_tap"),
            call("&macro_param_1to1"),
            kp("A"),
        ),
        params=("code",),
        wait_ms=0,
        tap_ms=0,
    )


MACRO_ORDER = {
    "windows": [
        "&AS_Shifted_v1_TKZ",
        "&AS_v1_TKZ",
        "&cur_EXTEND_LINE_v1_TKZ",
        "&cur_EXTEND_WORD_v1_TKZ",
        "&cur_SELECT_LINE_v1_TKZ",
        "&cur_SELECT_NONE_v1_TKZ",
        "&cur_SELECT_WORD_v1_TKZ",
        "&mod_tab_chord_v2_TKZ",
        "&mod_tab_v2_TKZ",
        "&mstr1_v1_TKZ",
        "&mstr2_v1_TKZ",
        "&symb_dotdot_v1_TKZ",
    ],
    "mac": [
        "&AS_Shifted_v1_TKZ",
        "&AS_v1_TKZ",
        "&cur_EXTEND_LINE_macos_v1_TKZ",
        "&cur_EXTEND_LINE_v1_TKZ",
        "&cur_EXTEND_WORD_macos_v1_TKZ",
        "&cur_EXTEND_WORD_v1_TKZ",
        "&cur_SELECT_LINE_macos_v1_TKZ",
        "&cur_SELECT_LINE_v1_TKZ",
        "&cur_SELECT_NONE_v1_TKZ",
        "&cur_SELECT_WORD_macos_v1_TKZ",
        "&cur_SELECT_WORD_v1_TKZ",
        "&mod_tab_chord_v2_TKZ",
        "&mod_tab_v2_TKZ",
        "&mstr1_v1_TKZ",
        "&mstr2_v1_TKZ",
        "&symb_dotdot_v1_TKZ",
    ],
    "dual": [
        "&AS_Shifted_v1_TKZ",
        "&AS_v1_TKZ",
        "&cur_EXTEND_LINE_macos_v1_TKZ",
        "&cur_EXTEND_LINE_v1_TKZ",
        "&cur_EXTEND_WORD_macos_v1_TKZ",
        "&cur_EXTEND_WORD_v1_TKZ",
        "&cur_SELECT_LINE_macos_v1_TKZ",
        "&cur_SELECT_LINE_v1_TKZ",
        "&cur_SELECT_NONE_v1_TKZ",
        "&cur_SELECT_WORD_macos_v1_TKZ",
        "&cur_SELECT_WORD_v1_TKZ",
        "&mod_tab_chord_v2_TKZ",
        "&mod_tab_v2_TKZ",
        "&mstr1_v1_TKZ",
        "&mstr2_v1_TKZ",
        "&symb_dotdot_v1_TKZ",
    ],
    "bilateral_windows": [
        "&AS_Shifted_v1_TKZ",
        "&AS_v1_TKZ",
        "&cur_EXTEND_LINE_v1_TKZ",
        "&cur_EXTEND_WORD_v1_TKZ",
        "&cur_SELECT_LINE_v1_TKZ",
        "&cur_SELECT_NONE_v1_TKZ",
        "&cur_SELECT_WORD_v1_TKZ",
        "&HRM_left_index_hold_v1B_TKZ",
        "&HRM_left_index_tap_v1B_TKZ",
        "&HRM_left_middy_hold_v1B_TKZ",
        "&HRM_left_middy_tap_v1B_TKZ",
        "&HRM_left_pinky_hold_v1B_TKZ",
        "&HRM_left_pinky_tap_v1B_TKZ",
        "&HRM_left_ring_hold_v1B_TKZ",
        "&HRM_left_ring_tap_v1B_TKZ",
        "&HRM_right_index_hold_v1B_TKZ",
        "&HRM_right_index_tap_v1B_TKZ",
        "&HRM_right_middy_hold_v1B_TKZ",
        "&HRM_right_middy_tap_v1B_TKZ",
        "&HRM_right_pinky_hold_v1B_TKZ",
        "&HRM_right_pinky_tap_v1B_TKZ",
        "&HRM_right_ring_hold_v1B_TKZ",
        "&HRM_right_ring_tap_v1B_TKZ",
        "&mod_tab_chord_v2_TKZ",
        "&mod_tab_v1_TKZ",
        "&mod_tab_v2_TKZ",
        "&mstr1_v1_TKZ",
        "&mstr2_v1_TKZ",
        "&symb_dotdot_v1_TKZ",
    ],
    "bilateral_mac": [
        "&AS_Shifted_v1_TKZ",
        "&AS_v1_TKZ",
        "&cur_EXTEND_LINE_macos_v1_TKZ",
        "&cur_EXTEND_LINE_v1_TKZ",
        "&cur_EXTEND_WORD_macos_v1_TKZ",
        "&cur_EXTEND_WORD_v1_TKZ",
        "&cur_SELECT_LINE_macos_v1_TKZ",
        "&cur_SELECT_LINE_v1_TKZ",
        "&cur_SELECT_NONE_v1_TKZ",
        "&cur_SELECT_WORD_macos_v1_TKZ",
        "&cur_SELECT_WORD_v1_TKZ",
        "&HRM_left_index_hold_v1B_TKZ",
        "&HRM_left_index_tap_v1B_TKZ",
        "&HRM_left_middy_hold_v1B_TKZ",
        "&HRM_left_middy_tap_v1B_TKZ",
        "&HRM_left_pinky_hold_v1B_TKZ",
        "&HRM_left_pinky_tap_v1B_TKZ",
        "&HRM_left_ring_hold_v1B_TKZ",
        "&HRM_left_ring_tap_v1B_TKZ",
        "&HRM_right_index_hold_v1B_TKZ",
        "&HRM_right_index_tap_v1B_TKZ",
        "&HRM_right_middy_hold_v1B_TKZ",
        "&HRM_right_middy_tap_v1B_TKZ",
        "&HRM_right_pinky_hold_v1B_TKZ",
        "&HRM_right_pinky_tap_v1B_TKZ",
        "&HRM_right_ring_hold_v1B_TKZ",
        "&HRM_right_ring_tap_v1B_TKZ",
        "&mod_tab_chord_v2_TKZ",
        "&mod_tab_v2_TKZ",
        "&mstr1_v1_TKZ",
        "&mstr2_v1_TKZ",
        "&symb_dotdot_v1_TKZ",
    ],
}


MACRO_OVERRIDES: Dict[str, Dict[str, MacroSpec]] = {
    "bilateral_windows": {
        "&mod_tab_chord_v2_TKZ": MacroSpec(
            name="&mod_tab_chord_v2_TKZ",
            description="mod_tab_switcher_chord -  TailorKey",
            bindings=(
                call("&macro_press"),
                call("&macro_param_2to1"),
                ks("&mo", "MACRO_PLACEHOLDER"),
                call("&macro_press"),
                call("&macro_param_1to1"),
                ks("&mod_tab_v1_TKZ", "MACRO_PLACEHOLDER"),
                call("&macro_pause_for_release"),
                call("&macro_release"),
                call("&macro_param_1to1"),
                ks("&mod_tab_v1_TKZ", "MACRO_PLACEHOLDER"),
                call("&macro_release"),
                call("&macro_param_2to1"),
                ks("&mo", "MACRO_PLACEHOLDER"),
            ),
            params=("code", "layer"),
            wait_ms=0,
            tap_ms=0,
        )
    }
}


__all__ = ["MACRO_DEFS", "MACRO_ORDER", "MACRO_OVERRIDES"]
