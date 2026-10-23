# PROGRESS — état d'avancement (mis à jour par l'agent après chaque tranche)

**Jalon courant :** MS-2 — Demande et faisabilité (prêt à démarrer)
**Dernière tranche terminée :** MS-1 validé par le PO (tag ms-1)
**Prochaine tranche :** MS-2, section 3 (voir `docs/milestones/MS-2.md`).

## Fait — MS-0 (fondations)

1. Socle, configuration, 23 modules, règles DR-01 à DR-07, `make check`.
2. Types énumérés et transitions générés, moteur d'états, journal chaîné, invariants PostgreSQL, RLS.
3. TST-18, traçabilité HTML/MD, image non root, CI, rapport et guide MS-0.

## Fait — MS-1 (gouvernance)

4. **T11 — Schémas et CEL.** Quatre JSON Schemas v1 versionnés ; évaluateur CEL restreint et encapsulé ; arithmétique décimale ; contrôle AST anti-`float` ; ADR-010.
5. **T12 — Base et service.** Migration `0002_governance` : `governance_artifact_versions`, `request_pins`, `change_proposals`, `governance_observations`, `role_assignments` ; déclencheurs d'immuabilité et de non-rétroactivité ; RLS ; service de gouvernance (rôles, versions, approbation, épinglage, impact).
6. **T13 — Pipeline et critères.** Pipeline en 9 étapes composables ; tests de règles ; observations sur exemple contradictoire ; CA-150, CA-151, CA-152, CA-153 verts.
7. **T14 — Console et démonstration.** SCR-15/SCR-17 avec en-tête FORGE ; API JSON ; scripts `demo-governance` et `seed-governance` ; refus d'un utilisateur ordinaire démontré.
8. **T15 — Documentation.** Rapport `docs/reports/MS-1-rapport.md`, guide `docs/reports/MS-1-demo.md`, ADR-010.

## Résultat

- `make check` : **vert** — format, mypy strict, dépendances, contrôle décimal, génération, **119 tests**, traçabilité.
- Tableau de bord : **MS-1, 4/4 CA exigibles verts**, 0 sans test, 191 CA hors périmètre, 54/54 transitions, 0 orphelin.
- TST-15 : vert ; lot de règles approuvé de bout en bout ; épinglage et non-rétroactivité testés.
- Aucun test, contrainte ou déclencheur MS-0 affaibli.

## Décisions prises

- Q-001 : FORGE dans l'en-tête de la console, jamais dans les livrables/messages.
- Q-002 : reprise depuis `suspended_from` du journal (corrigée MS-0).
- Q-003 : portes de traçabilité au périmètre cumulé.
- ADR-010 : `jsonschema` pour les schémas, évaluateur CEL restreint et décimal.
- E-01 : levée (remote https://github.com/alloganelie/FORGE.git configuré, code et tags poussés, CI GitHub Actions active).

## Questions en attente pour le Product Owner

- Aucune question bloquante (Q-001, Q-002, Q-003 tranchées).
- Points documentés du rapport MS-1 : ET-057/059/060/063/064/066 partiels et console sans OIDC (à compléter dans les jalons ultérieurs comme prévu).

## Prochaine commande à lancer

`make check` — puis démarrer MS-2 (voir `docs/milestones/MS-2.md`).
