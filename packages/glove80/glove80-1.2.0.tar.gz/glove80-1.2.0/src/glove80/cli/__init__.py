from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from ..layouts.generator import GenerationResult, available_layouts, generate_layouts
from ..layouts.family import REGISTRY

app = typer.Typer(help="Utilities for working with Glove80 layouts.")


def _print_results(results: list[GenerationResult]) -> None:
    for result in results:
        status = "updated" if result.changed else "unchanged"
        typer.echo(f"{result.layout}:{result.variant}: {result.destination} ({status})")


@app.command("families")
def families() -> None:
    """List registered layout families and their variants."""

    for registered in REGISTRY.families():
        variants = ", ".join(sorted(registered.family.variants()))
        typer.echo(f"{registered.name}: {variants}")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Show the top-level help when no sub-command is provided."""

    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command("generate")
def generate(
    layout: Optional[str] = typer.Option(None, help="Limit regeneration to a single layout family."),
    variant: Optional[str] = typer.Option(None, help="Limit regeneration to a single variant."),
    metadata: Optional[Path] = typer.Option(
        None,
        help="Optional path to a metadata JSON file (useful for layout experiments).",
    ),
    dry_run: bool = typer.Option(False, help="Only compare outputs; do not rewrite files."),
) -> None:
    """Regenerate release JSON artifacts from the canonical sources."""

    if metadata is not None and layout is None:
        raise typer.BadParameter("--metadata requires --layout to be specified")

    results = generate_layouts(layout=layout, variant=variant, metadata_path=metadata, dry_run=dry_run)
    if not results:
        available = ", ".join(available_layouts())
        typer.secho(f"No results generated. Known layouts: {available}", fg=typer.colors.YELLOW)
        raise typer.Exit(code=1)

    _print_results(results)


__all__ = ["app"]
