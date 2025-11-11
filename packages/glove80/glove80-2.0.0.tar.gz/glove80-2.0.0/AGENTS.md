# Glove80 Agent Guide

## Mission Recap
- This repository is the canonical, code-first source for every Glove80 layout family (Default, TailorKey, QuantumTouch, Glorious Engrammer). Declarative specs under `src/glove80/` generate the JSON releases under `layouts/<family>/releases/`.
- Never hand-edit the JSON releases. All changes flow through the Python specs, helpers, and the Typer CLI (`glove80 generate …`).
- `uv` drives dependencies, `just` wraps the two critical workflows: `just regen` (regenerate JSON) and `just ci` (pytest with coverage).

## Source-of-Truth Map
| Path | Role | Tips |
| --- | --- | --- |
| `src/glove80/families/<name>/specs/` | Typed dataclasses describing each layer/macro/combo. | Modify these when changing behavior; keep metadata (`metadata.json`) aligned. |
| `src/glove80/layouts/` | `LayoutBuilder`, registry (`family.py`), generator, schema helpers. | Builder helpers (`add_mouse_layers`, `add_home_row_mods`, etc.) are preferred over ad-hoc stitching. |
| `src/glove80/features/` | Reusable feature bundles returning `LayoutFeatureComponents`. | Use these to add cursor/mouse/HRM stacks without duplicating logic. |
| `src/glove80/cli/__init__.py` | Typer CLI for listing families and regenerating releases. | `uv run glove80 generate --layout <family> --variant <v>` mirrors `just regen-one`. |
| `layouts/<family>/` | Auto-generated release JSON + family README. | Validate diffs after regeneration; never edit directly. |
| `tests/<family>/` | Layer factories + parity checks. | Ensure `test_<family>_layout_matches_release[...]` stays green after changes. |
| `docs/architecture.md` | High-level data flow reference. | Update when generation pipeline or shared helpers change. |

## Day-to-Day Commands
- `uv sync` — install/update dependencies.
- `just regen` — regenerate every release JSON (must be clean before pushing).
- `just regen-one <family> <variant>` — tighten the loop while iterating on a single target.
- `uv run python -m glove80 generate --dry-run [--layout …]` — compare outputs without writing files (great for parity checks).
- `just ci` / `uv run pytest` — run the full test suite; scope to `tests/<family>/` for focused work.

## Common Workflows
1. **Adjust an existing layout variant**
   - Edit the relevant spec or layer factory in `src/glove80/families/<family>/`.
   - If you touch shared helpers, add/extend tests under `tests/<family>/` or `tests/test_builder.py`.
   - Run `uv run python -m glove80 generate --layout <family> --dry-run` to verify determinism, then `just regen` to update JSON.
2. **Introduce a new family or variant**
   - Create a new folder in `src/glove80/families/` with `metadata.json`, specs, and layer factories.
   - Register it in `glove80.layouts.family.REGISTRY` (usually by importing the family module in `src/glove80/families/__init__.py`).
   - Add parity tests under `tests/<family>/` plus a README in `layouts/<family>/` describing variants and layers.
3. **Add or reuse feature bundles**
   - Prefer returning `LayoutFeatureComponents` from helpers in `src/glove80/features/` and wiring them via `LayoutBuilder.add_*` methods.
   - When adding new helpers, cover them in `tests/test_features.py` and document intended usage in `docs/architecture.md` if the pipeline shifts.
4. **CLI or tooling tweaks**
   - The Typer app lives in `src/glove80/cli/__init__.py`. Update commands or presentation there and add coverage in `tests/test_cli.py`.

## Testing & Quality Gates
- Pytest only. Keep existing parity cases named `test_<family>_layout_matches_release[...]`.
- Shared helpers and layout builder logic are covered by `tests/test_builder.py`, `tests/test_features.py`, and the per-family suites—add targeted cases before expanding regression scope.
- CI (see `.github/workflows/ci.yml`) expects `just regen` and `just ci` to pass with zero diffs. Run both locally before proposing changes.

## Style & Documentation
- Python 3.11+, strict typing, 4-space indentation, Ruff/Black-compatible formatting (respect `pyproject.toml`).
- Keep commits focused and imperative (“Add QuantumTouch cursor helper”). Include regenerated JSON in the same commit with a note explaining why it changed.
- When workflow or API expectations change, update `docs/architecture.md` and the affected `layouts/<family>/README.md` files.

## Quick Triage Checklist (Before Opening a PR)
1. Working tree clean except for intentional code + regenerated JSON.
2. `just regen` followed by `git status` shows only expected release diffs.
3. `just ci` passes (or the scoped pytest run relevant to your change, with rationale recorded).
4. Documentation reflects new behavior and metadata stays in sync with generated payloads.

Keep this guide lean and adjust it whenever the workflow, tooling, or layout registry evolves.
