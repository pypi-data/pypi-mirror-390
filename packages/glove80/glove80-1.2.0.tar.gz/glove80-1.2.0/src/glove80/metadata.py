"""
Helpers for loading TailorKey variant metadata.

This keeps JSON parsing in one place (with types) so both the generator and the
library can share it safely.
"""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources
from pathlib import Path
from typing import Dict, List, TypedDict

DEFAULT_LAYOUT = "tailorkey"
LAYOUT_METADATA_PACKAGES: Dict[str, str] = {
    "default": "glove80.families.default",
    "tailorkey": "glove80.families.tailorkey",
    "quantum_touch": "glove80.families.quantum_touch",
    "glorious_engrammer": "glove80.families.glorious_engrammer",
}


class VariantMetadata(TypedDict):
    output: str
    title: str
    uuid: str
    parent_uuid: str
    date: int
    tags: List[str]
    notes: str


MetadataByVariant = Dict[str, VariantMetadata]


def _metadata_package(layout: str) -> str:
    try:
        return LAYOUT_METADATA_PACKAGES[layout]
    except KeyError as exc:  # pragma: no cover
        raise KeyError(f"Unknown layout '{layout}'. Available: {sorted(LAYOUT_METADATA_PACKAGES)}") from exc


def _load_metadata_from_path(metadata_path: Path) -> MetadataByVariant:
    with metadata_path.open(encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache()
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
        raise KeyError(f"Unknown variant '{name}' for layout '{layout}'. Available: {sorted(metadata)}") from exc
