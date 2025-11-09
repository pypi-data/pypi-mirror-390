import json
from pathlib import Path
from typing import Callable

import pytest

from glove80.metadata import MetadataByVariant, get_variant_metadata, load_metadata

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def default_metadata() -> MetadataByVariant:
    return load_metadata(layout="default")


@pytest.fixture(scope="session")
def default_variants(default_metadata: MetadataByVariant) -> list[str]:
    return sorted(default_metadata)


@pytest.fixture(scope="session")
def tailorkey_metadata() -> MetadataByVariant:
    return load_metadata(layout="tailorkey")


@pytest.fixture(scope="session")
def tailorkey_variants(tailorkey_metadata) -> list[str]:
    return sorted(tailorkey_metadata)


@pytest.fixture(scope="session")
def quantum_touch_metadata() -> MetadataByVariant:
    return load_metadata(layout="quantum_touch")


@pytest.fixture(scope="session")
def glorious_engrammer_metadata() -> MetadataByVariant:
    return load_metadata(layout="glorious_engrammer")


@pytest.fixture(scope="session")
def load_default_variant(repo_root: Path) -> Callable[[str], dict]:
    def _loader(variant: str) -> dict:
        meta = get_variant_metadata(variant, layout="default")
        path = repo_root / meta["output"]
        return json.loads(path.read_text())

    return _loader


@pytest.fixture(scope="session")
def load_tailorkey_variant(repo_root: Path) -> Callable[[str], dict]:
    def _loader(variant: str) -> dict:
        meta = get_variant_metadata(variant, layout="tailorkey")
        path = repo_root / meta["output"]
        return json.loads(path.read_text())

    return _loader


@pytest.fixture(scope="session")
def load_quantum_touch_variant(repo_root: Path) -> Callable[[str], dict]:
    def _loader(variant: str) -> dict:
        meta = get_variant_metadata(variant, layout="quantum_touch")
        path = repo_root / meta["output"]
        return json.loads(path.read_text())

    return _loader


@pytest.fixture(scope="session")
def load_glorious_engrammer_variant(repo_root: Path) -> Callable[[str], dict]:
    def _loader(variant: str) -> dict:
        meta = get_variant_metadata(variant, layout="glorious_engrammer")
        path = repo_root / meta["output"]
        return json.loads(path.read_text())

    return _loader
