#!/usr/bin/env python3
"""Tracabilite specification <-> tests (ET-353 a ET-356, ET-372, TT-01 a TT-05).

Sources :
  - docs/spec/ids.json (identifiants generes depuis les specifications) ;
  - marqueurs pytest @pytest.mark.ca / .spec / .tst ;
  - build/junit.xml (resultats du dernier passage) ;
  - rulepacks/state_machines/*.yaml (transitions a couvrir).

Sorties : docs/reports/spec-trace.{json,md,html} et l'historique par jalon.
Le tableau de bord est lisible sans terminal par le Product Owner.
"""

from __future__ import annotations

import argparse
import ast
import html
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
IDS_PATH = ROOT / "docs" / "spec" / "ids.json"
TESTS_DIR = ROOT / "backend" / "tests"
REPORTS = ROOT / "docs" / "reports"
JUNIT_DEFAULT = ROOT / "build" / "junit.xml"
HISTORY_PATH = REPORTS / "spec-trace-history.json"
JUSTIFICATIONS_PATH = REPORTS / "non-testable.yml"
RULEPACKS = ROOT / "rulepacks" / "state_machines"

CA_RE = re.compile(r"\bCA-\d{3}\b")
ID_RE = re.compile(r"\b[A-Z]{2,4}(?:-[A-Z])?-\d{1,3}\b")
TRANSITION_RE = re.compile(r"\bTR-[RCDVE]-\d{2}\b")


@dataclass
class TestCase:
    path: str
    qualname: str
    ca_ids: tuple[str, ...] = ()
    spec_ids: tuple[str, ...] = ()
    suite_ids: tuple[str, ...] = ()
    outcome: str = "not-run"

    @property
    def all_ids(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys((*self.ca_ids, *self.spec_ids, *self.suite_ids)))

    @property
    def node(self) -> str:
        return f"{self.path}::{self.qualname}"


@dataclass
class TransitionCoverage:
    identifier: str
    covered_by: list[str] = field(default_factory=list)


@dataclass
class Report:
    milestone: str
    tests: list[TestCase]
    criteria: dict[str, dict[str, Any]]
    requirements: dict[str, dict[str, Any]]
    transitions: dict[str, TransitionCoverage]
    unknown_ids: list[dict[str, str]]
    orphan_tests: list[str]
    milestone_criteria: list[str]
    evolution: dict[str, Any]
    justifications: dict[str, str]

    def summary(self) -> dict[str, Any]:
        counts = {"green": 0, "red": 0, "skipped": 0, "no-test": 0, "out-of-scope": 0}
        for entry in self.criteria.values():
            counts[str(entry["status"])] += 1
        covered_requirements = sum(1 for item in self.requirements.values() if item["covered"])
        in_scope = len(self.criteria) - counts["out-of-scope"]
        in_scope_green = counts["green"]
        return {
            "ca_total": len(self.criteria),
            "ca_green": counts["green"],
            "ca_red": counts["red"],
            "ca_skipped": counts["skipped"],
            "ca_no_test": counts["no-test"],
            "ca_out_of_scope": counts["out-of-scope"],
            "ca_percent": round(100 * counts["green"] / len(self.criteria), 1)
            if self.criteria
            else 0.0,
            "in_scope_total": in_scope,
            "in_scope_green": in_scope_green,
            "in_scope_percent": round(100 * in_scope_green / in_scope, 1) if in_scope else 0.0,
            "tests": len(self.tests),
            "orphan_tests": len(self.orphan_tests),
            "unknown_ids": len(self.unknown_ids),
            "requirements_total": len(self.requirements),
            "requirements_covered": covered_requirements,
            "requirements_percent": round(100 * covered_requirements / len(self.requirements), 1)
            if self.requirements
            else 0.0,
            "transitions_total": len(self.transitions),
            "transitions_covered": sum(1 for item in self.transitions.values() if item.covered_by),
        }


def load_ids() -> dict[str, Any]:
    data = json.loads(IDS_PATH.read_text(encoding="utf-8"))
    return {str(key): value for key, value in data.items()}


