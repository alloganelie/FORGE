"""Types purs de la gouvernance (MOD-02, ET-053)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any
from uuid import UUID


class ArtifactType(StrEnum):
    RULE_PACK = "rule_pack"
    TEMPLATE = "template"
    SOURCE_REGISTRY = "source_registry"
    CONTROL_CATALOG = "control_catalog"


class ArtifactStatus(StrEnum):
    DRAFT = "draft"
    APPROVED = "approved"
    RETIRED = "retired"


@dataclass(frozen=True, slots=True)
class Actor:
    """Acteur authentifie par la couche d'identite ; le role vient de la base."""

    id: UUID
    role: str
    display_name: str = ""

    @property
    def is_responsible(self) -> bool:
        return self.role == "responsible"


@dataclass(frozen=True, slots=True)
class ArtifactVersion:
    id: UUID
    workspace_id: UUID
    artifact_type: ArtifactType
    artifact_key: str
    version: int
    content: dict[str, Any]
    content_hash: str
    status: ArtifactStatus
    effective_from: str | None
    created_by: UUID
    created_at: str
    approved_at: str | None = None
    approved_by_decision: UUID | None = None
    schema_version: str = "v1"
    motif: str = ""


@dataclass(frozen=True, slots=True)
class Pin:
    request_id: UUID
    version_id: UUID
    pinned_at: str
    pinned_by: UUID


class GovernanceError(RuntimeError):
    """Erreur de gouvernance ; le message est communicable."""


class GovernanceDenied(GovernanceError):
    """Acteur non habilite : refus par defaut (RB-097, RF-250, RF-254)."""


class ArtifactNotFound(GovernanceError):
    """Artefact ou version introuvable."""


class InvalidTransition(GovernanceError):
    """Transition de statut interdite (GV-01, GV-02)."""


class ValidationFailure(GovernanceError):
    """Validation du pipeline en echec."""


class InvalidEffectiveDate(GovernanceError):
    """Date d'effet absente ou retrospective (RB-104)."""
