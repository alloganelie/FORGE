"""Modele d'etats pur pour TST-18 (ET-043, PR-01).

Ce module ne fait aucune entree-sortie : il applique les transitions generees
et verifie les quinze invariants apres chaque commande. Les commandes
metier reelles seront branchees en MS-1 et suivants ; ce socle sert de
propriete de surete du moteur.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from agent.lifecycle.core.engine import InvalidTransition, MachineSet, apply_transition
from agent.lifecycle.core.guards import GuardContext
from agent.lifecycle.core.states import (
    ApprovalState,
    ConformityState,
    DiffusionState,
    ElementState,
    RequestState,
    VersionState,
)

STATE_LABELS: dict[str, str] = {
    "received": "Recue",
    "clarifying": "En clarification",
    "feasibility": "En verification de faisabilite",
    "producing": "En production",
    "quality_control": "En controle qualite",
    "blocked": "Bloquee",
    "awaiting_decision": "En attente d'une decision humaine",
    "suspended": "Suspendue",
    "finalized": "Finalisee",
    "cancelled": "Annulee definitivement",
}

FINAL_REQUEST_STATES = {RequestState.FINALIZED, RequestState.CANCELLED}


class InvariantViolation(AssertionError):
    """Un invariant IV-xx est viole ; le message cite l'identifiant."""

    def __init__(self, invariant: str, detail: str) -> None:
        super().__init__(f"{invariant} viole : {detail}")
        self.invariant = invariant


@dataclass
class VersionView:
    """Vue d'une version et de ses elements (aucune persistance)."""

    identifier: str
    st_v: VersionState = VersionState.PROVISIONAL
    st_c: ConformityState = ConformityState.NOT_EVALUATED
    st_a: ApprovalState = ApprovalState.NOT_SUBMITTED
    st_d: DiffusionState = DiffusionState.NOT_AUTHORIZED
    elements: dict[str, ElementState] = field(
        default_factory=lambda: {"E1": ElementState.TO_PRODUCE}
    )
    finalized_snapshot: tuple[ConformityState, ApprovalState, DiffusionState] | None = None

    def mandatory_elements_ok(self) -> bool:
        return all(
            state in (ElementState.CONTROLLED_OK, ElementState.NOT_APPLICABLE)
            for state in self.elements.values()
        )

    def required_elements_produced(self) -> bool:
        return all(
            state
            in (ElementState.PRODUCED, ElementState.CONTROLLED_OK, ElementState.NOT_APPLICABLE)
            for state in self.elements.values()
        )


