from __future__ import annotations

from typing import TYPE_CHECKING

from glove80.layouts.layers import _transparent_layer, rows_to_layer_spec

if TYPE_CHECKING:
    from glove80.base import LayerSpec

# --- Base layers ---------------------------------------------------------


FUNC_ROW = ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10")
NUMBER_ROW = ("EQUAL", "N1", "N2", "N3", "N4", "N5", "N6", "N7", "N8", "N9")
BOTTOM_ROW_STANDARD = ("DEL", "LALT", "RALT", "RET", "SPACE", "UP", "DOWN", "LBKT", "RBKT", "PG_DN")

BASE_WINDOWS_ROWS = [
    FUNC_ROW,
    NUMBER_ROW,
    ("N0", "MINUS", "TAB", "Q", "W", "E", "R", "T", "Y", "U"),
    ("I", "O", "P", "BSLH", "ESC", "A", "S", "D", "F", "G"),
    ("H", "J", "K", "L", "SEMI", "SQT", "GRAVE", "Z", "X", "C"),
    ("V", "B", "LSHFT", "LCTRL", "&lower", "LGUI", "RCTRL", "RSHFT", "N", "M"),
    ("COMMA", "DOT", "FSLH", "PG_UP", "&magic", "HOME", "END", "LEFT", "RIGHT", "BSPC"),
    BOTTOM_ROW_STANDARD,
]

BASE_MAC_ROWS = [
    FUNC_ROW,
    NUMBER_ROW,
    ("N0", "MINUS", "TAB", "Q", "W", "E", "R", "T", "Y", "U"),
    ("I", "O", "P", "BSLH", "ESC", "A", "S", "D", "F", "G"),
    ("H", "J", "K", "L", "SEMI", "SQT", "GRAVE", "Z", "X", "C"),
    ("V", "B", "LSHFT", "LGUI", "&lower", "LCTRL", "RGUI", "RSHFT", "N", "M"),
    ("COMMA", "DOT", "FSLH", "PG_UP", "&magic", "HOME", "END", "LEFT", "RIGHT", "BSPC"),
    BOTTOM_ROW_STANDARD,
]

BASE_COLEMAK_ROWS = [
    FUNC_ROW,
    NUMBER_ROW,
    ("N0", "MINUS", "TAB", "Q", "W", "F", "P", "G", "J", "L"),
    ("U", "Y", "SEMI", "BSLH", "ESC", "A", "R", "S", "T", "D"),
    ("H", "N", "E", "I", "O", "SQT", "GRAVE", "Z", "X", "C"),
    ("V", "B", "LSHFT", "LCTRL", "&lower", "LGUI", "RCTRL", "RSHFT", "K", "M"),
    ("COMMA", "DOT", "FSLH", "PG_UP", "&magic", "HOME", "END", "LEFT", "RIGHT", "BSPC"),
    BOTTOM_ROW_STANDARD,
]

BASE_COLEMAK_DH_ROWS = [
    FUNC_ROW,
    NUMBER_ROW,
    ("N0", "MINUS", "TAB", "Q", "W", "F", "P", "B", "J", "L"),
    ("U", "Y", "SEMI", "BSLH", "ESC", "A", "R", "S", "T", "G"),
    ("M", "N", "E", "I", "O", "SQT", "GRAVE", "Z", "X", "C"),
    ("D", "V", "LSHFT", "LCTRL", "&lower", "LGUI", "RCTRL", "RSHFT", "K", "H"),
    ("COMMA", "DOT", "FSLH", "PG_UP", "&magic", "HOME", "END", "LEFT", "RIGHT", "BSPC"),
    BOTTOM_ROW_STANDARD,
]

BASE_DVORAK_ROWS = [
    FUNC_ROW,
    NUMBER_ROW,
    ("N0", "MINUS", "TAB", "SQT", "COMMA", "DOT", "P", "Y", "F", "G"),
    ("C", "R", "L", "SLASH", "ESC", "A", "O", "E", "U", "I"),
    ("D", "H", "T", "N", "S", "BSLH", "GRAVE", "SEMI", "Q", "J"),
    ("K", "X", "LSHFT", "LCTRL", "&lower", "LGUI", "RCTRL", "RSHFT", "B", "M"),
    ("W", "V", "Z", "PG_UP", "&magic", "HOME", "END", "LEFT", "RIGHT", "BSPC"),
    BOTTOM_ROW_STANDARD,
]

