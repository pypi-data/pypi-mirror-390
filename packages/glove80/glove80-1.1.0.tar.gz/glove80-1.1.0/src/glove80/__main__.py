from __future__ import annotations

from .cli import app


def main() -> None:  # pragma: no cover - thin Typer shim
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
