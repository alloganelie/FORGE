"""Corrections mecaniques nommees (ET-064, AF-01 a AF-05).

Le lot de regles ne contient jamais de code : il autorise et parametre une
fonction enregistree ici. Une fonction inconnue est refusee.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from typing import Any


class UnknownAutofix(ValueError):
    """Correction non enregistree : refus par defaut."""


def normalize_date(value: str, params: Mapping[str, Any]) -> str:
    """Normalise une date JJ/MM/AAAA en AAAA-MM-JJ (parametre explicite)."""
    match = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", value)
    if match is None:
        return value
    day, month, year = match.groups()
    return f"{year}-{month}-{day}"


def fix_typographic_quotes(value: str, params: Mapping[str, Any]) -> str:
    return value.replace("\u201c", '"').replace("\u201d", '"')


def renumber_headings(value: str, params: Mapping[str, Any]) -> str:
    counter = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal counter
        counter += 1
        return f"{counter}. {match.group(1)}"

    return re.sub(r"^#+\s+(.*)$", replace, value, flags=re.MULTILINE)


AUTOFIX_FUNCTIONS: dict[str, Callable[[str, Mapping[str, Any]], str]] = {
    "normalize_date": normalize_date,
    "fix_typographic_quotes": fix_typographic_quotes,
    "renumber_headings": renumber_headings,
}


def apply_autofix(name: str, value: str, params: Mapping[str, Any] | None = None) -> str:
    function = AUTOFIX_FUNCTIONS.get(name)
    if function is None:
        raise UnknownAutofix(f"correction inconnue : {name}")
    return function(value, params or {})
