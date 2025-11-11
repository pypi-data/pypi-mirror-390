"""Helpers for loading TailorKey variant metadata.

This keeps JSON parsing in one place (with types) so both the generator and the
library can share it safely.
"""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources, metadata as importlib_metadata
from typing import TYPE_CHECKING, Iterable, Iterator, Mapping, TypedDict, cast
from types import MappingProxyType

if TYPE_CHECKING:
    from pathlib import Path

DEFAULT_LAYOUT = "tailorkey"
_BUILTIN_LAYOUT_METADATA_PACKAGES: dict[str, str] = {
    "default": "glove80.families.default",
    "tailorkey": "glove80.families.tailorkey",
    "quantum_touch": "glove80.families.quantum_touch",
    "glorious_engrammer": "glove80.families.glorious_engrammer",
}
ENTRY_POINT_GROUP = "glove80.layouts"


class VariantMetadata(TypedDict):
    output: str
    title: str
    uuid: str
    parent_uuid: str
    date: int
    tags: list[str]
    notes: str


MetadataByVariant = dict[str, VariantMetadata]


def _selected_entry_points() -> Iterable[importlib_metadata.EntryPoint]:
    """Return iterable of entry points for ``ENTRY_POINT_GROUP`` across Python versions."""

    try:  # Python 3.10+ signature
        return importlib_metadata.entry_points(group=ENTRY_POINT_GROUP)
    except TypeError:  # older importlib_metadata without ``group`` kwarg
        entries = importlib_metadata.entry_points()
        if hasattr(entries, "select"):
            return entries.select(group=ENTRY_POINT_GROUP)
        # Legacy behavior: mapping from group -> sequence of entry points.
        legacy = cast(
            "Mapping[str, Iterable[importlib_metadata.EntryPoint]]",
            entries,
        )
        return legacy.get(ENTRY_POINT_GROUP, ())


def _iter_entry_point_layouts() -> Iterator[tuple[str, str]]:
    """Yield (name, package) pairs discovered via entry points."""

    try:
        selected = _selected_entry_points()
    except Exception:  # pragma: no cover - importlib metadata failure
        return iter(())

    return ((entry.name, entry.value) for entry in selected)


@lru_cache(maxsize=1)
def _combined_layout_metadata_packages() -> Mapping[str, str]:
    packages: dict[str, str] = dict(_BUILTIN_LAYOUT_METADATA_PACKAGES)
    for name, module_path in _iter_entry_point_layouts():
        packages[name] = module_path
    return MappingProxyType(packages)


def layout_metadata_packages() -> Mapping[str, str]:
    """Return the mapping of layout key -> metadata package (with plugins)."""

    return _combined_layout_metadata_packages()


# Back-compat alias for callers that still import the module-level map.
LAYOUT_METADATA_PACKAGES: Mapping[str, str] = layout_metadata_packages()


def _refresh_layout_metadata_packages_for_tests() -> None:
    """Reset cached discovery results (used by tests)."""

    _combined_layout_metadata_packages.cache_clear()
    global LAYOUT_METADATA_PACKAGES
    LAYOUT_METADATA_PACKAGES = layout_metadata_packages()


def _metadata_package(layout: str) -> str:
    packages = layout_metadata_packages()
    try:
        return packages[layout]
    except KeyError as exc:  # pragma: no cover
        msg = f"Unknown layout '{layout}'. Available: {sorted(packages)}"
        raise KeyError(msg) from exc


def _load_metadata_from_path(metadata_path: Path) -> MetadataByVariant:
    with metadata_path.open(encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache
def _load_packaged_metadata(layout: str) -> MetadataByVariant:
    package = _metadata_package(layout)
    resource = resources.files(package).joinpath("metadata.json")
    with resource.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_metadata(layout: str = DEFAULT_LAYOUT, path: Path | None = None) -> MetadataByVariant:
    """Load (and cache) the metadata file as typed objects."""
    if path is not None:
        return _load_metadata_from_path(path)
    return _load_packaged_metadata(layout)


def get_variant_metadata(
    name: str,
    *,
    layout: str = DEFAULT_LAYOUT,
    path: Path | None = None,
) -> VariantMetadata:
    """Return the metadata entry for a particular variant."""
    metadata = load_metadata(layout, path)
    try:
        return metadata[name]
    except KeyError as exc:  # pragma: no cover
        msg = f"Unknown variant '{name}' for layout '{layout}'. Available: {sorted(metadata)}"
        raise KeyError(msg) from exc
