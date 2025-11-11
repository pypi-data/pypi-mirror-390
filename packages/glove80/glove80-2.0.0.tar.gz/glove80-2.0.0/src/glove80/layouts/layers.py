"""Shared helpers for declarative layer construction."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeAlias

from glove80.base import KeySpec, LayerRef, LayerSpec
from glove80.specs.utils import kp

if TYPE_CHECKING:
    from collections.abc import Sequence

TokenTuple: TypeAlias = tuple[Any, ...]
Token: TypeAlias = KeySpec | TokenTuple | str | int | LayerRef
ParamToken: TypeAlias = Token


def _normalize_param_token(param: ParamToken) -> KeySpec:
    if isinstance(param, KeySpec):
        return param
    if isinstance(param, tuple):
        return _token_to_key(param)
    if isinstance(param, (str, int, LayerRef)):
        return KeySpec(param)
    msg = f"Unsupported parameter token type: {param!r}"
    raise TypeError(msg)


def _token_to_key(token: Token) -> KeySpec:
    if isinstance(token, KeySpec):
        return token
    if isinstance(token, tuple):
        head = token[0]
        params = tuple(_normalize_param_token(param) for param in token[1:])
        if isinstance(head, KeySpec):
            # Merge an existing KeySpec with additional params.
            return KeySpec(head.value, head.params + params)
        return KeySpec(head, params)
    if isinstance(token, str):
        if token.startswith("&"):
            return KeySpec(token)
        return kp(token)
    if isinstance(token, (int, LayerRef)):
        return KeySpec(token)
    msg = f"Unsupported token type: {token!r}"
    raise TypeError(msg)


def rows_to_layer_spec(rows: Sequence[Sequence[Any]]) -> LayerSpec:
    flat: list[Token] = [token for row in rows for token in row]
    if len(flat) != 80:  # pragma: no cover
        msg = f"Expected 80 entries for a layer, got {len(flat)}"
        raise ValueError(msg)
    overrides = {idx: _token_to_key(token) for idx, token in enumerate(flat)}
    return LayerSpec(overrides=overrides)


def _transparent_layer() -> LayerSpec:
    return LayerSpec(overrides={})


__all__ = ["Token", "_token_to_key", "_transparent_layer", "rows_to_layer_spec"]
