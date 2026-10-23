"""Gabarits de messages d'etat, versionnes et en francais (ET-233 a ET-244)."""

from __future__ import annotations

from typing import Final

TEMPLATE_VERSION: Final[str] = "v1"

STATE_LABELS: Final[dict[str, str]] = {
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

TEMPLATES: Final[dict[str, str]] = {
    "request_received": "Votre demande a ete enregistree. Etat : {state}.",
    "clarification_question": "Question : {question}",
    "clarification_requested": "Une clarification est necessaire. Etat : {state}.",
    "status": "Etat de la demande : {state}. {next_action}",
    "status_blocked": "La demande est bloquee. Motif : {reason}",
    "status_producing": (
        "La demande est en production. Aucun resultat n'est annonce avant les controles."
    ),
    "status_history": "Historique de la demande disponible.",
}

FORBIDDEN_STATE_WORDS: Final[tuple[str, ...]] = (
    "finalise",
    "conforme",
    "approuve",
    "diffuse",
    "termine",
)


def render(template_key: str, **values: str) -> str:
    template = TEMPLATES[template_key]
    return template.format(**values)


def filter_free_text(text: str, *, allowed_state_words: tuple[str, ...] = ()) -> str | None:
    """Filtre MG-02 : un texte libre ne peut annoncer un etat non atteint."""
    lowered = text.lower()
    for word in FORBIDDEN_STATE_WORDS:
        if word in lowered and word not in allowed_state_words:
            return None
    return text


def status_message(state: str, next_action: str = "", reason: str = "") -> str:
    if state == "blocked":
        return render("status_blocked", reason=reason or "condition indispensable non remplie")
    if state == "producing":
        return render("status_producing")
    return render("status", state=STATE_LABELS.get(state, state), next_action=next_action)
