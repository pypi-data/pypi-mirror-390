"""Keycode metadata sourced from the Glove80 layout editor.

This module holds the actual implementation; ``__init__`` re-exports the
public API to keep package inits minimal.
"""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources
from typing import TYPE_CHECKING, NewType, TypeGuard

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from collections.abc import Iterable


class KeyOption(BaseModel):
    """Single key definition as described by the layout editor bundle."""

    model_config = ConfigDict(populate_by_name=True)

    names: list[str]
    description: str
    context: str
    clarify: bool | None
    documentation: str | None = None
    os: dict[str, bool | None] = Field(default_factory=dict)
    footnotes: dict[str, str | list[str]] = Field(default_factory=dict)
    shortcut: str | None = None
    symbol: str | None = None
    shifted_from: str | None = Field(default=None, alias="shiftedFrom")

    @property
    def canonical_name(self) -> str:
        return self.names[0]


def _read_resource(name: str) -> str:
    # Data files live at the package root (glove80.keycodes)
    return resources.files(__package__).joinpath(name).read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def _raw_key_options() -> list[KeyOption]:
    return [KeyOption.model_validate(obj) for obj in json.loads(_read_resource("key_options.json"))]


def _iter_aliases(option: KeyOption) -> Iterable[str]:
    for name in option.names:
        yield name
        if name.endswith("(code)"):
            yield name[: -len("(code)")]
    if option.shortcut:
        yield option.shortcut
    if option.symbol:
        yield option.symbol


@lru_cache(maxsize=1)
def key_options_by_name() -> dict[str, KeyOption]:
    """Return a lookup table for every alias."""
    mapping: dict[str, KeyOption] = {}
    for option in _raw_key_options():
        for alias in _iter_aliases(option):
            mapping.setdefault(alias, option)
    return mapping


def _load_known_key_names() -> tuple[tuple[str, ...], frozenset[str]]:
    alias_names: set[str] = set()
    for option in _raw_key_options():
        alias_names.update(_iter_aliases(option))

    zmk_names: set[str] = set()
    zmk_data = json.loads(_read_resource("zmk.json"))
    for behavior in zmk_data:
        code = behavior.get("code")
        if code:
            zmk_names.add(str(code))
        for command in behavior.get("commands") or []:
            cmd_code = command.get("code")
            if cmd_code:
                zmk_names.add(str(cmd_code))

    names: set[str] = set()
    for alias in alias_names:
        if alias and not alias.startswith("&"):
            names.add(alias)

    names.update(zmk_names)
    names.add("MACRO_PLACEHOLDER")

    sorted_names = tuple(sorted(names))
    return sorted_names, frozenset(sorted_names)


KEY_NAME_VALUES, _KNOWN_KEY_NAMES = _load_known_key_names()
KnownKeyName = NewType("KnownKeyName", str)


def is_known_key_name(name: str) -> TypeGuard[KnownKeyName]:
    """Check whether the provided token is a recognized key name."""
    return name in _KNOWN_KEY_NAMES


def assert_known_key_name(name: str) -> None:
    """Fail loudly when a layer references a key the editor does not expose."""
    if name not in _KNOWN_KEY_NAMES:
        msg = f"Unknown key name '{name}'. Update key metadata if this is an intentional addition."
        raise ValueError(msg)


def all_key_names() -> Iterable[str]:
    """Expose every known name (aliases included)."""
    return KEY_NAME_VALUES


__all__ = [
    "KEY_NAME_VALUES",
    "KeyOption",
    "KnownKeyName",
    "all_key_names",
    "assert_known_key_name",
    "is_known_key_name",
    "key_options_by_name",
]
