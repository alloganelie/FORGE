"""ET-062 : aucun float dans le chemin de calcul."""

from __future__ import annotations

import pytest
from tools.check_decimal import find_float_usage


@pytest.mark.spec("ET-062")
def test_calculation_path_has_no_float_construction() -> None:
    assert find_float_usage() == []


@pytest.mark.spec("ET-062")
def test_float_construction_is_detected_in_a_synthetic_source() -> None:
    violations = find_float_usage("value = float('1.5')\n", "agent/transform/core/synthetic.py")
    assert violations
    assert "float" in violations[0]
