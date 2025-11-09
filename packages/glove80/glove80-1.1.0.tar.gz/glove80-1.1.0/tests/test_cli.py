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
