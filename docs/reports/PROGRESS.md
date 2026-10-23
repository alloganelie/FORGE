# PROGRESS — état d'avancement (mis à jour par l'agent après chaque tranche)

**Jalon courant :** MS-0 — Fondations (en cours)
**Dernière tranche terminée :** T2 — modules et règles de dépendance
**Prochaine tranche :** T3 — types énumérés et transitions générés depuis la spécification

## Fait
- **T1 — Socle et make check.** Dépôt, `pyproject.toml` verrouillé par `uv.lock`, `Makefile`, `tools/check.py`, configuration Pydantic validée au démarrage (ET-008), squelette FastAPI avec le nom FORGE réservé au frontend (ET-002, Q-001), CI GitHub Actions.
- **T2 — Modules et dépendances.** 23 modules MOD-01 à MOD-23 avec façade `api.py`, `events.py`, `core/` pur et `infra/` ; contrôle statique DR-01 à DR-07 (ET-005, ET-006), tests unitaires associés.

## À faire (ordonné)
1. T3 — génération des types énumérés (ET-017) et des transitions YAML (ET-035) depuis la spécification ; moteur d'états pur et gardes (ET-036, ET-039, ET-041).
2. T4 — base PostgreSQL, migrations, contraintes d'invariants, RLS, déclencheurs d'immutabilité (ET-013, ET-018, ET-019, ET-021, ET-027, ET-029).
3. T5 — journal chaîné : canonisation RFC 8785, `ledger.append`, vérification, tests de contournement (ET-022 à ET-026).
4. T6 — TST-18 : test à états aléatoires sur IV-01 à IV-15, contre PostgreSQL réel (ET-043, ET-358).
5. T7 — `spec_trace`, tableaux de bord HTML/MD, portes de couverture (ET-353 à ET-356, ET-372).
6. T8 — OpenAPI versionné, image Docker multi-étapes non root avec SBOM, compose local (ET-002, ET-009, ET-010).
7. T9 — rapport et guide de démonstration MS-0.

## Décisions prises (avec identifiants ADR si besoin)
- Q-001 : FORGE réservé au frontend et à l'infrastructure, absent des livrables et messages.
- ADR-001 à ADR-009 proposés dans `docs/adr/` (à compléter au fil des tranches).

## Questions en attente pour le Product Owner
- Voir `docs/reports/QUESTIONS.md`

## Prochaine commande à lancer
`make check`
