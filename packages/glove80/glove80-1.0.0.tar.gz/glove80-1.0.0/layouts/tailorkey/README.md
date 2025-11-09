# TailorKey Guide

TailorKey is the zero-code Glove80 layout curated by @moosy.
The code in `src/glove80/families/tailorkey` captures the entire layout in declarative specs so every variant (Windows, macOS, Dual, Bilateral) is reproducible.

## Canonical Layouts
- [TailorKey v4.2h](https://my.glove80.com/#/layout/user/12312d23-b371-445a-9183-83552767bd76) (accessed 8 Nov 2025)
- [TailorKey v4.2h - macOS](https://my.glove80.com/#/layout/user/eee91968-ac8e-4d6f-95a3-4a5e2f3b4b44) (accessed 8 Nov 2025)
- [TailorKey v4.2h - Dual OS version](https://my.glove80.com/#/layout/user/179300bf-aec6-456c-84d2-5c33d5be91b0) (accessed 8 Nov 2025)
- [TailorKey v4.2h Bilateral](https://my.glove80.com/#/layout/user/85f92852-413b-4931-ac7d-cf42e6b129eb) (accessed 8 Nov 2025)
- [TailorKey v4.2h - macOS Bilateral](https://my.glove80.com/#/layout/user/906466c2-8029-4831-9571-2bf250ca4505) (accessed 8 Nov 2025)

## Structure
- `specs/common.py` lists the canonical layer order and shared layout metadata fields.
- `specs/macros.py`, `specs/hold_taps.py`, `specs/combos.py`, and `specs/input_listeners.py` use the spec primitives to declare every behavioral building block.
- `layers/` contains focused factories for each ergonomic feature (HRM, cursor, mouse, typing, etc.).
- `layouts.py` stitches the generated layers, macros, combos, and metadata together using the helpers in `glove80.layouts.common`.

## Adding or Modifying Layers
1. Update/extend the appropriate spec file to describe the new behavior (for example, a new macro in `specs/macros.py`).
2. If a new physical layer is needed, add a factory in `layers/` and register it in `layers/__init__.py`.
3. Adjust `specs/common.py` (layer order) or the relevant data structure so the new layer is referenced from the layout.
4. Run `just regen` and `just ci` to ensure the JSON diff matches the expected change and all coverage remains green.

## New Release Variants
1. Add an entry to `src/glove80/layouts/tailorkey/metadata.json` with the UUID, parent UUID, notes, and destination under `layouts/tailorkey/releases/`.
2. If the variant needs special behavior, add a new variant key in the declarative spec modules (e.g., `MACRO_ORDER["variant_name"]`).
3. Regenerate and inspect the new file under `layouts/tailorkey/releases`.

## Testing Expectations
- For incremental changes, add or update a targeted test under `tests/tailorkey/` (mouse, HRM, etc.) to lock in the new expectations.
- The layout parity tests ensure the full JSON matches the generated structure, so intentional diffs must be checked in alongside code changes.
