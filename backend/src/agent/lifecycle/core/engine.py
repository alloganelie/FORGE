"""Moteur unique de transitions (ET-036, ET-037, ET-041).

Le moteur est pur : il recoit l'etat courant, la definition de la machine,
l'acteur et un instantane de contexte. Il ne lit ni la base, ni l'heure.
"""

from __future__ import annotations

from dataclasses import dataclass

from agent.lifecycle.core.guards import GuardContext, GuardResult, evaluate_guards
from agent.lifecycle.core.states import RequestState

ANY_NON_FINAL = "ANY_NON_FINAL"
ANY_NON_FINAL_EXCEPT_SUSPENDED = "ANY_NON_FINAL_EXCEPT_SUSPENDED"
DYNAMIC = "DYNAMIC"


class TransitionError(Exception):
    """Refus d'une transition ; ne revele jamais de raison interne au client."""


class UnknownTransition(TransitionError):
    def __init__(self, transition_id: str) -> None:
        super().__init__(f"transition inconnue : {transition_id}")
        self.transition_id = transition_id


class InvalidTransition(TransitionError):
    def __init__(
        self,
        transition_id: str,
        reason_internal: str,
        reason_communicable: str,
        failed_guards: tuple[GuardResult, ...] = (),
    ) -> None:
        super().__init__(reason_communicable)
        self.transition_id = transition_id
        self.reason_internal = reason_internal
        self.reason_communicable = reason_communicable
        self.failed_guards = failed_guards


class ResumeTargetError(TransitionError):
    def __init__(self, origin: RequestState | None) -> None:
        super().__init__("Reprise impossible : etat d'origine inconnu ou non reprenable")
        self.origin = origin


@dataclass(frozen=True, slots=True)
class Transition:
    id: str
    source: str | None
    target: str | None
    actors: tuple[str, ...]
    guards: tuple[str, ...]
    condition: str
    effects: tuple[str, ...]

    def matches_source(self, current: str | None, final_states: frozenset[str]) -> bool:
        if self.source is None:
            return current is None
        if current is None:
            return False
        if self.source == ANY_NON_FINAL:
            return current not in final_states
        if self.source == ANY_NON_FINAL_EXCEPT_SUSPENDED:
            return current not in final_states and current != RequestState.SUSPENDED.value
        return self.source == current


@dataclass(frozen=True, slots=True)
class Machine:
    axis: str
    entity: str
    states: tuple[str, ...]
    final_states: frozenset[str]
    transitions: tuple[Transition, ...]

    def transition(self, transition_id: str) -> Transition:
        for candidate in self.transitions:
            if candidate.id == transition_id:
                return candidate
        raise UnknownTransition(transition_id)


@dataclass(frozen=True, slots=True)
class MachineSet:
    """Les six machines chargees, indexees par axe."""

    by_axis: dict[str, Machine]

    def get(self, axis: str) -> Machine:
        try:
            return self.by_axis[axis]
        except KeyError as exc:
            raise ValueError(f"axe inconnu : {axis}") from exc

    @property
    def all_transitions(self) -> tuple[Transition, ...]:
        return tuple(
            transition for machine in self.by_axis.values() for transition in machine.transitions
        )


def resume_target(origin: RequestState | None) -> RequestState:
    """Etat de reprise pur (ET-041, TR-R-20).

    Q-002 : la specification permet de suspendre depuis tout etat non final
    (TR-R-19) mais TR-R-20 n'enumere pas Recue et Verification de faisabilite.
    Hypothese retenue : la reprise revient a l'etat d'origine, sans saut direct
    vers Finalisee. Une demande suspendue ne peut donc jamais etre finalisee.
    """
    if origin is None or origin in (
        RequestState.SUSPENDED,
        RequestState.FINALIZED,
        RequestState.CANCELLED,
    ):
        raise ResumeTargetError(origin)
    return origin


def apply_transition(
    machine: Machine,
    current: str | None,
    transition_id: str,
    actor: str,
    context: GuardContext,
) -> str:
    """Applique une transition pure et retourne le nouvel etat."""
    transition = machine.transition(transition_id)
    if not transition.matches_source(current, machine.final_states):
        raise InvalidTransition(
            transition_id,
            f"etat courant {current!r} incompatible avec la source {transition.source!r}",
            "Cette action n'est pas possible dans l'etat actuel de la demande.",
        )
    if actor not in transition.actors:
        raise InvalidTransition(
            transition_id,
            f"acteur {actor!r} non autorise pour {transition_id}",
            "Vous n'etes pas autorise a effectuer cette action.",
        )
    results = evaluate_guards(transition.guards, context)
    failures = tuple(result for result in results if not result.ok)
    if failures:
        raise InvalidTransition(
            transition_id,
            "; ".join(result.reason_internal for result in failures),
            failures[0].reason_communicable,
            failures,
        )
    if transition.target == DYNAMIC:
        return resume_target(context.suspended_from).value
    if transition.target is None:
        raise InvalidTransition(
            transition_id,
            "transition sans cible calculee",
            "Cette action n'est pas disponible.",
        )
    return transition.target
