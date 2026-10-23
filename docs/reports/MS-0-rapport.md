# Rapport de fin de jalon — MS-0 Fondations

**Date :** 2026-10-23  
**Jalon :** MS-0 — Fondations  
**Statut :** terminé, soumis à la revue du Product Owner  
**Périmètre :** dépôt, intégration continue, image, base de données et migrations, configuration, journal chaîné, moteur d'états généré, traçabilité spécification ↔ tests, règles de dépendance. Aucune fonction métier.

---

## 1. Résultat en une page

Les fondations sont opérationnelles et vérifiables par des preuves observables :

- `make check` est vert : format, typage strict, règles d'imports, génération, **77 tests**, traçabilité.
- **TST-18** est vert : 250 séquences aléatoires de commandes, invariants IV-01 à IV-15 vérifiés après chaque pas, plus un rejeu du parcours nominal sur PostgreSQL réel.
- Le **journal chaîné** est testé, y compris les tentatives de contournement : UPDATE, DELETE et TRUNCATE refusés ; un faux `self_hash` est détecté par recalcul ; deux écritures concurrentes produisent `request_seq` 1 et 2 sans trou.
- Le **tableau de bord** `docs/reports/spec-trace.html` est publié : 54/54 transitions couvertes, 0 test orphelin, 0 identifiant inconnu, 195 CA « hors périmètre » (MS-0 n'a aucun CA).
- L'**image** est construite localement, s'exécute avec l'UID 10001 et répond sur `/healthz` ; la CI publie une SBOM.

---

## 2. Critères de sortie du brief

| Critère | Résultat | Preuve |
|---|---|---|
| TST-18 vert (IV-01 à IV-15) | **Vert** | `backend/tests/property/test_tst18.py` (3 tests, Hypothesis 250 exemples) et `backend/tests/integration/test_tst18_db.py` (3 tests) |
| Journal chaîné testé, contournements compris | **Vert** | `backend/tests/integration/test_ledger_db.py` (6 tests), `test_ledger_core.py` (5 tests) |
| `spec_trace` publie un tableau de bord | **Vert** | `docs/reports/spec-trace.html`, `.md`, `.json`, historique `spec-trace-history.json` |
| Intégration continue verte | **Prête et verte localement** | `.github/workflows/ci.yml` ; `make check` exécuté localement. La première exécution GitHub reste à faire après création du remote (écart E-01) |
| `make check` existe et passe | **Vert** | sortie finale : 77 tests, `MS-0 : 0/0 CA exigibles verts, 0 sans test, 195 hors périmètre, 54/54 transitions couvertes, 0 orphelin` |

---

## 3. Ce qui a été construit

### 3.1 Dépôt et frontières

- 23 modules MOD-01 à MOD-23, chacun avec `api.py` (façade), `events.py`, `core/` pur et `infra/`.
- `tools/check_imports.py` vérifie DR-01 à DR-07 par analyse AST ; une violation fait échouer le build. Les règles dynamiques sont doublées par des déclencheurs PostgreSQL.
- `mypy` strict sur `backend/src`, `ruff` pour format et lint, `uv.lock` pour les versions.

### 3.2 Configuration et plateforme

- `Settings` Pydantic (préfixe `AGENT_`) : validation au démarrage, refus des variables inconnues, refus d'une URL non psycopg, secret obligatoire en production (ET-008).
- Port d'horloge injecté (`Clock`, `FixedClock`, `SystemClock`) et UUIDv7 générés par l'application (ET-014, ET-016).
- Quatre configurations séparées : `ops/env/local.env.example`, `ci.env`, `preprod.env.example`, `prod.env.example`.

### 3.3 Base de données et invariants

- PostgreSQL 17 avec pgvector, pgcrypto et pg_trgm ; migration Alembic `0001_foundations`.
- Types énumérés générés depuis F 8 et T 6.3 ; un test compare les valeurs PostgreSQL aux enums Python et aux identifiants ST.
- Contraintes `CHECK` inter-axes (IV-05, IV-12, IV-14, RB-114), déclencheurs d'immutabilité (journal, résultats de contrôle, documents, versions finalisées, atomes, éléments), blocage des écritures d'état hors moteur, gel des demandes finalisées/annulées.
- RLS activée et forcée sur les tables liées aux demandes ; rôle applicatif `agent_app` non propriétaire et sans `DELETE` (ET-029, ET-019).
- Test de migration upgrade → downgrade → upgrade sur une base temporaire (ET-020).

### 3.4 Journal chaîné

- `ledger_events` en ajout seul, y compris `TRUNCATE` ; `request_seq` sans trou sous verrou de la demande ; `prev_hash` du dernier événement ; `self_hash` calculé sur une sérialisation canonique RFC 8785.
- `append_event` écrit l'événement dans la transaction métier ; `state_changes` est alimenté dans la même transaction (ET-023, ET-024).
- `make verify-chain` recalcule toutes les chaînes ; `write_checkpoint` conserve une borne de contrôle (ET-025, partiel : pas encore de tâche périodique planifiée).

### 3.5 Moteur d'états

- Six machines (R, C, A, D, V, E) générées depuis F 8.2 à 8.7 et T 7.2 dans `rulepacks/state_machines/` ; 53 transitions + TR-R-22 déclarée comme non-transition (révision).
- Moteur pur, gardes pures, refus par défaut d'une garde inconnue, reprise pure (ET-036, ET-039, ET-041).
- Application transactionnelle : verrou, `row_version`, état, `state_changes`, journal ; conflit de version signalé (ET-037, ET-038 partiel : pas d'API 412).
- TST-18 sur le modèle pur et sur PostgreSQL réel.

### 3.6 Traçabilité et tableaux de bord

- `tools/spec_trace.py` lit `docs/spec/ids.json`, les marqueurs pytest et le JUnit, puis publie HTML/MD/JSON et l'historique.
- Portes bloquantes : identifiant inconnu (ET-356), test orphelin, transition non citée (ET-044), CA du périmètre non vert (ET-354).
- Porte ET-355 publiée dès MS-0, bloquante au jalon final (Q-003).
- Périmètre des CA : cumul des sections 4 des jalons ≤ courant. MS-0 n'a aucun CA ; les 195 CA sont affichés « hors périmètre » et ne sont pas comptés comme « sans test ».

### 3.7 Image et CI

- Image multi-étapes, non root (UID/GID 10001), deux rôles par `AGENT_ROLE` (ET-007, ET-009).
- `ops/compose.yaml` : PostgreSQL local, API, travailleur.
- CI : service PostgreSQL réel, `make check`, publication du tableau de bord, construction de l'image, vérification de l'UID et SBOM SPDX (ET-009).

---

## 4. Exigences techniques du brief (55)

### 4.1 Entièrement couvertes (35)

`ET-001` à `ET-010`, `ET-013` à `ET-018`, `ET-021` à `ET-024`, `ET-026` à `ET-029`, `ET-035`, `ET-036`, `ET-039`, `ET-041`, `ET-043`, `ET-044`, `ET-353`, `ET-354`, `ET-356`, `ET-358`, `ET-372`.

### 4.2 Partielles (20) et raison

| ET | Ce qui existe | Ce qui manque |
|---|---|---|
| ET-011 | Migration avant mise en service documentée ; compose local | Plateforme de conteneurs gérée et déploiement réel non disponibles en MS-0 |
| ET-012 | Images versionnées, downgrade testé | Politique « étendre puis contracter » non encore exercée par une deuxième migration |
| ET-019 | Aucun DELETE métier ; rôle applicatif sans DELETE | Procédure de purge et événement minimal de conservation (MS-8) |
| ET-020 | Migration versionnée, aller/retour sur base temporaire | Test sur copie de données avant/après avec jeu de données |
| ET-025 | `verify_chain`, `write_checkpoint` | Tâche périodique planifiée et alerte de sécurité |
| ET-037 | Verrou, version, existence, acteur, gardes, état, journal, projection | Politique d'autorisation, effets complets, file de jobs |
| ET-038 | Conflit `row_version` détecté | Traduction en erreur HTTP 412 (pas d'API métier en MS-0) |
| ET-040 | Prérequis inter-axes en gardes et contraintes | Couverture exhaustive des six axes |
| ET-042 | Effets lus depuis le YAML ; `set`/`clear` d'origine appliqués | `emit` et `job` dans une boîte d'envoi |
| ET-045 | Table `command_results` | Idempotence branchée sur les commandes |
| ET-046 | Table `step_runs` | Enregistrement par le pipeline |
| ET-047 | — | Verrou consultatif par demande |
| ET-048 | — | Bail, reprise et effets idempotents |
| ET-049 | — | Invalidation des `step_runs` dépendants |
| ET-050 | — | Règles déclaratives événement → job |
| ET-051 | — | File de jobs en base, priorités, concurrence |
| ET-052 | — | Signal d'arrêt coopératif à la suspension |
| ET-355 | Outil et tableau de bord ; porte publiée | Porte bloquante activée au jalon final |
| ET-357 | Unitaires, propriétés, intégration, acceptation | Tests de bout en bout (interface métier absente) |
| ET-359 | Propriétés d'états (TST-18) | Propriétés autorisations, calculs, A5, classification |

Les ET-045 à ET-052 dépendent du pipeline et des jobs, hors périmètre fonctionnel de MS-0 ; ils sont néanmoins identifiés pour ne pas donner l'illusion d'une couverture complète.

---

## 5. Tests ajoutés

| Fichier | Objet | Nombre |
|---|---|---|
| `backend/tests/unit/test_config.py` | configuration et refus | 6 |
| `backend/tests/unit/test_app.py` | API squelette, OpenAPI, frontend | 3 |
| `backend/tests/unit/test_dependency_rules.py` | DR-01 à DR-07, 23 modules | 9 |
| `backend/tests/unit/test_generated_enums.py` | ET-017, alignement spec/DB | 5 |
| `backend/tests/unit/test_state_machines.py` | transitions, gardes, reprise | 7 |
| `backend/tests/unit/test_transition_activation.py` | les 54 TR exercées | 2 |
| `backend/tests/unit/test_platform.py` | horloge, UUIDv7 | 5 |
| `backend/tests/unit/test_openapi.py` | contrat versionné | 2 |
| `backend/tests/unit/test_ledger_core.py` | canonisation, chaîne pure | 5 |
| `backend/tests/property/test_tst18.py` | TST-18, IV-01 à IV-15 | 3 |
| `backend/tests/integration/test_ledger_db.py` | journal réel, contournements, concurrence | 6 |
| `backend/tests/integration/test_schema_db.py` | schéma, contraintes, RLS, migrations | 12 |
| `backend/tests/integration/test_tst18_db.py` | parcours nominal persistant | 3 |
| `backend/tests/unit/test_spec_trace.py` | outil de traçabilité | 4 |
| `backend/tests/acceptance/test_ms0_exit_criteria.py` | preuves de sortie MS-0 | 4 |

**Total : 77 tests.** Les tests PostgreSQL sont marqués `integration` et utilisent une base réelle.

---

## 6. Écarts par rapport à la spécification

| Réf | Écart | Cause | Traitement |
|---|---|---|---|
| E-01 | La CI n'a pas encore tourné sur GitHub | Dépôt local sans remote | Workflow prêt ; exécution locale équivalente verte. À exécuter après création du remote |
| E-02 | ET-011/ET-012 : pas de déploiement géré ni de seconde migration | Pas d'environnement cloud ni d'historique de version en MS-0 | Documenté ; à traiter au jalon d'exploitation |
| E-03 | ET-019 : purge absente | Conservation = MS-8 | Table et privilèges prêts ; procédure à écrire |
| E-04 | ET-020 : test de migration sans jeu de données | Fondations sans données métier | Test aller/retour ajouté ; jeu de données au jalon suivant |
| E-05 | ET-037/038/040/042 : politiques, effets complets, API 412 | Aucune fonction métier en MS-0 | Moteur et transaction prêts ; à compléter avec les cas d'usage |
| E-06 | ET-045 à ET-052 : file de jobs, reprise, invalidation | Pipeline et jobs hors MS-0 | Tables de base présentes, mécanismes à venir |
| E-07 | ET-355 : porte non bloquante | Aucune exigence métier testable en MS-0 | Publiée ; bloquante au jalon final (Q-003) |
| E-08 | ET-357/359 : pas d'E2E, propriétés partielles | Pas d'interface métier | Pyramide posée ; complétée aux jalons suivants |
| E-09 | `make` absent par défaut sous Windows | Environnement local | `make` installé via winget ; repli documenté `python tools/check.py check` |

Aucun test, contrainte, déclencheur ou règle de dépendance n'a été affaibli, ignoré ou supprimé pour faire passer le build.

---

## 7. Décisions prises

- **Q-001 :** FORGE est réservé au frontend et à l'infrastructure ; il n'apparaît pas dans les livrables, rapports ou messages produits par le système.
- **Q-002 :** la reprise revient à l'état d'origine, y compris Reçue et Vérification de faisabilité ; aucune reprise directe vers Finalisée.
- **Q-003 :** les portes de traçabilité s'appliquent au périmètre cumulé des jalons ; ET-355 devient bloquante au jalon final.
- **ADR-001 à ADR-009** proposés dans `docs/adr/` : monolithe modulaire, pile Python, PostgreSQL, journal, machines, traçabilité, image, tests, configuration.
- Le nom du projet n'apparaît pas dans les rapports générés ; les documents de développement (README) le conservent conformément à Q-001.

---

## 8. Questions ouvertes pour le Product Owner

1. **Q-002** — valider la cible de reprise depuis Reçue et Vérification de faisabilité.
2. **Q-003** — valider le périmètre cumulé des portes de traçabilité et l'activation finale d'ET-355.
3. Valider les ADR-001 à ADR-009 (aucune dépendance nouvelle hors outillage de test).

---

## 9. Risques constatés

| Risque | Impact | Mitigation |
|---|---|---|
| CI non exécutée sur GitHub | Preuve distante manquante | Workflow identique à la commande locale ; lancer dès le remote créé |
| Docker requis pour les tests d'intégration | `make check` échoue sans moteur Docker | Message explicite ; `make db-up` ; CI fournit un service PostgreSQL |
| `make` absent sous Windows | Commande du brief indisponible | `make` installé ; repli `python tools/check.py check` documenté |
| 482 exigences RF/RB/RT sans test à MS-0 | Tableau de bord volumineux | Affichage « hors périmètre » et porte ET-355 au jalon final |
| ET-045 à ET-052 non implémentées | Fondations de jobs incomplètes | Identifiées ; à planifier avant les jalons de production |
| Downgrade de migration destructif | Perte de données si utilisé en production | Réservé au développement ; politique étendre/contracter à appliquer en production |

---

## 10. Définition de « terminé » (AGENTS.md §8)

- [x] CA visés verts et étiquetés — MS-0 n'a pas de CA ; les critères de sortie sont couverts.
- [x] Identifiants cités dans les tests et le rapport.
- [x] `make check` vert.
- [x] Aucun test, contrainte ou déclencheur affaibli.
- [x] Aucune logique métier hors domaine pur.
- [x] Décisions et questions consignées.
- [x] `PROGRESS.md` à jour.
- [x] Rapport et guide de démonstration écrits.
- [ ] Revue du Product Owner (PO-01, PO-02, PO-04, PO-10) — en attente.

---

## 11. Gabarit de rapport (AGENTS.md §7)

```text
Tâche / jalon : MS-0 — Fondations
Identifiants couverts : ET-001 à ET-044 (35 complets, 20 partiels), ET-353 à ET-356, ET-358, ET-372 ; IV-01 à IV-15 ; TR-R-01 à TR-R-27, TR-C-01 à TR-C-05, TR-A-01 à TR-A-04, TR-D-01 à TR-D-04, TR-V-01 à TR-V-03, TR-E-01 à TR-E-11
Tests ajoutés ou modifiés : 77 tests (unitaires, propriétés, intégration PostgreSQL, acceptation)
Résultat de make check : vert — 77 tests, 54/54 transitions couvertes, 0 orphelin, 0 identifiant inconnu
Écarts par rapport à la spécification : E-01 à E-09 (voir section 6)
Décisions prises : Q-001, Q-002, Q-003 ; ADR-001 à ADR-009
Questions ouvertes : Q-002, Q-003
Risques constatés : CI distante non exécutée ; Docker requis ; ET-045 à ET-052 à planifier
```