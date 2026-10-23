"""Modeles purs de la demande et du suivi (MS-2)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


class RequestDenied(RuntimeError):
    """Demande refusee : l'utilisateur n'est pas autorise (RF-009, RB-064)."""


@dataclass(frozen=True, slots=True)
class RequestView:
    id: UUID
    workspace_id: UUID
    author_id: UUID
    original_text: str
    deliverable_type: str | None
    target_format: str | None
    state: str
    diagnostic_only: bool
    created_at: str


@dataclass(frozen=True, slots=True)
class Clarification:
    id: UUID
    parameter: str
    question_text: str
    why_needed: str
    blocking: bool
    status: str
    answer: str | None = None


@dataclass(frozen=True, slots=True)
class SplitProposal:
    id: UUID
    original_text: str
    parts: tuple[str, ...]
    status: str


@dataclass(frozen=True, slots=True)
class Submission:
    request: RequestView | None
    split: SplitProposal | None
    questions: tuple[Clarification, ...] = ()
    analysis: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class FeasibilityPart:
    dimension: str
    verdict: str
    reason_code: str
    reason_public: str
    reason_internal: str


@dataclass(frozen=True, slots=True)
class FeasibilityReport:
    id: UUID
    request_id: UUID
    outcome: str
    parts: tuple[FeasibilityPart, ...]
    pinned_version_ids: tuple[UUID, ...]

    def reason_for(self, responsible: bool) -> str:
        blocked = [part for part in self.parts if part.verdict in {"blocked", "suspended"}]
        if not blocked:
            return "La demande est realisable."
        part = blocked[0]
        return part.reason_internal if responsible else part.reason_public


@dataclass(frozen=True, slots=True)
class TrackingItem:
    item_key: str
    label: str
    state: str


@dataclass(frozen=True, slots=True)
class StatusSnapshot:
    request_id: UUID
    request_state: str
    request_label: str
    steps_done: tuple[str, ...]
    current_step: str
    reasons: tuple[str, ...]
    expected: tuple[str, ...]
    next_action: str
    statuses: dict[str, str]
    items: tuple[TrackingItem, ...]
    message: str
    provisional: bool = True