def _marker_value(decorator: ast.AST) -> tuple[str, str] | None:
    if not isinstance(decorator, ast.Call):
        return None
    function = decorator.func
    if not isinstance(function, ast.Attribute):
        return None
    if function.attr not in {"ca", "spec", "tst"}:
        return None
    if not decorator.args or not isinstance(decorator.args[0], ast.Constant):
        return None
    return function.attr, str(decorator.args[0].value)


def _iter_functions(tree: ast.AST) -> list[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef]]:
    found: list[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef]] = []

    def visit(node: ast.AST, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qualname = f"{prefix}{child.name}"
                found.append((qualname, child))
            elif isinstance(child, ast.ClassDef):
                visit(child, f"{prefix}{child.name}.")
            else:
                visit(child, prefix)

    visit(tree, "")
    return found


def discover_tests() -> list[TestCase]:
    tests: list[TestCase] = []
    for path in sorted(TESTS_DIR.rglob("test_*.py")):
        relative = path.relative_to(ROOT).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        for qualname, node in _iter_functions(tree):
            if not node.name.startswith("test_"):
                continue
            ca_ids: list[str] = []
            spec_ids: list[str] = []
            suite_ids: list[str] = []
            for decorator in node.decorator_list:
                marker = _marker_value(decorator)
                if marker is None:
                    continue
                kind, value = marker
                if kind == "ca":
                    ca_ids.append(value)
                elif kind == "spec":
                    spec_ids.append(value)
                else:
                    suite_ids.append(value)
            tests.append(
                TestCase(
                    path=relative,
                    qualname=qualname,
                    ca_ids=tuple(ca_ids),
                    spec_ids=tuple(spec_ids),
                    suite_ids=tuple(suite_ids),
                )
            )
    return tests


def _module_path(classname: str) -> Path | None:
    parts = classname.split(".")
    for size in range(len(parts), 1, -1):
        candidate = ROOT.joinpath(*parts[:size]).with_suffix(".py")
        if candidate.is_file() and candidate.is_relative_to(ROOT / "backend" / "tests"):
            return candidate
    return None


def load_junit(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    import xml.etree.ElementTree as ET

    outcomes: dict[str, list[str]] = defaultdict(list)
    tree = ET.parse(path)
    for case in tree.getroot().iter("testcase"):
        classname = case.attrib.get("classname", "")
        name = case.attrib.get("name", "").split("[", 1)[0]
        module = _module_path(classname)
        if module is None:
            continue
        relative = module.relative_to(ROOT).as_posix()
        qualname = name
        if classname.count(".") > module.with_suffix("").as_posix().replace("/", ".").count("."):
            suffix = classname.split(module.with_suffix("").as_posix().replace("/", "."), 1)[-1]
            qualname = f"{suffix.strip('.')}.{name}" if suffix else name
        key = f"{relative}::{qualname}"
        if case.find("failure") is not None or case.find("error") is not None:
            outcomes[key].append("failed")
        elif case.find("skipped") is not None:
            outcomes[key].append("skipped")
        else:
            outcomes[key].append("passed")
    merged: dict[str, str] = {}
    for key, values in outcomes.items():
        if "failed" in values:
            merged[key] = "failed"
        elif "skipped" in values:
            merged[key] = "skipped"
        else:
            merged[key] = "passed"
    return merged


def apply_outcomes(tests: list[TestCase], junit: dict[str, str]) -> None:
    for test in tests:
        test.outcome = junit.get(test.node, "not-run")


def load_justifications() -> dict[str, str]:
    if not JUSTIFICATIONS_PATH.is_file():
        return {}
    raw = yaml.safe_load(JUSTIFICATIONS_PATH.read_text(encoding="utf-8")) or {}
    if isinstance(raw, dict) and isinstance(raw.get("justifications"), dict):
        raw = raw["justifications"]
    if not isinstance(raw, dict):
        return {}
    return {str(key): str(value) for key, value in raw.items()}


def load_transitions() -> dict[str, TransitionCoverage]:
    transitions: dict[str, TransitionCoverage] = {}
    for path in sorted(RULEPACKS.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            continue
        for item in data.get("transitions", []) or []:
            identifier = str(item["id"])
            transitions[identifier] = TransitionCoverage(identifier)
        for item in data.get("non_transitions", []) or []:
            identifier = str(item["id"])
            transitions[identifier] = TransitionCoverage(identifier)
    return transitions


def _test_sources() -> dict[str, str]:
    return {
        path.relative_to(ROOT).as_posix(): path.read_text(encoding="utf-8")
        for path in TESTS_DIR.rglob("*.py")
    }


def _section4_cas(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    lines = path.read_text(encoding="utf-8").splitlines()
    in_section = False
    found: set[str] = set()
    for line in lines:
        if line.startswith("## 4."):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            found.update(CA_RE.findall(line))
    return found


def milestone_criteria(milestone: str) -> list[str]:
    """Criteres exigibles a ce jalon : cumul des sections 4 des jalons <= courant.

    Le brief MS-0 ne porte aucun CA ; les 195 CA appartiennent aux jalons
    metier. La porte ET-354 s'applique donc au perimetre cumule, et devient
    globale au dernier jalon.
    """
    match = re.fullmatch(r"MS-(\d+)", milestone)
    if match is None:
        return []
    current = int(match.group(1))
    scope: set[str] = set()
    for path in sorted((ROOT / "docs" / "milestones").glob("MS-*.md")):
        candidate = re.fullmatch(r"MS-(\d+)", path.stem)
        if candidate is None or int(candidate.group(1)) > current:
            continue
        scope.update(_section4_cas(path))
    return sorted(scope)


def build_report(milestone: str, junit_path: Path) -> Report:
    ids = load_ids()
    tests = discover_tests()
    apply_outcomes(tests, load_junit(junit_path))
    sources = _test_sources()
    justifications = load_justifications()

    scope = set(milestone_criteria(milestone))
    criteria: dict[str, dict[str, Any]] = {}
    for identifier in sorted(key for key in ids if key.startswith("CA-")):
        related = [test for test in tests if identifier in test.ca_ids]
        if identifier not in scope:
            status = "out-of-scope"
        elif not related:
            status = "no-test"
        elif any(test.outcome == "failed" for test in related):
            status = "red"
        elif all(test.outcome in {"skipped", "not-run"} for test in related):
            status = "skipped"
        elif all(test.outcome == "passed" for test in related):
            status = "green"
        else:
            status = "red"
        criteria[identifier] = {
            "status": status,
            "tests": [test.node for test in related],
        }

    requirements: dict[str, dict[str, Any]] = {}
    for identifier in sorted(key for key in ids if key.split("-")[0] in {"RF", "RB", "RT"}):
        related = [test for test in tests if identifier in test.spec_ids]
        justification = justifications.get(identifier)
        requirements[identifier] = {
            "covered": bool(related) or justification is not None,
            "tests": [test.node for test in related],
            "justification": justification,
        }

    transitions = load_transitions()
    for identifier, coverage in transitions.items():
        for path, source in sources.items():
            if re.search(rf"\b{re.escape(identifier)}\b", source):
                coverage.covered_by.append(path)

    unknown: list[dict[str, str]] = []
    for test in tests:
        for identifier in test.all_ids:
            if identifier not in ids:
                unknown.append({"id": identifier, "test": test.node})

    orphans = [test.node for test in tests if not test.all_ids]
    milestone_ids = sorted(scope)
    evolution = compute_evolution(criteria, milestone)
    return Report(
        milestone=milestone,
        tests=tests,
        criteria=criteria,
        requirements=requirements,
        transitions=transitions,
        unknown_ids=unknown,
        orphan_tests=orphans,
        milestone_criteria=milestone_ids,
        evolution=evolution,
        justifications=justifications,
    )


def compute_evolution(criteria: dict[str, dict[str, Any]], milestone: str) -> dict[str, Any]:
    green = sum(1 for item in criteria.values() if item["status"] == "green")
    percent = round(100 * green / len(criteria), 1) if criteria else 0.0
    previous: dict[str, Any] | None = None
    if HISTORY_PATH.is_file():
        raw = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
        milestones = raw.get("milestones", {}) if isinstance(raw, dict) else {}
        candidates = [key for key in milestones if key < milestone]
        if candidates:
            previous = {"milestone": max(candidates), **milestones[max(candidates)]}
    delta = None
    if previous is not None:
        delta = round(percent - float(previous.get("ca_percent", 0.0)), 1)
    return {
        "ca_green": green,
        "ca_total": len(criteria),
        "ca_percent": percent,
        "previous": previous,
        "delta": delta,
    }


def gate_errors(report: Report, *, strict_requirements: bool) -> list[str]:
    errors: list[str] = []
    for item in report.unknown_ids:
        errors.append(f"ET-356 : identifiant inconnu {item['id']} cite par {item['test']}")
    for orphan in report.orphan_tests:
        errors.append(f"TT-03 : test orphelin (aucun identifiant) {orphan}")
    for identifier, coverage in sorted(report.transitions.items()):
        if not coverage.covered_by:
            errors.append(f"ET-044 : transition non couverte {identifier}")
    for identifier in report.milestone_criteria:
        entry = report.criteria.get(identifier)
        if entry is None:
            errors.append(f"ET-354 : critere du jalon absent du referentiel {identifier}")
        elif entry["status"] != "green":
            errors.append(f"ET-354 : critere du jalon non vert {identifier} ({entry['status']})")
    if strict_requirements:
        for identifier, entry in sorted(report.requirements.items()):
            if not entry["covered"]:
                errors.append(f"ET-355 : exigence sans test ni justification {identifier}")
    return errors


def _badge(status: str) -> str:
    labels = {
        "green": "vert",
        "red": "rouge",
        "skipped": "ignore",
        "no-test": "sans test",
        "out-of-scope": "hors perimetre",
    }
    return labels.get(status, status)


def render_markdown(report: Report) -> str:
    summary = report.summary()
    previous = report.evolution["previous"]
    lines = [
        "# Tableau de bord specification <-> tests",
        "",
        f"**Jalon :** {report.milestone}  ",
        f"**Genere :** {datetime.now(UTC).isoformat(timespec='seconds')}",
        "",
        "## Synthese",
        "",
        "| Indicateur | Valeur |",
        "|---|---|",
        f"| Criteres exigibles verts | {summary['in_scope_green']} / {summary['in_scope_total']} ({summary['in_scope_percent']} %) |",
        f"| Criteres exigibles rouges | {summary['ca_red']} |",
        f"| Criteres exigibles sans test | {summary['ca_no_test']} |",
        f"| Criteres exigibles ignores | {summary['ca_skipped']} |",
        f"| Criteres hors perimetre (jalons futurs) | {summary['ca_out_of_scope']} |",
        f"| Criteres verts (tous jalons) | {summary['ca_green']} / {summary['ca_total']} ({summary['ca_percent']} %) |",
        f"| Exigences RF/RB/RT couvertes | {summary['requirements_covered']} / {summary['requirements_total']} ({summary['requirements_percent']} %) |",
        f"| Transitions couvertes | {summary['transitions_covered']} / {summary['transitions_total']} |",
        f"| Tests | {summary['tests']} |",
        f"| Tests orphelins | {summary['orphan_tests']} |",
        f"| Identifiants inconnus | {summary['unknown_ids']} |",
        "",
    ]
    if previous:
        lines.append(
            f"**Evolution :** {report.evolution['delta']:+.1f} point(s) par rapport a "
            f"{previous['milestone']} ({previous.get('ca_percent', 0)} %)."
        )
    else:
        lines.append("**Evolution :** premier jalon mesure, aucune comparaison anterieure.")
    lines.append("")

    if report.milestone_criteria:
        lines += ["## Criteres du jalon", "", "| Critere | Statut | Tests |", "|---|---|---|"]
        for identifier in report.milestone_criteria:
            entry = report.criteria[identifier]
            lines.append(f"| {identifier} | {_badge(entry['status'])} | {len(entry['tests'])} |")
        lines.append("")
    else:
        lines += [
            "## Criteres du jalon",
            "",
            "Aucun critere d'acceptation exigible a ce jalon (les CA appartiennent aux jalons metier).",
            "",
        ]

    lines += ["## Criteres exigibles sans test", ""]
    missing = [key for key, value in report.criteria.items() if value["status"] == "no-test"]
    lines.append(f"{len(missing)} critere(s) sans test." if missing else "Aucun.")
    lines.append("")

    lines += ["## Exigences sans test", ""]
    uncovered = [key for key, value in report.requirements.items() if not value["covered"]]
    lines.append(
        f"{len(uncovered)} exigence(s) RF/RB/RT sans test ni justification. "
        "La porte ET-355 est active au jalon final."
        if uncovered
        else "Aucune."
    )
    lines.append("")

    lines += ["## Transitions non couvertes", ""]
    missing_transitions = [
        key for key, value in sorted(report.transitions.items()) if not value.covered_by
    ]
    lines.append(", ".join(missing_transitions) if missing_transitions else "Aucune.")
    lines.append("")

    lines += ["## Tests orphelins", ""]
    lines.append(
        "\n".join(f"- {item}" for item in report.orphan_tests) if report.orphan_tests else "Aucun."
    )
    lines.append("")

    lines += ["## Identifiants inconnus", ""]
    if report.unknown_ids:
        for item in report.unknown_ids:
            lines.append(f"- {item['id']} (cite par {item['test']})")
    else:
        lines.append("Aucun.")
    lines += ["", "---", "", "Genere par tools/spec_trace.py."]
    return "\n".join(lines) + "\n"


def render_html(report: Report) -> str:
    summary = report.summary()
    previous = report.evolution["previous"]

    def esc(value: object) -> str:
        return html.escape(str(value))

    criteria_rows = "".join(
        f"<tr class='{esc(entry['status'])}'><td>{esc(identifier)}</td>"
        f"<td><span class='badge {esc(entry['status'])}'>{esc(_badge(entry['status']))}</span></td>"
        f"<td>{len(entry['tests'])}</td></tr>"
        for identifier, entry in sorted(report.criteria.items())
    )
    milestone_rows = (
        "".join(
            f"<tr class='{esc(report.criteria[identifier]['status'])}'>"
            f"<td>{esc(identifier)}</td>"
            f"<td><span class='badge {esc(report.criteria[identifier]['status'])}'>"
            f"{esc(_badge(report.criteria[identifier]['status']))}</span></td>"
            f"<td>{len(report.criteria[identifier]['tests'])}</td></tr>"
            for identifier in report.milestone_criteria
        )
        or "<tr><td colspan='3'>Aucun critere propre a ce jalon.</td></tr>"
    )

    uncovered = [key for key, value in report.requirements.items() if not value["covered"]]
    uncovered_preview = "".join(f"<li>{esc(item)}</li>" for item in uncovered[:120])
    if len(uncovered) > 120:
        uncovered_preview += f"<li>... et {len(uncovered) - 120} autres</li>"

    orphan = "".join(f"<li>{esc(item)}</li>" for item in report.orphan_tests) or "<li>Aucun.</li>"
    unknown = (
        "".join(
            f"<li>{esc(item['id'])} (cite par {esc(item['test'])})</li>"
            for item in report.unknown_ids
        )
        or "<li>Aucun.</li>"
    )
    transitions = "".join(
        f"<tr class='{'green' if item.covered_by else 'red'}'>"
        f"<td>{esc(identifier)}</td><td>{len(item.covered_by)}</td></tr>"
        for identifier, item in sorted(report.transitions.items())
    )

    if previous:
        evolution = (
            f"{report.evolution['delta']:+.1f} point(s) par rapport a "
            f"{esc(previous['milestone'])} ({esc(previous.get('ca_percent', 0))} %)."
        )
    else:
        evolution = "Premier jalon mesure, aucune comparaison anterieure."

    template = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tableau de bord specification - tests</title>
<style>
:root { color-scheme: light; --ink:#17212b; --muted:#5b6b7b; --line:#d9e1e8;
  --green:#e7f6ec; --green-ink:#176b36; --red:#fdecec; --red-ink:#9b1c1c;
  --amber:#fff6dd; --amber-ink:#7a5200; --grey:#eef2f5; }
body { font-family: "Segoe UI", Arial, sans-serif; margin: 0; color: var(--ink);
  background: #f7f9fb; line-height: 1.45; }
main { max-width: 1100px; margin: 0 auto; padding: 28px 20px 60px; }
h1 { margin: 0 0 4px; font-size: 1.7rem; }
h2 { margin-top: 34px; border-bottom: 2px solid var(--line); padding-bottom: 6px; }
.sub { color: var(--muted); margin-top: 0; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 12px; margin: 22px 0; }
.card { background: #fff; border: 1px solid var(--line); border-radius: 10px;
  padding: 14px 16px; }
.card .n { font-size: 1.7rem; font-weight: 700; }
.card .l { color: var(--muted); font-size: .85rem; }
table { width: 100%; border-collapse: collapse; background: #fff; margin: 10px 0 20px; }
th, td { border: 1px solid var(--line); padding: 6px 9px; text-align: left; font-size: .9rem; }
th { background: var(--grey); }
tr.green td { background: var(--green); }
tr.red td { background: var(--red); }
tr.skipped td { background: var(--amber); }
.badge { display: inline-block; padding: 1px 8px; border-radius: 999px;
  font-size: .78rem; font-weight: 600; }
.badge.green { background: var(--green); color: var(--green-ink); }
.badge.red { background: var(--red); color: var(--red-ink); }
.badge.skipped { background: var(--amber); color: var(--amber-ink); }
.badge.no-test { background: var(--grey); color: var(--muted); }
.badge.out-of-scope { background: #f2f5f7; color: #7b8794; }
tr.out-of-scope td { color: #7b8794; background: #fafbfc; }
ul { background: #fff; border: 1px solid var(--line); border-radius: 8px;
  padding: 10px 24px; max-height: 260px; overflow: auto; }
.note { background: #fff; border-left: 4px solid #47617a; padding: 10px 14px; }
footer { margin-top: 40px; color: var(--muted); font-size: .8rem; }
</style>
</head>
<body>
<main>
<h1>Tableau de bord specification &harr; tests</h1>
<p class="sub">Jalon __MILESTONE__ &middot; genere le __DATE__ &middot; lecture sans terminal</p>

<div class="cards">
  <div class="card"><div class="n">__GREEN__ / __TOTAL__</div><div class="l">criteres exigibles verts (__PERCENT__ %)</div></div>
  <div class="card"><div class="n">__RED__</div><div class="l">criteres exigibles rouges</div></div>
  <div class="card"><div class="n">__NOTEST__</div><div class="l">criteres exigibles sans test</div></div>
  <div class="card"><div class="n">__SKIPPED__</div><div class="l">criteres exigibles ignores</div></div>
  <div class="card"><div class="n">__OUTSCOPE__</div><div class="l">criteres hors perimetre</div></div>
  <div class="card"><div class="n">__REQCOV__ / __REQTOT__</div><div class="l">exigences couvertes (__REQPCT__ %)</div></div>
  <div class="card"><div class="n">__TRCOV__ / __TRTOT__</div><div class="l">transitions couvertes</div></div>
  <div class="card"><div class="n">__NTESTS__</div><div class="l">tests executes</div></div>
  <div class="card"><div class="n">__ORPHANS__</div><div class="l">tests orphelins</div></div>
</div>
<p class="note"><strong>Evolution :</strong> __EVOLUTION__<br>
__SCOPE_NOTE__</p>

<h2>Criteres du jalon</h2>
<table><thead><tr><th>Critere</th><th>Statut</th><th>Tests</th></tr></thead>
<tbody>__MILESTONE_ROWS__</tbody></table>

<h2>Criteres d'acceptation (tous)</h2>
<table><thead><tr><th>Critere</th><th>Statut</th><th>Tests</th></tr></thead>
<tbody>__CRITERIA_ROWS__</tbody></table>

<h2>Exigences RF / RB / RT sans test</h2>
<p>__UNCOVERED_COUNT__ exigence(s) sans test ni justification. La porte ET-355 est active au jalon final ; elle est publiee ici des maintenant.</p>
<ul>__UNCOVERED__</ul>

<h2>Transitions</h2>
<table><thead><tr><th>Transition</th><th>Tests qui la citent</th></tr></thead>
<tbody>__TRANSITIONS__</tbody></table>

<h2>Tests orphelins</h2>
<ul>__ORPHAN_LIST__</ul>

<h2>Identifiants inconnus</h2>
<ul>__UNKNOWN_LIST__</ul>

<footer>Genere par tools/spec_trace.py &mdash; ne pas modifier a la main.</footer>
</main>
</body>
</html>
"""
    replacements = {
        "__MILESTONE__": esc(report.milestone),
        "__DATE__": esc(datetime.now(UTC).isoformat(timespec="seconds")),
        "__GREEN__": str(summary["in_scope_green"]),
        "__TOTAL__": str(summary["in_scope_total"]),
        "__PERCENT__": str(summary["in_scope_percent"]),
        "__OUTSCOPE__": str(summary["ca_out_of_scope"]),
        "__RED__": str(summary["ca_red"]),
        "__NOTEST__": str(summary["ca_no_test"]),
        "__SKIPPED__": str(summary["ca_skipped"]),
        "__REQCOV__": str(summary["requirements_covered"]),
        "__REQTOT__": str(summary["requirements_total"]),
        "__REQPCT__": str(summary["requirements_percent"]),
        "__TRCOV__": str(summary["transitions_covered"]),
        "__TRTOT__": str(summary["transitions_total"]),
        "__NTESTS__": str(summary["tests"]),
        "__ORPHANS__": str(summary["orphan_tests"]),
        "__EVOLUTION__": evolution,
        "__SCOPE_NOTE__": (
            f"{summary['ca_out_of_scope']} critere(s) hors perimetre : ils appartiennent "
            "a des jalons posterieurs et ne sont pas exiges avant leur jalon."
        ),
        "__MILESTONE_ROWS__": milestone_rows,
        "__CRITERIA_ROWS__": criteria_rows,
        "__UNCOVERED_COUNT__": str(len(uncovered)),
        "__UNCOVERED__": uncovered_preview or "<li>Aucune.</li>",
        "__TRANSITIONS__": transitions,
        "__ORPHAN_LIST__": orphan,
        "__UNKNOWN_LIST__": unknown,
    }
    for key, value in replacements.items():
        template = template.replace(key, value)
    return template


def write_history(report: Report) -> None:
    raw: dict[str, Any] = {"milestones": {}}
    if HISTORY_PATH.is_file():
        raw = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    summary = report.summary()
    raw.setdefault("milestones", {})[report.milestone] = {
        "ca_green": summary["ca_green"],
        "ca_total": summary["ca_total"],
        "ca_percent": summary["ca_percent"],
        "requirements_covered": summary["requirements_covered"],
        "transitions_covered": summary["transitions_covered"],
        "recorded_at": datetime.now(UTC).isoformat(timespec="seconds"),
    }
    HISTORY_PATH.write_text(json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_outputs(report: Report) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    data = {
        "milestone": report.milestone,
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "summary": report.summary(),
        "evolution": report.evolution,
        "criteria": report.criteria,
        "requirements": report.requirements,
        "transitions": {
            key: {"covered_by": value.covered_by} for key, value in report.transitions.items()
        },
        "orphan_tests": report.orphan_tests,
        "unknown_ids": report.unknown_ids,
    }
    (REPORTS / "spec-trace.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (REPORTS / "spec-trace.md").write_text(render_markdown(report), encoding="utf-8")
    (REPORTS / "spec-trace.html").write_text(render_html(report), encoding="utf-8")
    write_history(report)


def default_milestone() -> str:
    progress = REPORTS / "PROGRESS.md"
    if progress.is_file():
        match = re.search(r"Jalon courant\s*:\s*(MS-\d+)", progress.read_text(encoding="utf-8"))
        if match:
            return match.group(1)
    return "MS-0"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--milestone", default=None)
    parser.add_argument("--junit", default=str(JUNIT_DEFAULT))
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--strict-requirements", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    milestone = args.milestone or default_milestone()
    report = build_report(milestone, Path(args.junit))
    summary = report.summary()
    print(
        f"{milestone} : {summary['in_scope_green']}/{summary['in_scope_total']} CA exigibles verts, "
        f"{summary['ca_no_test']} sans test, {summary['ca_out_of_scope']} hors perimetre, "
        f"{summary['transitions_covered']}/{summary['transitions_total']} transitions couvertes, "
        f"{summary['tests']} tests, {summary['orphan_tests']} orphelins."
    )
    errors = (
        gate_errors(report, strict_requirements=args.strict_requirements) if args.strict else []
    )
    if args.write:
        write_outputs(report)
        print(
            "Tableaux de bord ecrits : docs/reports/spec-trace.html, spec-trace.md, spec-trace.json"
        )
    if errors:
        print("Portes de tracabilite en echec :", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
