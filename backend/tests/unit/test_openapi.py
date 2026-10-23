"""ET-002 : le contrat OpenAPI est genere et versionne."""

from __future__ import annotations

from pathlib import Path

import pytest
from tools.gen_openapi import main as gen_openapi_main


@pytest.mark.spec("ET-002")
def test_openapi_contract_is_versioned_and_current() -> None:
    path = Path("backend/openapi.json")
    assert path.is_file()
    assert gen_openapi_main(["--check"]) == 0


@pytest.mark.spec("ET-002")
def test_openapi_contains_health_contract() -> None:
    content = Path("backend/openapi.json").read_text(encoding="utf-8")
    assert '"/healthz"' in content
    assert "FORGE" in content
