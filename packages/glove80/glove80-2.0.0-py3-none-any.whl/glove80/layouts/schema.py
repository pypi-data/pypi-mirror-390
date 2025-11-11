"""Pydantic models for layout sections (incremental migration).

This module will gradually host strongly-typed models that mirror the JSON
shapes emitted by the builder. We introduce them model-by-model to keep
changes reviewable and tests green between commits.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, AliasChoices

from glove80.base import LayerRef


class Macro(BaseModel):
    """Macro section entry.

    Matches the structure produced by MacroSpec.to_dict() today.
    Unknown keys are forbidden; field aliases match the JSON casing.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    description: Optional[str] = None
    bindings: List[Any]
    params: List[str] = Field(default_factory=list)
    waitMs: Optional[int] = Field(default=None, validation_alias=AliasChoices("waitMs", "wait_ms"))
    tapMs: Optional[int] = Field(default=None, validation_alias=AliasChoices("tapMs", "tap_ms"))

    @field_validator("name")
    @classmethod
    def _validate_name(cls, v: str) -> str:
        if not v or not v.startswith("&"):
            raise ValueError("macro name must start with '&'")
        return v

    @field_validator("bindings", mode="before")
    @classmethod
    def _validate_bindings(cls, v: Any) -> List[Any]:
        from glove80.base import KeySpec  # lazy import to avoid cycles

        if isinstance(v, list) or isinstance(v, tuple):
            out: List[Any] = []
            for item in v:
                if isinstance(item, KeySpec):
                    out.append(item.to_dict())
                else:
                    out.append(item)
            if not out:
                raise ValueError("bindings must be non-empty")
            return out
        # If it's already a list-like, accept it as-is; Pydantic will validate later.
        from typing import cast

        return cast(List[Any], v)


class HoldTap(BaseModel):
    """Hold-tap behavior entry."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    description: Optional[str] = None
    bindings: List[str]
    tappingTermMs: Optional[int] = Field(
        default=None, validation_alias=AliasChoices("tappingTermMs", "tapping_term_ms")
    )
    flavor: Optional[Literal["balanced", "tap-preferred", "hold-preferred"]] = None
    quickTapMs: Optional[int] = Field(default=None, validation_alias=AliasChoices("quickTapMs", "quick_tap_ms"))
    requirePriorIdleMs: Optional[int] = Field(
        default=None, validation_alias=AliasChoices("requirePriorIdleMs", "require_prior_idle_ms")
    )
    holdTriggerOnRelease: Optional[bool] = Field(
        default=None, validation_alias=AliasChoices("holdTriggerOnRelease", "hold_trigger_on_release")
    )
    holdTriggerKeyPositions: Optional[List[int]] = Field(
        default=None, validation_alias=AliasChoices("holdTriggerKeyPositions", "hold_trigger_key_positions")
    )

    @classmethod
    def model_validate(cls, obj: Any, *args: Any, **kwargs: Any) -> "HoldTap":
        inst = super().model_validate(obj, *args, **kwargs)
        d = inst.model_dump()
        for k in ("tappingTermMs", "quickTapMs", "requirePriorIdleMs"):
            if d.get(k) is not None and d[k] < 0:
                raise ValueError(f"{k} must be non-negative")
        if d.get("holdTriggerKeyPositions"):
            for pos in d["holdTriggerKeyPositions"]:
                if not (0 <= pos <= 79):
                    raise ValueError("holdTriggerKeyPositions must be within 0..79")
        return inst


__all__ = ["Macro", "HoldTap"]


class Combo(BaseModel):
    """Combo section entry."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    description: Optional[str] = None
    binding: Dict[str, Any]
    keyPositions: List[int]
    layers: List[Union[int, "LayerRef"]]
    timeoutMs: Optional[int] = None

    @field_validator("binding", mode="before")
    @classmethod
    def _coerce_binding(cls, v: Any) -> Any:
        try:
            from glove80.base import KeySpec
        except Exception:
            KeySpec = None  # type: ignore
        if KeySpec is not None and isinstance(v, KeySpec):
            return v.to_dict()
        return v

    @field_validator("keyPositions")
    @classmethod
    def _validate_key_positions(cls, v: List[int]) -> List[int]:
        for pos in v:
            if not (0 <= pos <= 79):
                raise ValueError("keyPositions must be within 0..79")
        if not v:
            raise ValueError("keyPositions cannot be empty")
        return v


__all__.append("Combo")


class InputProcessor(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    params: List[Any] = Field(default_factory=list)

    @field_validator("code")
    @classmethod
    def _validate_code(cls, v: str) -> str:
        if not v:
            raise ValueError("processor code must be non-empty")
        return v


class ListenerNode(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    layers: List[Union[int, LayerRef]]
    description: Optional[str] = None
    inputProcessors: List[InputProcessor] = Field(default_factory=list)

    @classmethod
    def model_validate(cls, obj: Any, *args: Any, **kwargs: Any) -> "ListenerNode":
        inst = super().model_validate(obj, *args, **kwargs)
        if not inst.layers:
            raise ValueError("listener node layers cannot be empty")
        return inst


class InputListener(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    inputProcessors: List[InputProcessor] = Field(default_factory=list)
    nodes: List[ListenerNode]


__all__ += ["InputProcessor", "ListenerNode", "InputListener"]


class CommonFields(BaseModel):
    """Top-level, shared fields merged into every layout payload.

    We validate known keys while allowing extras so families can inject
    additional metadata (e.g., `creator`) without breaking validation.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    keyboard: str
    firmware_api_version: str
    locale: str
    unlisted: bool
    custom_defined_behaviors: str
    custom_devicetree: str
    config_parameters: List[Dict[str, Any]]
    layout_parameters: Dict[str, Any]
    creator: Optional[str] = None


__all__.append("CommonFields")


class LayoutPayload(BaseModel):
    """Top-level layout payload shape.

    Sections are fully typed (Macro/HoldTap/Combo/InputListener). We still
    serialize with aliases for byte-identical JSON artifacts.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    # Common fields
    keyboard: str
    firmware_api_version: str
    locale: str
    unlisted: bool
    custom_defined_behaviors: str
    custom_devicetree: str
    config_parameters: List[Dict[str, Any]]
    layout_parameters: Dict[str, Any]
    creator: Optional[str] = None

    # Sections
    layer_names: List[str]
    macros: List[Macro]
    holdTaps: List[HoldTap]
    combos: List[Combo]
    inputListeners: List[InputListener]
    layers: List[List[Dict[str, Any]]]

    # Attached metadata (optional)
    title: Optional[str] = None
    uuid: Optional[str] = None
    parent_uuid: Optional[str] = None
    date: Optional[Any] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None

    @classmethod
    def model_validate(cls, obj: Any, *args: Any, **kwargs: Any) -> "LayoutPayload":
        inst = super().model_validate(obj, *args, **kwargs)
        # Length checks
        if len(inst.layer_names) != len(inst.layers):
            raise ValueError("layers length must match layer_names length")
        # Verify each layer has 80 entries
        for layer in inst.layers:
            if len(layer) != 80:
                raise ValueError("each layer must have exactly 80 key entries")
        return inst


__all__.append("LayoutPayload")
