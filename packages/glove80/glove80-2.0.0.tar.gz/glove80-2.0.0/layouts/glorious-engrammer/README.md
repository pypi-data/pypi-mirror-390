# Glorious Engrammer Guide

Glorious Engrammer is Sunaku's multi-layer Glove80 layout with per-key RGB cues, mouse control, and ergonomic finger layers.
The sources in `src/glove80/families/glorious_engrammer` describe the layout declaratively so `just regen` reproduces the released JSON verbatim.

## Canonical Layouts (accessed 8 Nov 2025)
- [Glorious Engrammer v42-rc6 (preview)](https://my.glove80.com/#/layout/user/7cf03288-20db-42e0-9b80-4ace1c2fdbde) (accessed 8 Nov 2025)

## Structure
- `layer_rows.py` mirrors each of the 32 layers as row tuples that feed `rows_to_layer_spec`.
- `layers.py` converts the row data into `LayerSpec` objects and exposes `build_all_layers`.
- `specs.py` defines the `VariantSpec`, Sunaku's custom behavior strings, and the canonical layer order.
- `layouts.py` assembles the final payload, attaches metadata, and writes to `layouts/glorious-engrammer/releases`.

## Updating or Extending
1. Edit the relevant entries in `layer_rows.py` (or add a helper) to change a key's behavior, then re-run `just regen`.
2. Introduce new layers by adding row tuples plus entries in `LAYER_ORDER` inside `specs.py`.
3. Update `metadata.json` with the new UUID, title, and notes before checking in a regenerated release file.
4. Add or update tests under `tests/glorious_engrammer/` so parity checks catch regressions.
