"""Input listener definitions for TailorKey variants (Pydantic models)."""

from __future__ import annotations

from glove80.families.tailorkey.alpha_layouts import TAILORKEY_VARIANTS, base_variant_for
from glove80.layouts.listeners import make_mouse_listeners


def _listener_tuple(
    slow_xy: str,
    slow_scroll: str,
    warp_xy: str,
    warp_scroll: str,
) -> list:
    return list(
        make_mouse_listeners(
            slow_xy_description=slow_xy,
            slow_scroll_description=slow_scroll,
            warp_xy_description=warp_xy,
            warp_scroll_description=warp_scroll,
        )
    )


INPUT_LISTENER_DATA = {
    "windows": _listener_tuple("LAYER_MouseSlow", "LAYER_MouseSlow", "LAYER_MouseFast", "LAYER_MouseWarp"),
    "mac": _listener_tuple("LAYER_MouseSlow\n", "LAYER_MouseSlow\n", "LAYER_MouseWarp", "LAYER_MouseWarp"),
    "dual": _listener_tuple("LAYER_MouseSlow", "LAYER_MouseSlow\n", "LAYER_MouseWarp", "LAYER_MouseWarp"),
    "bilateral_windows": _listener_tuple("LAYER_MouseSlow", "LAYER_MouseSlow", "LAYER_MouseWarp", "LAYER_MouseWarp"),
    "bilateral_mac": _listener_tuple("LAYER_MouseSlow\n", "LAYER_MouseSlow\n", "LAYER_MouseWarp", "LAYER_MouseWarp"),
}

for _variant in TAILORKEY_VARIANTS:
    if _variant not in INPUT_LISTENER_DATA:
        template = base_variant_for(_variant)
        INPUT_LISTENER_DATA[_variant] = list(INPUT_LISTENER_DATA[template])


__all__ = ["INPUT_LISTENER_DATA"]
