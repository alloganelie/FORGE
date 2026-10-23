# Rapport de fin de jalon — MS-1 Gouvernance

**Date :** 2026-10-23  
**Jalon :** MS-1 — Gouvernance  
**Statut :** terminé, soumis à la revue du Product Owner  
**Périmètre :** artefacts de gouvernance versionnés, schémas JSON, pipeline de validation en 9 étapes, épinglage par demande, non-rétroactivité, évaluateur CEL décimal, console minimale SCR-15/SCR-17. Aucune fonction métier de production de livrable.

---

## 1. Résultat en une page

- `make check` est **vert** : 119 tests, mypy strict, règles de dépendance, contrôle anti-`float`, génération, traçabilité.
- Les quatre critères du jalon sont **verts** : CA-150, CA-151, CA-152, CA-153.
- **TST-15** est vert : 5 tests de gouvernance, dont un parcours complet de bout en bout.
- Le tableau de bord affiche **4/4 CA exigibles verts**, 0 sans test, 191 CA hors périmètre, 0 test orphelin.
- Un lot de règles d'exemple est créé, validé en 9 étapes, approuvé avec décision DH-07 et date d'effet, puis épinglé sur une demande. Les productions antérieures restent liées à l'ancienne version.
- La console **SCR-15** affiche FORGE dans son en-tête et présente le registre des sources avec ses quatre niveaux d'autorisation. La page **SCR-17** présente les utilisateurs et rôles.

---

## 2. Critères de sortie du brief

| Critère | Résultat | Preuve |
|---|---|---|
| TST-15 (gouvernance) vert | **Vert** | `backend/tests/acceptance/test_governance_ca.py` (5 tests, dont 4 CA et 1 parcours de bout en bout) |
| Lot de règles d'exemple approuvé de bout en bout | **Vert** | `test_tst15_rule_pack_end_to_end` et `make demo-governance` |
| Épinglage et non-rétroactivité testés | **Vert** | CA-150, CA-152, `test_governance_db.py` et `test_resume_db.py` (MS-0) |
| CA-150, CA-151, CA-152, CA-153 verts | **4/4** | tableau de bord `docs/reports/spec-trace.html` et tests étiquetés |

---

## 3. Ce qui a été construit

### 3.1 Données de gouvernance

Migration `0002_governance` :

- `governance_artifact_versions` : type, clé, version, contenu JSONB, empreinte SHA-256 canonique, schéma, statut, date d'effet, décision d'approbation, auteur et motif.
- `request_pins` : épinglage par demande, en ajout seul.
- `change_proposals` : propositions de changement (RF-266), sans écriture directe dans une version approuvée.
- `governance_observations` : observations d'exemples contradictoires.
- `role_assignments` : rôles datés, avec index unique d'une seule personne responsable active par espace.

Déclencheurs :

