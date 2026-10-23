# Rapport de fin de jalon — MS-2 Demande et faisabilité

**Date :** 2026-10-23  
**Jalon :** MS-2 — Demande et faisabilité  
**Statut :** terminé, soumis à la revue du Product Owner  
**Périmètre :** passerelle LLM en rejeu, compréhension de la demande, clarification, faisabilité, messages d'état et squelette de bout en bout.

---

## 1. Résultat en une page

- `make check` est **vert** : **160 tests**, mypy strict, règles de dépendance, contrôle décimal, génération, traçabilité.
- **35/35 CA exigibles** sont verts : les 31 CA de MS-2 et les 4 CA de MS-1 restent verts.
- **TST-01** (réception, clarification), **TST-02** (faisabilité) et **TST-14** (suivi) sont verts.
- Le parcours de bout en bout fonctionne : **demande → clarification → faisabilité → statut**, sans fournisseur LLM externe.
- Aucun message d'état n'annonce un état non atteint (CA-139, CA-140 ; EVL-H partielle).
- **E-01 est levée** : le remote GitHub, la branche master et les tags ms-0/ms-1 sont synchronisés, la CI est active.

---

## 2. Critères de sortie du brief

| Critère | Résultat | Preuve |
|---|---|---|
| TST-01 vert | **Vert** | 13 tests CA-001 à CA-010, CA-142, CA-189, CA-190 dans `backend/tests/acceptance/test_request_flow_ca.py` |
| TST-02 vert | **Vert** | CA-011 à CA-020 |
| Suivi avec statuts séparés | **Vert** | CA-135 à CA-140, `StatusStrip` Next.js, `request.status` |
| Squelette de bout en bout | **Vert** | `make demo-requests` et `test_ca135` à `test_ca143` |
| Aucune annonce d'état non atteint | **Vert** | CA-139, CA-140 ; gabarits français, filtre MG-02 |

---

## 3. Ce qui a été construit

### 3.1 Passerelle LLM

- `llm_gateway.run_task` est l'unique porte d'entrée (ET-247).
- Prompts versionnés et empreintés ; consigne anti-injection (ET-258, ET-259).
- Adaptateur de **rejeu strict** : aucune sortie réseau, aucun fournisseur payant en test ou CI.
- Sortie validée par Pydantic (ET-250) ; schémas plats et stricts (ET-251).
- Refus, troncature et sortie invalide sont des **échecs typés** (ET-252).
- Chaque appel est journalisé dans `llm_calls` : tâche, prompt, modèle, fournisseur, empreintes, jetons, issue (ET-256).
- Aucun outil, aucune fonction d'écriture exposée au modèle (ET-232, ET-260).

### 3.2 Demande et clarification

- Enregistrement du texte d'origine, de l'auteur, de la date et de l'état Reçue (CA-001).
- LT-01 extrait le type, le format, les paramètres et les ambiguïtés ; les citations sont vérifiées littéralement.
- Les paramètres déterminables ne produisent pas de question (CA-003) ; les ambiguïtés non significatives non plus (CA-005).
- Une ambiguïté bloquante passe la demande à **En clarification** et produit une question ciblée avec sa raison (CA-006).
- Les questions bloquantes sont hiérarchisées et limitées à un lot court (CA-007).
- Une réponse est enregistrée comme information fournie par l'utilisateur, **QI-02 candidate** (CA-190).
- Une demande multiple est détectée, aucune scission n'est faite sans confirmation ; la confirmation crée deux demandes indépendantes (CA-010, CA-189).
- Une instruction ponctuelle ne modifie aucune règle (CA-009).

### 3.3 Faisabilité

- Diagnostic déterministe en sept dimensions : modèle, règles, informations, autorisations, exigences, contradictions, préconditions (CA-012).
- Absence de modèle ou de règles : blocage MB-01, sans improvisation (CA-011).
- Condition indispensable absente : blocage avec motif communicable (CA-013).
- Droits incertains : suspension de l'opération (CA-017).
- Les versions de modèle, règles, registre et catalogue sont **épinglées** à la faisabilité (CA-016).
- Une modification ultérieure des règles ne change pas les épinglages (CA-018).
- Le mode diagnostic seul ne produit ni épinglage ni livrable (CA-019).
- Les motifs sont adaptés aux droits : général pour un utilisateur sans droit, détaillé pour la personne responsable (CA-020, CA-137, CA-138, CA-144).

