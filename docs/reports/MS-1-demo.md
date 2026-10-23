# Guide de démonstration — MS-1 Gouvernance

**Pour qui :** Product Owner, sans lecture de code.  
**Durée :** 30 à 45 minutes.  
**But :** vérifier les preuves observables de MS-1 et remplir la fiche de revue sans juger le code.

Ce guide suit `docs/CHECKLIST-PO.md`. MS-1 couvre PO-01, PO-02, PO-03, PO-04 et PO-10.

---

## 0. Préparer une copie propre (5 min)

Dans un terminal, à la racine du projet :

```powershell
git status
git log --oneline -1
```

Prérequis : Docker Desktop démarré, Python 3.13, `make` (ou repli `py -3.13 tools/check.py check`), PostgreSQL local via `make db-up`.

---

## 1. Lancer la chaîne complète (5 à 8 min)

```bash
make check
```

**Attendu (fin de sortie) :**

```text
119 passed in ...
MS-1 : 4/4 CA exigibles verts, 0 sans test, 191 hors perimetre, 54/54 transitions couvertes, 119 tests, 0 orphelins.
```

Les contrôles incluent désormais :

- `ET-062 : aucun float dans transform/core` ;
- les quatre JSON Schemas v1 ;
- les déclencheurs et contraintes de gouvernance ;
- les quatre CA et TST-15.

---

## 2. Vérifier les critères du jalon (5 min) — PO-02

```bash
make test-acceptance
```

**Attendu :** 9 tests verts, dont CA-150, CA-151, CA-152 et CA-153.

Pour voir seulement le scénario de l'exemple contradictoire :

```powershell
.\.venv\Scripts\python.exe -m pytest -q backend/tests/acceptance/test_governance_ca.py -k ca153
```

**Attendu :** 1 test vert. Le test vérifie que la règle formelle prévaut sur l'exemple et que l'incohérence est signalée comme observation.

---

## 3. Démonstration de gouvernance (5 min) — PO-03

```bash
make demo-governance
```

**Attendu :**

```text
1. Creation et approbation du modele et du catalogue de controles
2. Creation du lot de regles, validation 9 etapes, approbation
   - etapes : 9, resultat : OK
   - version 1 approuvee, date d'effet ...
3. Creation et approbation du registre des sources
   - niveaux : access, diffusion, integration, use
4. Epinglage de la demande sur le lot approuve
   - demandes epinglees : 1
5. Tentative de modification par un utilisateur ordinaire
   - refusee : Seule la personne responsable peut modifier un artefact de gouvernance.
6. Fin : transaction annulee, aucune donnee de demonstration conservee.
```

Cette démonstration prouve :

- le pipeline de **9 étapes** ;
- l'approbation avec **décision DH-07** et date d'effet ;
- les **quatre niveaux** d'autorisation du registre ;
- l'**épinglage** d'une demande ;
- le **refus** d'un utilisateur ordinaire ;
- l'absence de données conservées après la démonstration.

---

## 4. Ouvrir la console SCR-15 / SCR-17 (5 min) — PO-01, PO-04

1. Préparer une base de démonstration locale :

```bash
make seed-governance
```

Elle affiche l'espace de travail et les identifiants de démonstration. Les artefacts fictifs sont conservés dans la base locale uniquement.

2. Lancer la console :

```powershell
$env:AGENT_DATABASE_URL="postgresql+psycopg://agent:agent@localhost:55432/agent"
$env:AGENT_WORKSPACE_ID="11111111-1111-7111-8111-111111111111"
.\.venv\Scripts\python.exe -m uvicorn agent.interfaces.rest.app:app --port 8000
```

3. Ouvrir `http://127.0.0.1:8000/governance`.

**Bon :**

- l'en-tête affiche **FORGE** et « Framework for Orchestrated Report Generation and Evaluation » ;
- la table des artefacts montre les versions et leurs statuts (approved / retired) ;
- la section « Registre des sources » affiche **Accès, Usage, Intégration, Diffusion** ;
- le formulaire permet de créer un brouillon, de valider et d'approuver.

