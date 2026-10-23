"""Depot PostgreSQL de la demande, de la clarification et du suivi (MS-2)."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Connection, text

from agent.platform.api import new_uuid7
from agent.requests.core.models import (
    Clarification,
    FeasibilityPart,
    FeasibilityReport,
    RequestView,
    SplitProposal,
    TrackingItem,
)


def _iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(UTC).isoformat(timespec="microseconds")


def _request(row: Any) -> RequestView:
    return RequestView(
        id=row["id"],
        workspace_id=row["workspace_id"],
        author_id=row["author_id"],
        original_text=str(row["original_text"]),
        deliverable_type=row["deliverable_type"],
        target_format=row["target_format"],
        state=str(row["state"]),
        diagnostic_only=bool(row["diagnostic_only"]),
        created_at=_iso(row["created_at"]) or "",
    )


def insert_request(
    connection: Connection,
    *,
    workspace_id: UUID,
    author_id: UUID,
    text_value: str,
    deliverable_type: str | None,
    target_format: str | None,
    diagnostic_only: bool,
    at: datetime,
) -> RequestView:
    request_id = new_uuid7()
    connection.execute(
        text(
            """
            INSERT INTO requests
              (id, workspace_id, author_id, original_text, deliverable_type,
               target_format, diagnostic_only, state, created_at)
            VALUES
              (:id, :workspace_id, :author_id, :text_value, :deliverable_type,
               :target_format, :diagnostic_only, 'received', :at)
            """
        ),
        {
            "id": request_id,
            "workspace_id": workspace_id,
            "author_id": author_id,
            "text_value": text_value,
            "deliverable_type": deliverable_type,
            "target_format": target_format,
            "diagnostic_only": diagnostic_only,
            "at": at,
        },
    )
    row = (
        connection.execute(text("SELECT * FROM requests WHERE id = :id"), {"id": request_id})
        .mappings()
        .one()
    )
    return _request(row)


def get_request(connection: Connection, workspace_id: UUID, request_id: UUID) -> RequestView | None:
    row = (
        connection.execute(
            text("SELECT * FROM requests WHERE id = :id AND workspace_id = :workspace_id"),
            {"id": request_id, "workspace_id": workspace_id},
        )
        .mappings()
        .first()
    )
    return _request(row) if row is not None else None


def insert_analysis(
    connection: Connection,
    *,
    workspace_id: UUID,
    request_id: UUID,
    payload: dict[str, Any],
    at: datetime,
) -> None:
    connection.execute(
        text(
            """
            INSERT INTO request_analyses (id, workspace_id, request_id, payload, created_at)
            VALUES (:id, :workspace_id, :request_id, CAST(:payload AS jsonb), :at)
            """
        ),
        {
            "id": new_uuid7(),
            "workspace_id": workspace_id,
            "request_id": request_id,
            "payload": json.dumps(payload, ensure_ascii=False),
            "at": at,
        },
    )


def insert_parameter(
    connection: Connection,
    *,
    workspace_id: UUID,
    request_id: UUID,
    name: str,
    value: str,
    justification_quote: str,
    source: str,
    quality_status: str,
    at: datetime,
) -> None:
    connection.execute(
        text(
            """
            INSERT INTO request_parameters
              (id, workspace_id, request_id, name, value, justification_quote,
               source, quality_status, created_at)
            VALUES
              (:id, :workspace_id, :request_id, :name, :value, :quote,
               :source, CAST(:quality AS qi_status), :at)
            ON CONFLICT (request_id, name) DO NOTHING
            """
        ),
        {
            "id": new_uuid7(),
            "workspace_id": workspace_id,
            "request_id": request_id,
            "name": name,
            "value": value,
            "quote": justification_quote,
            "source": source,
            "quality": quality_status,
            "at": at,
        },
    )


def insert_clarification(
    connection: Connection,
    *,
    workspace_id: UUID,
    request_id: UUID,
    parameter: str,
    question_text: str,
    why_needed: str,
    blocking: bool,
    at: datetime,
) -> Clarification:
    clarification_id = new_uuid7()
    connection.execute(
        text(
            """
            INSERT INTO clarifications
              (id, workspace_id, request_id, parameter, question_text, why_needed,
               blocking, status, created_at)
            VALUES
              (:id, :workspace_id, :request_id, :parameter, :question_text, :why_needed,
               :blocking, 'open', :at)
            """
        ),
        {
            "id": clarification_id,
            "workspace_id": workspace_id,
            "request_id": request_id,
            "parameter": parameter,
            "question_text": question_text,
            "why_needed": why_needed,
            "blocking": blocking,
            "at": at,
        },
    )
    return Clarification(
        id=clarification_id,
        parameter=parameter,
        question_text=question_text,
        why_needed=why_needed,
        blocking=blocking,
        status="open",
    )


def list_clarifications(
    connection: Connection, workspace_id: UUID, request_id: UUID
) -> tuple[Clarification, ...]:
    rows = connection.execute(
        text(
            """
            SELECT id, parameter, question_text, why_needed, blocking, status, answer
              FROM clarifications
             WHERE workspace_id = :workspace_id AND request_id = :request_id
             ORDER BY blocking DESC, created_at
            """
        ),
        {"workspace_id": workspace_id, "request_id": request_id},
    ).mappings()
    return tuple(
        Clarification(
            id=row["id"],
            parameter=str(row["parameter"]),
            question_text=str(row["question_text"]),
            why_needed=str(row["why_needed"]),
            blocking=bool(row["blocking"]),
            status=str(row["status"]),
            answer=row["answer"],
        )
        for row in rows
    )


def answer_clarification(
    connection: Connection,
    *,
    workspace_id: UUID,
    clarification_id: UUID,
    answer: str,
    at: datetime,
) -> None:
    connection.execute(
        text(
            """
            UPDATE clarifications
               SET status = 'answered', answer = :answer, answered_at = :at
             WHERE id = :id AND workspace_id = :workspace_id
            """
        ),
        {"answer": answer, "at": at, "id": clarification_id, "workspace_id": workspace_id},
    )


def insert_message(
    connection: Connection,
    *,
    workspace_id: UUID,
    request_id: UUID,
    role: str,
    template_key: str,
    text_value: str,
    at: datetime,
) -> None:
    connection.execute(
        text(
            """
            INSERT INTO conversation_messages
              (id, workspace_id, request_id, role, template_key, text, created_at)
            VALUES (:id, :workspace_id, :request_id, :role, :template_key, :text_value, :at)
            """
        ),
        {
            "id": new_uuid7(),
            "workspace_id": workspace_id,
            "request_id": request_id,
            "role": role,
            "template_key": template_key,
            "text_value": text_value,
            "at": at,
        },
    )


def list_messages(
    connection: Connection, workspace_id: UUID, request_id: UUID
) -> tuple[dict[str, Any], ...]:
    rows = connection.execute(
        text(
            """
            SELECT id, role, template_key, text, created_at
              FROM conversation_messages
             WHERE workspace_id = :workspace_id AND request_id = :request_id
             ORDER BY created_at
            """
        ),
        {"workspace_id": workspace_id, "request_id": request_id},
    ).mappings()
    return tuple(
        {
            "id": str(row["id"]),
            "role": str(row["role"]),
            "template_key": str(row["template_key"]),
            "text": str(row["text"]),
            "created_at": _iso(row["created_at"]),
        }
        for row in rows
    )


def insert_report(
    connection: Connection,
    *,
    workspace_id: UUID,
    request_id: UUID,
    outcome: str,
    parts: tuple[FeasibilityPart, ...],
    pinned_version_ids: tuple[UUID, ...],
    at: datetime,
) -> FeasibilityReport:
    report_id = new_uuid7()
    payload = {
        "parts": [
            {
                "dimension": part.dimension,
                "verdict": part.verdict,
                "reason_code": part.reason_code,
                "reason_public": part.reason_public,
                "reason_internal": part.reason_internal,
            }
            for part in parts
        ],
        "pinned_version_ids": [str(item) for item in pinned_version_ids],
    }
    connection.execute(
        text(
            """
            INSERT INTO feasibility_reports
              (id, workspace_id, request_id, payload, outcome, created_at)
            VALUES (:id, :workspace_id, :request_id, CAST(:payload AS jsonb), :outcome, :at)
            """
        ),
        {
            "id": report_id,
            "workspace_id": workspace_id,
            "request_id": request_id,
            "payload": json.dumps(payload, ensure_ascii=False),
            "outcome": outcome,
            "at": at,
        },
    )
    return FeasibilityReport(
        id=report_id,
        request_id=request_id,
        outcome=outcome,
        parts=parts,
        pinned_version_ids=pinned_version_ids,
    )


def latest_report(
    connection: Connection, workspace_id: UUID, request_id: UUID
) -> FeasibilityReport | None:
    row = (
        connection.execute(
            text(
                """
            SELECT id, request_id, payload, outcome
              FROM feasibility_reports
             WHERE workspace_id = :workspace_id AND request_id = :request_id
             ORDER BY created_at DESC
             LIMIT 1
            """
            ),
            {"workspace_id": workspace_id, "request_id": request_id},
        )
        .mappings()
        .first()
    )
    if row is None:
        return None
    payload = dict(row["payload"])
    parts = tuple(
        FeasibilityPart(
            dimension=str(item["dimension"]),
            verdict=str(item["verdict"]),
            reason_code=str(item["reason_code"]),
            reason_public=str(item["reason_public"]),
            reason_internal=str(item["reason_internal"]),
        )
        for item in payload.get("parts", [])
    )
    return FeasibilityReport(
        id=row["id"],
        request_id=row["request_id"],
        outcome=str(row["outcome"]),
        parts=parts,
        pinned_version_ids=tuple(UUID(str(item)) for item in payload.get("pinned_version_ids", [])),
    )


def insert_split(
    connection: Connection,
    *,
    workspace_id: UUID,
    author_id: UUID,
    original_text: str,
    parts: tuple[str, ...],
    at: datetime,
) -> SplitProposal:
    split_id = new_uuid7()
    connection.execute(
        text(
            """
            INSERT INTO split_proposals
              (id, workspace_id, author_id, original_text, parts, status, created_at)
            VALUES (:id, :workspace_id, :author_id, :original_text, CAST(:parts AS jsonb),
                    'proposed', :at)
            """
        ),
        {
            "id": split_id,
            "workspace_id": workspace_id,
            "author_id": author_id,
            "original_text": original_text,
            "parts": json.dumps(list(parts), ensure_ascii=False),
            "at": at,
        },
    )
    return SplitProposal(id=split_id, original_text=original_text, parts=parts, status="proposed")


def get_split(connection: Connection, workspace_id: UUID, split_id: UUID) -> SplitProposal | None:
    row = (
        connection.execute(
            text(
                "SELECT id, original_text, parts, status FROM split_proposals "
                "WHERE id = :id AND workspace_id = :workspace_id"
            ),
            {"id": split_id, "workspace_id": workspace_id},
        )
        .mappings()
        .first()
    )
    if row is None:
        return None
    return SplitProposal(
        id=row["id"],
        original_text=str(row["original_text"]),
        parts=tuple(str(item) for item in row["parts"]),
        status=str(row["status"]),
    )


def confirm_split(connection: Connection, workspace_id: UUID, split_id: UUID, at: datetime) -> None:
    connection.execute(
        text(
            "UPDATE split_proposals SET status = 'confirmed' "
            "WHERE id = :id AND workspace_id = :workspace_id"
        ),
        {"id": split_id, "workspace_id": workspace_id, "at": at},
    )


def insert_item(
    connection: Connection,
    *,
    workspace_id: UUID,
    request_id: UUID,
    item_key: str,
    label: str,
    state: str,
    at: datetime,
) -> None:
    connection.execute(
        text(
            """
            INSERT INTO request_items
              (id, workspace_id, request_id, item_key, label, state, created_at)
            VALUES (:id, :workspace_id, :request_id, :item_key, :label, :state, :at)
            ON CONFLICT (request_id, item_key) DO NOTHING
            """
        ),
        {
            "id": new_uuid7(),
            "workspace_id": workspace_id,
            "request_id": request_id,
            "item_key": item_key,
            "label": label,
            "state": state,
            "at": at,
        },
    )


def list_items(
    connection: Connection, workspace_id: UUID, request_id: UUID
) -> tuple[TrackingItem, ...]:
    rows = connection.execute(
        text(
            "SELECT item_key, label, state FROM request_items "
            "WHERE workspace_id = :workspace_id AND request_id = :request_id ORDER BY created_at"
        ),
        {"workspace_id": workspace_id, "request_id": request_id},
    ).mappings()
    return tuple(
        TrackingItem(
            item_key=str(row["item_key"]), label=str(row["label"]), state=str(row["state"])
        )
        for row in rows
    )
