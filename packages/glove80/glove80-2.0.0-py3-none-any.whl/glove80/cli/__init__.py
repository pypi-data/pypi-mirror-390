from __future__ import annotations

from pathlib import Path
import textwrap
from string import Template

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from glove80.layouts.family import REGISTRY
from glove80.layouts.generator import GenerationResult, available_layouts, generate_layouts
from glove80.layouts.parse import parse_typed_sections

app = typer.Typer(help="Utilities for working with Glove80 layouts.")
console = Console()


def _print_results(results: list[GenerationResult]) -> None:
    table = Table(title="✨ Layout Generation Results", show_header=True, header_style="bold magenta")
    table.add_column("Layout", style="cyan", no_wrap=True)
    table.add_column("Variant", style="blue")
    table.add_column("Destination", style="white")
    table.add_column("Status", justify="center")

    for result in results:
        status_icon = "✅ updated" if result.changed else "⚪ unchanged"
        status_style = "[green]" if result.changed else "[dim white]"
        table.add_row(result.layout, result.variant, str(result.destination), f"{status_style}{status_icon}[/]")

    console.print(table)
    summary = ", ".join(f"{r.layout}:{r.variant}" for r in results)
    if summary:
        console.print(summary)


@app.command("families")
def families() -> None:
    """List registered layout families and their variants."""
    table = Table(title="🎹 Available Layout Families", show_header=True, header_style="bold cyan")
    table.add_column("Family", style="yellow", no_wrap=True)
    table.add_column("Variants", style="green")

    for registered in REGISTRY.families():
        variants = ", ".join(sorted(registered.family.variants()))
        table.add_row(registered.name, variants)

    console.print(table)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Show the top-level help when no sub-command is provided."""
    if ctx.invoked_subcommand is None:
        help_text = ctx.get_help()
        panel = Panel(help_text, title="[bold cyan]Glove80 Utilities[/]", border_style="cyan")
        console.print(panel)
        raise typer.Exit


@app.command("generate")
def generate(
    layout: str | None = typer.Option(None, help="Limit regeneration to a single layout family."),
    variant: str | None = typer.Option(None, help="Limit regeneration to a single variant."),
    metadata: Path | None = typer.Option(
        None,
        help="Optional path to a metadata JSON file (useful for layout experiments).",
    ),
    dry_run: bool = typer.Option(False, help="Only compare outputs; do not rewrite files."),
    out: Path | None = typer.Option(
        None,
        help="Override destination path (requires --layout and --variant). If provided with --metadata, only the destination is overridden.",
    ),
) -> None:
    """Regenerate release JSON artifacts from the canonical sources."""
    if metadata is not None and layout is None:
        msg = "--metadata requires --layout to be specified"
        raise typer.BadParameter(msg)

    if out is not None and (layout is None or variant is None):
        raise typer.BadParameter("--out requires both --layout and --variant")

    results = generate_layouts(
        layout=layout,
        variant=variant,
        metadata_path=metadata,
        dry_run=dry_run,
        out=out,
    )
    if not results:
        available = ", ".join(available_layouts())
        console.print(f"[bold yellow]⚠️  No results generated.[/] Known layouts: [cyan]{available}[/]")
        raise typer.Exit(code=1)

    _print_results(results)


_SCAFFOLD_TEMPLATE = Template(
    textwrap.dedent(
        """
        \"\"\"Starter spec for the $layout layout ($variant variant).

        Generated via ``glove80 scaffold``. Move this file into your project (for
        example ``src/glove80/families/$layout/specs.py``), update
        ``metadata.json`` so it knows about ``$variant``, and then fill in the
        sections below.
        \"\"\"

        from __future__ import annotations

        from typing import Any

        from glove80.base import KeySpec, LayerSpec, build_layer_from_spec
        from glove80.layouts.common import build_common_fields, compose_layout
        from glove80.layouts.schema import Combo, HoldTap, InputListener, Macro


        LAYOUT_KEY = "$layout"
        VARIANT = "$variant"

        COMMON_FIELDS = build_common_fields(
            creator="$creator",
            # TODO: keep metadata.json in sync with these fields.
        )

        LAYER_NAMES = ("Base",)
        LAYER_SPECS = {
            "Base": LayerSpec(
                overrides={
                    # 0: KeySpec("ESC"),
                    # 1: KeySpec("Q"),
                    # TODO: define the rest of the overrides for this layer.
                },
            ),
        }

        MACROS: list[Macro] = []
        HOLD_TAPS: list[HoldTap] = []
        COMBOS: list[Combo] = []
        INPUT_LISTENERS: list[InputListener] = []


        def build_layers() -> dict[str, list[dict[str, Any]]]:
            \"\"\"Expand LayerSpec definitions into firmware-friendly layers.\"\"\"

            return {name: build_layer_from_spec(spec) for name, spec in LAYER_SPECS.items()}


        def build_layout_payload() -> dict[str, Any]:
            \"\"\"Compose the layout dictionary the CLI would normally emit.\"\"\"

            return compose_layout(
                common_fields=COMMON_FIELDS,
                layer_names=LAYER_NAMES,
                generated_layers=build_layers(),
                metadata_key=LAYOUT_KEY,
                variant=VARIANT,
                macros=MACROS,
                hold_taps=HOLD_TAPS,
                combos=COMBOS,
                input_listeners=INPUT_LISTENERS,
            )
        """
    ).strip(),
)


def _render_scaffold_template(*, layout: str, variant: str, creator: str) -> str:
    return _SCAFFOLD_TEMPLATE.substitute(layout=layout, variant=variant, creator=creator)


@app.command("scaffold")
def scaffold(
    destination: Path = typer.Argument(
        ...,
        file_okay=True,
        dir_okay=False,
        help="Where to write the generated spec (e.g. src/glove80/families/custom/specs.py)",
    ),
    layout: str = typer.Option("custom_layout", help="Name of the layout family/metadata key."),
    variant: str = typer.Option("default", help="Variant identifier to pre-fill in the template."),
    creator: str = typer.Option("Your Name", help="Creator field stored in common metadata."),
    force: bool = typer.Option(False, "--force", help="Overwrite the destination if it already exists."),
) -> None:
    """Generate a starter Python spec for a new family/variant."""

    if destination.exists() and not force:
        msg = f"{destination} already exists (use --force to overwrite)"
        raise typer.BadParameter(msg)

    destination.parent.mkdir(parents=True, exist_ok=True)
    content = _render_scaffold_template(layout=layout, variant=variant, creator=creator)
    destination.write_text(content, encoding="utf-8")
    console.print(f"[green]✨ Wrote starter spec to[/] [cyan]{destination}[/]")


__all__ = ["app"]


@app.command("typed-parse")
def typed_parse(
    path: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, help="Path to a layout JSON file."),
) -> None:
    """Parse a layout JSON into typed Pydantic models and report a summary."""
    import json

    data = json.loads(path.read_text(encoding="utf-8"))
    payload, macros, hold_taps, combos, listeners = parse_typed_sections(data)

    table = Table(title=f"Typed Parse: {path.name}", show_header=True, header_style="bold green")
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Count", justify="right")
    table.add_row("layer_names", str(len(payload.layer_names)))
    table.add_row("macros", str(len(macros)))
    table.add_row("holdTaps", str(len(hold_taps)))
    table.add_row("combos", str(len(combos)))
    table.add_row("inputListeners", str(len(listeners)))
    console.print(table)

    console.print("[green]Validation OK[/] — sections parsed into typed models.")


# Friendly alias for typed-parse
@app.command("validate")
def validate(
    path: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, help="Path to a layout JSON file."),
) -> None:
    """Alias for ``typed-parse`` with a more descriptive name."""
    typed_parse(path)
