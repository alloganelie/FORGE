"""Application transactionnelle des transitions (ET-023, ET-024, ET-037, ET-038).

Le domaine decide (fonctions pures) ; ce depot ecrit l'etat, la projection
state_changes et l'evenement de journal dans la meme transaction.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Connection, text

from agent.ledger.api import append_event, latest_suspension_event
from agent.lifecycle.core.engine import (
    InvalidTransition,
    MachineSet,
    ResumeTargetError,
    apply_transition,
)
from agent.lifecycle.core.guards import GuardContext
from agent.platform.api import new_uuid7


class TransitionRejected(RuntimeError):
    """Refus metier ou technique d'une transition."""

    def __init__(self, transition_id: str, reason_internal: str, reason_communicable: str) -> None:
        super().__init__(reason_communicable)
        self.transition_id = transition_id
        self.reason_internal = reason_internal
        self.reason_communicable = reason_communicable


class ConcurrencyConflict(RuntimeError):
    """row_version obsolete : conflit d'ecriture concurrente (ET-038)."""


@dataclass(frozen=True, slots=True)
class AppliedTransition:
    transition_id: str
    axis: str
    entity_id: UUID
    from_state: str | None
    to_state: str
    ledger_seq: int
    request_seq: int | None
    row_version: int


_ACTOR_TYPE = {"agent": "agent", "system": "system"}


def _actor_type(actor: str) -> str:
    return _ACTOR_TYPE.get(actor, "human")


def _set_transition(connection: Connection, transition_id: str) -> None:
    connection.execute(
        text("SELECT set_config('app.transition_id', :value, true)"),
        {"value": transition_id},
    )


def _write_state_change(
    connection: Connection,
    *,
    workspace_id: UUID,
    entity_type: str,
    entity_id: UUID,
    axis: str,
    from_state: str | None,
    to_state: str,
    transition_id: str,
    actor: str,
    actor_id: UUID | None,
    at: datetime,
    ledger_seq: int,
) -> None:
    connection.execute(
        text(
            """
            INSERT INTO state_changes
              (id, workspace_id, entity_type, entity_id, axis, from_state, to_state,
               transition_id, actor_type, actor_id, reason_internal, reason_communicable,
               at, ledger_seq)
            VALUES
              (:id, :workspace_id, :entity_type, :entity_id, :axis, :from_state, :to_state,
               :transition_id, :actor_type, :actor_id, NULL, NULL, :at, :ledger_seq)
            """
        ),
        {
            "id": new_uuid7(),
            "workspace_id": workspace_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "axis": axis,
            "from_state": from_state,
            "to_state": to_state,
            "transition_id": transition_id,
            "actor_type": _actor_type(actor),
            "actor_id": actor_id,
            "at": at,
            "ledger_seq": ledger_seq,
        },
    )


