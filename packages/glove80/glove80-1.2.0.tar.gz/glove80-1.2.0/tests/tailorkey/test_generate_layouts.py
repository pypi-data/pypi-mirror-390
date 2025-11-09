import json

import pytest

from glove80.metadata import load_metadata
from glove80 import build_layout as build_family_layout


TAILORKEY_VARIANTS = sorted(load_metadata(layout="tailorkey").keys())


@pytest.mark.parametrize("variant", TAILORKEY_VARIANTS)
def test_generated_files_match_canonical_source(variant, tailorkey_metadata, repo_root):
    """Each release JSON must match its canonical source exactly."""

    meta = tailorkey_metadata[variant]
    source_path = repo_root / meta["output"]
    expected = json.loads(source_path.read_text())

    built = build_family_layout("tailorkey", variant)
    assert built == expected
