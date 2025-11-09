# QuantumTouch Guide

QuantumTouch expands on TailorKey concepts with bilateral HRM training layers and bespoke mouse behavior.
Its code lives in `src/glove80/families/quantum_touch` and mirrors the TailorKey structure so new features remain declarative.

## Canonical Layout
- [QuantumTouch80BHRM](https://my.glove80.com/#/layout/user/bdd76424-25f0-4a53-a250-c9fdde247bd6) (accessed 8 Nov 2025)

## Structure
- `specs/` contains macros, hold-taps, combos, and listener definitions tailored for the QuantumTouch training flow.
- `layers/` builds the base layer, HRM, finger-training layers, mouse variants, and the remaining supporting layers needed for the training workflow.
- `layouts.py` composes the ordered layer list, resolves references via `glove80.layouts.common`, and injects metadata from `src/glove80/layouts/quantum_touch/metadata.json`.

## Extending QuantumTouch
1. Update or add spec entries (e.g., combos, macros) under `specs/`.
2. Adjust the appropriate layer factory or add a new module under `layers/` if the layout needs additional behavior.
3. Register any new layer in `layers/__init__.py` so the layout builder can include it.
4. If you need another release variant, add it to `src/glove80/layouts/quantum_touch/metadata.json` and reference the desired output path under `layouts/quantum_touch/releases/`.

## Validation
- `tests/quantum_touch/test_layout.py` ensures the composed layout matches the canonical JSON exactly.
- Add extra tests (e.g., for new finger-training layers) alongside it if you change factory behavior.
- Always run `just regen` so the release artifact stays synchronized with the source code before committing.
