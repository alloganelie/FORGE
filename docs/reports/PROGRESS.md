# PROGRESS — état d'avancement (mis à jour par l'agent après chaque tranche)

**Jalon courant :** MS-0 — Fondations (terminé, en revue Product Owner)
**Dernière tranche terminée :** T9 — rapport et guide de démonstration
**Prochaine tranche :** aucune ; **ne pas commencer MS-1** avant la revue PO.

## Fait (par tranche)

1. **T1 — Socle et make check.** Dépôt Git, `pyproject.toml` verrouillé par `uv.lock`, `Makefile`, `tools/check.py`, configuration Pydantic validée au démarrage (ET-008), squelette FastAPI (ET-002), CI GitHub Actions.
2. **T2 — Modules et frontières.** 23 modules MOD-01 à MOD-23 avec façade `api.py`, `events.py`, `core/` pur et `infra/` ; contrôle statique DR-01 à DR-07 (ET-005, ET-006).
3. **T3 — Types et machines générés.** Enums ST/QI/LC/AN/RC/DH/AU générés (ET-017) ; transitions YAML générées depuis F 8 et T 7.2 (ET-035) ; moteur pur, gardes, reprise (ET-036, ET-039, ET-041).
4. **T4 — PostgreSQL et invariants.** Migration Alembic, types, tables, contraintes CHECK, déclencheurs d'immutabilité, RLS forcée, rôle applicatif sans DELETE (ET-013, ET-018, ET-019, ET-021, ET-027, ET-028, ET-029).
5. **T5 — Journal chaîné.** Canonisation RFC 8785, chaîne par demande, `append_event` transactionnel, vérification, tests de contournement UPDATE/DELETE/TRUNCATE, concurrence sans trou (ET-022 à ET-026).
6. **T6 — TST-18.** Test à états aléatoires Hypothesis (250 exemples) sur IV-01 à IV-15 ; rejeu du parcours nominal sur PostgreSQL réel (ET-043, ET-358).
7. **T7 — Traçabilité.** `tools/spec_trace.py`, portes ET-354/ET-356/ET-044, tableaux de bord HTML/MD/JSON, historique par jalon (ET-353 à ET-356, ET-372).
8. **T8 — Image et exploitation.** Dockerfile multi-étapes non root, deux rôles, compose local, quatre environnements, SBOM en CI (ET-007, ET-009, ET-010) ; outil `verify-chain` et démonstration `demo-ledger`.
9. **T9 — Documentation.** Rapport `docs/reports/MS-0-rapport.md` et guide `docs/reports/MS-0-demo.md` ; ADR-001 à ADR-009.

## Résultat

- `make check` : **vert** (format, mypy strict, dépendances, génération, 77 tests, traçabilité).
- TST-18 : **vert** ; 54/54 transitions couvertes ; 0 test orphelin ; 0 identifiant inconnu.
- Tableau de bord : `docs/reports/spec-trace.html`.

## Décisions prises

- Q-001 : FORGE réservé au frontend et à l'infrastructure, absent des livrables et messages.
- Q-002 : reprise vers l'état d'origine, y compris Reçue et Vérification de faisabilité (hypothèse).
- Q-003 : portes de traçabilité appliquées au périmètre cumulé des jalons ; ET-355 bloquante au jalon final (hypothèse).
- ADR-001 à ADR-009 dans `docs/adr/`.

## Questions en attente pour le Product Owner

- Q-002 et Q-003 dans `docs/reports/QUESTIONS.md`.

## Prochaine commande à lancer

`make check` — puis suivre `docs/reports/MS-0-demo.md`.
