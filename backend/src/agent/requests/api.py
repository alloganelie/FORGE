"""Service applicatif de la demande et de la faisabilite (MOD-03, MOD-05, MS-2)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import Connection

from agent.conversation.api import STATE_LABELS, render, status_message
from agent.governance.api import (
    ArtifactType,
    ArtifactVersion,
    GovernanceService,
)
from agent.lifecycle.api import GuardContext, apply_request_transition, load_machines
from agent.llm_gateway.api import (
    LlmAdapter,
    LlmError,
    LlmFailure,
    Lt01Output,
    Lt02Output,
    ReplayAdapter,
    run_task,
)
from agent.platform.api import Clock, SystemClock
from agent.requests.core.models import (
    Clarification,
    FeasibilityPart,
    FeasibilityReport,
    RequestDenied,
    RequestView,
    SplitProposal,
    StatusSnapshot,
    Submission,
    TrackingItem,
)
from agent.requests.infra import repository as repo

AUTHORIZED_SUBMIT_ROLES = frozenset({"user", "responsible"})


class RequestService:
    def __init__(
        self,
        connection: Connection,
        workspace_id: UUID,
        *,
        clock: Clock | None = None,
        adapter: LlmAdapter | None = None,
    ) -> None:
        self.connection = connection
        self.workspace_id = workspace_id
        self.clock = clock if clock is not None else SystemClock()
        self.adapter = adapter if adapter is not None else ReplayAdapter({})
        self.governance = GovernanceService(connection, workspace_id, clock=self.clock)

    def _actor(self, actor_id: UUID) -> Any:
        return self.governance.actor(actor_id)

    def _get(self, request_id: UUID) -> RequestView:
        request = repo.get_request(self.connection, self.workspace_id, request_id)
        if request is None:
            raise RequestDenied("Demande introuvable.")
        return request

    def _transition(
        self, request: RequestView, transition_id: str, actor_id: UUID, context: GuardContext
    ) -> RequestView:
        apply_request_transition(
            self.connection,
            load_machines(),
            request_id=request.id,
            transition_id=transition_id,
            actor="agent",
            actor_id=actor_id,
            workspace_id=self.workspace_id,
            at=self.clock.now(),
            context=context,
        )
        return self._get(request.id)

    def _clarification_questions(
        self, output: Lt01Output, request_id: UUID, actor_id: UUID
    ) -> tuple[Clarification, ...]:
        blocking = [item for item in output.ambiguities if item.blocking]
        if not blocking:
            return ()
        proposals: dict[str, Any] = {}
        try:
            lt02: Any = run_task(
                self.connection,
                task_id="LT-02",
                request_id=request_id,
                workspace_id=self.workspace_id,
                inputs={"ambiguities": [item.model_dump() for item in blocking]},
                adapter=self.adapter,
                clock=self.clock,
            )
            if isinstance(lt02, Lt02Output):
                proposals = {item.parameter: item for item in lt02.questions}
        except LlmError:
            proposals = {}
        created: list[Clarification] = []
        for ambiguity in blocking:
            proposal = proposals.get(ambiguity.parameter)
            created.append(
                repo.insert_clarification(
                    self.connection,
                    workspace_id=self.workspace_id,
                    request_id=request_id,
                    parameter=ambiguity.parameter,
                    question_text=(
                        proposal.text
                        if proposal is not None
                        else f"Pouvez-vous preciser le parametre {ambiguity.parameter} ?"
                    ),
                    why_needed=(
                        proposal.why_needed
                        if proposal is not None
                        else "Cette precision conditionne la validite du livrable."
                    ),
                    blocking=True,
                    at=self.clock.now(),
                )
            )
        return tuple(created)

    def submit(self, actor_id: UUID, text: str, *, diagnostic_only: bool = False) -> Submission:
        actor = self._actor(actor_id)
        if actor.role not in AUTHORIZED_SUBMIT_ROLES:
            raise RequestDenied("Vous n'etes pas autorise a soumettre ce type de demande.")
        output = run_task(
            self.connection,
            task_id="LT-01",
            request_id=None,
            workspace_id=self.workspace_id,
            inputs={"text": text},
            adapter=self.adapter,
            output_model=Lt01Output,
            clock=self.clock,
        )
        for parameter in output.parameters:
            if parameter.justification_quote and parameter.justification_quote not in text:
                raise LlmError(LlmFailure.INVALID_OUTPUT, "citation absente du texte")
        analysis = output.model_dump(mode="json")
        if output.multiple_deliverables_detected:
            split = repo.insert_split(
                self.connection,
                workspace_id=self.workspace_id,
                author_id=actor_id,
                original_text=text,
                parts=(f"Livrable 1 : {text}", f"Livrable 2 : {text}"),
                at=self.clock.now(),
            )
            return Submission(request=None, split=split, analysis=analysis)
        request = repo.insert_request(
            self.connection,
            workspace_id=self.workspace_id,
            author_id=actor_id,
            text_value=text,
            deliverable_type=output.candidate_type,
            target_format=output.requested_format,
            diagnostic_only=diagnostic_only,
            at=self.clock.now(),
        )
        repo.insert_analysis(
            self.connection,
            workspace_id=self.workspace_id,
            request_id=request.id,
            payload=analysis,
            at=self.clock.now(),
        )
        for parameter in output.parameters:
            repo.insert_parameter(
                self.connection,
                workspace_id=self.workspace_id,
                request_id=request.id,
                name=parameter.name,
                value=parameter.value,
                justification_quote=parameter.justification_quote,
                source="user",
                quality_status="candidate",
                at=self.clock.now(),
            )
        repo.insert_message(
            self.connection,
            workspace_id=self.workspace_id,
            request_id=request.id,
            role="system",
            template_key="request_received",
            text_value=render("request_received", state=STATE_LABELS[request.state]),
            at=self.clock.now(),
        )
        questions = self._clarification_questions(output, request.id, actor_id)
        if questions:
            request = self._transition(
                request, "TR-R-02", actor_id, GuardContext(ambiguity_significant=True)
            )
            repo.insert_message(
                self.connection,
                workspace_id=self.workspace_id,
                request_id=request.id,
                role="agent",
                template_key="clarification_requested",
                text_value=render("clarification_requested", state=STATE_LABELS[request.state]),
                at=self.clock.now(),
            )
        return Submission(request=request, split=None, questions=questions, analysis=analysis)

    def clarify(self, request_id: UUID, actor_id: UUID, answers: dict[str, str]) -> RequestView:
        self._actor(actor_id)
        request = self._get(request_id)
        for clarification in repo.list_clarifications(
            self.connection, self.workspace_id, request_id
        ):
            answer = answers.get(clarification.parameter)
            if answer is None or clarification.status == "answered":
                continue
            repo.answer_clarification(
                self.connection,
                workspace_id=self.workspace_id,
                clarification_id=clarification.id,
                answer=answer,
                at=self.clock.now(),
            )
            repo.insert_parameter(
                self.connection,
                workspace_id=self.workspace_id,
                request_id=request_id,
                name=clarification.parameter,
                value=answer,
                justification_quote=answer,
                source="user",
                quality_status="candidate",
                at=self.clock.now(),
            )
        remaining = [
            item
            for item in repo.list_clarifications(self.connection, self.workspace_id, request_id)
            if item.blocking and item.status == "open"
        ]
        if not remaining and request.state == "clarifying":
            request = self._transition(
                request, "TR-R-04", actor_id, GuardContext(answers_sufficient=True)
            )
        return request

    def _find_assets(
        self, request: RequestView
    ) -> tuple[
        ArtifactVersion | None,
        ArtifactVersion | None,
        ArtifactVersion | None,
        ArtifactVersion | None,
    ]:
        approved = self.governance.approved_versions()
        deliverable_type = request.deliverable_type or ""
        template = next(
            (
                item
                for item in approved
                if item.artifact_type is ArtifactType.TEMPLATE
                and (
                    item.artifact_key == deliverable_type
                    or item.content.get("template", {}).get("key") == deliverable_type
                )
            ),
            None,
        )
        rule = next(
            (
                item
                for item in approved
                if item.artifact_type is ArtifactType.RULE_PACK
                and any(
                    isinstance(deliverable, dict)
                    and str(deliverable.get("key", "")) == deliverable_type
                    for deliverable in item.content.get("deliverable_types", [])
                )
            ),
            None,
        )
        registry = next(
            (item for item in approved if item.artifact_type is ArtifactType.SOURCE_REGISTRY),
            None,
        )
        controls = next(
            (item for item in approved if item.artifact_type is ArtifactType.CONTROL_CATALOG),
            None,
        )
        return template, rule, registry, controls

    def assess_feasibility(
        self, request_id: UUID, actor_id: UUID, *, diagnostic_only: bool = False
    ) -> FeasibilityReport:
        self._actor(actor_id)
        request = self._get(request_id)
        if request.state == "received":
            request = self._transition(
                request, "TR-R-03", actor_id, GuardContext(parameters_sufficient=True)
            )
        elif request.state == "clarifying":
            open_questions = [
                item
                for item in repo.list_clarifications(self.connection, self.workspace_id, request_id)
                if item.blocking and item.status == "open"
            ]
            if open_questions:
                return self._to_clarify(request, "information manquante", "MB-10")
            request = self._transition(
                request, "TR-R-04", actor_id, GuardContext(answers_sufficient=True)
            )

        template, rule, registry, controls = self._find_assets(request)
        parts: list[FeasibilityPart] = []

        def add(dimension: str, verdict: str, code: str, public: str, internal: str = "") -> None:
            parts.append(
                FeasibilityPart(
                    dimension=dimension,
                    verdict=verdict,
                    reason_code=code,
                    reason_public=public,
                    reason_internal=internal or public,
                )
            )

        add(
            "model",
            "realizable" if template else "blocked",
            "OK" if template else "MB-01",
            "Le modele documentaire existe."
            if template
            else "Aucun modele approuve ne permet de produire ce livrable.",
            "" if template else "Modele documentaire absent.",
        )
        add(
            "rules",
            "realizable" if rule else "blocked",
            "OK" if rule else "MB-01",
            "Les regles applicables existent."
            if rule
            else "Aucune regle approuvee ne permet de produire ce livrable.",
            "" if rule else "Lot de regles absent.",
        )
        add(
            "information",
            "realizable" if request.deliverable_type else "to_clarify",
            "OK" if request.deliverable_type else "MB-10",
            "Les informations minimales sont disponibles."
            if request.deliverable_type
            else "Le type de livrable reste a preciser.",
        )
        uncertain = False
        access_blocked = False
        blocked_source = ""
        if registry is not None:
            for source in registry.content.get("sources", []):
                if not isinstance(source, dict):
                    continue
                authorizations = source.get("authorizations")
                if not isinstance(authorizations, dict):
                    continue
                use = authorizations.get("use")
                access = authorizations.get("access")
                if isinstance(use, dict) and use.get("uncertain") is True:
                    uncertain = True
                if isinstance(access, dict) and access.get("allowed") is False:
                    access_blocked = True
                    blocked_source = str(source.get("key", ""))
            if uncertain:
                add(
                    "authorizations",
                    "suspended",
                    "MB-13",
                    "Les droits sur une source necessaire sont incertains.",
                    "Droits incertains sur le registre.",
                )
            elif access_blocked:
                add(
                    "authorizations",
                    "blocked",
                    "MB-13",
                    "Une source necessaire n'est pas disponible pour cette demande.",
                    f"Source protegee indisponible : {blocked_source}.",
                )
            else:
                add("authorizations", "realizable", "OK", "Les autorisations sont disponibles.")
        else:
            add(
                "authorizations",
                "blocked",
                "MB-13",
                "Une source necessaire n'est pas disponible pour cette demande.",
                "Registre des sources absent.",
            )
        mandatory = (
            [
                item
                for item in template.content.get("elements", [])
                if isinstance(item, dict) and item.get("mandatory")
            ]
            if template
            else []
        )
        add(
            "requirements",
            "realizable" if mandatory else "to_clarify",
            "OK",
            "Les exigences obligatoires sont identifiees.",
        )
        add("contradictions", "realizable", "OK", "Aucune contradiction connue n'a ete identifiee.")
        allowed_formats: list[str] = []
        if rule is not None:
            for deliverable in rule.content.get("deliverable_types", []):
                if (
                    isinstance(deliverable, dict)
                    and str(deliverable.get("key", "")) == request.deliverable_type
                ):
                    allowed_formats = [str(item) for item in deliverable.get("allowed_formats", [])]
        format_blocked = bool(
            request.target_format
            and allowed_formats
            and request.target_format not in allowed_formats
        )
        add(
            "preconditions",
            "blocked" if format_blocked else "realizable",
            "MB-12" if format_blocked else "OK",
            "Le format demande n'est pas autorise pour ce type de livrable."
            if format_blocked
            else "Les conditions prealables sont satisfaites.",
        )
        verdicts = {item.verdict for item in parts}
        outcome = (
            "blocked"
            if "blocked" in verdicts
            else "suspended"
            if "suspended" in verdicts
            else "to_clarify"
            if "to_clarify" in verdicts
            else "realizable"
        )
        version_ids: list[UUID] = []
        if not diagnostic_only and outcome == "realizable":
            version_ids = [
                item.id for item in (template, rule, registry, controls) if item is not None
            ]
            if version_ids:
                self.governance.pin_for_request(request_id, tuple(version_ids), actor_id)
        report = repo.insert_report(
            self.connection,
            workspace_id=self.workspace_id,
            request_id=request_id,
            outcome=outcome,
            parts=tuple(parts),
            pinned_version_ids=tuple(version_ids),
            at=self.clock.now(),
        )
        if not diagnostic_only:
            if outcome == "realizable":
                self._transition(
                    request, "TR-R-05", actor_id, GuardContext(feasible_at_least_in_part=True)
                )
            elif outcome == "blocked":
                self._transition(request, "TR-R-06", actor_id, GuardContext(no_part_feasible=True))
            else:
                self._transition(
                    request,
                    "TR-R-07",
                    actor_id,
                    GuardContext(decision_uncovered_or_rights_uncertain=True),
                )
        return report

    def _to_clarify(self, request: RequestView, public: str, code: str) -> FeasibilityReport:
        part = FeasibilityPart(
            dimension="information",
            verdict="to_clarify",
            reason_code=code,
            reason_public=public,
            reason_internal=public,
        )
        return repo.insert_report(
            self.connection,
            workspace_id=self.workspace_id,
            request_id=request.id,
            outcome="to_clarify",
            parts=(part,),
            pinned_version_ids=(),
            at=self.clock.now(),
        )

    def status(self, request_id: UUID, actor_id: UUID) -> StatusSnapshot:
        actor = self._actor(actor_id)
        request = self._get(request_id)
        report = repo.latest_report(self.connection, self.workspace_id, request_id)
        clarifications = repo.list_clarifications(self.connection, self.workspace_id, request_id)
        responsible = actor.role == "responsible"
        reasons = [report.reason_for(responsible)] if report is not None else []
        expected = tuple(item.question_text for item in clarifications if item.status == "open")
        if report is not None and report.outcome == "suspended":
            expected = (*expected, "Une decision de la personne responsable est attendue.")
        next_action = (
            "Repondre aux questions de clarification." if expected else "Poursuivre le traitement."
        )
        label = STATE_LABELS.get(request.state, request.state)
        return StatusSnapshot(
            request_id=request.id,
            request_state=request.state,
            request_label=label,
            steps_done=tuple(
                step
                for step in ("reception", "comprehension", "faisabilite")
                if step != "faisabilite" or report is not None
            ),
            current_step=label,
            reasons=tuple(reasons),
            expected=expected,
            next_action=next_action,
            statuses={
                "C": "non evaluee",
                "A": "non soumise",
                "D": "non autorisee",
                "V": "provisoire",
            },
            items=repo.list_items(self.connection, self.workspace_id, request_id),
            message=status_message(request.state, next_action, reasons[0] if reasons else ""),
            provisional=True,
        )

    def history(self, request_id: UUID, actor_id: UUID) -> tuple[dict[str, Any], ...]:
        self._actor(actor_id)
        self._get(request_id)
        return repo.list_messages(self.connection, self.workspace_id, request_id)

    def add_tracking_item(self, request_id: UUID, item_key: str, label: str, state: str) -> None:
        repo.insert_item(
            self.connection,
            workspace_id=self.workspace_id,
            request_id=request_id,
            item_key=item_key,
            label=label,
            state=state,
            at=self.clock.now(),
        )

    def confirm_split(self, split_id: UUID, actor_id: UUID) -> tuple[RequestView, ...]:
        self._actor(actor_id)
        split = repo.get_split(self.connection, self.workspace_id, split_id)
        if split is None or split.status != "proposed":
            raise RequestDenied("Proposition de scission introuvable ou deja traitee.")
        created = tuple(
            repo.insert_request(
                self.connection,
                workspace_id=self.workspace_id,
                author_id=actor_id,
                text_value=part,
                deliverable_type=None,
                target_format=None,
                diagnostic_only=False,
                at=self.clock.now(),
            )
            for part in split.parts
        )
        repo.confirm_split(self.connection, self.workspace_id, split_id, self.clock.now())
        return created

    def reason_for(self, report: FeasibilityReport, actor_id: UUID) -> str:
        return report.reason_for(self._actor(actor_id).role == "responsible")


__all__ = [
    "FeasibilityPart",
    "FeasibilityReport",
    "RequestDenied",
    "RequestService",
    "RequestView",
    "SplitProposal",
    "StatusSnapshot",
    "Submission",
    "TrackingItem",
]
