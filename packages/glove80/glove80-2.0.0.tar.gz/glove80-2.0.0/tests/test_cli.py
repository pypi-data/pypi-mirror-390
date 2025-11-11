from __future__ import annotations

import json
import re
from pathlib import Path

from typer.testing import CliRunner

from glove80.cli import app

RUNNER = CliRunner()
REPO_ROOT = Path(__file__).resolve().parents[1]
TAILORKEY_METADATA = REPO_ROOT / "src/glove80/families/tailorkey/metadata.json"
ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def _strip_ansi(value: str) -> str:
    return ANSI_RE.sub("", value)


def test_cli_families_lists_registered() -> None:
    result = RUNNER.invoke(app, ["families"])
    assert result.exit_code == 0
    output = result.stdout
    for family in ("default", "tailorkey", "quantum_touch", "glorious_engrammer"):
        assert family in output


def test_cli_generate_dry_run_for_specific_variant() -> None:
    result = RUNNER.invoke(app, ["generate", "--layout", "tailorkey", "--variant", "windows", "--dry-run"])
    assert result.exit_code == 0
    assert "tailorkey:windows" in result.stdout


def test_cli_generate_requires_layout_when_metadata_provided() -> None:
    result = RUNNER.invoke(app, ["generate", "--metadata", str(TAILORKEY_METADATA)])
    assert result.exit_code != 0
    assert "--metadata requires --layout" in _strip_ansi(result.output)


def test_cli_generate_accepts_explicit_metadata_file() -> None:
    result = RUNNER.invoke(
        app,
        [
            "generate",
            "--layout",
            "tailorkey",
            "--variant",
            "windows",
            "--metadata",
            str(TAILORKEY_METADATA),
            "--dry-run",
        ],
    )
    assert result.exit_code == 0
    assert "tailorkey:windows" in result.stdout


def test_cli_generate_unknown_layout_error() -> None:
    result = RUNNER.invoke(app, ["generate", "--layout", "does-not-exist", "--dry-run"])
    assert result.exit_code != 0
    assert isinstance(result.exception, KeyError)
    assert "Unknown layout" in str(result.exception)


def test_cli_generate_accepts_hyphen_alias() -> None:
    # glorious-engrammer is an alias for glorious_engrammer
    result = RUNNER.invoke(app, ["generate", "--layout", "glorious-engrammer", "--dry-run"])
    assert result.exit_code == 0


def test_cli_generate_writes_output_with_custom_metadata(tmp_path: Path) -> None:
    metadata = json.loads(TAILORKEY_METADATA.read_text())
    entry = metadata["windows"]
    custom_output = tmp_path / "tailorkey-windows.json"
    entry["output"] = str(custom_output)
    custom_metadata = tmp_path / "metadata.json"
    custom_metadata.write_text(json.dumps({"windows": entry}))

    result = RUNNER.invoke(
        app,
        [
            "generate",
            "--layout",
            "tailorkey",
            "--variant",
            "windows",
            "--metadata",
            str(custom_metadata),
        ],
    )
    assert result.exit_code == 0
    assert custom_output.exists()


def test_cli_validate_alias_parses_release_file() -> None:
    # Use an existing release artifact for quick validation
    # TailorKey releases are present in the repo
    release_dir = REPO_ROOT / "layouts/tailorkey/releases"
    # Pick any file in the directory
    sample = next(p for p in release_dir.iterdir() if p.suffix == ".json")
    result = RUNNER.invoke(app, ["validate", str(sample)])
    assert result.exit_code == 0
    assert "Validation OK" in _strip_ansi(result.stdout)


def test_cli_generate_out_writes_to_custom_path(tmp_path: Path) -> None:
    dest = tmp_path / "tailorkey-windows.json"
    result = RUNNER.invoke(
        app,
        [
            "generate",
            "--layout",
            "tailorkey",
            "--variant",
            "windows",
            "--out",
            str(dest),
        ],
    )
    assert result.exit_code == 0
    assert dest.exists()


def test_cli_generate_out_overrides_metadata_destination(tmp_path: Path) -> None:
    # Prepare a custom metadata file pointing elsewhere, but provide --out

    # reuse TailorKey metadata as base
    import json

    metadata_path = TAILORKEY_METADATA
    meta = json.loads(metadata_path.read_text())
    entry = dict(meta["windows"])  # copy
    entry["output"] = str(tmp_path / "should-not-be-used.json")
    custom_meta = tmp_path / "metadata.json"
    custom_meta.write_text(json.dumps({"windows": entry}))

    dest = tmp_path / "dest.json"
    result = RUNNER.invoke(
        app,
        [
            "generate",
            "--layout",
            "tailorkey",
            "--variant",
            "windows",
            "--metadata",
            str(custom_meta),
            "--out",
            str(dest),
        ],
    )
    assert result.exit_code == 0
    assert dest.exists()


def test_cli_generate_out_requires_single_target(tmp_path: Path) -> None:
    # Missing --variant should error when --out is provided
    dest = tmp_path / "out.json"
    result = RUNNER.invoke(app, ["generate", "--layout", "tailorkey", "--out", str(dest), "--dry-run"])
    assert result.exit_code != 0
    assert "requires both --layout and --variant" in _strip_ansi(result.output)


def test_cli_scaffold_writes_template(tmp_path: Path) -> None:
    dest = tmp_path / "custom" / "specs.py"
    result = RUNNER.invoke(
        app,
        [
            "scaffold",
            str(dest),
            "--layout",
            "my_layout",
            "--variant",
            "beta",
            "--creator",
            "Ada",
        ],
    )
    assert result.exit_code == 0
    content = dest.read_text()
    assert 'LAYOUT_KEY = "my_layout"' in content
    assert 'VARIANT = "beta"' in content
    assert 'creator="Ada"' in content


def test_cli_scaffold_respects_force(tmp_path: Path) -> None:
    dest = tmp_path / "spec.py"
    dest.write_text("original")

    result = RUNNER.invoke(app, ["scaffold", str(dest)])
    assert result.exit_code != 0
    assert "already exists" in _strip_ansi(result.output)

    result = RUNNER.invoke(app, ["scaffold", str(dest), "--force"])
    assert result.exit_code == 0
    assert "Starter spec" in dest.read_text()
