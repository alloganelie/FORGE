"""Depot PostgreSQL de la gouvernance (ET-053, ET-057 a ET-060)."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Connection, text

from agent.governance.core.types import (
    ArtifactStatus,
    ArtifactType,
    ArtifactVersion,
    InvalidTransition,
    Pin,
)
from agent.ledger.api import append_event
from agent.platform.api import new_uuid7


def _iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(UTC).isoformat(timespec="microseconds")


def _version_from_row(row: Any) -> ArtifactVersion:
    return ArtifactVersion(
        id=row["id"],
        workspace_id=row["workspace_id"],
        artifact_type=ArtifactType(str(row["artifact_type"])),
        artifact_key=str(row["artifact_key"]),
        version=int(row["version"]),
        content=dict(row["content"]),
        content_hash=str(row["content_hash"]),
        status=ArtifactStatus(str(row["status"])),
        effective_from=_iso(row["effective_from"]),
        created_by=row["created_by"],
        created_at=_iso(row["created_at"]) or "",
        approved_at=_iso(row["approved_at"]),
        approved_by_decision=row["approved_by_decision"],
        schema_version=str(row["schema_version"]),
        motif=str(row["motif"]),
    )


def get_user(connection: Connection, workspace_id: UUID, user_id: UUID) -> dict[str, Any] | None:
    row = (
        connection.execute(
            text(
                """
            SELECT id, display_name, role
              FROM users
             WHERE id = :user_id AND workspace_id = :workspace_id AND active
            """
            ),
            {"user_id": user_id, "workspace_id": workspace_id},
        )
        .mappings()
        .first()
    )
    return dict(row) if row is not None else None


def list_users(connection: Connection, workspace_id: UUID) -> tuple[dict[str, Any], ...]:
    rows = connection.execute(
        text(
            """
            SELECT id, display_name, role, active
              FROM users
             WHERE workspace_id = :workspace_id
             ORDER BY role, display_name
            """
        ),
        {"workspace_id": workspace_id},
    ).mappings()
    return tuple(dict(row) for row in rows)


def get_version(
    connection: Connection, workspace_id: UUID, version_id: UUID
) -> ArtifactVersion | None:
    row = (
        connection.execute(
            text(
                """
            SELECT id, workspace_id, artifact_type, artifact_key, version, content,
                   content_hash, schema_version, status, effective_from,
                   approved_by_decision, created_by, created_at, approved_at, retired_at, motif
              FROM governance_artifact_versions
             WHERE id = :version_id AND workspace_id = :workspace_id
            """
            ),
            {"version_id": version_id, "workspace_id": workspace_id},
        )
        .mappings()
        .first()
    )
    return _version_from_row(row) if row is not None else None


def list_versions(
    connection: Connection, workspace_id: UUID, *, status: ArtifactStatus | None = None
) -> tuple[ArtifactVersion, ...]:
    query = """
        SELECT id, workspace_id, artifact_type, artifact_key, version, content,
               content_hash, schema_version, status, effective_from,
               approved_by_decision, created_by, created_at, approved_at, retired_at, motif
          FROM governance_artifact_versions
         WHERE workspace_id = :workspace_id
    """
    parameters: dict[str, Any] = {"workspace_id": workspace_id}
    if status is not None:
        query += " AND status = :status"
        parameters["status"] = status.value
    query += " ORDER BY artifact_type, artifact_key, version"
    return tuple(
        _version_from_row(row) for row in connection.execute(text(query), parameters).mappings()
    )


def insert_draft(
    connection: Connection,
    *,
    workspace_id: UUID,
    artifact_type: ArtifactType,
    artifact_key: str,
    content: dict[str, Any],
    content_hash: str,
    created_by: UUID,
    created_at: datetime,
    motif: str,
    schema_version: str = "v1",
) -> ArtifactVersion:
    next_version: int = int(
        connection.execute(
            text(
                """
            SELECT COALESCE(MAX(version), 0) + 1
              FROM governance_artifact_versions
             WHERE workspace_id = :workspace_id
               AND artifact_type = :artifact_type
               AND artifact_key = :artifact_key
            """
            ),
            {
                "workspace_id": workspace_id,
                "artifact_type": artifact_type.value,
                "artifact_key": artifact_key,
            },
        ).scalar_one()
    )
    version_id = new_uuid7()
    connection.execute(
        text(
            """
            INSERT INTO governance_artifact_versions
              (id, workspace_id, artifact_type, artifact_key, version, content,
               content_hash, schema_version, status, created_by, created_at, motif)
            VALUES
              (:id, :workspace_id, :artifact_type, :artifact_key, :version,
               CAST(:content AS jsonb), :content_hash, :schema_version, 'draft',
               :created_by, :created_at, :motif)
            """
        ),
        {
            "id": version_id,
            "workspace_id": workspace_id,
            "artifact_type": artifact_type.value,
            "artifact_key": artifact_key,
            "version": int(next_version),
            "content": json.dumps(content, ensure_ascii=False),
            "content_hash": content_hash,
            "schema_version": schema_version,
            "created_by": created_by,
            "created_at": created_at,
            "motif": motif,
        },
    )
    version = get_version(connection, workspace_id, version_id)
    if version is None:
        raise RuntimeError("version de gouvernance non relue apres insertion")
    return version


def approve_version(
    connection: Connection,
    *,
    workspace_id: UUID,
    version_id: UUID,
    actor_id: UUID,
    effective_from: datetime,
    reason: str,
    approved_at: datetime,
) -> ArtifactVersion:
    row = (
        connection.execute(
            text(
                """
            SELECT status, artifact_type, artifact_key, version, content_hash
              FROM governance_artifact_versions
             WHERE id = :version_id AND workspace_id = :workspace_id
             FOR UPDATE
            """
            ),
            {"version_id": version_id, "workspace_id": workspace_id},
        )
        .mappings()
        .first()
    )
    if row is None:
        raise InvalidTransition("Version de gouvernance introuvable.")
    if ArtifactStatus(str(row["status"])) is not ArtifactStatus.DRAFT:
        raise InvalidTransition("Seul un brouillon peut etre approuve.")

    decision_id = new_uuid7()
    connection.execute(
        text(
            """
            INSERT INTO decisions
              (id, workspace_id, request_id, type, object_type, object_id,
               decider_id, outcome, reason, scope, decided_at)
            VALUES
              (:id, :workspace_id, NULL, 'rule_change', 'governance_artifact_version',
               :object_id, :decider_id, 'approved', :reason, CAST(:scope AS jsonb), :decided_at)
            """
        ),
        {
            "id": decision_id,
            "workspace_id": workspace_id,
            "object_id": version_id,
            "decider_id": actor_id,
            "reason": reason,
            "scope": json.dumps(
                {
                    "artifact_type": str(row["artifact_type"]),
                    "artifact_key": str(row["artifact_key"]),
                    "version": int(row["version"]),
                    "content_hash": str(row["content_hash"]),
                }
            ),
            "decided_at": approved_at,
        },
    )

    connection.execute(
        text(
            """
            UPDATE governance_artifact_versions
               SET status = 'approved',
                   effective_from = :effective_from,
                   approved_by_decision = :decision_id,
                   approved_at = :approved_at
             WHERE id = :version_id
            """
        ),
        {
            "effective_from": effective_from,
            "decision_id": decision_id,
            "approved_at": approved_at,
            "version_id": version_id,
        },
    )
    connection.execute(
        text(
            """
            UPDATE governance_artifact_versions
               SET status = 'retired', retired_at = :approved_at
             WHERE workspace_id = :workspace_id
               AND artifact_type = :artifact_type
               AND artifact_key = :artifact_key
               AND status = 'approved'
               AND id <> :version_id
            """
        ),
        {
            "approved_at": approved_at,
            "workspace_id": workspace_id,
            "artifact_type": str(row["artifact_type"]),
            "artifact_key": str(row["artifact_key"]),
            "version_id": version_id,
        },
    )
    append_event(
        connection,
        workspace_id=workspace_id,
        request_id=None,
        event_type="GovernanceArtifactApproved",
        payload={
            "version_id": str(version_id),
            "artifact_type": str(row["artifact_type"]),
            "artifact_key": str(row["artifact_key"]),
            "version": int(row["version"]),
            "content_hash": str(row["content_hash"]),
            "decision_id": str(decision_id),
        },
        actor_type="human",
        actor_id=actor_id,
        at=approved_at,
    )
    version = get_version(connection, workspace_id, version_id)
    if version is None:
        raise RuntimeError("version approuvee non relue")
    return version


def insert_pin(
    connection: Connection,
    *,
    workspace_id: UUID,
    request_id: UUID,
    version_id: UUID,
    pinned_by: UUID,
    pinned_at: datetime,
) -> None:
    connection.execute(
        text(
            """
            INSERT INTO request_pins
              (request_id, version_id, workspace_id, pinned_by, pinned_at)
            VALUES (:request_id, :version_id, :workspace_id, :pinned_by, :pinned_at)
            ON CONFLICT (request_id, version_id) DO NOTHING
            """
        ),
        {
            "request_id": request_id,
            "version_id": version_id,
            "workspace_id": workspace_id,
            "pinned_by": pinned_by,
            "pinned_at": pinned_at,
        },
    )


def list_pins(connection: Connection, workspace_id: UUID, request_id: UUID) -> tuple[Pin, ...]:
    rows = connection.execute(
        text(
            """
            SELECT request_id, version_id, pinned_at, pinned_by
              FROM request_pins
             WHERE workspace_id = :workspace_id AND request_id = :request_id
             ORDER BY pinned_at, version_id
            """
        ),
        {"workspace_id": workspace_id, "request_id": request_id},
    ).mappings()
    return tuple(
        Pin(
            request_id=row["request_id"],
            version_id=row["version_id"],
            pinned_at=_iso(row["pinned_at"]) or "",
            pinned_by=row["pinned_by"],
        )
        for row in rows
    )


def count_pins_for_version(connection: Connection, version_id: UUID) -> int:
    return int(
        connection.execute(
            text("SELECT COUNT(*) FROM request_pins WHERE version_id = :version_id"),
            {"version_id": version_id},
        ).scalar_one()
    )


def requests_pinned_to(connection: Connection, version_id: UUID) -> tuple[UUID, ...]:
    rows: list[UUID] = list(
        connection.execute(
            text(
                "SELECT request_id FROM request_pins "
                "WHERE version_id = :version_id ORDER BY request_id"
            ),
            {"version_id": version_id},
        ).scalars()
    )
    return tuple(rows)


def insert_observations(
    connection: Connection,
    *,
    workspace_id: UUID,
    version_id: UUID,
    observations: tuple[Any, ...],
    at: datetime,
) -> None:
    for observation in observations:
        connection.execute(
            text(
                """
                INSERT INTO governance_observations
                  (id, workspace_id, artifact_version_id, code, message, rule_id,
                   example_id, created_at)
                VALUES
                  (:id, :workspace_id, :version_id, :code, :message, :rule_id,
                   :example_id, :at)
                """
            ),
            {
                "id": new_uuid7(),
                "workspace_id": workspace_id,
                "version_id": version_id,
                "code": observation.code,
                "message": observation.message,
                "rule_id": observation.rule_id or None,
                "example_id": observation.example_id or None,
                "at": at,
            },
        )
