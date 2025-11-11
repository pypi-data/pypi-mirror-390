"""Alpha layout helpers for TailorKey variants."""

from __future__ import annotations

from typing import TYPE_CHECKING

from glove80.families.default.layer_data import (
    BASE_COLEMAK_DH_ROWS,
    BASE_COLEMAK_ROWS,
    BASE_DVORAK_ROWS,
    BASE_WINDOWS_ROWS,
)

if TYPE_CHECKING:
    from glove80.base import Layer

ALPHA_ROW_SETS: dict[str, list[list[str]]] = {
    "qwerty": [list(row) for row in BASE_WINDOWS_ROWS],
    "colemak": [list(row) for row in BASE_COLEMAK_ROWS],
    "colemak_dh": [list(row) for row in BASE_COLEMAK_DH_ROWS],
    "dvorak": [list(row) for row in BASE_DVORAK_ROWS],
}


def _flatten(rows: list[list[str]]) -> list[str]:
    return [value for row in rows for value in row]


FLAT_ALPHA_MAP: dict[str, list[str]] = {name: _flatten(rows) for name, rows in ALPHA_ROW_SETS.items()}

BASE_VARIANTS = ("windows", "mac", "dual", "bilateral_windows", "bilateral_mac")
ALTERNATE_LAYOUTS = tuple(name for name in ALPHA_ROW_SETS if name != "qwerty")


def _variant_name_for_layout(layout: str, base_variant: str) -> str:
    if layout == "qwerty":
        return base_variant
    if base_variant == "windows":
        return layout
    return f"{layout}_{base_variant}"


VARIANT_ALPHA_LAYOUT: dict[str, str] = dict.fromkeys(BASE_VARIANTS, "qwerty")
VARIANT_BASE_VARIANT: dict[str, str] = {variant: variant for variant in BASE_VARIANTS}

for layout in ALTERNATE_LAYOUTS:
    variant_name = _variant_name_for_layout(layout, "windows")
    VARIANT_ALPHA_LAYOUT[variant_name] = layout
    VARIANT_BASE_VARIANT[variant_name] = "windows"
    for base_variant in BASE_VARIANTS[1:]:
        derived = _variant_name_for_layout(layout, base_variant)
        VARIANT_ALPHA_LAYOUT[derived] = layout
        VARIANT_BASE_VARIANT[derived] = base_variant

TAILORKEY_VARIANTS: list[str] = list(VARIANT_ALPHA_LAYOUT)


def layout_for_variant(variant: str) -> str:
    try:
        return VARIANT_ALPHA_LAYOUT[variant]
    except KeyError as exc:  # pragma: no cover
        msg = f"Unknown TailorKey variant '{variant}'"
        raise KeyError(msg) from exc


def needs_alpha_remap(variant: str) -> bool:
    """Return True when the variant swaps the alpha layout away from QWERTY."""
    return layout_for_variant(variant) != "qwerty"


def base_variant_for(variant: str) -> str:
    try:
        return VARIANT_BASE_VARIANT[variant]
    except KeyError as exc:  # pragma: no cover
        msg = f"Unknown TailorKey variant '{variant}'"
        raise KeyError(msg) from exc


def variant_for_layout_and_base(layout: str, base_variant: str) -> str:
    """Return the variant name representing the layout/base combination."""
    name = _variant_name_for_layout(layout, base_variant)
    if name not in VARIANT_ALPHA_LAYOUT:  # pragma: no cover
        msg = f"Unsupported layout/base combination: {layout}/{base_variant}"
        raise KeyError(msg)
    return name


def variant_alias(variant: str, base_variant: str) -> str:
    """Return the variant name for the same layout but a different base capability."""
    layout = layout_for_variant(variant)
    return variant_for_layout_and_base(layout, base_variant)


def remap_layer_keys(layer: Layer, variant: str) -> None:
    layout = layout_for_variant(variant)
    if layout == "qwerty":
        return
    tokens = FLAT_ALPHA_MAP[layout]
    for index, entry in enumerate(layer):
        target = tokens[index]
        value = entry.get("value")
        if value == "&kp" and entry.get("params"):
            primary = entry["params"][0]
            # Skip nested macros such as LS(KP)
            if isinstance(primary, dict) and not primary.get("params"):
                primary["value"] = target
        elif value and value.startswith("&HRM_") and entry.get("params"):
            entry["params"][-1]["value"] = target
        elif value == "&AS_v1_TKZ" and entry.get("params"):
            entry["params"][0]["value"] = target