def apply_request_transition(
    connection: Connection,
    machines: MachineSet,
    *,
    request_id: UUID,
    transition_id: str,
    actor: str,
    actor_id: UUID | None,
    workspace_id: UUID,
    at: datetime,
    context: GuardContext,
    expected_row_version: int | None = None,
) -> AppliedTransition:
    """Applique une transition de l'axe R en une seule transaction."""
    if not transition_id.startswith("TR-R-"):
        raise ValueError("transition de demande attendue")
    _set_transition(connection, transition_id)
    row = (
        connection.execute(
            text(
                """
            SELECT state, waiting_origin, suspended_from, row_version
              FROM requests
             WHERE id = :request_id
             FOR UPDATE
            """
            ),
            {"request_id": request_id},
        )
        .mappings()
        .first()
    )
    if row is None:
        raise TransitionRejected(transition_id, "demande inconnue", "Element introuvable.")
    current = str(row["state"])
    if expected_row_version is not None and int(row["row_version"]) != expected_row_version:
        raise ConcurrencyConflict("row_version obsolete")

    effective_context = context
    if transition_id == "TR-R-20":
        suspension_event = latest_suspension_event(connection, request_id)
        suspended_value = (
            suspension_event.get("suspended_from") if suspension_event is not None else None
        )
        if not isinstance(suspended_value, str):
            raise TransitionRejected(
                transition_id,
                "evenement de suspension absent du journal",
                "La reprise n'est pas possible : l'evenement de suspension est introuvable.",
            )
        projected = row["suspended_from"]
        if projected is not None and str(projected) != suspended_value:
            raise TransitionRejected(
                transition_id,
                "projection suspended_from incoherente avec le journal",
                "La reprise n'est pas possible : l'etat de suspension est incoherent.",
            )
        effective_context = replace(context, suspension_event=suspension_event)

    try:
        target = apply_transition(
            machines.get("R"), current, transition_id, actor, effective_context
        )
    except InvalidTransition as exc:
        raise TransitionRejected(
            transition_id, exc.reason_internal, exc.reason_communicable
        ) from exc
    except ResumeTargetError as exc:
        raise TransitionRejected(
            transition_id,
            "etat de suspension invalide dans le journal",
            "La reprise n'est pas possible : l'etat de suspension est invalide.",
        ) from exc

    waiting_origin = row["waiting_origin"]
    suspended_from = row["suspended_from"]
    if target == "suspended":
        suspended_from = current
    elif transition_id == "TR-R-20":
        suspended_from = None
    if target in ("blocked", "awaiting_decision"):
        waiting_origin = current
    elif transition_id in ("TR-R-13", "TR-R-14", "TR-R-23", "TR-R-24", "TR-R-26"):
        waiting_origin = None

    updated = connection.execute(
        text(
            """
            UPDATE requests
               SET state = :state,
                   waiting_origin = :waiting_origin,
                   suspended_from = :suspended_from,
                   row_version = row_version + 1
             WHERE id = :request_id
         RETURNING row_version
            """
        ),
        {
            "state": target,
            "waiting_origin": waiting_origin,
            "suspended_from": suspended_from,
            "request_id": request_id,
        },
    ).one()

    payload: dict[str, Any] = {
        "transition_id": transition_id,
        "axis": "R",
        "entity_id": str(request_id),
        "from_state": current,
        "to_state": target,
        "actor": actor,
    }
    if transition_id == "TR-R-19":
        payload["suspended_from"] = current
    event = append_event(
        connection,
        workspace_id=workspace_id,
        request_id=request_id,
        event_type="StateTransitionApplied",
        payload=payload,
        actor_type=_actor_type(actor),
        actor_id=actor_id,
        at=at,
    )
    _write_state_change(
        connection,
        workspace_id=workspace_id,
        entity_type="request",
        entity_id=request_id,
        axis="R",
        from_state=current,
        to_state=target,
        transition_id=transition_id,
        actor=actor,
        actor_id=actor_id,
        at=at,
        ledger_seq=event.seq,
    )
    return AppliedTransition(
        transition_id=transition_id,
        axis="R",
        entity_id=request_id,
        from_state=current,
        to_state=target,
        ledger_seq=event.seq,
        request_seq=event.request_seq,
        row_version=int(updated[0]),
    )


_VERSION_COLUMNS = {"C": "st_c", "A": "st_a", "D": "st_d", "V": "st_v"}


