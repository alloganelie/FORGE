"""Facade applicative du module MOD-02 (governance).

Le service orchestre les ports purs (validation, formules) et le depot
PostgreSQL. Aucune logique metier n'est implementee dans l'interface HTTP.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Final
from uuid import UUID

from sqlalchemy import Connection

from agent.anomalies.api import AUTOFIX_FUNCTIONS
from agent.governance.core.approval import require_draft, require_future_effective_date
from agent.governance.core.impact import ImpactReport
from agent.governance.core.roles import require_responsible
from agent.governance.core.types import (
    Actor,
    ArtifactStatus,
    ArtifactType,
    ArtifactVersion,
    GovernanceDenied,
    InvalidEffectiveDate,
    InvalidTransition,
    Pin,
    ValidationFailure,
)
from agent.governance.core.validation import (
    Observation,
    ValidationContext,
    ValidationReport,
    run_pipeline,
)
from agent.governance.infra.formulas import CelFormulaEngine
from agent.governance.infra.repository import (
    approve_version,
    get_user,
    get_version,
    insert_draft,
    insert_observations,
    insert_pin,
    list_pins,
    list_users,
    list_versions,
    requests_pinned_to,
)
from agent.governance.infra.schemas import JsonSchemaStore
from agent.ledger.api import canonicalize
from agent.platform.api import Clock, SystemClock

MODULE_ID: Final[str] = "MOD-02"
MODULE_NAME: Final[str] = "governance"


class GovernanceValidationFailure(ValidationFailure):
    """Le pipeline de validation refuse l'artefact."""

    def __init__(self, report: ValidationReport) -> None:
        super().__init__("La validation de l'artefact a echoue.")
        self.report = report


@dataclass(frozen=True, slots=True)
class ModuleInfo:
    module_id: str
    name: str


def module_info() -> ModuleInfo:
    return ModuleInfo(module_id=MODULE_ID, name=MODULE_NAME)


def _iso(value: datetime) -> str:
    return value.astimezone(UTC).isoformat(timespec="microseconds")


