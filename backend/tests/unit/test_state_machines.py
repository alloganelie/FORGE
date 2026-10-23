"""ET-035, ET-036, ET-039, ET-041 : machines, moteur et gardes purs."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest
import yaml
from tools.gen_transitions import main as gen_transitions_main

from agent.lifecycle.api import (
    GuardContext,
    InvalidTransition,
    ResumeTargetError,
    UnknownTransition,
    apply_transition,
    load_machines,
    resume_target,
)
from agent.lifecycle.core import states
from agent.lifecycle.core.guards import GUARDS


def _permissive_context(machine_axis: str, transition: object) -> GuardContext:
    guards = transition.guards
    origin = None
    if "origin_is_producing" in guards:
        origin = states.RequestState.PRODUCING
    elif "origin_is_feasibility" in guards:
        origin = states.RequestState.FEASIBILITY
    elif "origin_is_quality_control" in guards:
        origin = states.RequestState.QUALITY_CONTROL
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
        approval=states.ApprovalState.APPROVED,
        diffusion_rights_verified=True,
        scope_changed=True,
        approver_authorized=True,
        mandatory_control_failed=True,
        waiting_origin=origin,
        suspended_from=states.RequestState.PRODUCING,
    )


def _concrete_source(transition: object, machine: object) -> str | None:
    source = transition.source
    if source is None:
        return None
    if source == "ANY_NON_FINAL":
        return states.RequestState.RECEIVED.value
    if source == "ANY_NON_FINAL_EXCEPT_SUSPENDED":
        return states.RequestState.RECEIVED.value
    return source


@pytest.mark.spec("ET-035")
def test_six_axes_and_all_spec_transitions_are_present() -> None:
    machines = load_machines()
    assert tuple(machines.by_axis) == ("R", "C", "A", "D", "V", "E")
    all_ids = {transition.id for transition in machines.all_transitions}
    functional = yaml.safe_load(
        Path("rulepacks/state_machines/request.yaml").read_text(encoding="utf-8")
    )
    non_transitions = {item["id"] for item in functional["non_transitions"]}
    assert "TR-R-22" in non_transitions
    assert len(all_ids) + len(non_transitions) == 54


@pytest.mark.spec("ET-035")
def test_generated_transitions_are_up_to_date() -> None:
    assert gen_transitions_main(["--check"]) == 0


@pytest.mark.spec("ET-036")
def test_every_transition_can_be_applied_with_permissive_context() -> None:
    machines = load_machines()
    for machine in machines.by_axis.values():
        for transition in machine.transitions:
            current = _concrete_source(transition, machine)
            context = _permissive_context(machine.axis, transition)
            target = apply_transition(
                machine, current, transition.id, transition.actors[0], context
            )
            assert target in machine.states, transition.id
            if transition.target != "DYNAMIC":
                assert target == transition.target


@pytest.mark.spec("ET-039")
def test_every_guard_used_by_yaml_exists_and_is_pure() -> None:
    machines = load_machines()
    used = {guard for transition in machines.all_transitions for guard in transition.guards}
    assert used <= set(GUARDS)
    context = GuardContext()
    for name in used:
        first = GUARDS[name](context)
        second = GUARDS[name](context)
        assert first == second
        assert first.ok is False
        assert "reason_internal" in first.__dataclass_fields__


@pytest.mark.spec("ET-036")
def test_unknown_transition_and_wrong_actor_are_rejected() -> None:
    machine = load_machines().get("R")
    with pytest.raises(UnknownTransition):
        apply_transition(machine, "received", "TR-X-99", "agent", GuardContext())
    with pytest.raises(InvalidTransition):
        apply_transition(
            machine,
            "received",
            "TR-R-02",
            "responsible",
            _permissive_context("R", machine.transition("TR-R-02")),
        )


@pytest.mark.spec("ET-036")
def test_guard_failure_rejects_without_internal_reason_leak() -> None:
    machine = load_machines().get("R")
    assert machine.transition("TR-R-02").id == "TR-R-02"
    with pytest.raises(InvalidTransition) as raised:
        apply_transition(machine, "received", "TR-R-02", "agent", GuardContext())
    assert (
        raised.value.reason_communicable
        == "Cette action n'est pas possible dans l'etat actuel de la demande."
    )
    assert "ambiguity_significant" in raised.value.reason_internal


@pytest.mark.spec("ET-041")
def test_resume_target_is_total_on_resumable_states() -> None:
    for state in states.RequestState:
        if state in (
            states.RequestState.SUSPENDED,
            states.RequestState.FINALIZED,
            states.RequestState.CANCELLED,
        ):
            with pytest.raises(ResumeTargetError):
                resume_target(state)
        else:
            assert resume_target(state) is state


@pytest.mark.spec("ET-041")
def test_dynamic_transition_uses_resume_target() -> None:
    machine = load_machines().get("R")
    transition = machine.transition("TR-R-20")
    context = replace(
        _permissive_context("R", transition), suspended_from=states.RequestState.FEASIBILITY
    )
    assert (
        apply_transition(machine, "suspended", "TR-R-20", "responsible", context) == "feasibility"
    )
