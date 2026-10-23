"""Chargement et application des JSON Schemas versionnes (ET-054)."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from typing import Any, Final

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError

from agent.documents_io.api import read_utf8
from agent.governance.core.types import ArtifactType
from agent.governance.core.validation import Finding

DEFAULT_SCHEMA_DIR: Final[str] = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "schemas", "v1")
)


class SchemaStoreError(RuntimeError):
    """Schema absent ou invalide : le demarrage de la validation echoue."""


def _json_path(error: ValidationError) -> str:
    path = "$"
    for part in error.absolute_path:
        path += f"[{part}]" if isinstance(part, int) else f".{part}"
    return path


class JsonSchemaStore:
    """Valide un artefact contre le schema v1 de son type."""

    def __init__(self, directory: str | None = None) -> None:
        self.directory = directory if directory is not None else DEFAULT_SCHEMA_DIR
        self._validators: dict[ArtifactType, Draft202012Validator] = {}

    def _validator(self, artifact_type: ArtifactType) -> Draft202012Validator:
        if artifact_type not in self._validators:
            filename = f"{artifact_type.value}.schema.json"
            path = os.path.join(self.directory, filename)
            try:
                schema: Any = json.loads(read_utf8(path))
            except (OSError, json.JSONDecodeError) as exc:
                raise SchemaStoreError(f"schema illisible : {filename}") from exc
            try:
                Draft202012Validator.check_schema(schema)
            except SchemaError as exc:
                raise SchemaStoreError(f"schema invalide : {filename}") from exc
            self._validators[artifact_type] = Draft202012Validator(schema)
        return self._validators[artifact_type]

    def validate(
        self, artifact_type: ArtifactType, content: Mapping[str, Any]
    ) -> tuple[Finding, ...]:
        validator = self._validator(artifact_type)
        findings = tuple(
            Finding(code="schema", message=error.message, path=_json_path(error))
            for error in sorted(
                validator.iter_errors(dict(content)), key=lambda item: list(item.absolute_path)
            )
        )
        return findings
