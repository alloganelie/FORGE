"""Arithmetique decimale explicite (FM-02, ET-062).

Aucun float : le contexte est declare et transmis a chaque calcul.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_DOWN, ROUND_HALF_EVEN, ROUND_HALF_UP, ROUND_UP, Context, Decimal
from typing import Final

ROUNDING_MODES: Final[dict[str, str]] = {
    "half_up": ROUND_HALF_UP,
    "half_even": ROUND_HALF_EVEN,
    "down": ROUND_DOWN,
    "up": ROUND_UP,
}


@dataclass(frozen=True, slots=True)
class DecimalPolicy:
    """Contexte explicite de precision et d'arrondi (FM-02)."""

    precision: int = 28
    rounding: str = "half_up"

    def context(self) -> Context:
        if self.rounding not in ROUNDING_MODES:
            raise ValueError(f"mode d'arrondi inconnu : {self.rounding}")
        return Context(prec=self.precision, rounding=ROUNDING_MODES[self.rounding])


@dataclass(frozen=True, slots=True)
class UnitTable:
    """Table de conversion declaree dans un lot (FM-04, ET-063)."""

    units: frozenset[str]
    conversions: dict[tuple[str, str], Decimal]

    def convert(self, value: Decimal, from_unit: str, to_unit: str) -> Decimal:
        if from_unit == to_unit:
            return value
        if from_unit not in self.units or to_unit not in self.units:
            raise UnitConversionError(f"unite non declaree : {from_unit} -> {to_unit}")
        try:
            factor = self.conversions[(from_unit, to_unit)]
        except KeyError as exc:
            raise UnitConversionError(
                f"conversion non declaree : {from_unit} -> {to_unit}"
            ) from exc
        return value * factor


class UnitConversionError(ValueError):
    """Conversion absente ou implicite : refus, jamais d'approximation."""


def to_decimal(value: object) -> Decimal:
    """Convertit sans jamais passer par un float."""
    if isinstance(value, bool):
        raise DecimalConversionError("un booleen n'est pas un nombre")
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, str):
        try:
            return Decimal(value)
        except Exception as exc:
            raise DecimalConversionError(f"decimal invalide : {value!r}") from exc
    raise DecimalConversionError(f"type non decimal : {type(value).__name__}")


class DecimalConversionError(ValueError):
    """Valeur non convertible en decimal sans perte."""
