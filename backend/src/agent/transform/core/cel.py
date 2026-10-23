"""Evaluateur CEL restreint et encapsule (FM-01 a FM-06, ET-061, ET-062).

Sous-ensemble volontairement limite : litteraux, identifiants, appels de
fonctions enregistrees, operateurs arithmetiques et de comparaison, listes.
Aucun eval, aucune execution dynamique, aucun float.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from decimal import Decimal
from operator import ge, gt, le, lt
from typing import Any, Final

from agent.transform.core.decimal_math import (
    ROUNDING_MODES,
    DecimalConversionError,
    DecimalPolicy,
    UnitTable,
    to_decimal,
)

MAX_DEPTH: Final[int] = 32
MAX_LIST_SIZE: Final[int] = 1000


class CelError(ValueError):
    """Formule refusee : syntaxe, fonction ou type invalide."""


class CelSyntaxError(CelError):
    pass


class CelEvaluationError(CelError):
    pass


@dataclass(frozen=True, slots=True)
class Literal:
    value: Any


@dataclass(frozen=True, slots=True)
class Identifier:
    name: str


@dataclass(frozen=True, slots=True)
class Call:
    name: str
    arguments: tuple[Node, ...]


@dataclass(frozen=True, slots=True)
class Unary:
    operator: str
    operand: Node


@dataclass(frozen=True, slots=True)
class Binary:
    operator: str
    left: Node
    right: Node


@dataclass(frozen=True, slots=True)
class ListExpression:
    items: tuple[Node, ...]


Node = Literal | Identifier | Call | Unary | Binary | ListExpression

_TOKEN = re.compile(
    r"\s*(?:(\d+(?:\.\d+)?)|(\"(?:[^\"\\]|\\.)*\")|"
    r"([A-Za-z_][A-Za-z0-9_.]*)|(==|!=|>=|<=|&&|\|\||[()\[\],+\-*/!<>]))"
)

_FUNCTIONS: Final[dict[str, tuple[int, int]]] = {
    "dec": (1, 1),
    "add": (2, 2),
    "sub": (2, 2),
    "mul": (2, 2),
    "div": (2, 2),
    "sum": (1, 1),
    "avg": (1, 1),
    "rnd": (3, 3),
    "to_unit": (2, 2),
    "pct": (2, 2),
    "min": (1, 2),
    "max": (1, 2),
    "count": (1, 1),
}


@dataclass(frozen=True, slots=True)
class CompiledExpression:
    formula: str
    root: Node
    fingerprint: str


@dataclass(frozen=True, slots=True)
class CalculationResult:
    value: str
    decimal_value: Decimal | None
    formula_hash: str
    unit: str | None


class _Tokenizer:
    def __init__(self, text: str) -> None:
        self.text = text
        self.tokens: list[tuple[str, str]] = []
        self._scan()

    def _scan(self) -> None:
        position = 0
        while position < len(self.text):
            match = _TOKEN.match(self.text, position)
            if match is None:
                raise CelSyntaxError(f"caractere inattendu a la position {position}")
            position = match.end()
            number, string, identifier, operator = match.groups()
            if number is not None:
                self.tokens.append(("number", number))
            elif string is not None:
                try:
                    value = json.loads(string)
                except json.JSONDecodeError as exc:
                    raise CelSyntaxError("chaine invalide") from exc
                self.tokens.append(("string", value))
            elif identifier is not None:
                self.tokens.append(("identifier", identifier))
            elif operator is not None:
                self.tokens.append(("operator", operator))
        self.tokens.append(("eof", ""))


class _Parser:
    def __init__(self, text: str) -> None:
        self.tokens = _Tokenizer(text).tokens
        self.index = 0

    def peek(self) -> tuple[str, str]:
        return self.tokens[self.index]

    def take(self) -> tuple[str, str]:
        token = self.tokens[self.index]
        self.index += 1
        return token

    def expect(self, operator: str) -> None:
        kind, value = self.take()
        if kind != "operator" or value != operator:
            raise CelSyntaxError(f"operateur {operator!r} attendu, recu {value!r}")

    def parse(self) -> Node:
        expression = self.parse_or()
        if self.peek()[0] != "eof":
            raise CelSyntaxError(f"jeton inattendu : {self.peek()[1]!r}")
        return expression

    def parse_or(self) -> Node:
        left = self.parse_and()
        while self.peek() == ("operator", "||"):
            self.take()
            left = Binary("||", left, self.parse_and())
        return left

    def parse_and(self) -> Node:
        left = self.parse_equality()
        while self.peek() == ("operator", "&&"):
            self.take()
            left = Binary("&&", left, self.parse_equality())
        return left

    def parse_equality(self) -> Node:
        left = self.parse_comparison()
        while self.peek() in (("operator", "=="), ("operator", "!=")):
            operator = self.take()[1]
            left = Binary(operator, left, self.parse_comparison())
        return left

    def parse_comparison(self) -> Node:
        left = self.parse_additive()
        while self.peek() in (
            ("operator", "<"),
            ("operator", "<="),
            ("operator", ">"),
            ("operator", ">="),
        ):
            operator = self.take()[1]
            left = Binary(operator, left, self.parse_additive())
        return left

    def parse_additive(self) -> Node:
        left = self.parse_multiplicative()
        while self.peek() in (("operator", "+"), ("operator", "-")):
            operator = self.take()[1]
            left = Binary(operator, left, self.parse_multiplicative())
        return left

    def parse_multiplicative(self) -> Node:
        left = self.parse_unary()
        while self.peek() in (("operator", "*"), ("operator", "/")):
            operator = self.take()[1]
            left = Binary(operator, left, self.parse_unary())
        return left

    def parse_unary(self) -> Node:
        if self.peek() in (("operator", "-"), ("operator", "!")):
            operator = self.take()[1]
            return Unary(operator, self.parse_unary())
        return self.parse_primary()

    def parse_primary(self) -> Node:
        kind, value = self.take()
        if kind == "number":
            return Literal(Decimal(value))
        if kind == "string":
            return Literal(value)
        if kind == "identifier":
            if value == "true":
                return Literal(True)
            if value == "false":
                return Literal(False)
            if value == "null":
                return Literal(None)
            if self.peek() == ("operator", "("):
                self.take()
                arguments: list[Node] = []
                if self.peek() != ("operator", ")"):
                    arguments.append(self.parse_or())
                    while self.peek() == ("operator", ","):
                        self.take()
                        arguments.append(self.parse_or())
                self.expect(")")
                return Call(value, tuple(arguments))
            return Identifier(value)
        if kind == "operator" and value == "(":
            expression = self.parse_or()
            self.expect(")")
            return expression
        if kind == "operator" and value == "[":
            items: list[Node] = []
            if self.peek() != ("operator", "]"):
                items.append(self.parse_or())
                while self.peek() == ("operator", ","):
                    self.take()
                    items.append(self.parse_or())
            self.expect("]")
            return ListExpression(tuple(items))
        raise CelSyntaxError(f"expression attendue, recu {value!r}")


def _check(node: Node) -> None:
    if isinstance(node, Call):
        if "." in node.name:
            raise CelError(f"fonction non enregistree : {node.name}")
        arity = _FUNCTIONS.get(node.name)
        if arity is None:
            raise CelError(f"fonction non enregistree : {node.name}")
        minimum, maximum = arity
        if not minimum <= len(node.arguments) <= maximum:
            raise CelError(f"arite invalide pour {node.name}")
        for argument in node.arguments:
            _check(argument)
    elif isinstance(node, Unary):
        _check(node.operand)
    elif isinstance(node, Binary):
        _check(node.left)
        _check(node.right)
    elif isinstance(node, ListExpression):
        if len(node.items) > MAX_LIST_SIZE:
            raise CelError("liste trop grande")
        for item in node.items:
            _check(item)


def compile_expression(formula: str) -> CompiledExpression:
    if not formula.strip():
        raise CelSyntaxError("formule vide")
    root = _Parser(formula).parse()
    _check(root)
    return CompiledExpression(
        formula=formula,
        root=root,
        fingerprint=hashlib.sha256(formula.encode("utf-8")).hexdigest(),
    )


@dataclass(frozen=True, slots=True)
class EvaluationContext:
    inputs: dict[str, Any]
    unit_table: UnitTable | None = None
    policy: DecimalPolicy = field(default_factory=DecimalPolicy)
    depth: int = 0


def _normalise(value: Any) -> Any:
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return value
    if isinstance(value, float):
        raise CelEvaluationError("les flottants sont interdits dans le calcul")
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, Decimal):
        return value
    if isinstance(value, list):
        if len(value) > MAX_LIST_SIZE:
            raise CelEvaluationError("liste trop grande")
        return [_normalise(item) for item in value]
    raise CelEvaluationError(f"valeur non supportee : {type(value).__name__}")


def _resolve(name: str, inputs: dict[str, Any]) -> Any:
    parts = name.split(".")
    if parts and parts[0] in {"inputs", "facts"}:
        current: Any = inputs
        for part in parts[1:]:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                raise CelEvaluationError(f"identifiant inconnu : {name}")
        return _normalise(current)
    if name in inputs:
        return _normalise(inputs[name])
    raise CelEvaluationError(f"identifiant inconnu : {name}")


def _decimal(value: Any) -> Decimal:
    try:
        return to_decimal(value)
    except DecimalConversionError as exc:
        raise CelEvaluationError(str(exc)) from exc


def _as_bool(value: Any) -> bool:
    if not isinstance(value, bool):
        raise CelEvaluationError("booleen attendu")
    return value


def _compare(operator: str, left: Any, right: Any) -> bool:
    if (isinstance(left, Decimal) and isinstance(right, Decimal)) or (
        isinstance(left, str) and isinstance(right, str)
    ):
        pass
    else:
        if operator == "==":
            return bool(left == right)
        if operator == "!=":
            return bool(left != right)
        raise CelEvaluationError("comparaison de types incompatibles")
    if operator == "==":
        return bool(left == right)
    if operator == "!=":
        return bool(left != right)
    if operator == "<":
        return bool(lt(left, right))
    if operator == "<=":
        return bool(le(left, right))
    if operator == ">":
        return bool(gt(left, right))
    if operator == ">=":
        return bool(ge(left, right))
    raise CelEvaluationError(f"operateur inconnu : {operator}")


def _evaluate(node: Node, context: EvaluationContext) -> Any:
    if context.depth > MAX_DEPTH:
        raise CelEvaluationError("profondeur maximale depassee")
    if isinstance(node, Literal):
        return _normalise(node.value)
    if isinstance(node, Identifier):
        return _resolve(node.name, context.inputs)
    if isinstance(node, ListExpression):
        return [
            _evaluate(
                item,
                EvaluationContext(
                    context.inputs, context.unit_table, context.policy, context.depth + 1
                ),
            )
            for item in node.items
        ]
    if isinstance(node, Unary):
        value = _evaluate(
            node.operand,
            EvaluationContext(
                context.inputs, context.unit_table, context.policy, context.depth + 1
            ),
        )
        if node.operator == "-":
            return -_decimal(value)
        if node.operator == "!":
            return not _as_bool(value)
        raise CelEvaluationError(f"operateur unaire inconnu : {node.operator}")
    if isinstance(node, Binary):
        left = _evaluate(
            node.left,
            EvaluationContext(
                context.inputs, context.unit_table, context.policy, context.depth + 1
            ),
        )
        right = _evaluate(
            node.right,
            EvaluationContext(
                context.inputs, context.unit_table, context.policy, context.depth + 1
            ),
        )
        if node.operator in {"&&", "||"}:
            return (
                _as_bool(left) and _as_bool(right)
                if node.operator == "&&"
                else _as_bool(left) or _as_bool(right)
            )
        if node.operator in {"==", "!=", "<", "<=", ">", ">="}:
            return _compare(node.operator, left, right)
        if node.operator in {"+", "-", "*", "/"}:
            if node.operator == "+" and isinstance(left, str) and isinstance(right, str):
                return left + right
            first, second = _decimal(left), _decimal(right)
            if node.operator == "+":
                return first + second
            if node.operator == "-":
                return first - second
            if node.operator == "*":
                return first * second
            if second == 0:
                raise CelEvaluationError("division par zero")
            return first / second
        raise CelEvaluationError(f"operateur binaire inconnu : {node.operator}")
    if isinstance(node, Call):
        arguments = tuple(
            _evaluate(
                argument,
                EvaluationContext(
                    context.inputs, context.unit_table, context.policy, context.depth + 1
                ),
            )
            for argument in node.arguments
        )
        return _call(node.name, arguments, context)
    raise CelEvaluationError("noeud inconnu")


def _call(name: str, arguments: tuple[Any, ...], context: EvaluationContext) -> Any:
    if name == "dec":
        return _decimal(arguments[0])
    if name in {"add", "sub", "mul", "div"}:
        left, right = _decimal(arguments[0]), _decimal(arguments[1])
        if name == "add":
            return left + right
        if name == "sub":
            return left - right
        if name == "mul":
            return left * right
        if right == 0:
            raise CelEvaluationError("division par zero")
        return left / right
    if name in {"sum", "avg"}:
        values = [_decimal(item) for item in arguments[0]]
        if not values:
            raise CelEvaluationError("liste vide")
        total = sum(values, Decimal(0))
        return total if name == "sum" else total / Decimal(len(values))
    if name == "rnd":
        value = _decimal(arguments[0])
        places_decimal = _decimal(arguments[1])
        if places_decimal != places_decimal.to_integral_value():
            raise CelEvaluationError("nombre de decimales non entier")
        places = int(places_decimal)
        mode = arguments[2]
        if not isinstance(mode, str) or mode not in ROUNDING_MODES:
            raise CelEvaluationError(f"mode d'arrondi inconnu : {mode!r}")
        quantum = Decimal(1).scaleb(-places)
        return value.quantize(quantum, rounding=ROUNDING_MODES[mode])
    if name == "to_unit":
        value = _decimal(arguments[0])
        unit = arguments[1]
        if not isinstance(unit, str):
            raise CelEvaluationError("unite attendue")
        if context.unit_table is None or unit not in context.unit_table.units:
            raise CelEvaluationError(f"unite non declaree : {unit}")
        return value
    if name == "pct":
        numerator, denominator = _decimal(arguments[0]), _decimal(arguments[1])
        if denominator == 0:
            raise CelEvaluationError("division par zero")
        return numerator / denominator * Decimal(100)
    if name in {"min", "max"}:
        values = arguments[0] if len(arguments) == 1 else list(arguments)
        decimals = [_decimal(item) for item in values]
        if not decimals:
            raise CelEvaluationError("liste vide")
        return min(decimals) if name == "min" else max(decimals)
    if name == "count":
        return Decimal(len(arguments[0]))
    raise CelEvaluationError(f"fonction non enregistree : {name}")


def evaluate(
    expression: CompiledExpression, inputs: dict[str, Any], unit_table: UnitTable | None = None
) -> Any:
    return _evaluate(expression.root, EvaluationContext(inputs=inputs, unit_table=unit_table))


def calculate(
    formula: str,
    inputs: dict[str, Any],
    *,
    unit_table: UnitTable | None = None,
    unit_out: str | None = None,
) -> CalculationResult:
    expression = compile_expression(formula)
    value = evaluate(expression, inputs, unit_table)
    decimal_value = value if isinstance(value, Decimal) else None
    if isinstance(value, bool):
        rendered = "true" if value else "false"
    elif isinstance(value, Decimal):
        rendered = str(value)
    elif value is None:
        rendered = "null"
    elif isinstance(value, str):
        rendered = value
    else:
        rendered = json.dumps(value, ensure_ascii=False, default=str)
    return CalculationResult(
        value=rendered,
        decimal_value=decimal_value,
        formula_hash=expression.fingerprint,
        unit=unit_out,
    )