class GovernanceService:
    """Operations de gouvernance pour une connexion et un espace de travail."""

    def __init__(
        self,
        connection: Connection,
        workspace_id: UUID,
        *,
        clock: Clock | None = None,
        schema_store: JsonSchemaStore | None = None,
        formula_engine: CelFormulaEngine | None = None,
    ) -> None:
        self.connection = connection
        self.workspace_id = workspace_id
        self.clock = clock if clock is not None else SystemClock()
        self.schema_store = schema_store if schema_store is not None else JsonSchemaStore()
        self.formula_engine = formula_engine if formula_engine is not None else CelFormulaEngine()

    def actor(self, user_id: UUID) -> Actor:
        row = get_user(self.connection, self.workspace_id, user_id)
        if row is None:
            raise GovernanceDenied("Acteur inconnu ou inactif dans cet espace de travail.")
        return Actor(id=row["id"], role=str(row["role"]), display_name=str(row["display_name"]))

    def list_artifacts(self) -> tuple[ArtifactVersion, ...]:
        return list_versions(self.connection, self.workspace_id)

    def list_actors(self) -> tuple[Actor, ...]:
        return tuple(
            Actor(id=row["id"], role=str(row["role"]), display_name=str(row["display_name"]))
            for row in list_users(self.connection, self.workspace_id)
        )

    def get_artifact(self, version_id: UUID) -> ArtifactVersion:
        version = get_version(self.connection, self.workspace_id, version_id)
        if version is None:
            raise GovernanceDenied("Version de gouvernance introuvable.")
        return version

    def create_draft(
        self,
        actor: Actor,
        artifact_type: str,
        artifact_key: str,
        content: Mapping[str, Any],
        motif: str,
    ) -> ArtifactVersion:
        require_responsible(actor)
        try:
            parsed_type = ArtifactType(artifact_type)
        except ValueError as exc:
            raise GovernanceDenied(f"Type d'artefact inconnu : {artifact_type}") from exc
        if not artifact_key.strip():
            raise GovernanceDenied("La cle de l'artefact est obligatoire.")
        content_dict = dict(content)
        content_hash = hashlib.sha256(canonicalize(content_dict)).hexdigest()
        return insert_draft(
            self.connection,
            workspace_id=self.workspace_id,
            artifact_type=parsed_type,
            artifact_key=artifact_key,
            content=content_dict,
            content_hash=content_hash,
            created_by=actor.id,
            created_at=self.clock.now(),
            motif=motif,
        )

    def _approved(self) -> tuple[ArtifactVersion, ...]:
        return list_versions(self.connection, self.workspace_id, status=ArtifactStatus.APPROVED)

    def impact(self, version_id: UUID) -> ImpactReport:
        pinned = requests_pinned_to(self.connection, version_id)
        version = self.get_artifact(version_id)
        dependent_models: set[str] = set()
        dependent_controls: set[str] = set()
        approved_rules = [
            item for item in self._approved() if item.artifact_type is ArtifactType.RULE_PACK
        ]
        if version.artifact_type is ArtifactType.TEMPLATE:
            for item in approved_rules:
                for deliverable_type in item.content.get("deliverable_types", []):
                    if not isinstance(deliverable_type, Mapping):
                        continue
                    template = deliverable_type.get("template")
                    if (
                        isinstance(template, Mapping)
                        and str(template.get("key", "")) == version.artifact_key
                    ):
                        dependent_models.add(str(deliverable_type.get("key", "")))
        if version.artifact_type is ArtifactType.CONTROL_CATALOG:
            control_ids = {
                str(control.get("id", ""))
                for control in version.content.get("controls", [])
                if isinstance(control, Mapping)
            }
            for item in approved_rules:
                for deliverable_type in item.content.get("deliverable_types", []):
                    if not isinstance(deliverable_type, Mapping):
                        continue
                    controls = {
                        str(control) for control in deliverable_type.get("mandatory_controls", [])
                    }
                    if controls & control_ids:
                        dependent_controls.add(str(deliverable_type.get("key", "")))
                        template = deliverable_type.get("template")
                        if isinstance(template, Mapping):
                            dependent_models.add(str(template.get("key", "")))
        return ImpactReport(
            replaced_version_id=version_id,
            pinned_requests=pinned,
            dependent_models=tuple(sorted(dependent_models)),
            dependent_controls=tuple(sorted(dependent_controls)),
        )

    def validate(self, version_id: UUID) -> ValidationReport:
        version = self.get_artifact(version_id)
        approved = self._approved()
        templates = {
            item.artifact_key: item.content
            for item in approved
            if item.artifact_type is ArtifactType.TEMPLATE
        }
        controls: dict[str, Mapping[str, Any]] = {}
        for item in approved:
            if item.artifact_type is ArtifactType.CONTROL_CATALOG:
                for control in item.content.get("controls", []):
                    if isinstance(control, Mapping):
                        controls[str(control.get("id", ""))] = control
        sources = {
            str(source.get("key", ""))
            for item in approved
            if item.artifact_type is ArtifactType.SOURCE_REGISTRY
            for source in item.content.get("sources", [])
            if isinstance(source, Mapping)
        }
        transformations = {
            str(transformation.get("id", ""))
            for item in approved
            if item.artifact_type is ArtifactType.RULE_PACK
            for transformation in item.content.get("transformations", [])
            if isinstance(transformation, Mapping)
        }
        units = {
            str(unit)
            for item in approved
            if item.artifact_type is ArtifactType.RULE_PACK
            for calculation in item.content.get("calculations", [])
            if isinstance(calculation, Mapping)
            for unit in [
                calculation.get("unit_out"),
                *[
                    entry.get("unit")
                    for entry in calculation.get("inputs", [])
                    if isinstance(entry, Mapping)
                ],
            ]
            if isinstance(unit, str) and unit
        }
        context = ValidationContext(
            schema_validator=self.schema_store,
            formula_engine=self.formula_engine,
            templates=templates,
            controls=controls,
            sources=frozenset(sources),
            transformations=frozenset(transformations),
            units=frozenset(units),
            autofix_functions=frozenset(AUTOFIX_FUNCTIONS),
            impact=self.impact(version_id),
        )
        report = run_pipeline(version.artifact_type, version.content, context)
        if report.observations:
            insert_observations(
                self.connection,
                workspace_id=self.workspace_id,
                version_id=version_id,
                observations=report.observations,
                at=self.clock.now(),
            )
        return report

    def approve(
        self,
        actor: Actor,
        version_id: UUID,
        effective_from: datetime,
        reason: str,
    ) -> ArtifactVersion:
        require_responsible(actor)
        if effective_from.tzinfo is None:
            raise InvalidEffectiveDate("La date d'effet doit porter un fuseau horaire.")
        now = self.clock.now()
        effective = effective_from.astimezone(UTC)
        require_future_effective_date(_iso(effective), _iso(now))
        version = self.get_artifact(version_id)
        require_draft(version.status)
        report = self.validate(version_id)
        if not report.ok:
            raise GovernanceValidationFailure(report)
        return approve_version(
            self.connection,
            workspace_id=self.workspace_id,
            version_id=version_id,
            actor_id=actor.id,
            effective_from=effective,
            reason=reason,
            approved_at=now,
        )

    def pin_request(
        self, actor: Actor, request_id: UUID, version_ids: tuple[UUID, ...]
    ) -> tuple[Pin, ...]:
        require_responsible(actor)
        for version_id in version_ids:
            version = self.get_artifact(version_id)
            if version.status is not ArtifactStatus.APPROVED:
                raise InvalidTransition("Seule une version approuvee peut etre epinglee.")
            insert_pin(
                self.connection,
                workspace_id=self.workspace_id,
                request_id=request_id,
                version_id=version_id,
                pinned_by=actor.id,
                pinned_at=self.clock.now(),
            )
        return list_pins(self.connection, self.workspace_id, request_id)

    def pins_for_request(self, request_id: UUID) -> tuple[Pin, ...]:
        return list_pins(self.connection, self.workspace_id, request_id)

    def source_authorizations(self, version_id: UUID, source_key: str) -> dict[str, Any]:
        version = self.get_artifact(version_id)
        if version.artifact_type is not ArtifactType.SOURCE_REGISTRY:
            raise GovernanceDenied("Cet artefact n'est pas un registre des sources.")
        for source in version.content.get("sources", []):
            if isinstance(source, Mapping) and str(source.get("key", "")) == source_key:
                authorizations = source.get("authorizations")
                if not isinstance(authorizations, Mapping):
                    raise GovernanceDenied("Autorisations absentes pour cette source.")
                return {
                    str(key): dict(value) if isinstance(value, Mapping) else value
                    for key, value in authorizations.items()
                }
        raise GovernanceDenied(f"Source inconnue dans le registre : {source_key}")

    def evaluate_rule(self, version_id: UUID, rule_id: str, inputs: Mapping[str, Any]) -> Any:
        version = self.get_artifact(version_id)
        for rule in version.content.get("rules", []):
            if isinstance(rule, Mapping) and str(rule.get("id", "")) == rule_id:
                formula = rule.get("formula")
                if not isinstance(formula, str):
                    raise GovernanceDenied("Formule absente pour cette regle.")
                return self.formula_engine.evaluate(formula, inputs)
        raise GovernanceDenied(f"Regle inconnue : {rule_id}")


__all__ = [
    "ArtifactStatus",
    "ArtifactType",
    "ArtifactVersion",
    "GovernanceDenied",
    "GovernanceService",
    "GovernanceValidationFailure",
    "InvalidEffectiveDate",
    "InvalidTransition",
    "ModuleInfo",
    "Observation",
    "module_info",
]
