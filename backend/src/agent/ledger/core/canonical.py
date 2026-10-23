"""Canonisation JSON RFC 8785 (ET-022, DC-08).

Le sous-ensemble accepte couvre les charges du journal : null, booleens,
entiers, chaines, listes et objets a cles chaines. Les flottants sont refuses
explicitement : les montants et compteurs du domaine sont des entiers, et un
flottant rendrait le hachage dependant de la representation binaire.
"""

from __future__ import annotations

import json
from typing import Any


class CanonicalizationError(ValueError):
    """Valeur non canonisable : le hachage serait ambigu."""


def _escape_string(value: str) -> str:
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise CanonicalizationError("chaine non UTF-8 (surrogate isole)") from exc
    return json.dumps(value, ensure_ascii=False, allow_nan=False)


def _key_order(key: str) -> bytes:
    # RFC 8785 : tri par unites de code UTF-16, equivalent a l'ordre ECMAScript.
    return key.encode("utf-16-be")


def _serialize(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        raise CanonicalizationError("les flottants ne sont pas canonisables dans le journal")
    if isinstance(value, str):
        return _escape_string(value)
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(_serialize(item) for item in value) + "]"
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise CanonicalizationError("les cles d'objet doivent etre des chaines")
        items = sorted(value.items(), key=lambda item: _key_order(item[0]))
        return (
            "{" + ",".join(f"{_escape_string(key)}:{_serialize(item)}" for key, item in items) + "}"
        )
    raise CanonicalizationError(f"type non canonisable : {type(value).__name__}")


def canonicalize(value: Any) -> bytes:
    """Retourne la representation canonique UTF-8 (RFC 8785)."""
    return _serialize(value).encode("utf-8")
