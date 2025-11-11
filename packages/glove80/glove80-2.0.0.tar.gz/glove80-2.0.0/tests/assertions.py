"""Lightweight assertions tailored for gigantic layout payloads."""

from __future__ import annotations

import json
from hashlib import sha256
from typing import Any

__all__ = ["assert_layout_equal"]


def assert_layout_equal(actual: dict, expected: dict, *, label: str | None = None, max_diffs: int = 5) -> None:
    """Compare two layout dictionaries without dumping megabytes of JSON."""
    if actual == expected:
        return

    mismatches: list[str] = []
    for key in sorted(set(actual) | set(expected)):
        left = actual.get(key)
        right = expected.get(key)
        if left != right:
            mismatches.append(_describe_mismatch(key, left, right))
        if len(mismatches) >= max_diffs:
            break

    scope = f" for {label}" if label else ""
    summary = "; ".join(mismatches) if mismatches else "unexpected structural mismatch"
    msg = f"Layout mismatch{scope}: {summary}. Run `just regen` to refresh releases or inspect the generated JSON."
    raise AssertionError(
        msg,
    )


def _describe_mismatch(key: str, actual: Any, expected: Any) -> str:
    if actual is None and expected is None:
        return f"{key} differs (both None)"

    if isinstance(actual, list) and isinstance(expected, list):
        seq_msg = _describe_sequence_difference(actual, expected)
        if seq_msg:
            return f"{key}: {seq_msg}"

    if isinstance(actual, dict) and isinstance(expected, dict):
        dict_msg = _describe_mapping_difference(actual, expected)
        if dict_msg:
            return f"{key}: {dict_msg}"

    return f"{key}: {_fingerprint(actual)} vs {_fingerprint(expected)}"


def _describe_sequence_difference(left: list[Any], right: list[Any]) -> str | None:
    if len(left) != len(right):
        return f"length {len(left)} != {len(right)}"
    for idx, (l_entry, r_entry) in enumerate(zip(left, right, strict=False)):
        if l_entry != r_entry:
            return f"index {idx} {_short_repr(l_entry)} != {_short_repr(r_entry)}"
    return None


def _describe_mapping_difference(left: dict[str, Any], right: dict[str, Any]) -> str | None:
    missing = sorted(set(right) - set(left))
    if missing:
        return f"missing keys {missing[:3]}"
    extra = sorted(set(left) - set(right))
    if extra:
        return f"unexpected keys {extra[:3]}"
    for key in sorted(left):
        if left[key] != right.get(key):
            return f"key '{key}' {_short_repr(left[key])} != {_short_repr(right.get(key))}"
    return None


def _fingerprint(value: Any) -> str:
    try:
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    except (TypeError, ValueError):  # pragma: no cover - diagnostic fallback
        return _short_repr(value)
    digest = sha256(encoded).hexdigest()[:8]
    return f"digest={digest} {_summary(value)}"


def _summary(value: Any) -> str:
    if isinstance(value, list):
        return f"list(len={len(value)})"
    if isinstance(value, dict):
        return f"dict(keys={len(value)})"
    return _short_repr(value)


def _short_repr(value: Any, limit: int = 80) -> str:
    text = repr(value)
    if len(text) > limit:
        return text[: limit - 3] + "..."
    return text
