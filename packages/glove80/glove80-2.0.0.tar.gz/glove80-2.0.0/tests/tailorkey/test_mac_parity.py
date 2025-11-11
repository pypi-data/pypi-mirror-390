from glove80 import build_layout


LAYER_DIFFS = {
    "Mouse": {30, 32, 55, 56, 57},
    "Symbol": {30, 32},
    "Cursor": {
        27,
        28,
        30,
        31,
        35,
        37,
        39,
        40,
        46,
        47,
        48,
        49,
        50,
        51,
        52,
        53,
        56,
        57,
        58,
        63,
        64,
        65,
        66,
        67,
        68,
        71,
        72,
        73,
        74,
        75,
        76,
        77,
        79,
    },
}


def _layer(layout: dict, name: str) -> list[dict]:
    idx = layout["layer_names"].index(name)
    return layout["layers"][idx]


def _diffs(left: list[dict], right: list[dict]) -> set[int]:
    return {idx for idx, (lhs, rhs) in enumerate(zip(left, right, strict=False)) if lhs != rhs}


def test_tailorkey_mac_windows_parity() -> None:
    windows = build_layout("tailorkey", "windows")
    mac = build_layout("tailorkey", "mac")

    for layer_name, expected in LAYER_DIFFS.items():
        diff = _diffs(_layer(windows, layer_name), _layer(mac, layer_name))
        assert diff == expected, f"Unexpected diffs for {layer_name}: {sorted(diff)}"
