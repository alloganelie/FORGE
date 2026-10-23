"""Registre des gardes : fonctions pures (ET-039, T 7.3).

Une garde ne lit ni l'heure, ni le hasard, ni la base : elle recoit un
instantane immuable. Une garde inconnue refuse par defaut.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

from agent.lifecycle.core.states import ApprovalState, RequestState

COMMUNICABLE_REFUSAL = "Cette action n'est pas possible dans l'etat actuel de la demande."


@dataclass(frozen=True, slots=True)
class GuardResult:
    """Resultat d'une garde : raison interne + raison communicable (PT-09)."""

    ok: bool
    reason_internal: str
    reason_communicable: str

    @classmethod
    def allowed(cls) -> GuardResult:
        return cls(ok=True, reason_internal="", reason_communicable="")

    @classmethod
    def denied(cls, reason_internal: str) -> GuardResult:
        return cls(
            ok=False,
            reason_internal=reason_internal,
            reason_communicable=COMMUNICABLE_REFUSAL,
        )


@dataclass(frozen=True, slots=True)
class GuardContext:
    """Instantane immuable evalue par les gardes.

    Les drapeaux correspondent aux conditions de la specification 7.2/7.3 ;
    ils sont renseignes par les cas d'usage, jamais par un modele de langage.
    """

    author_authorized: bool = False
    ambiguity_significant: bool = False
    parameters_sufficient: bool = False
    feasible_at_least_in_part: bool = False
    no_part_feasible: bool = False
    decision_uncovered_or_rights_uncertain: bool = False
    new_ambiguity: bool = False
    all_required_elements_produced: bool = False
    no_operation_can_progress: bool = False
    only_human_decision_progresses: bool = False
    only_user_answer_progresses: bool = False
    cause_lifted: bool = False
    decision_recorded: bool = False
    decision_insufficient: bool = False
    lift_requires_decision: bool = False
    answer_sufficient: bool = False
    answers_sufficient: bool = False
    feasibility_acquired: bool = False
    failure_requires_production: bool = False
    correction_requires_decision: bool = False
    all_mandatory_controls_passed: bool = False
    version_conforming: bool = False
    mandatory_elements_ok: bool = False
    reports_produced: bool = False
    explicit_confirmation: bool = False
    not_finalized: bool = False
    retention_allows_resume: bool = False
    version_finalized: bool = False
    approval: ApprovalState | None = None
    diffusion_rights_verified: bool = False
    scope_changed: bool = False
    approver_authorized: bool = False
    mandatory_control_failed: bool = False
    waiting_origin: RequestState | None = None
    suspended_from: RequestState | None = None
    suspension_event: Mapping[str, Any] | None = None
    flags: Mapping[str, bool] = field(default_factory=dict)

    def flag(self, name: str) -> bool:
        return bool(self.flags.get(name, False))


Guard = Callable[[GuardContext], GuardResult]


def _flag_guard(name: str) -> Guard:
    def guard(context: GuardContext) -> GuardResult:
        if bool(getattr(context, name)):
            return GuardResult.allowed()
        return GuardResult.denied(f"garde {name} non satisfaite")

    guard.__name__ = f"guard_{name}"
    return guard


def _origin_guard(name: str, origin: RequestState) -> Guard:
    def guard(context: GuardContext) -> GuardResult:
        if context.waiting_origin is origin:
            return GuardResult.allowed()
        return GuardResult.denied(f"origine d'attente differente de {origin.value}")

    guard.__name__ = name
    return guard


def _approval_guard(context: GuardContext) -> GuardResult:
    if context.approval in (ApprovalState.APPROVED, ApprovalState.NOT_REQUIRED):
        return GuardResult.allowed()
    return GuardResult.denied("approbation ni approuvee ni non requise")


def _diffusion_guard(context: GuardContext) -> GuardResult:
    if context.diffusion_rights_verified:
        return GuardResult.allowed()
    return GuardResult.denied("droits de diffusion non verifies pour chaque destinataire")


_FLAG_GUARDS = (
    "all_mandatory_controls_passed",
    "all_required_elements_produced",
    "ambiguity_significant",
    "answer_sufficient",
    "answers_sufficient",
    "approver_authorized",
    "author_authorized",
    "cause_lifted",
    "correction_requires_decision",
    "decision_insufficient",
    "decision_recorded",
    "decision_uncovered_or_rights_uncertain",
    "explicit_confirmation",
    "failure_requires_production",
    "feasibility_acquired",
    "feasible_at_least_in_part",
    "lift_requires_decision",
    "mandatory_control_failed",
    "mandatory_elements_ok",
    "new_ambiguity",
    "no_operation_can_progress",
    "no_part_feasible",
    "not_finalized",
    "only_human_decision_progresses",
    "only_user_answer_progresses",
    "parameters_sufficient",
    "reports_produced",
    "retention_allows_resume",
    "scope_changed",
    "version_conforming",
    "version_finalized",
)

GUARDS: Mapping[str, Guard] = {
    **{name: _flag_guard(name) for name in _FLAG_GUARDS},
    "approval_approved_or_not_required": _approval_guard,
    "diffusion_rights_verified_per_recipient": _diffusion_guard,
    "origin_is_feasibility": _origin_guard("origin_is_feasibility", RequestState.FEASIBILITY),
    "origin_is_producing": _origin_guard("origin_is_producing", RequestState.PRODUCING),
    "origin_is_quality_control": _origin_guard(
        "origin_is_quality_control", RequestState.QUALITY_CONTROL
    ),
}


def evaluate_guards(names: tuple[str, ...], context: GuardContext) -> tuple[GuardResult, ...]:
    """Evalue les gardes dans l'ordre ; une garde inconnue refuse."""
    results: list[GuardResult] = []
    for name in names:
        guard = GUARDS.get(name)
        if guard is None:
            results.append(GuardResult.denied(f"garde inconnue : {name}"))
            continue
        results.append(guard(context))
    return tuple(results)
