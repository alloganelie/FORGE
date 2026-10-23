"""Types et erreurs typées de la passerelle LLM (LG-04, ET-252)."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class LlmTask(StrEnum):
    LT_01 = "LT-01"
    LT_02 = "LT-02"
    LT_10 = "LT-10"


class LlmFailure(StrEnum):
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    REFUSAL = "refusal"
    TRUNCATED = "truncated"
    INVALID_OUTPUT = "invalid_output"
    BUDGET_EXCEEDED = "budget_exceeded"
    FIXTURE_MISSING = "fixture_missing"


class LlmError(RuntimeError):
    """Echec typé : un refus ou une sortie invalide n'est jamais un succès."""

    def __init__(self, failure: LlmFailure, detail: str = "") -> None:
        super().__init__(f"{failure.value}: {detail}" if detail else failure.value)
        self.failure = failure


@dataclass(frozen=True, slots=True)
class LlmResponse:
    output: Mapping[str, Any]
    stop_reason: str = "stop"
    tokens_in: int = 0
    tokens_out: int = 0
    model: str = "replay"
    provider: str = "replay"


@dataclass(frozen=True, slots=True)
class LlmCallRecord:
    id: Any
    task_id: str
    validation_outcome: str
    stop_reason: str
