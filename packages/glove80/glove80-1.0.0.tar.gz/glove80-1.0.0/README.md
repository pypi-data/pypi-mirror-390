# Glove80 Layout Toolkit

This repository is the canonical, code-first source of the Glove80 layout families ([Default](layouts/default/README.md), [TailorKey](layouts/tailorkey/README.md), [QuantumTouch](layouts/quantum_touch/README.md), and [Glorious Engrammer](layouts/glorious-engrammer/README.md)).
Every release JSON under `layouts/*/releases` can be regenerated deterministically from the declarative specs and metadata checked into `src/glove80`.

## Highlights
- The default, TailorKey, QuantumTouch, and Glorious Engrammer families live under `src/glove80/families/` with typed specs, factories, and regression tests.
- Metadata travels with the package (`src/glove80/families/*/metadata.json`), so the CLI and library always agree on UUIDs, release notes, and output paths.
- A Typer-powered CLI (`glove80 generate …`) replaces ad-hoc scripts and keeps the regeneration workflow uniform across layouts.
- Release artifacts are grouped under `layouts/<layout>/releases`, keeping the repo root clean while preserving the published JSON verbatim.

## Quick Start
1. Install dependencies (the repo uses [uv](https://github.com/astral-sh/uv)):
   ```bash
   uv sync
   ```
2. Regenerate every release JSON:
   ```bash
   just regen
   ```
3. Run the full regression suite (per-layer tests + layout parity checks):
   ```bash
   just ci
   ```
4. Need a single variant? Use the CLI directly:
   ```bash
   glove80 generate --layout tailorkey --variant mac
   ```

`just --list` shows the available helper tasks.

## Using the Python API
The public API lives on the root package:

```python
from glove80 import build_layout, list_families

print(list_families())  # ['default', 'tailorkey', 'quantum_touch', 'glorious_engrammer']
layout = build_layout("tailorkey", "mac")
```

`build_layout(<family>, <variant>)` always returns the same dictionary that the CLI would write into `layouts/<family>/releases/…`.

## Repository Layout
```
.
├─ layouts/                     # checked-in release JSON + layout-specific README.md files
│  ├─ default/
│  │  └─ releases/
│  ├─ tailorkey/
│  │  └─ releases/
│  ├─ quantum_touch/
│  │  └─ releases/
│  └─ glorious-engrammer/
│     └─ releases/
├─ docs/                        # architecture overview
├─ src/glove80/
│  ├─ cli/                      # Typer CLI
│  ├─ layouts/                  # registry, common helpers, CLI wiring
│  └─ families/                 # default, TailorKey, QuantumTouch, Glorious Engrammer implementations + metadata
│     ├─ default/
│     ├─ tailorkey/
│     ├─ quantum_touch/
│     └─ glorious_engrammer/
└─ tests/                       # split by layout family
```

- Read `docs/architecture.md` for a walkthrough of the data flow and regeneration pipeline.
- `layouts/default/README.md`, `layouts/tailorkey/README.md`, `layouts/quantum_touch/README.md`, and `layouts/glorious-engrammer/README.md` explain how each layout family is structured, the available layers, and the steps for adding new variants.

## CI Contract
`.github/workflows/ci.yml` runs the same steps you do locally:
- `just regen` must leave `layouts/*/releases` unchanged or the build fails, proving the checked-in JSON matches the current code.
- `just ci` (`uv run pytest`) covers every layer factory plus whole-layout comparisons.
- Pull requests are required to keep both commands clean, so regeneration plus tests are the only gatekeepers.

## Contributing
1. Edit specs or metadata, re-run `just regen`, and inspect the resulting diffs under `layouts/`.
2. Extend/adjust the targeted per-layer tests under `tests/<layout>/` when you change behavior.
3. Document intentional changes in the relevant `layouts/<family>/README.md` (and `docs/architecture.md` if the pipeline changes) so future contributors understand the rationale.
