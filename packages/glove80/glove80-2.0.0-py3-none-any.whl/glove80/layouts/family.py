"""Protocol and registry for layout families."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, Any

if TYPE_CHECKING:
    from collections.abc import Iterable


class LayoutFamily(Protocol):
    """Common interface every layout family must implement."""

    name: str

    def variants(self) -> Iterable[str]:
        """Return the iterable of supported variant identifiers."""

    def build(self, variant: str) -> dict[str, Any]:
        """Build the layout payload for the requested variant."""

    def metadata_key(self) -> str:
        """Return the metadata namespace used in sources/layouts.<family>."""


@dataclass(frozen=True)
class RegisteredFamily:
    name: str
    family: LayoutFamily


class LayoutRegistry:
    """Simple registry for layout families."""

    def __init__(self) -> None:
        self._families: dict[str, LayoutFamily] = {}

    def register(self, family: LayoutFamily) -> None:
        if family.name in self._families:  # pragma: no cover
            msg = f"Duplicate layout family '{family.name}'"
            raise ValueError(msg)
        self._families[family.name] = family

    def get(self, name: str) -> LayoutFamily:
        return self._families[name]

    def families(self) -> Iterable[RegisteredFamily]:
        return (RegisteredFamily(name, family) for name, family in sorted(self._families.items()))


REGISTRY = LayoutRegistry()


def get_family(name: str) -> LayoutFamily:
    return REGISTRY.get(name)


def list_families() -> list[str]:
    return [registered.name for registered in REGISTRY.families()]


def build_layout(family: str, variant: str) -> dict[str, Any]:
    return get_family(family).build(variant)


# ----------------------------- name aliasing -----------------------------
# Cosmetic alias for CLI ergonomics and friendlier UX.
# Keep canonical registry names unchanged.
ALIAS_TO_CANONICAL: dict[str, str] = {
    "glorious-engrammer": "glorious_engrammer",
}


def canonical_family_name(name: str) -> str:
    """Return the canonical registry key for a possibly-aliased name."""
    return ALIAS_TO_CANONICAL.get(name, name)


__all__ = [
    "REGISTRY",
    "LayoutFamily",
    "LayoutRegistry",
    "RegisteredFamily",
    "build_layout",
    "get_family",
    "list_families",
    "canonical_family_name",
]