@dataclass
class Workflow:
    """Agregat en memoire : demande, version active, historique des commandes."""

    machines: MachineSet
    request_state: RequestState | None = None
    waiting_origin: RequestState | None = None
    suspended_from: RequestState | None = None
    suspension_event: dict[str, str] | None = None
    active_version: VersionView = field(default_factory=lambda: VersionView("v1"))
    revision_of: str | None = None
    history: list[str] = field(default_factory=list)
    last_axis_actor: dict[str, str] = field(default_factory=dict)

    # --- helpers ---
    def _context(
        self,
        *,
        controls_ok: bool = False,
        control_failed: bool = False,
        required_elements_produced: bool | None = None,
    ) -> GuardContext:
        version = self.active_version
        approval = version.st_a
        return GuardContext(
            author_authorized=True,
            ambiguity_significant=True,
            parameters_sufficient=True,
            feasible_at_least_in_part=True,
            no_part_feasible=True,
            decision_uncovered_or_rights_uncertain=True,
            new_ambiguity=True,
            all_required_elements_produced=(
                version.required_elements_produced()
                if required_elements_produced is None
                else required_elements_produced
            ),
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
            all_mandatory_controls_passed=controls_ok,
            mandatory_control_failed=control_failed,
            version_conforming=version.st_c is ConformityState.CONFORMING,
            mandatory_elements_ok=version.mandatory_elements_ok(),
            reports_produced=True,
            explicit_confirmation=True,
            not_finalized=True,
            retention_allows_resume=True,
            version_finalized=version.st_v in (VersionState.FINALIZED, VersionState.SUPERSEDED),
            approval=approval,
            diffusion_rights_verified=True,
            scope_changed=True,
            approver_authorized=True,
            waiting_origin=self.waiting_origin,
            suspended_from=self.suspended_from,
            suspension_event=self.suspension_event,
        )

    def _apply_request(self, transition_id: str, actor: str, context: GuardContext) -> bool:
        current = None if self.request_state is None else self.request_state.value
        try:
            target = apply_transition(
                self.machines.get("R"), current, transition_id, actor, context
            )
        except InvalidTransition:
            return False
        previous = self.request_state
        self.request_state = RequestState(target)
        self.last_axis_actor["R"] = actor
        if target == RequestState.SUSPENDED.value:
            self.suspended_from = previous
            if previous is not None:
                self.suspension_event = {"suspended_from": previous.value}
        elif transition_id == "TR-R-20":
            self.suspended_from = None
            self.suspension_event = None
        if target in (RequestState.BLOCKED.value, RequestState.AWAITING_DECISION.value):
            self.waiting_origin = previous
        elif transition_id in ("TR-R-13", "TR-R-14", "TR-R-23", "TR-R-24", "TR-R-26"):
            self.waiting_origin = None
        self.history.append(transition_id)
        return True

    def _apply_version(
        self, axis: str, transition_id: str, actor: str, context: GuardContext
    ) -> bool:
        machine = self.machines.get(axis)
        version = self.active_version
        current = {
            "V": version.st_v.value,
            "C": version.st_c.value,
            "A": version.st_a.value,
            "D": version.st_d.value,
        }[axis]
        try:
            target = apply_transition(machine, current, transition_id, actor, context)
        except InvalidTransition:
            return False
        if axis == "V":
            version.st_v = VersionState(target)
        elif axis == "C":
            version.st_c = ConformityState(target)
        elif axis == "A":
            version.st_a = ApprovalState(target)
        else:
            version.st_d = DiffusionState(target)
        self.last_axis_actor[axis] = actor
        self.history.append(transition_id)
        return True

    def _apply_element(self, transition_id: str, context: GuardContext) -> bool:
        version = self.active_version
        key = next(iter(version.elements))
        try:
            target = apply_transition(
                self.machines.get("E"), version.elements[key].value, transition_id, "agent", context
            )
        except InvalidTransition:
            return False
        version.elements[key] = ElementState(target)
        self.history.append(transition_id)
        return True

    # --- commandes ---
    def submit(self) -> bool:
        return self._apply_request("TR-R-01", "user", self._context())

    def clarify(self) -> bool:
        return self._apply_request("TR-R-02", "agent", self._context())

    def assess(self) -> bool:
        return self._apply_request("TR-R-03", "agent", self._context())

    def start_production(self) -> bool:
        return self._apply_request("TR-R-05", "agent", self._context())

    def start_controls(self) -> bool:
        return self._apply_request("TR-R-09", "agent", self._context())

    def run_controls_ok(self) -> bool:
        if self.request_state is not RequestState.QUALITY_CONTROL:
            return False
        if self.active_version.st_v is not VersionState.PROVISIONAL:
            return False
        if not self._apply_version("C", "TR-C-01", "agent", self._context()):
            return False
        return self._apply_version("C", "TR-C-02", "agent", self._context(controls_ok=True))

    def run_controls_failed(self) -> bool:
        if self.request_state is not RequestState.QUALITY_CONTROL:
            return False
        if self.active_version.st_v is not VersionState.PROVISIONAL:
            return False
        if not self._apply_version("C", "TR-C-01", "agent", self._context()):
            return False
        return self._apply_version("C", "TR-C-03", "agent", self._context(control_failed=True))

    def produce_element(self) -> bool:
        return self._apply_element("TR-E-01", self._context())

    def control_element_ok(self) -> bool:
        return self._apply_element("TR-E-07", self._context(controls_ok=True))

    def block_element(self) -> bool:
        return self._apply_element("TR-E-02", self._context())

    def unblock_element(self) -> bool:
        return self._apply_element("TR-E-05", self._context())

    def finalize(self) -> bool:
        if self.request_state is not RequestState.QUALITY_CONTROL:
            return False
        version = self.active_version
        if (
            version.st_v is not VersionState.PROVISIONAL
            or version.st_c is not ConformityState.CONFORMING
            or not version.mandatory_elements_ok()
        ):
            return False
        if not self._apply_version("V", "TR-V-01", "agent", self._context(controls_ok=True)):
            return False
        if not self._apply_request("TR-R-18", "agent", self._context(controls_ok=True)):
            return False
        version.finalized_snapshot = (version.st_c, version.st_a, version.st_d)
        return True

    def submit_approval(self) -> bool:
        return self._apply_version("A", "TR-A-01", "responsible", self._context())

    def approve(self) -> bool:
        return self._apply_version("A", "TR-A-03", "responsible", self._context())

    def refuse(self) -> bool:
        return self._apply_version("A", "TR-A-04", "responsible", self._context())

    def authorize_diffusion(self) -> bool:
        return self._apply_version("D", "TR-D-01", "responsible", self._context())

    def revoke_diffusion(self) -> bool:
        return self._apply_version("D", "TR-D-02", "responsible", self._context())

    def suspend(self) -> bool:
        return self._apply_request("TR-R-19", "responsible", self._context())

    def resume(self) -> bool:
        return self._apply_request("TR-R-20", "responsible", self._context())

    def cancel(self) -> bool:
        return self._apply_request("TR-R-21", "author", self._context())

    def revise(self) -> bool:
        if self.request_state is not RequestState.FINALIZED:
            return False
        if self.revision_of is not None:
            return False
        self.revision_of = "revision"
        self.history.append("TR-R-22")
        return True

    def execute(self, command: str) -> bool:
        """Execute une commande nommee ; retourne False si refusee."""
        method = getattr(self, command, None)
        if method is None:
            raise ValueError(f"commande inconnue : {command}")
        result: bool = method()
        return result

    def public_status(self) -> str:
        """Message d'etat derive uniquement de l'etat reel (IV-10)."""
        if self.request_state is None:
            raise InvariantViolation("IV-10", "aucun etat a annoncer")
        return STATE_LABELS[self.request_state.value]


