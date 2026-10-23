"""Autorisations de gouvernance (RB-097 a RB-108, RF-250, RF-254)."""

from __future__ import annotations

from agent.governance.core.types import Actor, GovernanceDenied

RESPONSIBLE = "responsible"


def require_responsible(actor: Actor) -> None:
    """Seule la personne responsable modifie les artefacts (refus par defaut)."""
    if actor.role != RESPONSIBLE:
        raise GovernanceDenied(
            "Seule la personne responsable peut modifier un artefact de gouvernance."
        )
