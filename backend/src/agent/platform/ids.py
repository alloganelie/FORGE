"""Identifiants UUIDv7 generes par l'application (ET-014, DC-01)."""

from __future__ import annotations

import secrets
from uuid import UUID

from agent.platform.clock import Clock, SystemClock

_RANDOM_BITS = 74
_RAND_B_MASK = (1 << 62) - 1


def uuid7(timestamp_ms: int, random_bytes: bytes) -> UUID:
    """Construit un UUIDv7 a partir d'un horodatage ms et de 10 octets aleatoires."""
    if timestamp_ms < 0 or timestamp_ms >= (1 << 48):
        raise ValueError("horodatage hors plage UUIDv7")
    if len(random_bytes) < 10:
        raise ValueError("au moins 10 octets aleatoires sont requis")
    randomness = int.from_bytes(random_bytes[:10], "big") & ((1 << _RANDOM_BITS) - 1)
    most_significant = (timestamp_ms << 16) | 0x7000 | (randomness >> 62)
    least_significant = (0b10 << 62) | (randomness & _RAND_B_MASK)
    return UUID(int=(most_significant << 64) | least_significant)


def new_uuid7(clock: Clock | None = None) -> UUID:
    """UUIDv7 de production : horloge injectee + alea cryptographique."""
    current = (clock if clock is not None else SystemClock()).now()
    timestamp_ms = int(current.timestamp() * 1000)
    return uuid7(timestamp_ms, secrets.token_bytes(10))


def uuid7_timestamp_ms(value: UUID) -> int:
    """Extrait l'horodatage d'un UUIDv7 (utile aux tests et au tri)."""
    if value.version != 7:
        raise ValueError("UUIDv7 attendu")
    return value.int >> 80
