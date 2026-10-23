# ADR-008 — Outillage de test et hypothèses de propriété

- **Statut :** proposé (MS-0)
- **Date :** 2026-10-23
- **Références :** ET-043, ET-044, ET-353 à ET-359, ADR-017 (spécification technique)

## Contexte

La pyramide de tests doit couvrir le domaine pur, les propriétés, l'intégration
et l'acceptation. TST-18 doit tourner à chaque intégration.

## Décision

- pytest + pytest-cov pour l'exécution, hypothesis pour TST-18 et les
  propriétés, mypy strict et ruff pour la qualité.
- Les tests PostgreSQL sont marqués @pytest.mark.integration et utilisent
  une base réelle ; make check les exécute.
- httpx2 est ajouté uniquement comme dépendance de test, car
  starlette.testclient 1.9 l'exige. Il ne sert jamais en production.
- Les tests d'acceptation vivent dans backend/tests/acceptance/ et sont
  étiquetés par identifiant.

## Conséquences

- Une régression d'invariant est détectée par Hypothesis avec une suite
  réductible.
- Les tests d'intégration peuvent être lancés seuls avec
  python tools/check.py integration.
- make check nécessite Docker localement pour démarrer PostgreSQL si la base
  n'est pas déjà joignable.

## Alternatives écartées

- Doubler la base : interdit par ET-358.
- Ajouter une bibliothèque de snapshot : non nécessaire au périmètre MS-0.
