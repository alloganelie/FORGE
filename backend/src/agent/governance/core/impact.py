"""Analyse d'impact pure (ET-057, RF-258)."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ImpactReport:
    replaced_version_id: UUID
    pinned_requests: tuple[UUID, ...] = ()
    dependent_models: tuple[str, ...] = ()
    dependent_controls: tuple[str, ...] = ()

    @property
    def ready(self) -> bool:
        return True

    def as_dict(self) -> dict[str, object]:
        return {
            "replaced_version_id": str(self.replaced_version_id),
            "pinned_requests": [str(item) for item in self.pinned_requests],
            "dependent_models": list(self.dependent_models),
            "dependent_controls": list(self.dependent_controls),
        }
