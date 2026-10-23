"""ET-014, ET-016 : horloge injectee et identifiants UUIDv7."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import pytest

from agent.platform.api import FixedClock, SystemClock, new_uuid7, uuid7, uuid7_timestamp_ms
from agent.platform.clock import Clock


@pytest.mark.spec("ET-016")
def test_fixed_clock_is_deterministic() -> None:
    instant = datetime(2026, 10, 23, 12, 0, tzinfo=UTC)
    clock: Clock = FixedClock(instant)
    assert clock.now() == instant
    assert clock.now() == instant


@pytest.mark.spec("ET-016")
def test_system_clock_is_utc_aware() -> None:
    assert SystemClock().now().tzinfo is not None


@pytest.mark.spec("ET-014")
def test_uuid7_layout_and_version() -> None:
    value = uuid7(1_700_000_000_000, b"\x00" * 10)
    assert isinstance(value, UUID)
    assert value.version == 7
    assert value.variant == "specified in RFC 4122"
    assert uuid7_timestamp_ms(value) == 1_700_000_000_000


@pytest.mark.spec("ET-014")
def test_uuid7_is_sortable_by_timestamp() -> None:
    earlier = uuid7(1_700_000_000_000, b"\xff" * 10)
    later = uuid7(1_700_000_001_000, b"\x00" * 10)
    assert earlier < later


@pytest.mark.spec("ET-014")
def test_new_uuid7_uses_injected_clock() -> None:
    instant = datetime(2026, 10, 23, 12, 0, tzinfo=UTC)
    value = new_uuid7(FixedClock(instant))
    assert uuid7_timestamp_ms(value) == int(instant.timestamp() * 1000)