def apply_version_transition(
    connection: Connection,
    machines: MachineSet,
    *,
    version_id: UUID,
    transition_id: str,
    actor: str,
    actor_id: UUID | None,
    workspace_id: UUID,
    at: datetime,
    context: GuardContext,
) -> AppliedTransition:
    """Applique une transition C, A, D ou V a une version."""
    axis = transition_id.split("-")[1] if transition_id.count("-") >= 2 else ""
    if axis not in _VERSION_COLUMNS:
        raise ValueError("transition de version attendue")
    _set_transition(connection, transition_id)
    row = (
        connection.execute(
            text(
                """
            SELECT v.st_c, v.st_a, v.st_d, v.st_v, v.row_version, d.request_id
              FROM deliverable_versions v
              JOIN deliverables d ON d.id = v.deliverable_id
             WHERE v.id = :version_id
             FOR UPDATE OF v
            """
            ),
            {"version_id": version_id},
        )
        .mappings()
        .first()
    )
    if row is None:
        raise TransitionRejected(transition_id, "version inconnue", "Element introuvable.")
    current = str(row[f"st_{axis.lower()}"])
    try:
        target = apply_transition(machines.get(axis), current, transition_id, actor, context)
    except InvalidTransition as exc:
        raise TransitionRejected(
            transition_id, exc.reason_internal, exc.reason_communicable
        ) from exc

    finalized_at = at if (axis == "V" and target == "finalized") else None
    connection.execute(
        text(
            """
            UPDATE deliverable_versions
               SET st_c = CASE WHEN :axis = 'C'
                               THEN CAST(CAST(:target AS text) AS st_conformity) ELSE st_c END,
                   st_a = CASE WHEN :axis = 'A'
                               THEN CAST(CAST(:target AS text) AS st_approval) ELSE st_a END,
                   st_d = CASE WHEN :axis = 'D'
                               THEN CAST(CAST(:target AS text) AS st_diffusion) ELSE st_d END,
                   st_v = CASE WHEN :axis = 'V'
                               THEN CAST(CAST(:target AS text) AS st_version) ELSE st_v END,
                   finalized_at = COALESCE(:finalized_at, finalized_at),
                   row_version = row_version + 1
             WHERE id = :version_id
            """
        ),
        {
            "axis": axis,
            "target": target,
            "finalized_at": finalized_at,
            "version_id": version_id,
        },
    )

    request_id = row["request_id"]
    event = append_event(
        connection,
        workspace_id=workspace_id,
        request_id=request_id,
        event_type="StateTransitionApplied",
        payload={
            "transition_id": transition_id,
            "axis": axis,
            "entity_id": str(version_id),
            "from_state": current,
            "to_state": target,
            "actor": actor,
        },
        actor_type=_actor_type(actor),
        actor_id=actor_id,
        at=at,
    )
    _write_state_change(
        connection,
        workspace_id=workspace_id,
        entity_type="deliverable_version",
        entity_id=version_id,
        axis=axis,
        from_state=current,
        to_state=target,
        transition_id=transition_id,
        actor=actor,
        actor_id=actor_id,
        at=at,
        ledger_seq=event.seq,
    )
    return AppliedTransition(
        transition_id=transition_id,
        axis=axis,
        entity_id=version_id,
        from_state=current,
        to_state=target,
        ledger_seq=event.seq,
        request_seq=event.request_seq,
        row_version=int(row["row_version"]) + 1,
    )


def apply_element_transition(
    connection: Connection,
    machines: MachineSet,
    *,
    element_id: UUID,
    transition_id: str,
    actor: str,
    actor_id: UUID | None,
    workspace_id: UUID,
    at: datetime,
    context: GuardContext,
) -> AppliedTransition:
    """Applique une transition de l'axe E a un element de version."""
    if not transition_id.startswith("TR-E-"):
        raise ValueError("transition d'element attendue")
    _set_transition(connection, transition_id)
    row = (
        connection.execute(
            text(
                """
            SELECT e.st_e, v.st_v, d.request_id
              FROM elements e
              JOIN deliverable_versions v ON v.id = e.version_id
              JOIN deliverables d ON d.id = v.deliverable_id
             WHERE e.id = :element_id
             FOR UPDATE OF e
            """
            ),
            {"element_id": element_id},
        )
        .mappings()
        .first()
    )
    if row is None:
        raise TransitionRejected(transition_id, "element inconnu", "Element introuvable.")
    if str(row["st_v"]) in ("finalized", "superseded"):
        raise TransitionRejected(
            transition_id,
            "version finalisee",
            "Cette version ne peut plus etre modifiee.",
        )
    current = str(row["st_e"])
    try:
        target = apply_transition(machines.get("E"), current, transition_id, actor, context)
    except InvalidTransition as exc:
        raise TransitionRejected(
            transition_id, exc.reason_internal, exc.reason_communicable
        ) from exc

    connection.execute(
        text("UPDATE elements SET st_e = :target WHERE id = :element_id"),
        {"target": target, "element_id": element_id},
    )
    event = append_event(
        connection,
        workspace_id=workspace_id,
        request_id=row["request_id"],
        event_type="StateTransitionApplied",
        payload={
            "transition_id": transition_id,
            "axis": "E",
            "entity_id": str(element_id),
            "from_state": current,
            "to_state": target,
            "actor": actor,
        },
        actor_type=_actor_type(actor),
        actor_id=actor_id,
        at=at,
    )
    _write_state_change(
        connection,
        workspace_id=workspace_id,
        entity_type="element",
        entity_id=element_id,
        axis="E",
        from_state=current,
        to_state=target,
        transition_id=transition_id,
        actor=actor,
        actor_id=actor_id,
        at=at,
        ledger_seq=event.seq,
    )
    return AppliedTransition(
        transition_id=transition_id,
        axis="E",
        entity_id=element_id,
        from_state=current,
        to_state=target,
        ledger_seq=event.seq,
        request_seq=event.request_seq,
        row_version=0,
    )