BASE_WORKMAN_ROWS = [
    FUNC_ROW,
    NUMBER_ROW,
    ("N0", "MINUS", "TAB", "Q", "D", "R", "W", "B", "J", "F"),
    ("U", "P", "SEMI", "BSLH", "ESC", "A", "S", "H", "T", "G"),
    ("Y", "N", "E", "O", "I", "SQT", "GRAVE", "Z", "X", "M"),
    ("C", "V", "LSHFT", "LCTRL", "&lower", "LGUI", "RCTRL", "RSHFT", "K", "L"),
    ("COMMA", "DOT", "FSLH", "PG_UP", "&magic", "HOME", "END", "LEFT", "RIGHT", "BSPC"),
    BOTTOM_ROW_STANDARD,
]

BASE_KINESIS_ROWS = [
    ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10"),
    ("EQUAL", "N1", "N2", "N3", "N4", "N5", "N6", "N7", "N8", "N9"),
    ("N0", "MINUS", "TAB", "Q", "W", "E", "R", "T", "Y", "U"),
    ("I", "O", "P", "BSLH", "ESC", "A", "S", "D", "F", "G"),
    ("H", "J", "K", "L", "SEMI", "SQT", "LSHFT", "Z", "X", "C"),
    ("V", "B", "LCTRL", "LALT", "HOME", "PG_UP", "LGUI", "RCTRL", "N", "M"),
    ("COMMA", "DOT", "FSLH", "RSHFT", "&magic", "GRAVE", "CAPSLOCK", "LEFT", "RIGHT", "BSPC"),
    ("DEL", "END", "PG_DN", "RET", "SPACE", "UP", "DOWN", "LBKT", "RBKT", "&lower"),
]

BASE_MOUSE_ROWS = [
    ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10"),
    ("EQUAL", "N1", "N2", "N3", "N4", "N5", "N6", "N7", "N8", "N9"),
    ("N0", "MINUS", "TAB", "Q", "W", "E", "R", "T", "Y", "U"),
    ("I", "O", "P", "BSLH", "ESC", "A", "S", "D", "F", "G"),
    ("H", "J", "K", "L", "SEMI", "SQT", "GRAVE", "Z", "X", "C"),
    ("V", "B", "LSHFT", "LCTRL", ("&to", 1), "LGUI", "RCTRL", "RSHFT", "N", "M"),
    ("COMMA", "DOT", "FSLH", "PG_UP", "&magic", "HOME", "END", "LEFT", "RIGHT", "BSPC"),
    ("DEL", "LALT", "RALT", ("&lt", 2, "RET"), "SPACE", "UP", "DOWN", "LBKT", "RBKT", "PG_DN"),
]

BASE_WINDOWS = rows_to_layer_spec(BASE_WINDOWS_ROWS)
BASE_MAC = rows_to_layer_spec(BASE_MAC_ROWS)
BASE_COLEMAK = rows_to_layer_spec(BASE_COLEMAK_ROWS)
BASE_COLEMAK_DH = rows_to_layer_spec(BASE_COLEMAK_DH_ROWS)
BASE_DVORAK = rows_to_layer_spec(BASE_DVORAK_ROWS)
BASE_WORKMAN = rows_to_layer_spec(BASE_WORKMAN_ROWS)
BASE_KINESIS = rows_to_layer_spec(BASE_KINESIS_ROWS)
BASE_MOUSE = rows_to_layer_spec(BASE_MOUSE_ROWS)

# --- Lower layers --------------------------------------------------------

LOWER_STANDARD_ROWS = [
    ("C_BRI_DN", "C_BRI_UP", "C_PREV", "C_NEXT", "C_PP", "C_MUTE", "C_VOL_DN", "C_VOL_UP", "&none", "PAUSE_BREAK"),
    ("&trans", "&none", "&none", "&none", "&none", "HOME", "LEFT_PARENTHESIS", "KP_NUM", "KP_EQUAL", "KP_SLASH"),
    (
        "KP_MULTIPLY",
        "PRINTSCREEN",
        "&trans",
        "&none",
        "&none",
        "UP_ARROW",
        "&none",
        "END",
        "RIGHT_PARENTHESIS",
        "KP_N7",
    ),
    ("KP_N8", "KP_N9", "KP_MINUS", "SCROLLLOCK", "&trans", "&none", "LEFT_ARROW", "DOWN_ARROW", "RIGHT_ARROW", "PG_UP"),
    ("PERCENT", "KP_N4", "KP_N5", "KP_N6", "KP_PLUS", "&none", "&trans", "K_APP", "&none", "F11"),
    ("F12", "PG_DN", "&trans", "&trans", ("&to", 0), "&trans", "&trans", "&trans", "COMMA", "KP_N1"),
    ("KP_N2", "KP_N3", "KP_ENTER", "&trans", "&magic", "CAPS", "INS", "F11", "F12", "&trans"),
    ("&trans", "&trans", "&trans", "&trans", "&trans", "KP_N0", "KP_N0", "KP_DOT", "KP_ENTER", "&trans"),
]

