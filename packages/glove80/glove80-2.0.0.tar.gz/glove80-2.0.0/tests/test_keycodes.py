from __future__ import annotations

import pytest

from glove80.base import KeySpec
from glove80.keycodes import key_options_by_name


def test_alias_is_accepted_without_conversion() -> None:
    spec = KeySpec("LCTRL")
    assert spec.value == "LCTRL"


def test_unknown_key_raises() -> None:
    with pytest.raises(ValueError):
        KeySpec("NOT_A_REAL_KEY")


def test_special_key_names_allowed() -> None:
    spec = KeySpec("BT_CLR")
    assert spec.value == "BT_CLR"


def test_shortcut_aliases_supported() -> None:
    spec = KeySpec("6")
    assert spec.value == "6"


def test_manual_placeholders_allowed() -> None:
    spec = KeySpec("MACRO_PLACEHOLDER")
    assert spec.value == "MACRO_PLACEHOLDER"


def test_registry_contains_aliases() -> None:
    registry = key_options_by_name()
    assert "A" in registry
    assert "N1" in registry
