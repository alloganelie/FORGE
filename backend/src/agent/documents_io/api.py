"""Facade applicative du module MOD-22 (documents_io).

Seul ce module lit et ecrit des fichiers (DR-06). Les lots de regles versionnes
passent par ce port pour rester remplacables par un stockage objet.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

MODULE_ID: Final[str] = "MOD-22"
MODULE_NAME: Final[str] = "documents_io"


class DocumentIOError(RuntimeError):
    """Lecture ou ecriture impossible ; aucun chemin interne n'est expose."""


@dataclass(frozen=True, slots=True)
class ModuleInfo:
    """Description stable de la facade, utile aux tests de frontieres."""

    module_id: str
    name: str


def module_info() -> ModuleInfo:
    return ModuleInfo(module_id=MODULE_ID, name=MODULE_NAME)


def read_utf8(path: str) -> str:
    """Lit un fichier texte UTF-8 (port de stockage local)."""
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise DocumentIOError(f"lecture impossible : {path}") from exc