LOWER_KINESIS_ROWS = [
    ("C_BRI_DN", "C_BRI_UP", "C_PREV", "C_NEXT", "C_PP", "C_MUTE", "C_VOL_DN", "C_VOL_UP", "&none", "PAUSE_BREAK"),
    ("&trans", "&none", "&none", "&none", "&none", "HOME", "LEFT_PARENTHESIS", "KP_NUM", "KP_EQUAL", "KP_SLASH"),
    (
        "KP_MULTIPLY",
        "PRINTSCREEN",
        "&trans",
        "&none",
        "&none",
        "UP_ARROW",
        "&none",
        "END",
        "RIGHT_PARENTHESIS",
        "KP_N7",
    ),
    ("KP_N8", "KP_N9", "KP_MINUS", "SCROLLLOCK", "&trans", "&none", "LEFT_ARROW", "DOWN_ARROW", "RIGHT_ARROW", "PG_UP"),
    ("PERCENT", "KP_N4", "KP_N5", "KP_N6", "KP_PLUS", "&none", "&trans", "K_APP", "&none", "F11"),
    ("F12", "PG_DN", "&trans", "&trans", "&trans", "&trans", "&trans", "&trans", "COMMA", "KP_N1"),
    ("KP_N2", "KP_N3", "KP_ENTER", "&trans", "&magic", "CAPS", "INS", "F11", "F12", "&trans"),
    ("&trans", "&trans", "&trans", "&trans", "&trans", "KP_N0", "KP_N0", "KP_DOT", "KP_ENTER", ("&to", 0)),
]

LOWER_STANDARD = rows_to_layer_spec(LOWER_STANDARD_ROWS)
LOWER_KINESIS = rows_to_layer_spec(LOWER_KINESIS_ROWS)

# --- Magic / Factory -----------------------------------------------------

MAGIC_FACTORY_ROWS = [
    (("&bt", "BT_CLR"), "&none", "&none", "&none", "&none", "&none", "&none", "&none", "&none", ("&bt", "BT_CLR_ALL")),
    ("&none", "&none", "&none", "&none", "&none", "&none", "&none", "&none", "&none", "&none"),
    (
        "&none",
        "&none",
        "&none",
        ("&rgb_ug", "RGB_SPI"),
        ("&rgb_ug", "RGB_SAI"),
        ("&rgb_ug", "RGB_HUI"),
        ("&rgb_ug", "RGB_BRI"),
        ("&rgb_ug", "RGB_TOG"),
        "&none",
        "&none",
    ),
    (
        "&none",
        "&none",
        "&none",
        "&none",
        "&bootloader",
        ("&rgb_ug", "RGB_SPD"),
        ("&rgb_ug", "RGB_SAD"),
        ("&rgb_ug", "RGB_HUD"),
        ("&rgb_ug", "RGB_BRD"),
        ("&rgb_ug", "RGB_EFF"),
    ),
    ("&none", "&none", "&none", "&none", "&none", "&bootloader", "&reset", "&none", "&none", "&none"),
    ("&none", "&none", "&bt_2", "&bt_3", "&none", "&none", "&none", "&none", "&none", "&none"),
    ("&none", "&none", "&none", "&reset", "&none", "&none", "&none", "&none", "&none", "&bt_0"),
    ("&bt_1", ("&out", "OUT_USB"), "&none", "&none", "&none", "&none", "&none", "&none", "&none", ("&to", 3)),
]

