"""Ecriture et verification du journal en PostgreSQL (ET-022 a ET-026).

Toute ecriture passe par append_event : verrou de la demande, request_seq sans
trou, prev_hash du precedent, self_hash canonique, insertion atomique.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Connection, text

from agent.ledger.core.hashchain import (
    GENESIS_HASH,
    ChainVerification,
    LedgerRecord,
    compute_self_hash,
    verify_events,
)


@dataclass(frozen=True, slots=True)
class AppendedEvent:
    seq: int
    request_seq: int | None
    prev_hash: str
    self_hash: str


def _iso(value: datetime) -> str:
    if value.tzinfo is None:
        raise ValueError("horodatage du journal sans fuseau")
    return value.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _load_records(connection: Connection, workspace_id: UUID) -> tuple[LedgerRecord, ...]:
    rows = connection.execute(
        text(
            """
            SELECT seq, workspace_id, request_id, request_seq, event_type, payload,
                   actor_type, actor_id, at, prev_hash, self_hash
              FROM ledger_events
             WHERE workspace_id = :workspace_id
             ORDER BY seq
            """
        ),
        {"workspace_id": workspace_id},
    ).mappings()
    return tuple(
        LedgerRecord(
            seq=int(row["seq"]),
            workspace_id=row["workspace_id"],
            request_id=row["request_id"],
            request_seq=row["request_seq"],
            event_type=str(row["event_type"]),
            payload=dict(row["payload"]),
            actor_type=str(row["actor_type"]),
            actor_id=row["actor_id"],
            at=_iso(row["at"]),
            prev_hash=str(row["prev_hash"]),
            self_hash=str(row["self_hash"]),
        )
        for row in rows
    )


def append_event(
    connection: Connection,
    *,
    workspace_id: UUID,
    request_id: UUID | None,
    event_type: str,
    payload: dict[str, Any],
    actor_type: str,
    actor_id: UUID | None,
    at: datetime,
) -> AppendedEvent:
    """Ajoute un evenement chaine ; doit etre appele dans la transaction metier."""
    if at.tzinfo is None:
        raise ValueError("horodatage du journal sans fuseau")
    at = at.astimezone(UTC)
    request_seq: int | None = None
    prev_hash = GENESIS_HASH
    if request_id is not None:
        locked = connection.execute(
            text("SELECT id FROM requests WHERE id = :request_id FOR UPDATE"),
            {"request_id": request_id},
        ).first()
        if locked is None:
            raise ValueError("demande inconnue pour l'evenement de journal")
        last = connection.execute(
            text(
                """
                SELECT request_seq, self_hash
                  FROM ledger_events
                 WHERE request_id = :request_id
                 ORDER BY request_seq DESC
                 LIMIT 1
                """
            ),
            {"request_id": request_id},
        ).first()
        if last is None:
            request_seq, prev_hash = 1, GENESIS_HASH
        else:
            request_seq, prev_hash = int(last[0]) + 1, str(last[1])

    draft = LedgerRecord(
        seq=None,
        workspace_id=workspace_id,
        request_id=request_id,
        request_seq=request_seq,
        event_type=event_type,
        payload=payload,
        actor_type=actor_type,
        actor_id=actor_id,
        at=_iso(at),
        prev_hash=prev_hash,
        self_hash="",
    )
    self_hash = compute_self_hash(draft, prev_hash)
    row = connection.execute(
        text(
            """
            INSERT INTO ledger_events
              (workspace_id, request_id, request_seq, event_type, payload,
               actor_type, actor_id, at, prev_hash, self_hash)
            VALUES
              (:workspace_id, :request_id, :request_seq, :event_type, CAST(:payload AS jsonb),
               :actor_type, :actor_id, :at, :prev_hash, :self_hash)
            RETURNING seq
            """
        ),
        {
            "workspace_id": workspace_id,
            "request_id": request_id,
            "request_seq": request_seq,
            "event_type": event_type,
            "payload": json.dumps(payload, ensure_ascii=False),
            "actor_type": actor_type,
            "actor_id": actor_id,
            "at": at,
            "prev_hash": prev_hash,
            "self_hash": self_hash,
        },
    ).one()
    return AppendedEvent(
        seq=int(row[0]),
        request_seq=request_seq,
        prev_hash=prev_hash,
        self_hash=self_hash,
    )


def latest_suspension_event(connection: Connection, request_id: UUID) -> dict[str, Any] | None:
    """Dernier evenement TR-R-19 d'une demande (Q-002, ET-041).

    Le journal est la source de verite du champ suspended_from ; aucune autre
    table n'est interrogee pour reconstituer l'etat de suspension.
    """
    row = connection.execute(
        text(
            """
            SELECT payload
              FROM ledger_events
             WHERE request_id = :request_id
               AND event_type = 'StateTransitionApplied'
               AND payload->>'transition_id' = 'TR-R-19'
             ORDER BY request_seq DESC
             LIMIT 1
            """
        ),
        {"request_id": request_id},
    ).first()
    if row is None or not isinstance(row[0], dict):
        return None
    return dict(row[0])


def verify_chain(connection: Connection, workspace_id: UUID) -> ChainVerification:
    """Recalcule toute la chaine d'un espace de travail."""
    return verify_events(_load_records(connection, workspace_id))


def write_checkpoint(
    connection: Connection,
    *,
    workspace_id: UUID,
    checkpoint_id: UUID,
    at: datetime,
) -> ChainVerification:
    """Verifie la chaine et conserve une borne de controle (ET-025)."""
    result = verify_chain(connection, workspace_id)
    bounds = connection.execute(
        text("SELECT MIN(seq), MAX(seq) FROM ledger_events WHERE workspace_id = :workspace_id"),
        {"workspace_id": workspace_id},
    ).one()
    connection.execute(
        text(
            """
            INSERT INTO chain_checkpoints
              (id, workspace_id, checked_at, first_seq, last_seq, ok, detail)
            VALUES
              (:id, :workspace_id, :at, :first_seq, :last_seq, :ok, CAST(:detail AS jsonb))
            """
        ),
        {
            "id": checkpoint_id,
            "workspace_id": workspace_id,
            "at": at,
            "first_seq": bounds[0],
            "last_seq": bounds[1],
            "ok": result.ok,
            "detail": json.dumps({"errors": list(result.errors), "checked": result.checked}),
        },
    )
    return result
