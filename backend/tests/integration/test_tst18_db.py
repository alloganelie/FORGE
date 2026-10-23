"""TST-18 cote PostgreSQL : transitions persistees, journal et projection (ET-023, ET-024).

Le modele pur est couvert par backend/tests/property/test_tst18.py. Ce test
rejoue le parcours nominal contre une base reelle et verifie que l'etat,
state_changes et le journal restent dans la meme transaction.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import pytest
from sqlalchemy import Connection, text

from agent.ledger.api import verify_chain
from agent.lifecycle.api import (
    ConcurrencyConflict,
    GuardContext,
    TransitionRejected,
    apply_element_transition,
    apply_request_transition,
    apply_version_transition,
    load_machines,
)
from agent.lifecycle.core.states import ApprovalState

WORKSPACE_ID = UUID("11111111-1111-7111-8111-111111111111")
REQUEST_ID = UUID("44444444-4444-7444-8444-444444444444")
DELIVERABLE_ID = UUID("66666666-6666-7666-8666-666666666666")
VERSION_ID = UUID("77777777-7777-7777-8777-777777777777")
ELEMENT_ID = UUID("88888888-8888-7888-8888-888888888888")
ACTOR_ID = UUID("22222222-2222-7222-8222-222222222222")
AT = datetime(2026, 10, 23, 12, 0, tzinfo=UTC)


def _context() -> GuardContext:
    return GuardContext(
        author_authorized=True,
        ambiguity_significant=True,
        parameters_sufficient=True,
        feasible_at_least_in_part=True,
        no_part_feasible=True,
        decision_uncovered_or_rights_uncertain=True,
        new_ambiguity=True,
        all_required_elements_produced=True,
        no_operation_can_progress=True,
        only_human_decision_progresses=True,
        only_user_answer_progresses=True,
        cause_lifted=True,
        decision_recorded=True,
        decision_insufficient=True,
        lift_requires_decision=True,
        answer_sufficient=True,
        answers_sufficient=True,
        feasibility_acquired=True,
        failure_requires_production=True,
        correction_requires_decision=True,
        all_mandatory_controls_passed=True,
        version_conforming=True,
        mandatory_elements_ok=True,
        reports_produced=True,
        explicit_confirmation=True,
        not_finalized=True,
        retention_allows_resume=True,
        version_finalized=True,
        approval=ApprovalState.APPROVED,
        diffusion_rights_verified=True,
        scope_changed=True,
        approver_authorized=True,
        mandatory_control_failed=True,
    )


def _seed_version(connection: Connection) -> None:
    connection.execute(
        text(
            """
            INSERT INTO deliverables (id, workspace_id, request_id, type_key, target_format)
            VALUES (:deliverable_id, :workspace_id, :request_id, 'note', 'md')
            """
        ),
        {
            "deliverable_id": DELIVERABLE_ID,
            "workspace_id": WORKSPACE_ID,
            "request_id": REQUEST_ID,
        },
    )
    connection.execute(
        text(
            """
            INSERT INTO deliverable_versions
              (id, workspace_id, deliverable_id, number, st_v, st_c, st_a, st_d)
            VALUES (:version_id, :workspace_id, :deliverable_id, 1, 'provisional', 'not_evaluated',
                    'not_submitted', 'not_authorized')
            """
        ),
        {
            "version_id": VERSION_ID,
            "workspace_id": WORKSPACE_ID,
            "deliverable_id": DELIVERABLE_ID,
        },
    )
    connection.execute(
        text(
            """
            INSERT INTO elements (id, workspace_id, version_id, element_key, mandatory, st_e)
            VALUES (:element_id, :workspace_id, :version_id, 'E1', true, 'to_produce')
            """
        ),
        {
            "element_id": ELEMENT_ID,
            "workspace_id": WORKSPACE_ID,
            "version_id": VERSION_ID,
        },
    )


@pytest.mark.integration
@pytest.mark.tst("TST-18")
@pytest.mark.spec("ET-023")
@pytest.mark.spec("ET-024")
@pytest.mark.spec("ET-037")
@pytest.mark.spec("RT-035")
def test_nominal_path_is_persisted_atomically(seeded: Connection) -> None:
    _seed_version(seeded)
    machines = load_machines()
    context = _context()

    def request_transition(transition_id: str, actor: str = "agent") -> object:
        return apply_request_transition(
            seeded,
            machines,
            request_id=REQUEST_ID,
            transition_id=transition_id,
            actor=actor,
            actor_id=ACTOR_ID,
            workspace_id=WORKSPACE_ID,
            at=AT,
            context=context,
        )

    def version_transition(transition_id: str, actor: str = "agent") -> object:
        return apply_version_transition(
            seeded,
            machines,
            version_id=VERSION_ID,
            transition_id=transition_id,
            actor=actor,
            actor_id=ACTOR_ID,
            workspace_id=WORKSPACE_ID,
            at=AT,
            context=context,
        )

    assert request_transition("TR-R-03").to_state == "feasibility"
    assert request_transition("TR-R-05").to_state == "producing"
    assert (
        apply_element_transition(
            seeded,
            machines,
            element_id=ELEMENT_ID,
            transition_id="TR-E-01",
            actor="agent",
            actor_id=ACTOR_ID,
            workspace_id=WORKSPACE_ID,
            at=AT,
            context=context,
        ).to_state
        == "produced"
    )
    assert (
        apply_element_transition(
            seeded,
            machines,
            element_id=ELEMENT_ID,
            transition_id="TR-E-07",
            actor="agent",
            actor_id=ACTOR_ID,
            workspace_id=WORKSPACE_ID,
            at=AT,
            context=context,
        ).to_state
        == "controlled_ok"
    )
    version_transition("TR-C-01")
    version_transition("TR-C-02")
    assert request_transition("TR-R-09").to_state == "quality_control"
    assert version_transition("TR-V-01").to_state == "finalized"
    assert request_transition("TR-R-18").to_state == "finalized"

    state = seeded.execute(
        text("SELECT state, row_version FROM requests WHERE id = :id"), {"id": REQUEST_ID}
    ).one()
    assert state[0] == "finalized"
    assert state[1] == 4

    changes = seeded.execute(
        text(
            """
            SELECT axis, transition_id, ledger_seq
              FROM state_changes
             WHERE entity_id IN (:request_id, :version_id, :element_id)
             ORDER BY ledger_seq
            """
        ),
        {"request_id": REQUEST_ID, "version_id": VERSION_ID, "element_id": ELEMENT_ID},
    ).all()
    assert len(changes) == 9
    assert sum(1 for row in changes if row[0] == "R") == 4
    assert sum(1 for row in changes if row[0] == "E") == 2
    assert sum(1 for row in changes if row[0] in ("C", "V")) == 3
    assert [row[2] for row in changes] == sorted(row[2] for row in changes)

    chain = verify_chain(seeded, WORKSPACE_ID)
    assert chain.ok, chain.errors
    assert chain.checked == 9


@pytest.mark.integration
@pytest.mark.spec("ET-038")
def test_row_version_conflict_is_refused(seeded: Connection) -> None:
    _seed_version(seeded)
    machines = load_machines()
    with pytest.raises(ConcurrencyConflict):
        apply_request_transition(
            seeded,
            machines,
            request_id=REQUEST_ID,
            transition_id="TR-R-03",
            actor="agent",
            actor_id=ACTOR_ID,
            workspace_id=WORKSPACE_ID,
            at=AT,
            context=_context(),
            expected_row_version=99,
        )


@pytest.mark.integration
@pytest.mark.spec("ET-036")
def test_wrong_actor_is_refused_and_transaction_unchanged(seeded: Connection) -> None:
    _seed_version(seeded)
    machines = load_machines()
    with pytest.raises(TransitionRejected):
        apply_request_transition(
            seeded,
            machines,
            request_id=REQUEST_ID,
            transition_id="TR-R-03",
            actor="user",
            actor_id=ACTOR_ID,
            workspace_id=WORKSPACE_ID,
            at=AT,
            context=_context(),
        )
    assert (
        seeded.execute(
            text("SELECT state FROM requests WHERE id = :id"), {"id": REQUEST_ID}
        ).scalar_one()
        == "received"
    )
