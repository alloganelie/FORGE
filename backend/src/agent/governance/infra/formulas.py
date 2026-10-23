"""Adaptateur du domaine de gouvernance vers l'evaluateur CEL (ET-061)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from agent.transform.api import compile_expression, evaluate


class CelFormulaEngine:
    """Port etroit : compiler et evaluer, sans exposer le moteur CEL."""

    def compile(self, formula: str) -> object:
        return compile_expression(formula)

    def evaluate(self, formula: str, inputs: Mapping[str, Any]) -> Any:
        return evaluate(compile_expression(formula), dict(inputs))