MAGIC_STANDARD_ROWS = [
    (("&bt", "BT_CLR"), "&none", "&none", "&none", "&none", "&none", "&none", "&none", "&none", ("&bt", "BT_CLR_ALL")),
    ("&none", "&none", "&none", "&none", "&none", "&none", "&none", "&none", "&none", "&none"),
    (
        "&none",
        "&none",
        "&none",
        ("&rgb_ug", "RGB_SPI"),
        ("&rgb_ug", "RGB_SAI"),
        ("&rgb_ug", "RGB_HUI"),
        ("&rgb_ug", "RGB_BRI"),
        ("&rgb_ug", "RGB_TOG"),
        "&none",
        "&none",
    ),
    (
        "&none",
        "&none",
        "&none",
        "&none",
        "&bootloader",
        ("&rgb_ug", "RGB_SPD"),
        ("&rgb_ug", "RGB_SAD"),
        ("&rgb_ug", "RGB_HUD"),
        ("&rgb_ug", "RGB_BRD"),
        ("&rgb_ug", "RGB_EFF"),
    ),
    ("&none", "&none", "&none", "&none", "&none", "&bootloader", "&reset", "&none", "&none", "&none"),
    ("&none", "&none", "&bt_2", "&bt_3", "&none", "&none", "&none", "&none", "&none", "&none"),
    ("&none", "&none", "&none", "&reset", "&none", "&none", "&none", "&none", "&none", "&bt_0"),
    ("&bt_1", ("&out", "OUT_USB"), "&none", "&none", "&none", "&none", "&none", "&none", "&none", "&none"),
]

FACTORY_LAYER_ROWS = [
    (
        "NUMBER_0",
        "NUMBER_6",
        "NUMBER_2",
        "NUMBER_8",
        "NUMBER_4",
        "NUMBER_4",
        "NUMBER_8",
        "NUMBER_2",
        "NUMBER_6",
        "NUMBER_0",
    ),
    (
        "NUMBER_1",
        "NUMBER_7",
        "NUMBER_3",
        "NUMBER_9",
        "NUMBER_5",
        "NUMBER_0",
        "NUMBER_0",
        "NUMBER_5",
        "NUMBER_9",
        "NUMBER_3",
    ),
    (
        "NUMBER_7",
        "NUMBER_1",
        "NUMBER_2",
        "NUMBER_8",
        "NUMBER_4",
        "NUMBER_0",
        "NUMBER_6",
        "NUMBER_1",
        "NUMBER_1",
        "NUMBER_6",
    ),
    (
        "NUMBER_0",
        "NUMBER_4",
        "NUMBER_8",
        "NUMBER_2",
        "NUMBER_3",
        "NUMBER_9",
        "NUMBER_5",
        "NUMBER_1",
        "NUMBER_7",
        "NUMBER_2",
    ),
    (
        "NUMBER_2",
        "NUMBER_7",
        "NUMBER_1",
        "NUMBER_5",
        "NUMBER_9",
        "NUMBER_3",
        "NUMBER_4",
        "NUMBER_0",
        "NUMBER_6",
        "NUMBER_2",
    ),
    (
        "NUMBER_8",
        "NUMBER_3",
        "NUMBER_4",
        "NUMBER_5",
        "NUMBER_6",
        "NUMBER_6",
        "NUMBER_5",
        "NUMBER_4",
        "NUMBER_3",
        "NUMBER_8",
    ),
    (
        "NUMBER_2",
        "NUMBER_6",
        "NUMBER_0",
        "NUMBER_4",
        "NUMBER_5",
        "NUMBER_1",
        "NUMBER_7",
        "NUMBER_3",
        "NUMBER_9",
        "NUMBER_7",
    ),
    (
        "NUMBER_8",
        "NUMBER_9",
        "NUMBER_9",
        "NUMBER_8",
        "NUMBER_7",
        "NUMBER_9",
        "NUMBER_3",
        "NUMBER_7",
        "NUMBER_1",
        "NUMBER_5",
    ),
]

MAGIC_FACTORY = rows_to_layer_spec(MAGIC_FACTORY_ROWS)
MAGIC_STANDARD = rows_to_layer_spec(MAGIC_STANDARD_ROWS)
FACTORY_LAYER = rows_to_layer_spec(FACTORY_LAYER_ROWS)

# --- Mouse layers --------------------------------------------------------

