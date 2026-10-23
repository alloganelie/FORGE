"""Adaptateur de rejeu : aucune sortie reseau, fixtures strictes (MS-2)."""

from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import Any

from agent.llm_gateway.core.types import LlmError, LlmFailure, LlmResponse


class ReplayAdapter:
    """Rejoue une reponse enregistree par tache ; aucune autre entree n'est acceptee."""

    def __init__(self, responses: Mapping[str, LlmResponse | Mapping[str, Any]]) -> None:
        self.responses = dict(responses)

    def complete(self, task_id: str, inputs: Mapping[str, Any]) -> LlmResponse:
        del inputs
        response = self.responses.get(task_id)
        if response is None:
            raise LlmError(LlmFailure.FIXTURE_MISSING, task_id)
        if isinstance(response, LlmResponse):
            return LlmResponse(
                output=copy.deepcopy(dict(response.output)),
                stop_reason=response.stop_reason,
                tokens_in=response.tokens_in,
                tokens_out=response.tokens_out,
                model=response.model,
                provider=response.provider,
            )
        return LlmResponse(output=copy.deepcopy(dict(response)))


class UnavailableProvider:
    """Fournisseur reel non configure : échoue explicitement, jamais silencieusement."""

    def complete(self, task_id: str, inputs: Mapping[str, Any]) -> LlmResponse:
        del task_id, inputs
        raise LlmError(LlmFailure.PROVIDER_UNAVAILABLE, "aucun fournisseur configure")
