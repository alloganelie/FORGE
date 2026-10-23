"""Regles pures d'approbation et de non-retroactivite (GV-02 a GV-04, RB-104)."""

from __future__ import annotations

from agent.governance.core.types import ArtifactStatus, InvalidEffectiveDate, InvalidTransition


def require_draft(status: ArtifactStatus) -> None:
    if status is not ArtifactStatus.DRAFT:
        raise InvalidTransition("Seul un brouillon peut etre approuve.")


def require_future_effective_date(effective_from: str, now_iso: str) -> None:
    """Compare deux instants ISO 8601 UTC ; une date passee est retrospective."""
    if not effective_from or effective_from <= now_iso:
        raise InvalidEffectiveDate(
            "La date d'effet doit etre explicite et strictement posterieure a maintenant."
        )


def require_impact(impact_ready: bool) -> None:
    if not impact_ready:
        raise InvalidTransition("L'analyse d'impact doit etre produite avant l'approbation.")
