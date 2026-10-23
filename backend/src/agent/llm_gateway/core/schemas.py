"""Schemas plats des sorties LLM de MS-2 (Annexe B, LG-06)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ParamValue(StrictModel):
    name: str
    value: str
    justification_quote: str


class AmbiguityFlag(StrictModel):
    parameter: str
    reason: str
    blocking: bool = False


class Lt01Output(StrictModel):
    candidate_type: str
    objective: str
    context: str
    purpose: str
    constraints: list[str]
    parameters: list[ParamValue]
    ambiguities: list[AmbiguityFlag]
    multiple_deliverables_detected: bool
    requested_format: str | None = None


class ClarificationQuestion(StrictModel):
    parameter: str
    text: str
    why_needed: str


class Lt02Output(StrictModel):
    questions: list[ClarificationQuestion]


class CommandProposal(StrictModel):
    command: Literal[
        "submit_request",
        "answer_clarification",
        "provide_information",
        "ask_status",
        "suspend_request",
        "resume_request",
        "request_cancellation",
        "request_revision",
        "split_request",
        "none",
    ]
    parameters_json: str
    confidence: Literal["high", "medium", "low"]


class Lt01Request(StrictModel):
    text: str = Field(min_length=1, max_length=20_000)