### 3.4 Suivi et messages

- `StatusSnapshot` expose : étapes terminées, étape courante, motifs, éléments attendus, prochaine action, axes **R, C, A, D, V séparés**, version provisoire (CA-135).
- Les éléments terminés, suspendus, bloqués, en attente de décision et finalisés sont distingués (CA-136).
- Les messages d'état sont rendus par gabarits français versionnés ; les états fonctionnels ne sont pas confondus avec les étapes internes (ET-233, ET-244, CA-140).
- Le filtre MG-02 refuse les annonces d'états interdits dans un texte libre ; un message bloqué est remplacé par un gabarit neutre (ET-236).
- L'historique des échanges est consultable (CA-143).

### 3.5 Interface Next.js

- `frontend/` : App Router, TypeScript strict (ET-293).
- En-tête **FORGE** dans le layout (Q-001).
- `StatusStrip` présente séparément R, C, A, D, V et le badge **provisoire** (ET-295, ET-296).
- Aucune règle métier dans les composants (ET-294).
- Le squelette n'est pas encore branché à l'API dans `make check` ; il est prêt pour MS-3.

---

## 4. Exigences techniques du brief (39)

### 4.1 Entièrement couvertes (24)

`ET-232`, `ET-233`, `ET-234`, `ET-235`, `ET-237`, `ET-239`, `ET-240`, `ET-241`, `ET-242`, `ET-244`, `ET-245`, `ET-247`, `ET-250`, `ET-251`, `ET-252`, `ET-253`, `ET-256`, `ET-258`, `ET-260`, `ET-293`, `ET-294`, `ET-295`, `ET-296`, `ET-298`.

### 4.2 Partielles (15)

| ET | Ce qui existe | Ce qui manque |
|---|---|---|
| ET-231 | Schéma `CommandProposal` avec liste blanche | Routeur LT-10 exécutant les commandes |
| ET-236 | Filtre MG-02 et gabarits | Application systématique aux questions LT-02 |
| ET-238 | Détection de demandes multiples | Détection de doublons sans fusion |
| ET-243 | Motifs publics sans jargon | Gabarits MB complets par code |
| ET-246 | Journal des messages | Détection et consignation des injections |
| ET-248 | Adaptateur de rejeu + fournisseur indisponible | Adaptateurs Anthropic/OpenAI réellement utilisables |
| ET-249 | Modèle et fournisseur enregistrés | Correspondance rôle → modèle configurable |
| ET-254 | Schémas Pydantic | Comparaison d'énumérations insensible à la casse |
| ET-255 | Paramètres journalisés | Température/paramètres par tâche |
| ET-257 | Aucun accès base/réseau au modèle | Autorisation AU-2 et minimisation avant appel |
| ET-259 | Consigne anti-injection présente | Assemblage délimité des données dans le prompt |
| ET-261 | — | Cache du préfixe et taux de réussite |
| ET-262 | — | Budget de jetons/appels par tâche et demande |
| ET-297 | — | Confirmation d'annulation en deux étapes |
| ET-299 | — | Reprise sur conflit 412 côté interface |

Ces écarts sont hors des critères de sortie MS-2 ou relèvent des jalons suivants ; ils sont consignés pour ne pas donner l'illusion d'une couverture complète.

---

## 5. Tests ajoutés

| Fichier | Objet | Nombre |
|---|---|---|
| `backend/tests/acceptance/test_request_flow_ca.py` | 31 CA MS-2 et parcours TST-01/TST-02/TST-14 | 31 |
| `backend/tests/unit/test_llm_gateway.py` | rejeu, validation, échecs typés, journal, prompts | 5 |
| `backend/tests/unit/test_frontend_contract.py` | Next.js, en-tête FORGE, StatusStrip, badge provisoire | 5 |

**Total du jalon : 160 tests.** Le tableau de bord MS-2 affiche 35/35 CA exigibles verts.

---

## 6. Écarts et limites