4. Ouvrir `http://127.0.0.1:8000/users` : la page **SCR-17** affiche les utilisateurs, leurs rôles et le nombre de personnes responsables.

5. **Tentative de violation (PO-04) :** dans la console, choisissez « Utilisateur ordinaire » comme acteur, puis créez un brouillon de registre. Attendu : un message de refus, aucune version créée. Le rôle est lu en base ; il n'est pas décidé par l'interface.

6. Arrêter le serveur avec `Ctrl+C`.

---

## 5. Vérifier les schémas et le calcul décimal (3 min)

1. Ouvrir le dossier `backend/src/agent/governance/schemas/v1/` : quatre schémas JSON versionnés.
2. `make check` exécute le contrôle anti-`float` : le résultat doit être `ET-062 : aucun float dans transform/core`.
3. Ouvrir `backend/src/agent/transform/core/cel.py` : les fonctions autorisées sont limitées à la liste FM-03 ; une fonction inconnue est refusée à la compilation.
4. Le test `test_decimal_formula_is_reproducible` vérifie qu'une même formule et les mêmes entrées donnent la même valeur et la même représentation.

---

## 6. Vérifier la non-rétroactivité (3 min)

Les tests CA-150 et CA-152 montrent qu'après l'approbation d'une nouvelle version :

- l'ancienne version passe à `retired` ;
- l'épinglage de la demande reste sur l'ancienne version ;
- le contenu de l'ancienne version est inchangé.

Pour observer directement la démonstration, `make demo-governance` affiche l'épinglage ; les tests PostgreSQL vérifient l'immuabilité et le refus d'une date d'effet passée.

---

## 7. Tableau de bord (3 min) — PO-01

Ouvrir `docs/reports/spec-trace.html`.

**Attendu :**

- jalon MS-1 ;
- **4 / 4** CA exigibles verts ;
- 0 CA rouge, 0 sans test, 0 ignoré ;
- 191 CA hors périmètre (jalons suivants) ;
- 54/54 transitions couvertes ;
- 0 test orphelin, 0 identifiant inconnu.

La section « Criteres du jalon » liste CA-150 à CA-153 en vert.

---

## 8. Remplir la fiche de revue

| Vérification | MS-1 | Où / quoi regarder | Résultat attendu | Votre verdict |
|---|---|---|---|---|
| PO-01 Tableau de bord | ✔ | `docs/reports/spec-trace.html` | 4/4 CA, 0 rouge, 0 sans test, 0 orphelin | |
| PO-02 CA du jalon verts | ✔ | `make test-acceptance` | CA-150 à CA-153 verts | |
| PO-03 Parcours du jalon | ✔ | `make demo-governance` et console | Lot approuvé, registre, épinglage | |
| PO-04 Violation refusée | ✔ | Console avec utilisateur ordinaire | Refus explicite, aucune version créée | |
| PO-05 à PO-09 | — | — | Non applicables à MS-1 | |
| PO-10 Rapport traité | ✔ | `docs/reports/MS-1-rapport.md` | Écarts E-01, E-10 à E-14 listés | |

**Verdict attendu si tout est bon :** « Validé ».  
**Si un point est rouge :** citez l'étape et le message exacts ; ne validez pas par défaut.

---

## 9. Ce que vous ne verrez pas encore

- Aucune authentification OIDC : la console est une console de **démonstration** ; le rôle est lu en base mais l'acteur est choisi dans l'interface. Ne l'exposez pas sur un réseau non maîtrisé.
- Pas de production de livrable : MS-1 gouverne les règles, pas la génération.
- Pas de cache d'artefacts ni de tables de conversion branchées dans les lots (ET-060/ET-063 partiels).
- Pas d'application effective des corrections mécaniques aux atomes (ET-064 partiel).

---

## 10. Nettoyage

```bash
make db-down
```

Cette commande supprime la base locale de démonstration et ses artefacts fictifs.

---

## Résumé des commandes

```bash
make check
make test-acceptance
make demo-governance
make seed-governance
make db-up / db-down
```
