"""Common metadata for QuantumTouch layouts."""

from glove80.layouts.common import build_common_fields

CUSTOM_BEHAVIORS = """// "Meh" key to define custom commands in e.g., VSCode
// NOTE: Using right-side keys because of Keyd remaps in Linux
#define MEH_KEY RA(RC(RIGHT_SHIFT))

behaviors {
    // Shift + Backspace for Delete
    bspc_del: backspace_delete {
        compatible = "zmk,behavior-mod-morph";
        #binding-cells = <0>;
        bindings = <&kp BACKSPACE>, <&kp DELETE>;
        mods = <(MOD_LSFT|MOD_RSFT)>;
        keep-mods = <0>;
    };

    // Double tap to toggle caps word
    td_caps_lshift: tap_dance_caps_lshift {
        compatible = "zmk,behavior-tap-dance";
        #binding-cells = <0>;
        tapping-term-ms = <200>;
        bindings = <&kp LSHIFT>, <&caps_word>;
    };
    td_caps_rshift: tap_dance_caps_rshift {
        compatible = "zmk,behavior-tap-dance";
        #binding-cells = <0>;
        tapping-term-ms = <200>;
        bindings = <&kp RSHIFT>, <&caps_word>;
    };
    // (Sticky) Double tap to toggle caps word
    td_caps_lshift_sk: tap_dance_caps_lshift_sk {
        compatible = "zmk,behavior-tap-dance";
        #binding-cells = <0>;
        tapping-term-ms = <200>;
        bindings = <&sk LSHIFT>, <&caps_word>;
    };
    td_caps_rshift_sk: tap_dance_caps_rshift_sk {
        compatible = "zmk,behavior-tap-dance";
        #binding-cells = <0>;
        tapping-term-ms = <200>;
        bindings = <&sk RSHIFT>, <&caps_word>;
    };

    // Double tap Command for Enter
    td_lgui_enter: td_lgui_enter {
        compatible = "zmk,behavior-tap-dance";
        #binding-cells = <0>;
        tapping-term-ms = <200>;
        bindings = <&kp LGUI>, <&kp ENTER>;
    };
    // (Sticky) Double tap Command for Enter
    td_lgui_enter_sk: td_lgui_enter_sk {
        compatible = "zmk,behavior-tap-dance";
        #binding-cells = <0>;
        tapping-term-ms = <200>;
        bindings = <&sk LGUI>, <&kp ENTER>;
    };

    behavior_caps_word {
        continue-list = <
            UNDERSCORE
            BACKSPACE DELETE
            N1 N2 N3 N4 N5 N6 N7 N8 N9 N0
            LSHFT RSHFT
        >;
        mods = <(MOD_LSFT | MOD_RSFT)>;
    };

    // Mac-style word navigation with Alt (Option)
    alt_left_word: alt_left_word {
        compatible = "zmk,behavior-mod-morph";
        #binding-cells = <0>;
        bindings = <&kp LC(LEFT)>, <&kp LEFT>;
        mods = <(MOD_LSFT|MOD_LCTL)>;
        keep-mods = <(MOD_LSFT|MOD_LCTL)>;
    };

    alt_right_word: alt_right_word {
        compatible = "zmk,behavior-mod-morph";
        #binding-cells = <0>;
        bindings = <&kp LC(RIGHT)>, <&kp RIGHT>;
        mods = <(MOD_LSFT|MOD_LCTL)>;
        keep-mods = <(MOD_LSFT|MOD_LCTL)>;
    };

    // Mac-style Shift + Backspace for Delete
    alt_bspc_del_morph: alt_bspc_del_morph {
        compatible = "zmk,behavior-mod-morph";
        #binding-cells = <0>;
        bindings = <&kp LC(BSPC)>, <&kp LC(DEL)>;
        mods = <(MOD_LSFT|MOD_RSFT)>;
    };

    cmd_bspc_del_morph: cmd_bspc_del_morph {
        compatible = "zmk,behavior-mod-morph";
        #binding-cells = <0>;
        bindings = <&cmd_backspace>, <&cmd_delete>;
        mods = <(MOD_LSFT|MOD_RSFT)>;
    };

};

macros {

    // Delete line left (Cmd+Backspace)
    cmd_backspace: cmd_backspace {
        label = "&CMD_BACKSPACE";
        compatible = "zmk,behavior-macro";
        #binding-cells = <0>;
        bindings = <&macro_press &kp LSHFT>, <&macro_tap &kp HOME>, <&macro_release &kp LSHFT>, <&macro_tap &kp BSPC>;
    };

    // Delete line right (Cmd+Delete)
    cmd_delete: cmd_delete {
        label = "&CMD_DELETE";
        compatible = "zmk,behavior-macro";
        #binding-cells = <0>;
        bindings = <&macro_press &kp LSHFT>, <&macro_tap &kp END>, <&macro_release &kp LSHFT>, <&macro_tap &kp DEL>;
    };
};"""

COMMON_FIELDS = build_common_fields(
    creator="basnijholt",
    custom_defined_behaviors=CUSTOM_BEHAVIORS.rstrip(),
    custom_devicetree='&mt {\n    flavor = "tap-preferred";\n    tapping-term-ms = <220>;\n};',
    config_parameters=[
        {"paramName": "BLE_BAS", "value": "y"},
        {"paramName": "HID_POINTING", "value": "y"},
        {"paramName": "EXPERIMENTAL_RGB_UNDERGLOW_AUTO_OFF_USB", "value": "y"},
    ],
)

LAYER_NAMES = [
    "Base",
    "HRM",
    "Original",
    "Lower",
    "Mouse",
    "MouseSlow",
    "MouseFast",
    "MouseWarp",
    "Magic",
    "LeftIndex",
    "LeftMiddle",
    "LeftRing",
    "LeftPinky",
    "RightIndex",
    "RightMiddle",
    "RightRing",
    "RightPinky",
]

__all__ = ["COMMON_FIELDS", "LAYER_NAMES"]