| Réf | Écart | Cause | Traitement |
|---|---|---|---|
| E-20 | Adaptateurs fournisseurs réels non branchés | La CI doit rester en rejeu ; aucun secret de fournisseur | Interface d'adaptateur prête ; tests en rejeu uniquement |
| E-21 | Routeur LT-10 non exécuté | Périmètre MS-2 centré sur la demande et la faisabilité | Schéma et liste blanche posés ; exécution en MS-3 |
| E-22 | Interface Next.js non construite par `make check` | Dépendances Node non installées dans la chaîne Python | Squelette et test statique ; build à intégrer avec le pipeline frontend |
| E-23 | Filtre MG-02 non appliqué aux questions LT-02 | Les questions sont déjà contrôlées par le schéma | À compléter avant le pilote |
| E-24 | Budgets, cache et minimisation AU-2 partiels | Relèvent de l'exploitation et de la sécurité | Identifiés dans les ET partiels |
| E-25 | EVL-H seulement partielle | Aucune évaluation LLM rejouée en MS-2 | Les tests CA-139/CA-140 couvrent l'absence d'annonce d'état ; suite EVL en MS-8 |

Aucun test, contrainte, déclencheur ou règle de dépendance n'a été affaibli, ignoré ou supprimé.

---

## 7. Décisions prises

- **Rejeu strict** : les tests et la CI n'appellent jamais un fournisseur payant ; `ReplayAdapter` est l'adaptateur par défaut.
- **Validation locale** : toute sortie LLM passe par Pydantic ; un refus, une troncature ou une sortie invalide est un échec typé.
- **Aucun outil** : les schémas et l'adaptateur n'exposent aucune fonction d'écriture.
- **E-01 levée** : le remote GitHub et la CI sont actifs (information PO).
- Q-001, Q-002, Q-003 restent inchangées.

---

## 8. Questions ouvertes

Aucune question bloquante. Les points E-20 à E-25 sont des écarts de périmètre documentés.

---

## 9. Risques constatés

| Risque | Impact | Mitigation |
|---|---|---|
| Aucun fournisseur réel testé | Comportement de production non prouvé | Adaptateurs et contrats prêts ; évaluations en MS-8 |
| Interface Next.js non construite en CI | Régression frontend non détectée | Tests statiques ; pipeline frontend à ajouter |
| Questions LT-02 non filtrées | Petit risque de formulation | Gabarits et schéma ; filtre à brancher |
| Faisabilité déterministe simplifiée | Certains cas réels non couverts | Sept dimensions et motifs MB posés ; enrichment en MS-3/MS-4 |
| `StatusStrip` non connecté à l'API | Parcours visuel incomplet | Squelette prêt pour MS-3 |

---

## 10. Définition de « terminé »

- [x] CA-001 à CA-020, CA-135 à CA-144, CA-142, CA-189, CA-190 verts et étiquetés.
- [x] Identifiants cités dans les tests et le rapport.
- [x] `make check` vert (160 tests).
- [x] Aucun test, contrainte ou déclencheur affaibli.
- [x] Aucune logique métier dans l'interface ; elle appelle le service.
- [x] Décisions et écarts consignés.
- [x] `PROGRESS.md` à jour.
- [x] Rapport et guide de démonstration écrits.
- [ ] Revue du Product Owner — en attente.

---

## 11. Gabarit de rapport (AGENTS.md §7)

```text
Tâche / jalon : MS-2 — Demande et faisabilité
Identifiants couverts : CA-001 à CA-020, CA-135 à CA-144, CA-142, CA-189, CA-190 ; TST-01, TST-02, TST-14 ; ET-231 à ET-262, ET-293 à ET-299
Tests ajoutés ou modifiés : 41 tests (31 CA, 5 passerelle, 5 interface), 160 au total
Résultat de make check : vert — 160 tests, 35/35 CA exigibles verts, 54/54 transitions, 0 orphelin
Écarts par rapport à la spécification : E-20 à E-25 ; ET-231/238/243/246/248/249/253 à 255/257/259/261/262/297/299 partiels
Décisions prises : rejeu strict, validation Pydantic, aucun outil LLM ; E-01 levée
Questions ouvertes : aucune question bloquante
Risques constatés : fournisseur réel non testé, interface non construite en CI, filtrage LT-02 à compléter
```