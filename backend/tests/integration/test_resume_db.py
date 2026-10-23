"""Q-002, ET-041 : la reprise lit suspended_from dans le journal (PostgreSQL).

Le contexte fourni a la reprise ne contient volontairement aucun etat de
suspension : seule la lecture de l'evenement TR-R-19 permet de retrouver
l'etat du moment de la suspension.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import pytest
from sqlalchemy import Connection, text

from agent.lifecycle.api import (
    GuardContext,
    apply_request_transition,
    load_machines,
)

WORKSPACE_ID = UUID("11111111-1111-7111-8111-111111111111")
REQUEST_ID = UUID("44444444-4444-7444-8444-444444444444")
ACTOR_ID = UUID("22222222-2222-7222-8222-222222222222")
AT = datetime(2026, 10, 23, 12, 0, tzinfo=UTC)


def _context() -> GuardContext:
    return GuardContext(
        parameters_sufficient=True,
        feasible_at_least_in_part=True,
        retention_allows_resume=True,
    )


def _apply(connection: Connection, transition_id: str, actor: str) -> object:
    return apply_request_transition(
        connection,
        load_machines(),
        request_id=REQUEST_ID,
        transition_id=transition_id,
        actor=actor,
        actor_id=ACTOR_ID,
        workspace_id=WORKSPACE_ID,
        at=AT,
        context=_context(),
    )


@pytest.mark.integration
@pytest.mark.spec("ET-041")
@pytest.mark.spec("TR-R-19")
@pytest.mark.spec("TR-R-20")
def test_resume_reads_suspension_state_from_ledger(seeded: Connection) -> None:
    assert _apply(seeded, "TR-R-03", "agent").to_state == "feasibility"
    assert _apply(seeded, "TR-R-05", "agent").to_state == "producing"
    assert _apply(seeded, "TR-R-19", "responsible").to_state == "suspended"

    row = seeded.execute(
        text(
            """
            SELECT state, suspended_from
              FROM requests
             WHERE id = :id
            """
        ),
        {"id": REQUEST_ID},
    ).one()
    assert row[0] == "suspended"
    assert row[1] == "producing"

    suspension_payload = seeded.execute(
        text(
            """
            SELECT payload
              FROM ledger_events
             WHERE request_id = :request_id
               AND payload->>'transition_id' = 'TR-R-19'
             ORDER BY request_seq DESC
             LIMIT 1
            """
        ),
        {"request_id": REQUEST_ID},
    ).scalar_one()
    assert suspension_payload["suspended_from"] == "producing"
    assert suspension_payload["suspended_from"] != "received"

    # Le contexte de reprise ne porte aucun etat : le depot doit lire le journal.
    resume_context = GuardContext(retention_allows_resume=True)
    result = apply_request_transition(
        seeded,
        load_machines(),
        request_id=REQUEST_ID,
        transition_id="TR-R-20",
        actor="responsible",
        actor_id=ACTOR_ID,
        workspace_id=WORKSPACE_ID,
        at=AT,
        context=resume_context,
    )
    assert result.to_state == "producing"
    assert result.from_state == "suspended"

    row = seeded.execute(
        text("SELECT state, suspended_from FROM requests WHERE id = :id"),
        {"id": REQUEST_ID},
    ).one()
    assert row[0] == "producing"
    assert row[1] is None
