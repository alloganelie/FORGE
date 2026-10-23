"""Q-002, ET-041 : la reprise revient a l'etat du moment de la suspension.

La source de verite est le champ suspended_from de l'evenement TR-R-19 du
journal, jamais l'etat initial de la demande.
"""

from __future__ import annotations

import pytest

from agent.lifecycle.api import (
    GuardContext,
    ResumeTargetError,
    apply_transition,
    load_machines,
    resume_target,
)
from agent.lifecycle.core.states import RequestState
from agent.lifecycle.core.workflow import Workflow


@pytest.mark.spec("ET-041")
@pytest.mark.spec("TR-R-20")
def test_resume_target_reads_suspended_from_event() -> None:
    assert resume_target({"suspended_from": "quality_control"}) is RequestState.QUALITY_CONTROL
    assert resume_target({"suspended_from": "received"}) is RequestState.RECEIVED


@pytest.mark.spec("ET-041")
@pytest.mark.spec("TR-R-20")
def test_resume_target_rejects_missing_or_invalid_event() -> None:
    with pytest.raises(ResumeTargetError):
        resume_target({})
    with pytest.raises(ResumeTargetError):
        resume_target({"suspended_from": "etat_inconnu"})
    with pytest.raises(ResumeTargetError):
        resume_target({"suspended_from": "suspended"})


@pytest.mark.spec("ET-041")
@pytest.mark.spec("TR-R-20")
def test_engine_prefers_suspension_event_over_initial_state() -> None:
    machine = load_machines().get("R")
    context = GuardContext(
        retention_allows_resume=True,
        suspended_from=RequestState.RECEIVED,
        suspension_event={"suspended_from": "quality_control"},
    )
    assert (
        apply_transition(machine, "suspended", "TR-R-20", "responsible", context)
        == "quality_control"
    )


@pytest.mark.spec("ET-041")
@pytest.mark.spec("TR-R-19")
@pytest.mark.spec("TR-R-20")
def test_workflow_resume_returns_state_at_suspension() -> None:
    workflow = Workflow(load_machines())
    assert workflow.submit()
    assert workflow.assess()
    assert workflow.start_production()
    assert workflow.suspend()
    assert workflow.request_state is RequestState.SUSPENDED
    assert workflow.suspension_event == {"suspended_from": "producing"}
    assert workflow.resume()
    assert workflow.request_state is RequestState.PRODUCING
