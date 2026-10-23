"""ET-005 / DR-01 a DR-07 : outils de controle et frontieres des modules."""

from __future__ import annotations

from pathlib import Path

import pytest
from tools.check_imports import MODULES, find_violations, scan_source


def _rules(source: str, relpath: str) -> set[str]:
    return {violation.rule for violation in scan_source(source, relpath)}


@pytest.mark.spec("DR-01")
def test_core_cannot_import_infrastructure() -> None:
    source = "import sqlalchemy\nfrom datetime import datetime\n"
    assert "DR-01" in _rules(source, "agent/requests/core/rules.py")


@pytest.mark.spec("DR-02")
def test_module_must_use_other_module_facade() -> None:
    assert "DR-02" in _rules("from agent.evidence.core import x\n", "agent/mapping/infra/repo.py")
    assert "DR-02" not in _rules(
        "from agent.evidence.api import x\n", "agent/mapping/infra/repo.py"
    )


@pytest.mark.spec("DR-03")
def test_only_lifecycle_writes_state_columns() -> None:
    source = "def f(request):\n    request.state = 'blocked'\n"
    assert "DR-03" in _rules(source, "agent/requests/api.py")
    assert "DR-03" not in _rules(source, "agent/lifecycle/infra/repo.py")


@pytest.mark.spec("DR-04")
def test_only_ledger_touches_ledger_events() -> None:
    assert "DR-04" in _rules('TABLE = "ledger_events"\n', "agent/reporting/api.py")
    assert "DR-04" not in _rules('TABLE = "ledger_events"\n', "agent/ledger/api.py")


@pytest.mark.spec("DR-05")
def test_only_llm_gateway_imports_provider_sdks() -> None:
    assert "DR-05" in _rules("import openai\n", "agent/conversation/api.py")
    assert "DR-05" not in _rules("import openai\n", "agent/llm_gateway/infra/openai_adapter.py")


@pytest.mark.spec("DR-06")
def test_only_documents_io_does_file_io() -> None:
    assert "DR-06" in _rules("from pathlib import Path\n", "agent/reporting/api.py")
    assert "DR-06" not in _rules("from pathlib import Path\n", "agent/documents_io/api.py")


@pytest.mark.spec("DR-07")
def test_interfaces_have_no_business_rules() -> None:
    assert "DR-07" in _rules(
        "from agent.lifecycle.core import states\n", "agent/interfaces/rest/app.py"
    )
    assert "DR-07" in _rules('X = "TR-R-18"\n', "agent/interfaces/rest/app.py")


@pytest.mark.spec("MOD-01")
@pytest.mark.spec("MOD-23")
def test_all_23_modules_have_facade_and_events() -> None:
    assert len(MODULES) == 23
    agent_root = Path("backend/src/agent")
    for module in MODULES:
        assert (agent_root / module / "api.py").is_file(), module
        assert (agent_root / module / "events.py").is_file(), module
        assert (agent_root / module / "core" / "__init__.py").is_file(), module


@pytest.mark.spec("DR-01")
def test_repository_respects_dependency_rules() -> None:
    assert find_violations() == []
