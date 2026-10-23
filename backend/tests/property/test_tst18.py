"""TST-18 : test a etats aleatoires, invariants IV-01 a IV-15 (ET-043, PR-01).

Le modele applique les transitions generees et verifie les quinze invariants
apres chaque commande. Le meme scenario deterministe est rejoue sur PostgreSQL
dans backend/tests/integration/test_tst18_db.py.
"""

from __future__ import annotations

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from agent.lifecycle.api import load_machines
from agent.lifecycle.core.workflow import COMMANDS, Workflow, check_invariants


def _new_workflow() -> Workflow:
    workflow = Workflow(load_machines())
    assert workflow.submit()
    check_invariants(workflow)
    return workflow


@pytest.mark.property
@pytest.mark.tst("TST-18")
@pytest.mark.spec("ET-043")
@pytest.mark.spec("PR-01")
@pytest.mark.spec("IV-01")
@pytest.mark.spec("IV-02")
@pytest.mark.spec("IV-03")
@pytest.mark.spec("IV-04")
@pytest.mark.spec("IV-05")
@pytest.mark.spec("IV-06")
@pytest.mark.spec("IV-07")
@pytest.mark.spec("IV-08")
@pytest.mark.spec("IV-09")
@pytest.mark.spec("IV-10")
@pytest.mark.spec("IV-11")
@pytest.mark.spec("IV-12")
@pytest.mark.spec("IV-13")
@pytest.mark.spec("IV-14")
@pytest.mark.spec("IV-15")
@settings(
    max_examples=250,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much],
)
@given(st.lists(st.sampled_from(COMMANDS), min_size=1, max_size=40))
def test_random_command_sequences_preserve_invariants(commands: list[str]) -> None:
    workflow = _new_workflow()
    for command in commands:
        workflow.execute(command)
        check_invariants(workflow)


@pytest.mark.property
@pytest.mark.tst("TST-18")
@pytest.mark.spec("IV-05")
@pytest.mark.spec("IV-13")
@pytest.mark.spec("IV-15")
def test_nominal_path_reaches_finalization_and_diffusion() -> None:
    workflow = _new_workflow()
    for command in (
        "assess",
        "start_production",
        "produce_element",
        "control_element_ok",
        "start_controls",
        "run_controls_ok",
        "finalize",
    ):
        assert workflow.execute(command), command
        check_invariants(workflow)
    assert workflow.request_state is not None
    assert workflow.request_state.value == "finalized"
    assert workflow.active_version.st_v.value == "finalized"
    assert workflow.active_version.st_a.value == "not_submitted"
    assert workflow.active_version.st_d.value == "not_authorized"
    assert workflow.execute("submit_approval")
    assert workflow.execute("approve")
    assert workflow.execute("authorize_diffusion")
    check_invariants(workflow)
    assert workflow.active_version.st_d.value == "authorized"


@pytest.mark.property
@pytest.mark.tst("TST-18")
@pytest.mark.spec("IV-06")
@pytest.mark.spec("IV-12")
def test_suspension_resume_and_cancellation_path() -> None:
    workflow = _new_workflow()
    for command in ("assess", "start_production", "block_element", "suspend"):
        assert workflow.execute(command), command
        check_invariants(workflow)
    assert workflow.request_state is not None
    assert workflow.request_state.value == "suspended"
    assert workflow.execute("resume")
    check_invariants(workflow)
    assert workflow.request_state.value == "producing"
    assert workflow.execute("cancel")
    check_invariants(workflow)
    assert workflow.request_state.value == "cancelled"
    assert not workflow.execute("finalize")
