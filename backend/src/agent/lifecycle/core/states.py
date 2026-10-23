"""Types enumeres generes depuis la specification (ET-017, DC-05).

NE PAS MODIFIER A LA MAIN. Regenerer : python tools/gen_enums.py
Sources : specification fonctionnelle section 8, specification technique 6.3.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class RequestState(StrEnum):
    """Valeurs alignees sur le type PostgreSQL st_request."""

    RECEIVED = "received"
    CLARIFYING = "clarifying"
    FEASIBILITY = "feasibility"
    PRODUCING = "producing"
    QUALITY_CONTROL = "quality_control"
    BLOCKED = "blocked"
    AWAITING_DECISION = "awaiting_decision"
    SUSPENDED = "suspended"
    FINALIZED = "finalized"
    CANCELLED = "cancelled"


class ConformityState(StrEnum):
    """Valeurs alignees sur le type PostgreSQL st_conformity."""

    NOT_EVALUATED = "not_evaluated"
    IN_CONTROL = "in_control"
    NON_CONFORMING = "non_conforming"
    CONFORMING = "conforming"


class ApprovalState(StrEnum):
    """Valeurs alignees sur le type PostgreSQL st_approval."""

    NOT_SUBMITTED = "not_submitted"
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    REFUSED = "refused"


class DiffusionState(StrEnum):
    """Valeurs alignees sur le type PostgreSQL st_diffusion."""

    NOT_AUTHORIZED = "not_authorized"
    AUTHORIZED = "authorized"
    REVOKED = "revoked"


class VersionState(StrEnum):
    """Valeurs alignees sur le type PostgreSQL st_version."""

    PROVISIONAL = "provisional"
    FINALIZED = "finalized"
    SUPERSEDED = "superseded"
    ABANDONED = "abandoned"


class ElementState(StrEnum):
    """Valeurs alignees sur le type PostgreSQL st_element."""

    TO_PRODUCE = "to_produce"
    PRODUCED = "produced"
    BLOCKED = "blocked"
    AWAITING = "awaiting"
    CONTROLLED_OK = "controlled_ok"
    NON_CONFORMING = "non_conforming"
    NOT_APPLICABLE = "not_applicable"


class QualityStatus(StrEnum):
    """Valeurs alignees sur le type PostgreSQL qi_status."""

    VERIFIED = "verified"
    CANDIDATE = "candidate"
    UNCERTAIN = "uncertain"
    CONTRADICTORY = "contradictory"
    OUT_OF_PERIOD = "out_of_period"
    PROHIBITED = "prohibited"
    ABSENT = "absent"


class LcStatus(StrEnum):
    """Valeurs alignees sur le type PostgreSQL lc_status."""

    SATISFIED = "satisfied"
    PARTIAL = "partial"
    TO_CLARIFY = "to_clarify"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class AtomOrigin(StrEnum):
    """Valeurs alignees sur le type PostgreSQL atom_origin."""

    QUOTATION = "quotation"
    REFORMULATION = "reformulation"
    COMPUTATION = "computation"
    TEMPLATE_TEXT = "template_text"
    STRUCTURE = "structure"


class ControlOutcome(StrEnum):
    """Valeurs alignees sur le type PostgreSQL control_outcome."""

    PASSED = "passed"
    FAILED = "failed"
    NOT_EXECUTABLE = "not_executable"
    NOT_APPLICABLE = "not_applicable"


class AnomalyClass(StrEnum):
    """Valeurs alignees sur le type PostgreSQL anomaly_class."""

    ESTABLISHED_NONCONFORMITY = "established_nonconformity"
    ESTABLISHED_INCONSISTENCY = "established_inconsistency"
    OBSERVATION = "observation"


class DecisionType(StrEnum):
    """Valeurs alignees sur le type PostgreSQL decision_type."""

    CONTRADICTION_ARBITRATION = "contradiction_arbitration"
    UNCOVERED_DECISION = "uncovered_decision"
    EXCEPTION = "exception"
    TEMPORARY_SOURCE_AUTHORIZATION = "temporary_source_authorization"
    APPROVAL = "approval"
    DIFFUSION_AUTHORIZATION = "diffusion_authorization"
    RULE_CHANGE = "rule_change"
    PRIORITY_ARBITRATION = "priority_arbitration"
    CANCELLATION = "cancellation"
    UNCOVERED_CORRECTION = "uncovered_correction"


class AuthLevel(StrEnum):
    """Valeurs alignees sur le type PostgreSQL auth_level."""

    ACCESS = "access"
    USE = "use"
    INTEGRATION = "integration"
    DIFFUSION = "diffusion"

SPEC_IDS: Final[dict[str, dict[str, str]]] = {
    "RequestState": {
        "received": "ST-R-01",
        "clarifying": "ST-R-02",
        "feasibility": "ST-R-03",
        "producing": "ST-R-04",
        "quality_control": "ST-R-05",
        "blocked": "ST-R-06",
        "awaiting_decision": "ST-R-07",
        "suspended": "ST-R-08",
        "finalized": "ST-R-09",
        "cancelled": "ST-R-10",
    },
    "ConformityState": {
        "not_evaluated": "ST-C-01",
        "in_control": "ST-C-02",
        "non_conforming": "ST-C-03",
        "conforming": "ST-C-04",
    },
    "ApprovalState": {
        "not_submitted": "ST-A-01",
        "not_required": "ST-A-02",
        "pending": "ST-A-03",
        "approved": "ST-A-04",
        "refused": "ST-A-05",
    },
    "DiffusionState": {
        "not_authorized": "ST-D-01",
        "authorized": "ST-D-02",
        "revoked": "ST-D-03",
    },
    "VersionState": {
        "provisional": "ST-V-01",
        "finalized": "ST-V-02",
        "superseded": "ST-V-03",
        "abandoned": "ST-V-04",
    },
    "ElementState": {
        "to_produce": "ST-E-01",
        "produced": "ST-E-02",
        "blocked": "ST-E-03",
        "awaiting": "ST-E-04",
        "controlled_ok": "ST-E-05",
        "non_conforming": "ST-E-06",
        "not_applicable": "ST-E-07",
    },
    "QualityStatus": {
        "verified": "QI-01",
        "candidate": "QI-02",
        "uncertain": "QI-03",
        "contradictory": "QI-04",
        "out_of_period": "QI-05",
        "prohibited": "QI-06",
        "absent": "QI-07",
    },
    "LcStatus": {
        "satisfied": "LC-01",
        "partial": "LC-02",
        "to_clarify": "LC-03",
        "blocked": "LC-04",
        "not_applicable": "LC-05",
    },
    "ControlOutcome": {
        "passed": "RC-1",
        "failed": "RC-2",
        "not_executable": "RC-3",
        "not_applicable": "RC-4",
    },
    "AnomalyClass": {
        "established_nonconformity": "AN-1",
        "established_inconsistency": "AN-2",
        "observation": "AN-3",
    },
    "DecisionType": {
        "contradiction_arbitration": "DH-01",
        "uncovered_decision": "DH-02",
        "exception": "DH-03",
        "temporary_source_authorization": "DH-04",
        "approval": "DH-05",
        "diffusion_authorization": "DH-06",
        "rule_change": "DH-07",
        "priority_arbitration": "DH-08",
        "cancellation": "DH-09",
        "uncovered_correction": "DH-10",
    },
    "AuthLevel": {
        "access": "AU-1",
        "use": "AU-2",
        "integration": "AU-3",
        "diffusion": "AU-4",
    },
}

AXIS_ENUM_NAMES: Final[dict[str, str]] = {
    "R": "RequestState",
    "C": "ConformityState",
    "A": "ApprovalState",
    "D": "DiffusionState",
    "V": "VersionState",
    "E": "ElementState",
}

AXIS_STATE_IDS: Final[dict[str, dict[str, str]]] = {
    "R": {
        "received": "ST-R-01",
        "clarifying": "ST-R-02",
        "feasibility": "ST-R-03",
        "producing": "ST-R-04",
        "quality_control": "ST-R-05",
        "blocked": "ST-R-06",
        "awaiting_decision": "ST-R-07",
        "suspended": "ST-R-08",
        "finalized": "ST-R-09",
        "cancelled": "ST-R-10",
    },
    "C": {
        "not_evaluated": "ST-C-01",
        "in_control": "ST-C-02",
        "non_conforming": "ST-C-03",
        "conforming": "ST-C-04",
    },
    "A": {
        "not_submitted": "ST-A-01",
        "not_required": "ST-A-02",
        "pending": "ST-A-03",
        "approved": "ST-A-04",
        "refused": "ST-A-05",
    },
    "D": {
        "not_authorized": "ST-D-01",
        "authorized": "ST-D-02",
        "revoked": "ST-D-03",
    },
    "V": {
        "provisional": "ST-V-01",
        "finalized": "ST-V-02",
        "superseded": "ST-V-03",
        "abandoned": "ST-V-04",
    },
    "E": {
        "to_produce": "ST-E-01",
        "produced": "ST-E-02",
        "blocked": "ST-E-03",
        "awaiting": "ST-E-04",
        "controlled_ok": "ST-E-05",
        "non_conforming": "ST-E-06",
        "not_applicable": "ST-E-07",
    },
}
