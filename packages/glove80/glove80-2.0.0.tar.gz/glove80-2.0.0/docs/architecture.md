# Architecture

This project keeps every part of the Glove80 layout toolchain in version control so the published JSON artifacts can be recreated exactly from code.

## Source of Truth
- **Specs (`src/glove80/families/*/specs/`)** define macros, hold-taps, combos, input listeners, and per-layer overrides using typed dataclasses from `glove80.specs.primitives`.
- **Layer factories (`src/glove80/families/*/layers/`)** build sparse `LayerSpec` objects into the 80-key arrays expected by the Glove80 firmware.
- TailorKey factories mix and match reusable helpers (mouse, cursor, HRM, etc.), while QuantumTouch layers reuse the same primitives to build finger variants.
- Glorious Engrammer stores Sunaku's 32 layers as explicit row tuples that feed the same `rows_to_layer_spec` helper as the other families.
- **Metadata (`src/glove80/families/<family>/metadata.json`)** stores the immutable release information checked in by the original layout authors (UUIDs, parent UUIDs, titles, tags, notes, and the relative output path). Packaging the metadata keeps CLI invocations and library imports perfectly aligned.

## Generation Flow
1. Discovery derives from a single source of truth: `glove80.metadata.layout_metadata_packages()`.
   Built-in families live in `glove80.families.*`, and additional packages can
   register themselves via the `glove80.layouts` entry-point group. For each
   package value (e.g., `glove80.families.tailorkey`), the generator imports its `.layouts`
   module to register the family.
2. `glove80.layouts.generator` iterates the registry, builds each variant, augments it with metadata, and writes JSON to `layouts/<family>/releases`.
3. Re-running the command is idempotent: if the serialized JSON already matches the generated payload, the file is left untouched.

## Shared Helpers
`glove80/layouts/common.py` and the higher-level `glove80.layouts.LayoutBuilder` codify the shared logic between layout families: resolving `LayerRef` placeholders (always-on), assembling the ordered layer list, and injecting metadata fields. You can compose layouts directly via `compose_layout()` (simple cases) or use the builder (advanced ordering and feature insertion). The builder exposes ergonomics-focused helpers such as `add_mouse_layers()`, `add_cursor_layer()`, and `add_home_row_mods()`.

```python
from glove80.layouts import LayoutBuilder
from glove80.layouts.components import LayoutFeatureComponents
from glove80.families.tailorkey.layers import build_mouse_layers, build_cursor_layer, build_hrm_layers

def _hrm_layers_for(variant: str):
    layers = build_hrm_layers(variant)
    return LayoutFeatureComponents(layers=layers)

generated_layers = build_all_layers(variant)
builder = LayoutBuilder(
    metadata_key="tailorkey",
    variant=variant,
    common_fields=COMMON_FIELDS,
    layer_names=_layer_names(variant),
    mouse_layers_provider=build_mouse_layers,
    cursor_layers_provider=lambda v: {"Cursor": build_cursor_layer(v)},
    home_row_provider=_hrm_layers_for,
)
builder.add_layers(generated_layers)
builder.add_home_row_mods(target_layer="Typing", position="before")
builder.add_cursor_layer(insert_after="Autoshift")
builder.add_mouse_layers(insert_after="Lower")
payload = builder.build()
```

The helper methods guarantee that the required macros, combos, input listeners, and layer indices stay in sync each time the feature is applied, so TailorKey, Default, QuantumTouch, Glorious Engrammer, and any user scripts all share one consistent pipeline.

### Feature Merging (single implementation)
Runtime feature application and builder feature insertion both use a single shared helper: `glove80.layouts.merge.merge_components`. This eliminates drift between the two code paths.

### CLI Notes
- `glove80 validate <file>` is a friendlier alias for `typed-parse`.
- `glove80 generate --out <path>` overrides the destination path when `--layout` and `--variant` are provided.
- `glove80 scaffold src/glove80/families/custom/specs.py --layout custom --variant beta` writes a starter Python spec with placeholders for layers, macros, and metadata.
- The CLI accepts `glorious-engrammer` as an alias for `glorious_engrammer`.

### Third-party layout discovery
External packages can contribute families without editing this repo by
declaring an entry point in `pyproject.toml`:

```toml
[project.entry-points."glove80.layouts"]
custom = "my_package.families.custom"
```

Each entry maps a layout key (`custom`) to the module path that contains both
`metadata.json` and the corresponding `layouts` module. During `glove80
generate`, these packages are imported alongside the built-in families, so the
CLI and Python API discover them automatically.

### Top-level API
For simple scripting, import from `glove80` directly:
```python
from glove80 import list_families, build_layout, apply_feature, bilateral_home_row_components
```

## Tests & CI
- Layer-focused tests under `tests/tailorkey/` lock down every specialized factory (HRM, cursor, mouse, etc.).
- Parity tests under `tests/glorious_engrammer/` ensure the Sunaku release stays identical to the generated payload.
- Layout parity tests compare the composed dictionary against the checked-in JSON for every variant in `layouts/<layout>/releases`.
- The GitHub Actions `ci.yml` workflow runs `just regen` and `just ci`, so a pull request cannot be merged unless the generated JSON matches the code and all tests pass.
