# ADR-002 — Pile Python et gestion des dépendances

- **Statut :** proposé (MS-0)
- **Date :** 2026-10-23
- **Références :** ET-001, ET-002, ET-003, ET-004, ADR-002 et ADR-017 (spécification technique)

## Contexte

Le backend doit être en Python ≥ 3.13, typé strictement, avec FastAPI,
Pydantic v2, SQLAlchemy 2, Alembic et psycopg 3. Les versions doivent être
épinglées et reproductibles.

## Décision

- Python 3.13, pyproject.toml unique, uv comme outil unique de résolution,
  uv.lock versionné. uv sync --locked est exécuté par make check.
- Typage strict mypy sur backend/src ; format et lint ruff.
- Contrat OpenAPI généré par tools/gen_openapi.py dans backend/openapi.json
  et vérifié par make check.
- Toute nouvelle dépendance exige un ADR.

## Conséquences

- Une mise à jour de dépendance passe la chaîne complète et le verrou change.
- uv.lock est la source de vérité des versions ; aucun pip install manuel
  n'est nécessaire.

## Alternatives écartées

- Poetry/pip-tools : un seul outil demandé (ET-004), uv couvre verrou et
  environnement.
- Typage progressif : incompatible avec ET-001 (strict, bloquant).
