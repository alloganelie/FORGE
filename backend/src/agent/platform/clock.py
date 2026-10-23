"""Port d'horloge (ET-016, DC-03). Le domaine ne lit jamais l'heure systeme."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol


class Clock(Protocol):
    def now(self) -> datetime:
        """Retourne un instant conscient du fuseau, en UTC."""
        ...


@dataclass(frozen=True, slots=True)
class SystemClock:
    """Horloge de production, injectee aux adaptateurs."""

    def now(self) -> datetime:
        return datetime.now(UTC)


@dataclass(frozen=True, slots=True)
class FixedClock:
    """Horloge deterministe pour les tests et les rejeux."""

    instant: datetime

    def now(self) -> datetime:
        if self.instant.tzinfo is None:
            raise ValueError("FixedClock exige un instant conscient du fuseau")
        return self.instant.astimezone(UTC)
