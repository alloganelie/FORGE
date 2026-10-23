"""Pipeline de validation en 9 etapes composables (ET-054 a ET-058).

Les etapes sont pures et recoivent leurs ports (schema, formules, impact).
Elles ne lisent ni la base, ni l'heure, ni des fichiers.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any, Protocol

from agent.governance.core.impact import ImpactReport
from agent.governance.core.types import ArtifactType

ALLOWED_FORMATS = frozenset({"docx", "pdf", "xlsx", "pptx", "csv", "md"})
PASSED = "passed"
FAILED = "failed"
WARNING = "warning"


class SchemaValidatorPort(Protocol):
    def validate(
        self, artifact_type: ArtifactType, content: Mapping[str, Any]
    ) -> tuple[Finding, ...]: ...


class FormulaEnginePort(Protocol):
    def compile(self, formula: str) -> object: ...

    def evaluate(self, formula: str, inputs: Mapping[str, Any]) -> Any: ...


@dataclass(frozen=True, slots=True)
class Finding:
    code: str
    message: str
    path: str = ""
    severity: str = "error"


@dataclass(frozen=True, slots=True)
class Observation:
    code: str
    message: str
    rule_id: str = ""
    example_id: str = ""


@dataclass(frozen=True, slots=True)
class StepReport:
    number: int
    name: str
    status: str
    findings: tuple[Finding, ...] = ()
    details: dict[str, Any] = field(default_factory=dict)
    observations: tuple[Observation, ...] = ()


@dataclass(frozen=True, slots=True)
class ValidationReport:
    steps: tuple[StepReport, ...]
    observations: tuple[Observation, ...] = ()

    @property
    def ok(self) -> bool:
        return all(step.status != FAILED for step in self.steps)

    @property
    def warnings(self) -> tuple[StepReport, ...]:
        return tuple(step for step in self.steps if step.status == WARNING)

    def step(self, number: int) -> StepReport | None:
        for item in self.steps:
            if item.number == number:
                return item
        return None


@dataclass(frozen=True, slots=True)
class ValidationContext:
    schema_validator: SchemaValidatorPort
    formula_engine: FormulaEnginePort
    templates: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)
    controls: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)
    sources: frozenset[str] = frozenset()
    transformations: frozenset[str] = frozenset()
    units: frozenset[str] = frozenset()
    autofix_functions: frozenset[str] = frozenset()
    impact: ImpactReport | None = None
    regression_cases: tuple[Mapping[str, Any], ...] = ()


def _error(code: str, message: str, path: str = "") -> Finding:
    return Finding(code=code, message=message, path=path)


def step_schema(
    artifact_type: ArtifactType, content: Mapping[str, Any], context: ValidationContext
) -> StepReport:
    findings = context.schema_validator.validate(artifact_type, content)
    return StepReport(1, "schema", FAILED if findings else PASSED, findings)


def _elements(content: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    raw = content.get("elements", [])
    return [item for item in raw if isinstance(item, Mapping)] if isinstance(raw, list) else []


def _rules(content: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    raw = content.get("rules", [])
    return [item for item in raw if isinstance(item, Mapping)] if isinstance(raw, list) else []


def step_references(
    artifact_type: ArtifactType, content: Mapping[str, Any], context: ValidationContext
) -> StepReport:
    findings: list[Finding] = []
    if artifact_type is ArtifactType.RULE_PACK:
        for index, item in enumerate(content.get("deliverable_types", [])):
            if not isinstance(item, Mapping):
                continue
            template = item.get("template")
            if isinstance(template, Mapping):
                key = str(template.get("key", ""))
                if key not in context.templates:
                    findings.append(
                        _error(
                            "reference_inconnue",
                            f"modele inconnu : {key}",
                            f"deliverable_types[{index}].template",
                        )
                    )
            for control in item.get("mandatory_controls", []):
                if str(control) not in context.controls:
                    findings.append(
                        _error(
                            "reference_inconnue",
                            f"controle inconnu : {control}",
                            f"deliverable_types[{index}].mandatory_controls",
                        )
                    )
        rule_ids = {str(rule.get("id", "")) for rule in _rules(content)}
        for index, example in enumerate(content.get("examples", [])):
            if isinstance(example, Mapping) and str(example.get("rule_id", "")) not in rule_ids:
                findings.append(
                    _error(
                        "reference_inconnue",
                        f"regle inconnue : {example.get('rule_id')}",
                        f"examples[{index}]",
                    )
                )
    elif artifact_type is ArtifactType.TEMPLATE:
        keys = {str(item.get("key", "")) for item in _elements(content)}
        for index, item in enumerate(_elements(content)):
            for dependency in item.get("depends_on", []):
                if str(dependency) not in keys:
                    findings.append(
                        _error(
                            "reference_inconnue",
                            f"element inconnu : {dependency}",
                            f"elements[{index}].depends_on",
                        )
                    )
            for transformation in item.get("allowed_transformations", []):
                if str(transformation) not in context.transformations:
                    findings.append(
                        _error(
                            "reference_inconnue",
                            f"transformation inconnue : {transformation}",
                            f"elements[{index}].allowed_transformations",
                        )
                    )
        for index, item in enumerate(_elements(content)):
            for info in item.get("needed_information", []):
                if isinstance(info, Mapping) and "default_value" in info:
                    findings.append(
                        _error(
                            "valeur_par_defaut",
                            "valeur par defaut interdite",
                            f"elements[{index}].needed_information",
                        )
                    )
    elif artifact_type is ArtifactType.SOURCE_REGISTRY:
        seen: set[str] = set()
        for index, source in enumerate(content.get("sources", [])):
            if not isinstance(source, Mapping):
                continue
            key = str(source.get("key", ""))
            if key in seen:
                findings.append(
                    _error("reference_dupliquee", f"source dupliquee : {key}", f"sources[{index}]")
                )
            seen.add(key)
    elif artifact_type is ArtifactType.CONTROL_CATALOG:
        seen = set()
        for index, control in enumerate(content.get("controls", [])):
            if not isinstance(control, Mapping):
                continue
            identifier = str(control.get("id", ""))
            if identifier in seen:
                findings.append(
                    _error(
                        "reference_dupliquee",
                        f"controle duplique : {identifier}",
                        f"controls[{index}]",
                    )
                )
            seen.add(identifier)
    return StepReport(2, "references", FAILED if findings else PASSED, tuple(findings))


def step_cycles(
    artifact_type: ArtifactType, content: Mapping[str, Any], context: ValidationContext
) -> StepReport:
    if artifact_type is not ArtifactType.TEMPLATE:
        return StepReport(3, "cycles", PASSED)
    graph: dict[str, tuple[str, ...]] = {
        str(item.get("key", "")): tuple(str(dep) for dep in item.get("depends_on", []))
        for item in _elements(content)
    }
    visiting: set[str] = set()
    visited: set[str] = set()
    findings: list[Finding] = []

    def visit(node: str, path: tuple[str, ...]) -> None:
        if node in visiting:
            findings.append(_error("cycle", f"cycle de dependances : {' -> '.join((*path, node))}"))
            return
        if node in visited:
            return
        visiting.add(node)
        for dependency in graph.get(node, ()):
            if dependency in graph:
                visit(dependency, (*path, node))
        visiting.remove(node)
        visited.add(node)

    for key in graph:
        visit(key, ())
    return StepReport(3, "cycles", FAILED if findings else PASSED, tuple(findings))


def step_formulas(
    artifact_type: ArtifactType, content: Mapping[str, Any], context: ValidationContext
) -> StepReport:
    findings: list[Finding] = []
    formulas: list[tuple[str, Any]] = []
    for index, calculation in enumerate(content.get("calculations", [])):
        if isinstance(calculation, Mapping):
            formulas.append((f"calculations[{index}].formula", calculation.get("formula")))
            unit_out = calculation.get("unit_out")
            if isinstance(unit_out, str) and context.units and unit_out not in context.units:
                findings.append(
                    _error(
                        "unite_inconnue",
                        f"unite de sortie inconnue : {unit_out}",
                        f"calculations[{index}].unit_out",
                    )
                )
    for index, rule in enumerate(_rules(content)):
        formulas.append((f"rules[{index}].formula", rule.get("formula")))
    for index, test in enumerate(content.get("rule_tests", [])):
        if isinstance(test, Mapping):
            formulas.append((f"rule_tests[{index}].formula", test.get("formula")))
    for path, formula in formulas:
        if not isinstance(formula, str):
            findings.append(_error("formule_invalide", "formule absente", path))
            continue
        try:
            context.formula_engine.compile(formula)
        except Exception as exc:  # le port traduit toute erreur en refus
            findings.append(_error("formule_invalide", str(exc), path))
    return StepReport(4, "formules", FAILED if findings else PASSED, tuple(findings))


def step_coherence(
    artifact_type: ArtifactType, content: Mapping[str, Any], context: ValidationContext
) -> StepReport:
    findings: list[Finding] = []
    if artifact_type is ArtifactType.RULE_PACK:
        for index, autofix in enumerate(content.get("autofix", [])):
            if (
                isinstance(autofix, Mapping)
                and str(autofix.get("function", "")) not in context.autofix_functions
            ):
                findings.append(
                    _error(
                        "autofix_inconnue",
                        f"correction non enregistree : {autofix.get('function')}",
                        f"autofix[{index}]",
                    )
                )
        for index, item in enumerate(content.get("deliverable_types", [])):
            if not isinstance(item, Mapping):
                continue
            for control in item.get("mandatory_controls", []):
                if str(control) not in context.controls:
                    findings.append(
                        _error(
                            "controle_obligatoire_absent",
                            f"controle absent du catalogue : {control}",
                            f"deliverable_types[{index}]",
                        )
                    )
            for output in item.get("allowed_formats", []):
                if str(output) not in ALLOWED_FORMATS:
                    findings.append(
                        _error(
                            "format_interdit",
                            f"format non autorise : {output}",
                            f"deliverable_types[{index}].allowed_formats",
                        )
                    )
    elif artifact_type is ArtifactType.TEMPLATE:
        for index, item in enumerate(_elements(content)):
            for transformation in item.get("allowed_transformations", []):
                if str(transformation) not in context.transformations:
                    findings.append(
                        _error(
                            "transformation_non_autorisee",
                            f"transformation non autorisee : {transformation}",
                            f"elements[{index}]",
                        )
                    )
    return StepReport(5, "coherence", FAILED if findings else PASSED, tuple(findings))


def step_forbidden(
    artifact_type: ArtifactType, content: Mapping[str, Any], context: ValidationContext
) -> StepReport:
    findings: list[Finding] = []

    def walk(value: Any, path: str) -> None:
        if isinstance(value, Mapping):
            for key, item in value.items():
                child = f"{path}.{key}" if path else str(key)
                if key in {"default_value", "default"}:
                    findings.append(
                        _error(
                            "valeur_par_defaut",
                            "aucune valeur par defaut ne peut combler une lacune",
                            child,
                        )
                    )
                walk(item, child)
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, f"{path}[{index}]")

    walk(content, "")
    for index, rule in enumerate(content.get("priority_rules", [])):
        if not isinstance(rule, Mapping):
            continue
        order = rule.get("order")
        if (
            not isinstance(order, list)
            or not order
            or any(str(item) in {"implicit", "latest", "last"} for item in order)
        ):
            findings.append(
                _error(
                    "ordre_implicite",
                    "ordre de priorite explicite requis",
                    f"priority_rules[{index}]",
                )
            )
    if artifact_type is ArtifactType.TEMPLATE:
        for index, item in enumerate(_elements(content)):
            if item.get("on_missing") not in {"block", "omit", "mention_unavailable"}:
                findings.append(
                    _error(
                        "on_missing_invalide", "on_missing explicite requis", f"elements[{index}]"
                    )
                )
    return StepReport(6, "interdits", FAILED if findings else PASSED, tuple(findings))


def _equivalent(actual: Any, expected: Any) -> bool:
    if isinstance(actual, bool) or isinstance(expected, bool):
        return actual is expected
    if isinstance(actual, Decimal):
        try:
            return actual == Decimal(str(expected))
        except (InvalidOperation, ValueError):
            return False
    if isinstance(actual, str) and isinstance(expected, str):
        return bool(actual == expected)
    return bool(actual == expected)


def step_rule_tests(
    artifact_type: ArtifactType, content: Mapping[str, Any], context: ValidationContext
) -> StepReport:
    findings: list[Finding] = []
    observations: list[Observation] = []
    for index, test in enumerate(content.get("rule_tests", [])):
        if not isinstance(test, Mapping):
            continue
        formula = test.get("formula")
        inputs = test.get("inputs", {})
        if not isinstance(formula, str) or not isinstance(inputs, Mapping):
            findings.append(
                _error("test_invalide", "test de regle invalide", f"rule_tests[{index}]")
            )
            continue
        try:
            actual = context.formula_engine.evaluate(formula, inputs)
        except Exception as exc:
            findings.append(_error("test_invalide", str(exc), f"rule_tests[{index}]"))
            continue
        if not _equivalent(actual, test.get("expected")):
            findings.append(
                _error("test_echoue", "resultat different de l'attendu", f"rule_tests[{index}]")
            )
    rules = {str(rule.get("id", "")): rule for rule in _rules(content)}
    for index, example in enumerate(content.get("examples", [])):
        if not isinstance(example, Mapping):
            continue
        rule = rules.get(str(example.get("rule_id", "")))
        if rule is None:
            continue
        formula = rule.get("formula")
        inputs = example.get("inputs", {})
        if not isinstance(formula, str) or not isinstance(inputs, Mapping):
            continue
        try:
            actual = context.formula_engine.evaluate(formula, inputs)
        except Exception as exc:
            findings.append(_error("exemple_invalide", str(exc), f"examples[{index}]"))
            continue
        if not _equivalent(actual, example.get("claimed_outcome")):
            observations.append(
                Observation(
                    code="example_contradicts_rule",
                    message=(
                        "L'exemple contredit la regle : la regle prevaut, "
                        "l'incoherence est signalee."
                    ),
                    rule_id=str(example.get("rule_id", "")),
                    example_id=str(example.get("id", "")),
                )
            )
    return StepReport(
        7,
        "tests de regles",
        FAILED if findings else PASSED,
        tuple(findings),
        observations=tuple(observations),
    )


def step_regression(
    artifact_type: ArtifactType, content: Mapping[str, Any], context: ValidationContext
) -> StepReport:
    findings: list[Finding] = []
    for index, case in enumerate(context.regression_cases):
        formula = case.get("formula")
        inputs = case.get("inputs", {})
        if not isinstance(formula, str) or not isinstance(inputs, Mapping):
            continue
        try:
            actual = context.formula_engine.evaluate(formula, inputs)
        except Exception as exc:
            findings.append(_error("regression_invalide", str(exc), f"regression[{index}]"))
            continue
        if not _equivalent(actual, case.get("expected")):
            findings.append(
                _error(
                    "regression_detectee",
                    "resultat different du dossier de reference",
                    f"regression[{index}]",
                )
            )
    status = WARNING if findings else PASSED
    return StepReport(8, "regression", status, tuple(findings))


def step_impact(
    artifact_type: ArtifactType, content: Mapping[str, Any], context: ValidationContext
) -> StepReport:
    impact = context.impact
    return StepReport(
        9,
        "impact",
        PASSED,
        details=impact.as_dict()
        if impact is not None
        else {"pinned_requests": [], "dependent_models": [], "dependent_controls": []},
    )


STEP_FUNCTIONS = {
    1: step_schema,
    2: step_references,
    3: step_cycles,
    4: step_formulas,
    5: step_coherence,
    6: step_forbidden,
    7: step_rule_tests,
    8: step_regression,
    9: step_impact,
}


def run_pipeline(
    artifact_type: ArtifactType,
    content: Mapping[str, Any],
    context: ValidationContext,
    steps: tuple[int, ...] | None = None,
) -> ValidationReport:
    selected = steps if steps is not None else tuple(range(1, 10))
    reports: list[StepReport] = []
    observations: list[Observation] = []
    for number in selected:
        function = STEP_FUNCTIONS[number]
        try:
            report = function(artifact_type, content, context)
        except Exception as exc:
            report = StepReport(number, f"etape {number}", FAILED, (_error("exception", str(exc)),))
        reports.append(report)
        observations.extend(report.observations)
    return ValidationReport(tuple(reports), tuple(observations))
