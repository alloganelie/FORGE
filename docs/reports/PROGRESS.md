# PROGRESS — état d'avancement (mis à jour par l'agent après chaque tranche)

**Jalon courant :** MS-2 — Demande et faisabilité (terminé, en revue Product Owner)
**Dernière tranche terminée :** T20 — rapport et guide de démonstration MS-2
**Prochaine tranche :** aucune ; **ne pas commencer MS-3** avant la revue PO.

## Fait — MS-0 (fondations)

1. Socle, configuration, 23 modules, règles DR-01 à DR-07, `make check`.
2. Types énumérés et transitions générés, moteur d'états, journal chaîné, invariants PostgreSQL, RLS.
3. TST-18, traçabilité HTML/MD, image non root, CI, rapport et guide MS-0.

## Fait — MS-1 (gouvernance)

4. **T11 — Schémas et CEL.** JSON Schemas v1, évaluateur CEL décimal, contrôle anti-`float`, ADR-010.
5. **T12 — Base et service.** Migration `0002_governance`, artefacts immuables, épinglage, rôles, RLS.
6. **T13 — Pipeline et critères.** Pipeline 9 étapes, CA-150 à CA-153, TST-15.
7. **T14 — Console et démonstration.** SCR-15/SCR-17 avec FORGE, API, démos.
8. **T15 — Documentation.** Rapport et guide MS-1.

## Fait — MS-2 (demande et faisabilité)

9. **T16 — Migration et passerelle LLM.** `0003_requests` ; `run_task` unique, validation Pydantic, erreurs typées, journal `llm_calls`, rejeu strict sans fournisseur externe.
10. **T17 — Compréhension et clarification.** LT-01/LT-02 en rejeu, paramètres avec citation, questions bloquantes hiérarchisées, CA-001 à CA-010, CA-142, CA-189, CA-190.
11. **T18 — Faisabilité.** Diagnostic en 7 dimensions, motifs MB, épinglage des versions, blocage/suspension, CA-011 à CA-020.
12. **T19 — Suivi et interface.** Gabarits d'état français, statuts R/C/A/D/V séparés, historique, SCR-15/MS-2 Next.js avec `StatusStrip`, CA-135 à CA-144.
13. **T20 — Documentation.** Rapport `docs/reports/MS-2-rapport.md`, guide `docs/reports/MS-2-demo.md`, démo `make demo-requests`.

## Résultat

- `make check` : **vert** — **160 tests**, mypy strict, dépendances, contrôle décimal, génération, traçabilité.
- Tableau de bord : **MS-2, 35/35 CA exigibles verts** (31 CA MS-2 + 4 CA MS-1 cumulés), 0 sans test, 160 tests, 0 orphelin.
- TST-01, TST-02 et TST-14 (partie suivi) : verts.
- Squelette de bout en bout : demande → clarification → faisabilité → statut, démontré par `make demo-requests`.
- Aucun test, contrainte ou déclencheur des jalons précédents affaibli.

## Décisions prises

- Q-001 : FORGE dans l'en-tête de l'interface, jamais dans les messages/livrables.
- Q-002, Q-003 : décisions antérieures inchangées.
- E-01 : **levée** — remote GitHub configuré, branches/tags synchronisés, CI active (information PO).
- MS-2 : les tests et la CI utilisent uniquement des réponses LLM rejouées (`ReplayAdapter`) ; aucun fournisseur payant.
- Les sorties LLM sont validées par Pydantic ; un refus ou une sortie invalide est un échec typé.

## Questions en attente pour le Product Owner

- Aucune question bloquante.
- Points partiels documentés : ET-231/238/243/246/248/249/253 à 255/257/259/261/262/297/299 ; voir le rapport MS-2.

## Prochaine commande à lancer

`make check` — puis suivre `docs/reports/MS-2-demo.md`.
