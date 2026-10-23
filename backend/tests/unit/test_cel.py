"""ET-061, ET-062, FM-03 : evaluateur CEL encapsule et decimal."""

from __future__ import annotations

from decimal import Decimal

import pytest

from agent.transform.core.cel import (
    CelError,
    CelEvaluationError,
    calculate,
    compile_expression,
    evaluate,
)
from agent.transform.core.decimal_math import UnitConversionError, UnitTable


@pytest.mark.spec("ET-061")
@pytest.mark.spec("ET-062")
def test_decimal_formula_is_reproducible() -> None:
    formula = 'rnd(mul(div(dec(inputs.n), dec(inputs.d)), dec("100")), 1, "half_up")'
    first = calculate(formula, {"n": "1", "d": "3"})
    second = calculate(formula, {"n": "1", "d": "3"})
    assert first.value == "33.3"
    assert first.decimal_value == Decimal("33.3")
    assert first.formula_hash == second.formula_hash
    assert first.value == second.value


@pytest.mark.spec("ET-061")
def test_integer_and_string_literals_are_decimal() -> None:
    assert evaluate(compile_expression('add(1, dec("2"))'), {}) == Decimal("3")


@pytest.mark.spec("ET-061")
def test_rule_comparison_returns_boolean() -> None:
    formula = 'dec(inputs.amount) >= dec("100")'
    assert evaluate(compile_expression(formula), {"amount": "150"}) is True
    assert evaluate(compile_expression(formula), {"amount": "50"}) is False


@pytest.mark.spec("ET-061")
def test_unknown_function_is_rejected_at_compilation() -> None:
    with pytest.raises(CelError):
        compile_expression("unknown(1)")


@pytest.mark.spec("ET-062")
def test_float_input_is_rejected() -> None:
    with pytest.raises(CelEvaluationError):
        evaluate(compile_expression("dec(inputs.n)"), {"n": 1.5})


@pytest.mark.spec("ET-061")
def test_sum_avg_min_max_count_on_lists() -> None:
    assert evaluate(compile_expression('sum([dec("1"), dec("2")])'), {}) == Decimal("3")
    assert evaluate(compile_expression('avg([dec("2"), dec("4")])'), {}) == Decimal("3")
    assert evaluate(compile_expression('min([dec("3"), dec("1")])'), {}) == Decimal("1")
    assert evaluate(compile_expression("count([1, 2, 3])"), {}) == Decimal("3")


@pytest.mark.spec("ET-063")
def test_unit_conversion_requires_a_declared_table() -> None:
    table = UnitTable(
        units=frozenset({"person", "percent"}),
        conversions={("person", "percent"): Decimal("100")},
    )
    assert table.convert(Decimal("2"), "person", "percent") == Decimal("200")
    with pytest.raises(UnitConversionError):
        table.convert(Decimal("2"), "person", "kg")


@pytest.mark.spec("ET-062")
def test_rnd_modes_are_explicit() -> None:
    assert calculate('rnd(dec("2.345"), 2, "half_up")', {}).value == "2.35"
    assert calculate('rnd(dec("2.345"), 2, "down")', {}).value == "2.34"
    with pytest.raises(CelEvaluationError):
        evaluate(compile_expression('rnd(dec("2.3"), 1, "unknown")'), {})
