"""Reusable spec dataclasses for macros, hold-taps, combos, and listeners."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Sequence

from ..base import KeySpec, LayerRef


def _serialize_simple(value: Any) -> Any:
    """Convert supported parameter types into JSON-friendly structures."""

    if isinstance(value, KeySpec):
        return value.to_dict()
    if isinstance(value, LayerRef):
        return value
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {k: _serialize_simple(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize_simple(item) for item in value]
    raise TypeError(f"Unsupported parameter type: {type(value)!r}")  # pragma: no cover


@dataclass(frozen=True)
class MacroSpec:
    """Structured representation of a macro definition."""

    name: str
    description: str
    bindings: Sequence[KeySpec]
    params: Sequence[str] = ()
    wait_ms: int | None = None
    tap_ms: int | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "name": self.name,
            "description": self.description,
            "bindings": [binding.to_dict() for binding in self.bindings],
            "params": list(self.params),
        }
        if self.wait_ms is not None:
            data["waitMs"] = self.wait_ms
        if self.tap_ms is not None:
            data["tapMs"] = self.tap_ms
        return data


@dataclass(frozen=True)
class HoldTapSpec:
    """Declarative hold-tap definition."""

    name: str
    description: str
    bindings: Sequence[str]
    tapping_term_ms: int | None = None
    flavor: str | None = None
    quick_tap_ms: int | None = None
    require_prior_idle_ms: int | None = None
    hold_trigger_on_release: bool | None = None
    hold_trigger_key_positions: Sequence[int] | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "name": self.name,
            "description": self.description,
            "bindings": list(self.bindings),
        }
        if self.tapping_term_ms is not None:
            data["tappingTermMs"] = self.tapping_term_ms
        if self.flavor is not None:
            data["flavor"] = self.flavor
        if self.quick_tap_ms is not None:
            data["quickTapMs"] = self.quick_tap_ms
        if self.require_prior_idle_ms is not None:
            data["requirePriorIdleMs"] = self.require_prior_idle_ms
        if self.hold_trigger_on_release is not None:
            data["holdTriggerOnRelease"] = self.hold_trigger_on_release
        if self.hold_trigger_key_positions is not None:
            data["holdTriggerKeyPositions"] = list(self.hold_trigger_key_positions)
        return data


@dataclass(frozen=True)
class ComboSpec:
    """Combo definition for TailorKey/QuantumTouch layouts."""

    name: str
    description: str
    binding: KeySpec
    key_positions: Sequence[int]
    layers: Sequence[int | LayerRef]
    timeout_ms: int | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "name": self.name,
            "description": self.description,
            "binding": self.binding.to_dict(),
            "keyPositions": list(self.key_positions),
            "layers": list(self.layers),
        }
        if self.timeout_ms is not None:
            data["timeoutMs"] = self.timeout_ms
        return data


@dataclass(frozen=True)
class InputProcessorSpec:
    """Helper for mmv/msc processor blocks."""

    code: str
    params: Sequence[Any] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "params": [_serialize_simple(param) for param in self.params],
        }


@dataclass(frozen=True)
class InputListenerNodeSpec:
    """Single listener node (layer binding plus processors)."""

    code: str
    layers: Sequence[int | LayerRef]
    description: str | None = None
    input_processors: Sequence[InputProcessorSpec] = ()

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "code": self.code,
            "layers": list(self.layers),
            "inputProcessors": [proc.to_dict() for proc in self.input_processors],
        }
        if self.description is not None:
            data["description"] = self.description
        return data


@dataclass(frozen=True)
class InputListenerSpec:
    """Top-level listener consisting of multiple nodes."""

    code: str
    nodes: Sequence[InputListenerNodeSpec]
    input_processors: Sequence[InputProcessorSpec] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "inputProcessors": [proc.to_dict() for proc in self.input_processors],
            "nodes": [node.to_dict() for node in self.nodes],
        }


def materialize_sequence(items: Iterable[Any]) -> list[Any]:
    """Convert spec objects (with to_dict) into dictionaries."""

    result = []
    for item in items:
        if hasattr(item, "to_dict"):
            result.append(item.to_dict())
        else:
            result.append(item)
    return result
