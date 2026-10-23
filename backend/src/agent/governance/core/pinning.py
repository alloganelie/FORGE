"""Epinglage par demande (ET-059, ET-060, RF-028, RF-185)."""

from __future__ import annotations

from agent.governance.core.types import ArtifactStatus, ArtifactVersion, GovernanceError


class PinError(GovernanceError):
    pass


def require_approved(version: ArtifactVersion) -> None:
    if version.status is not ArtifactStatus.APPROVED:
        raise PinError("Seule une version approuvee peut etre epinglee.")


def resolve_artifact(
    artifact_type: str, pins: tuple[ArtifactVersion, ...], versions: tuple[ArtifactVersion, ...]
) -> ArtifactVersion:
    """Une lecture de regle passe par l'epinglage, jamais par la derniere version."""
    for version in versions:
        if str(version.artifact_type) == artifact_type and version.id in {pin.id for pin in pins}:
            return version
    raise PinError("Aucune version epinglee pour ce type d'artefact.")
