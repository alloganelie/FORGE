# PROGRESS — état d'avancement (mis à jour par l'agent après chaque tranche)

**Jalon courant :** MS-1 — Gouvernance (terminé, en revue Product Owner)
**Dernière tranche terminée :** T15 — rapport et guide de démonstration MS-1
**Prochaine tranche :** aucune ; **ne pas commencer MS-2** avant la revue PO.

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
- E-01 : aucun remote Git configuré dans cet environnement ; la CI n'a donc pas pu être déclenchée sur GitHub. Le workflow et l'exécution locale équivalente sont verts.

## Questions en attente pour le Product Owner

- Aucune question bloquante.
- Points à arbitrer dans le rapport : ET-057/059/060/063/064/066 partiels, et console de démonstration sans OIDC (rôle lu en base mais acteur choisi dans l'interface).

## Prochaine commande à lancer

`make check` — puis suivre `docs/reports/MS-1-demo.md`.