- une version **approuvée est immuable** (contenu, empreinte, date d'effet, décision) ; seule la transition approved → retired est permise (GV-01, ET-053) ;
- une approbation exige une décision et une date d'effet, et refuse une date rétroactive (GV-02, RB-104, ET-058) ;
- les épinglages sont en ajout seul (ET-059) ;
- la RLS est activée et forcée sur les tables de gouvernance.

### 3.2 Schémas JSON versionnés

Quatre schémas draft 2020-12 dans `backend/src/agent/governance/schemas/v1/` :

- `rule_pack.schema.json`
- `template.schema.json`
- `source_registry.schema.json`
- `control_catalog.schema.json`

Ils sont chargés par `JsonSchemaStore` et appliqués à l'ouverture et à l'approbation. Une erreur est rejetée avec son chemin JSON (ET-054).

### 3.3 Pipeline de validation en 9 étapes

`governance/core/validation.py` expose neuf étapes composables :

1. Schéma JSON.
2. Références (modèle, contrôle, transformation, règle).
3. Cycles du graphe `depends_on` des éléments (ET-121).
4. Formules CEL : compilation, fonctions enregistrées, unités déclarées.
5. Cohérence : contrôles obligatoires, formats, transformations, corrections autorisées.
6. Interdits : valeur par défaut qui comblerait une lacune, ordre de priorité implicite.
7. Tests de règles *étant donné / attendu* fournis avec le lot.
8. Régression sur dossiers de référence (avertissement bloquant).
9. Analyse d'impact (demandes épinglées, modèles et contrôles dépendants).

Chaque étape produit un rapport détaillé ; un échec rend le rapport global non conforme et bloque l'approbation.

### 3.4 Évaluateur CEL et arithmétique décimale

- `transform/core/cel.py` : sous-ensemble CEL encapsulé, sans `eval`, sans exécution dynamique, avec profondeur et taille de liste bornées.
- Fonctions enregistrées FM-03 : `dec`, `add`, `sub`, `mul`, `div`, `sum`, `avg`, `rnd`, `to_unit`, `pct`, `min`, `max`, `count`.
- `decimal.Decimal` et contexte explicite ; `float` refusé à l'entrée et interdit par le contrôle `tools/check_decimal.py` (ET-062).
- Tables de conversion d'unités déclaratives dans `decimal_math.UnitTable` ; aucune conversion implicite (ET-063, partiel).

### 3.5 Épinglage et non-rétroactivité

- `GovernanceService.pin_request` n'épingle que des versions approuvées.
- Une nouvelle approbation retire l'ancienne version approuvée de la même clé, sans modifier les épinglages existants.
- CA-150 et CA-152 vérifient qu'une demande reste liée à l'ancienne version après une nouvelle approbation.
- L'analyse d'impact liste les demandes épinglées et, pour un modèle ou un catalogue remplacé, les modèles dépendants.

### 3.6 Console SCR-15 / SCR-17

- `GET /governance` : en-tête **FORGE** (Q-001), création de brouillon, liste des versions, validation, approbation, registre des sources avec les quatre niveaux AU-1 à AU-4.
- `GET /users` : utilisateurs, rôles, compteur de personnes responsables.
- API JSON : artefacts, validation, approbation, épinglage, autorisations d'une source.
- Le rôle de l'acteur est lu en base ; l'acteur est choisi dans la console pour la démonstration. L'authentification OIDC n'est pas encore branchée (écart E-11).

---

## 4. Exigences techniques du brief (15)

### 4.1 Entièrement couvertes (9)

`ET-053`, `ET-054`, `ET-055`, `ET-056`, `ET-058`, `ET-061`, `ET-062`, `ET-065`, `ET-121`.

### 4.2 Partielles (6)

| ET | Ce qui existe | Ce qui manque |
|---|---|---|
| ET-057 | Analyse d'impact : demandes épinglées, modèles et contrôles dépendants | Propagation complète des dépendances et des sorties de modèles |
| ET-059 | Épinglage explicite par le service, tests de non-rétroactivité | Branchement automatique à l'étape de faisabilité (MS-2) |
| ET-060 | Chargement par identifiant de version et empreinte stockée | Cache d'artefacts par empreinte et invalidation |
| ET-063 | `UnitTable` déclarative et test de conversion absente | Branchement des tables de conversion dans le schéma de lot |
| ET-064 | Registre de fonctions nommées et contrôle d'autorisation dans le lot | Application effective aux atomes lors d'une correction |
| ET-066 | Console de validation et d'approbation, API d'impact | Affichage détaillé de l'impact dans la console |

Aucune de ces partialités ne bloque les quatre CA ni les critères de sortie. Elles sont listées pour la revue et pour les jalons suivants.

---

## 5. Tests ajoutés

| Fichier | Objet | Nombre |
|---|---|---|
| `backend/tests/acceptance/test_governance_ca.py` | CA-150 à CA-153 et parcours TST-15 | 5 |
| `backend/tests/integration/test_governance_console.py` | SCR-15/SCR-17, FORGE, acteur requis | 2 |
| `backend/tests/integration/test_governance_db.py` | immuabilité, non-rétroactivité, épinglage, responsable unique | 5 |
| `backend/tests/unit/test_cel.py` | CEL, décimal, unités, reproductibilité | 8 |
| `backend/tests/unit/test_decimal_guard.py` | absence de `float` | 2 |
| `backend/tests/unit/test_governance_rules.py` | rôles, dates, épinglage, impact, autofix | 7 |
| `backend/tests/unit/test_governance_validation.py` | schéma, cycles, interdits, tests de règles, impact, autofix | 8 |

**Total du jalon : 119 tests.** Le tableau de bord MS-1 affiche 4/4 CA exigibles verts.

---

## 6. Écarts et limites

| Réf | Écart | Cause | Traitement |
|---|---|---|---|
| E-01 | CI non déclenchée sur GitHub | Aucun remote Git configuré dans l'environnement | Workflow identique à `make check`, exécution locale verte ; à déclencher dès qu'un remote existe |
| E-10 | ET-057/059/060/063/064/066 partiels | Périmètre MS-1 centré sur les CA ; certaines intégrations appartiennent à MS-2/MS-5 | Documenté ci-dessus, sans affaiblir les tests |
| E-11 | Console sans OIDC | L'authentification relève d'un jalon ultérieur ; le rôle est néanmoins lu en base | Console marquée « démonstration » ; aucune donnée réelle ; API à protéger avant production |
| E-12 | Sous-ensemble CEL, pas le moteur CEL complet | Intégration d'un moteur complet non nécessaire au MVP ; port remplaçable | ADR-010 ; formules hors sous-ensemble refusées, jamais approximées |
| E-13 | Impact non affiché dans la console | API disponible, écran minimal | Affichage prévu avec le reste de SCR-15 |
| E-14 | Pas de cache d'artefacts par empreinte | ET-060 non bloquant pour les CA | À ajouter avec le chargement de production |

Aucun test, contrainte, déclencheur ou règle de dépendance n'a été affaibli, ignoré ou supprimé.

---

## 7. Décisions prises

- **ADR-010** : `jsonschema` pour les schémas versionnés ; évaluateur CEL restreint et encapsulé ; arithmétique décimale stricte.
- **Q-001** : FORGE apparaît dans l'en-tête de la console, jamais dans les livrables ou messages.
- **Q-002/Q-003** : décisions MS-0 rappelées, inchangées.
- Le contenu d'exemple des lots est un contenu de **démonstration**, non une décision métier : il sera remplacé par les lots fournis par la personne responsable.

---

## 8. Questions ouvertes

Aucune question bloquante. Les points E-10 à E-14 sont des écarts de périmètre documentés, à arbitrer lors de la revue.

---

## 9. Risques constatés

| Risque | Impact | Mitigation |
|---|---|---|
| Console sans authentification | Un acteur peut être choisi dans l'interface de démonstration | Rôle lu en base, interface marquée démonstration, OIDC avant production |
| CI distante non exécutée | Preuve GitHub manquante | Workflow prêt ; exécution locale identique |
| Sous-ensemble CEL | Formules complexes refusées | Refus explicite, jamais d'approximation ; port remplaçable |
| ET-057/060 partiels | Impact/cache incomplets | À compléter avant le pilote |
| Données de démonstration locales | Le script `seed-governance` conserve des artefacts fictifs | Aucune donnée réelle ; réinitialisation par `make db-down` |

---

## 10. Définition de « terminé »

- [x] CA-150, CA-151, CA-152, CA-153 verts et étiquetés.
- [x] Identifiants cités dans les tests et le rapport.
- [x] `make check` vert (119 tests).
- [x] Aucun test, contrainte ou déclencheur affaibli.
- [x] Aucune logique métier dans l'interface : elle appelle le service.
- [x] Décisions et écarts consignés.
- [x] `PROGRESS.md` à jour.
- [x] Rapport et guide de démonstration écrits.
- [ ] Revue du Product Owner — en attente.

---

## 11. Gabarit de rapport (AGENTS.md §7)

```text
Tâche / jalon : MS-1 — Gouvernance
Identifiants couverts : ET-053 à ET-058, ET-061 à ET-066, ET-121 ; CA-150 à CA-153 ; TST-15 ; RF-250 à RF-259 ; RB-097, RB-104, RB-105
Tests ajoutés ou modifiés : 37 tests de gouvernance, 119 tests au total
Résultat de make check : vert — 119 tests, MS-1 4/4 CA exigibles verts, 54/54 transitions, 0 orphelin
Écarts par rapport à la spécification : E-01, E-10 à E-14
Décisions prises : ADR-010 ; Q-001/Q-002/Q-003 rappelées
Questions ouvertes : aucune question bloquante
Risques constatés : console sans OIDC, CI distante non exécutée, ET-057/060 partiels
```