MOUSE_LAYER_ROWS = [
    ("&trans",) * 10,
    ("&trans",) * 10,
    (
        "&trans",
        "&trans",
        "&trans",
        "&trans",
        ("&msc", "SCRL_LEFT"),
        ("&mmv", "MOVE_UP"),
        ("&msc", "SCRL_RIGHT"),
        "&trans",
        "&trans",
        ("&msc", "SCRL_LEFT"),
    ),
    (
        ("&msc", "SCRL_UP"),
        ("&msc", "SCRL_DOWN"),
        ("&msc", "SCRL_RIGHT"),
        "&trans",
        "&trans",
        ("&msc", "SCRL_UP"),
        ("&mmv", "MOVE_LEFT"),
        ("&mmv", "MOVE_DOWN"),
        ("&mmv", "MOVE_RIGHT"),
        "&trans",
    ),
    (
        "&trans",
        ("&mo", "5"),
        ("&mo", "4"),
        ("&mo", 3),
        "&trans",
        "&trans",
        "&trans",
        ("&msc", "SCRL_DOWN"),
        ("&mo", 3),
        ("&mo", "4"),
    ),
    (
        ("&mo", "5"),
        "&trans",
        ("&mkp", "MCLK"),
        "&trans",
        ("&mkp", "MB5"),
        "&trans",
        "&trans",
        "&trans",
        "&trans",
        ("&mmv", "MOVE_LEFT"),
    ),
    (
        ("&mmv", "MOVE_UP"),
        ("&mmv", "MOVE_DOWN"),
        ("&mmv", "MOVE_RIGHT"),
        "&trans",
        "&trans",
        "&trans",
        "&trans",
        "&trans",
        "&trans",
        ("&mkp", "LCLK"),
    ),
    (
        ("&mkp", "RCLK"),
        ("&mkp", "MB4"),
        "&trans",
        "&trans",
        "&trans",
        ("&mkp", "LCLK"),
        ("&mkp", "RCLK"),
        ("&mkp", "MCLK"),
        ("&mkp", "MB4"),
        ("&mkp", "MB5"),
    ),
]

MOUSE_LAYER = rows_to_layer_spec(MOUSE_LAYER_ROWS)
TRANSPARENT_MOUSE_LAYER = _transparent_layer()

# --- Public mappings -----------------------------------------------------

BASE_LAYERS: dict[str, LayerSpec] = {
    "factory_default": BASE_WINDOWS,
    "factory_default_macos": BASE_MAC,
    "colemak": BASE_COLEMAK,
    "colemak_dh": BASE_COLEMAK_DH,
    "dvorak": BASE_DVORAK,
    "workman": BASE_WORKMAN,
    "kinesis": BASE_KINESIS,
    "mouse_emulation": BASE_MOUSE,
}

LOWER_LAYERS: dict[str, LayerSpec] = {
    "factory_default": LOWER_STANDARD,
    "factory_default_macos": LOWER_STANDARD,
    "colemak": LOWER_STANDARD,
    "colemak_dh": LOWER_STANDARD,
    "dvorak": LOWER_STANDARD,
    "workman": LOWER_STANDARD,
    "mouse_emulation": LOWER_STANDARD,
    "kinesis": LOWER_KINESIS,
}

MAGIC_LAYERS: dict[str, LayerSpec] = {
    "factory_default": MAGIC_FACTORY,
    "factory_default_macos": MAGIC_FACTORY,
    "colemak": MAGIC_STANDARD,
    "colemak_dh": MAGIC_STANDARD,
    "dvorak": MAGIC_STANDARD,
    "workman": MAGIC_STANDARD,
    "kinesis": MAGIC_STANDARD,
    "mouse_emulation": MAGIC_STANDARD,
}

FACTORY_LAYERS: dict[str, LayerSpec] = {
    "factory_default": FACTORY_LAYER,
    "factory_default_macos": FACTORY_LAYER,
}

MOUSE_EXTRAS: dict[str, dict[str, LayerSpec]] = {
    "mouse_emulation": {
        "Mouse": MOUSE_LAYER,
        "MouseSlow": TRANSPARENT_MOUSE_LAYER,
        "MouseFast": TRANSPARENT_MOUSE_LAYER,
        "MouseWarp": TRANSPARENT_MOUSE_LAYER,
    },
}

__all__ = [
    "BASE_LAYERS",
    "FACTORY_LAYERS",
    "LOWER_LAYERS",
    "MAGIC_LAYERS",
    "MOUSE_EXTRAS",
]
