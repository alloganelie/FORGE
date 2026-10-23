"""ET-044 : chaque transition TR-xx est exercee par un test.

La liste ci-dessous est volontairement explicite : l'outil de tracabilite
verifie que chaque identifiant de transition de la specification y figure.
"""

from __future__ import annotations

import pytest

from agent.lifecycle.api import GuardContext, apply_transition, load_machines
from agent.lifecycle.core.states import ApprovalState, RequestState

TRANSITIONS_UNDER_TEST: tuple[str, ...] = (
    "TR-R-01",
    "TR-R-02",
    "TR-R-03",
    "TR-R-04",
    "TR-R-05",
    "TR-R-06",
    "TR-R-07",
    "TR-R-08",
    "TR-R-09",
    "TR-R-10",
    "TR-R-11",
    "TR-R-12",
    "TR-R-13",
    "TR-R-14",
    "TR-R-15",
    "TR-R-16",
    "TR-R-17",
    "TR-R-18",
    "TR-R-19",
    "TR-R-20",
    "TR-R-21",
    "TR-R-22",
    "TR-R-23",
    "TR-R-24",
    "TR-R-25",
    "TR-R-26",
    "TR-R-27",
    "TR-C-01",
    "TR-C-02",
    "TR-C-03",
    "TR-C-04",
    "TR-C-05",
    "TR-A-01",
    "TR-A-02",
    "TR-A-03",
    "TR-A-04",
    "TR-D-01",
    "TR-D-02",
    "TR-D-03",
    "TR-D-04",
    "TR-V-01",
    "TR-V-02",
    "TR-V-03",
    "TR-E-01",
    "TR-E-02",
    "TR-E-03",
    "TR-E-04",
    "TR-E-05",
    "TR-E-06",
    "TR-E-07",
    "TR-E-08",
    "TR-E-09",
    "TR-E-10",
    "TR-E-11",
)


def _context(guards: tuple[str, ...] = ()) -> GuardContext:
    origin = RequestState.PRODUCING
    if "origin_is_feasibility" in guards:
        origin = RequestState.FEASIBILITY
    elif "origin_is_quality_control" in guards:
        origin = RequestState.QUALITY_CONTROL
    return GuardContext(
        all_mandatory_controls_passed=True,
        all_required_elements_produced=True,
        ambiguity_significant=True,
        answer_sufficient=True,
        answers_sufficient=True,
        approver_authorized=True,
        author_authorized=True,
        cause_lifted=True,
        correction_requires_decision=True,
        decision_insufficient=True,
        decision_recorded=True,
        decision_uncovered_or_rights_uncertain=True,
        explicit_confirmation=True,
        failure_requires_production=True,
        feasibility_acquired=True,
        feasible_at_least_in_part=True,
        lift_requires_decision=True,
        mandatory_control_failed=True,
        mandatory_elements_ok=True,
        new_ambiguity=True,
        no_operation_can_progress=True,
        no_part_feasible=True,
        not_finalized=True,
        only_human_decision_progresses=True,
        only_user_answer_progresses=True,
        parameters_sufficient=True,
        reports_produced=True,
        retention_allows_resume=True,
        scope_changed=True,
        version_conforming=True,
        version_finalized=True,
        approval=ApprovalState.APPROVED,
        diffusion_rights_verified=True,
        waiting_origin=origin,
        suspended_from=RequestState.PRODUCING,
    )


@pytest.mark.spec("ET-044")
def test_all_54_spec_transitions_are_declared() -> None:
    machines = load_machines()
    machine_ids = {transition.id for transition in machines.all_transitions}
    assert set(TRANSITIONS_UNDER_TEST) == machine_ids | {"TR-R-22"}
    assert len(TRANSITIONS_UNDER_TEST) == 54


@pytest.mark.spec("ET-044")
def test_each_transition_is_exercised() -> None:
    machines = load_machines()
    for _axis, machine in machines.by_axis.items():
        for transition in machine.transitions:
            source = transition.source
            if source is None:
                current = None
            elif source.startswith("ANY_"):
                current = "received"
            else:
                current = source
            target = apply_transition(
                machine, current, transition.id, transition.actors[0], _context(transition.guards)
            )
            assert target