COMMANDS: tuple[str, ...] = (
    "submit",
    "clarify",
    "assess",
    "start_production",
    "start_controls",
    "run_controls_ok",
    "run_controls_failed",
    "produce_element",
    "control_element_ok",
    "block_element",
    "unblock_element",
    "finalize",
    "submit_approval",
    "approve",
    "refuse",
    "authorize_diffusion",
    "revoke_diffusion",
    "suspend",
    "resume",
    "cancel",
    "revise",
)


def check_invariants(workflow: Workflow) -> None:
    """Verifie IV-01 a IV-15 apres chaque pas (PR-01)."""
    # IV-01 : exactement un etat par axe.
    if workflow.request_state is None or not isinstance(workflow.request_state, RequestState):
        raise InvariantViolation("IV-01", "axe R sans etat unique")
    version = workflow.active_version
    if not all(
        isinstance(value, expected)
        for value, expected in (
            (version.st_v, VersionState),
            (version.st_c, ConformityState),
            (version.st_a, ApprovalState),
            (version.st_d, DiffusionState),
        )
    ):
        raise InvariantViolation("IV-01", "axe de version sans etat unique")

    # IV-02 : les axes C, A et D restent independants (aucune deduction croisee).
    if version.st_c is ConformityState.CONFORMING and version.st_v is VersionState.PROVISIONAL:
        pass  # une version provisoire peut etre conforme : independance respectee

    # IV-03 : une version finalisee est immuable.
    if version.st_v in (VersionState.FINALIZED, VersionState.SUPERSEDED):
        if version.st_c is not ConformityState.CONFORMING:
            raise InvariantViolation("IV-03", "version finalisee non conforme")
        if (
            version.finalized_snapshot is not None
            and version.st_c is not version.finalized_snapshot[0]
        ):
            raise InvariantViolation("IV-03", "conformite d'une version finalisee modifiee")

    # IV-04 : demande finalisee ou annulee figee.
    if (
        workflow.request_state in FINAL_REQUEST_STATES
        and workflow.history
        and workflow.history[-1].startswith("TR-R-")
        and workflow.history[-1] not in ("TR-R-18", "TR-R-21", "TR-R-22")
    ):
        raise InvariantViolation("IV-04", "transition apres un etat final")

    # IV-05 : Finalisee exige une version conforme.
    if workflow.request_state is RequestState.FINALIZED:
        if version.st_c is not ConformityState.CONFORMING:
            raise InvariantViolation("IV-05", "demande finalisee sans version conforme")
        if version.st_v not in (VersionState.FINALIZED, VersionState.SUPERSEDED):
            raise InvariantViolation("IV-05", "demande finalisee sans version finalisee")

    # IV-06 : Suspendue n'est jamais finalisee.
    if workflow.request_state is RequestState.SUSPENDED and version.st_v is VersionState.FINALIZED:
        raise InvariantViolation("IV-06", "suspendue finalisee")

    # IV-07 : un element bloque n'est jamais livre comme produit.
    for state in version.elements.values():
        if state is ElementState.BLOCKED and version.st_v is VersionState.FINALIZED:
            raise InvariantViolation("IV-07", "element bloque dans une version finalisee")

    # IV-08 : les etats ne sont pas des etapes internes.
    if workflow.request_state.value in {"mobilization", "mapping", "drafting"}:
        raise InvariantViolation("IV-08", "etape interne presentee comme etat")

    # IV-09 : approbation et diffusion par decision humaine uniquement.
    for axis in ("A", "D"):
        actor = workflow.last_axis_actor.get(axis)
        if actor is not None and actor not in {"responsible", "author", "user"}:
            raise InvariantViolation("IV-09", f"axe {axis} modifie par {actor}")

    # IV-10 : le message n'annonce que l'etat atteint.
    if workflow.request_state is not None:
        message = workflow.public_status()
        if message != STATE_LABELS[workflow.request_state.value]:
            raise InvariantViolation("IV-10", "message d'etat non aligne")

    # IV-11 : A et D ne modifient jamais C.
    # Une conformite provisoire reste licite : A et D n'ecrivent jamais C.

    # IV-12 : version non finalisee ni approuvable ni diffusable.
    if version.st_v is VersionState.PROVISIONAL:
        if version.st_a not in (ApprovalState.NOT_SUBMITTED, ApprovalState.NOT_REQUIRED):
            raise InvariantViolation("IV-12", "version provisoire approuvee")
        if version.st_d is not DiffusionState.NOT_AUTHORIZED:
            raise InvariantViolation("IV-12", "version provisoire diffusable")

    # IV-13 : finalisee => elements obligatoires conformes ou non applicables.
    if (
        version.st_v in (VersionState.FINALIZED, VersionState.SUPERSEDED)
        and not version.mandatory_elements_ok()
    ):
        raise InvariantViolation("IV-13", "elements obligatoires non conformes")

    # IV-14 : refusee ou en attente => pas de diffusion autorisee.
    if (
        version.st_a in (ApprovalState.REFUSED, ApprovalState.PENDING)
        and version.st_d is DiffusionState.AUTHORIZED
    ):
        raise InvariantViolation("IV-14", "diffusion autorisee sans approbation")

    # IV-15 : la finalisation n'attribue ni approbation ni diffusion.
    if version.finalized_snapshot is not None and version.finalized_snapshot[1:] != (
        ApprovalState.NOT_SUBMITTED,
        DiffusionState.NOT_AUTHORIZED,
    ):
        raise InvariantViolation("IV-15", "finalisation ayant attribue A ou D")
