# Kit pour l'agent de codage — mode d'emploi (pour le Product Owner)

Ce kit permet de confier la construction du produit à un agent de codage (DeepSeek Harness, Claude Code ou autre) **jalon par jalon**, avec un seul prompt par jalon, **sans que l'agent relise les 585 Ko de spécifications à chaque fois**.

## 1. Ce que contient le kit

```text
AGENTS.md                      # consignes permanentes (≈ 5 Ko) — la seule chose lue systématiquement
CLAUDE.md                      # renvoie à AGENTS.md (pour Claude Code)
LISEZ-MOI.md                   # ce fichier (pour vous, pas pour l'agent)
Makefile                       # raccourcis de lecture (make spec ID=CA-099)
docs/
├── spec/
│   ├── _sources/              # les deux spécifications complètes (archives de référence)
│   ├── INDEX.md               # où se trouve chaque section et chaque famille d'identifiants (numéros de lignes)
│   └── ids.json               # annuaire des 2 068 identifiants
├── CHECKLIST-PO.md            # votre fiche de revue d'un jalon (10 vérifications, pas à pas)
├── milestones/MS-0.md … MS-9.md   # un BRIEF par jalon : exactement ce qu'il faut lire et faire (8 à 26 Ko)
├── prompts/
│   ├── PROMPT-MS-0.md … MS-9.md   # le prompt à coller pour chaque jalon
│   ├── PROMPT-REPRISE.md          # pour reprendre après une interruption
│   └── PROMPT-REVUE.md            # pour faire relire un jalon par un agent indépendant
└── reports/                   # PROGRESS.md (état), QUESTIONS.md (vos décisions), rapport + guide de démo de chaque jalon
tools/
├── spec.py                    # lecteur par tranches : show / section / search / refs / toc
└── gen_briefs.py              # régénère les briefs et les prompts si les spécifications changent
```

## 2. Pourquoi l'agent ne relit pas tout

| Ce que l'agent lit | Taille | Jetons (ordre de grandeur) |
|---|---|---|
| Les deux spécifications en entier | 585 Ko | ≈ 160 000 |
| **Démarrage d'une session avec ce kit** : AGENTS.md + PROGRESS.md + un brief | 15 à 32 Ko | **≈ 4 000 à 9 000** |
| Une précision ponctuelle : `python tools/spec.py show CA-099` | quelques lignes | quelques dizaines |

Le brief d'un jalon contient déjà, en texte complet, les exigences techniques et les critères d'acceptation du jalon. L'agent n'ouvre le reste que **sur demande**, par identifiant ou par section.
Si une session est interrompue, `PROGRESS.md` permet de reprendre sans tout relire.

## 3. Mise en route (une fois)

1. Créez un dossier de projet vide et **dézippez le kit à sa racine**. Initialisez `git` et faites un premier commit.
2. Vérifiez que **Python 3.9 ou plus** est disponible (`python3 --version`) : l'outil de lecture n'a besoin de rien d'autre.
3. Vérifiez que votre agent peut **exécuter des commandes** dans le dossier (`python3 tools/spec.py show CA-099` doit afficher un critère).
4. Vérifiez quel fichier de consignes votre agent lit automatiquement. *À vérifier dans la documentation de l'outil* : le fichier `AGENTS.md` est une convention répandue, mais je n'ai pas pu confirmer que DeepSeek Harness le lit. Cela n'a pas d'importance ici : **chaque prompt de jalon demande explicitement de lire `AGENTS.md` en premier**.
5. Configurez les clés d'accès aux modèles **en variables d'environnement**, jamais dans le dépôt.

## 4. Boucle de travail recommandée (un jalon à la fois)

```text
1. Collez docs/prompts/PROMPT-MS-0.md          → l'agent travaille seul jusqu'à la fin du jalon
2. L'agent rend : code + tests verts + docs/reports/MS-0-rapport.md + MS-0-demo.md (guide pas à pas) + questions éventuelles
3. Vous lancez la relecture indépendante : docs/prompts/PROMPT-REVUE.md (idéalement avec un autre modèle)
4. Vous appliquez la checklist du Product Owner : docs/CHECKLIST-PO.md
5. Vous répondez aux questions de docs/reports/QUESTIONS.md, vous faites `git commit` et `git tag ms-0`
6. Jalon suivant : PROMPT-MS-1.md, et ainsi de suite
```

**Checklist du Product Owner (sans lire le code)** — le détail pas à pas, avec ce qu'il faut essayer à chaque jalon, est dans `docs/CHECKLIST-PO.md`. Résumé :

1. `make spec-trace` ne régresse pas (tableau de bord spécification ↔ tests).
2. Les critères du jalon sont verts.
3. La démonstration du parcours du jalon fonctionne.
4. Une tentative de **violation** est refusée (approuver une version provisoire, diffuser une version non approuvée, annuler sans confirmation, modifier une version finalisée).
5. Les trois statuts (conformité, approbation, diffusion) sont **toujours séparés** à l'écran.
6. Les messages de blocage sont clairs et **ne révèlent pas** d'information protégée.
7. Dans la visionneuse, chaque passage d'un livrable montre sa **source**.
8. Les journaux ne contiennent pas de données sensibles.
9. Les évaluations des modèles de langage respectent leurs seuils.
10. Les écarts et questions du rapport de fin de jalon sont traités.

## 5. « Tout en une passe, avec juste un prompt » ?

C'est **possible de le tenter**, mais ce n'est pas ce que je recommande, pour quatre raisons :

- **Le volume** : 384 exigences techniques, 195 critères d'acceptation, 10 jalons. Une session unique dérive : l'agent oublie, simplifie ou contourne.
- **Les invariants** (états, immutabilité, preuves) sont le cœur du produit. Une erreur précoce se répercute sur tout le reste ; on la détecte jalon par jalon, pas à la fin.
- **L'outil est récent** : DeepSeek Harness est un outil libre en préversion (publié en 2026). Il peut être excellent ; il n'a pas encore l'historique d'outils plus anciens.
- **La qualité dépend surtout du modèle** qui tourne dedans, pas seulement de l'outil. Ce cahier des charges est exigeant (déclencheurs de base de données, moteur d'autorisation, signature cryptographique).

**Ce que le kit permet à la place : un « pilote automatique par jalon »** — un prompt par jalon, l'agent travaille seul jusqu'à ce que les tests passent, sans que vous interveniez, puis il s'arrête pour votre validation. C'est le meilleur compromis entre autonomie et contrôle.
Si votre outil sait être lancé sans interface (mode « non interactif »), vous pouvez enchaîner les jalons dans un script **avec un arrêt obligatoire** si `make check` échoue ; sinon, collez les prompts un par un. *À vérifier dans la documentation de l'outil.*

**Conseil de démarrage** : lancez **MS-0 uniquement** comme essai (budget limité), et jugez la qualité du résultat avant d'engager la suite. Pour les modules délicats (déclencheurs de base de données, moteur d'autorisation, scellement), envisagez de faire relire ou écrire par un second modèle, si votre outil permet de déléguer à d'autres agents.

## 6. Points de vigilance

- **Confidentialité** : un agent de codage envoie à son fournisseur de modèle des extraits du code et des fichiers qu'il lit. Le dépôt ne doit contenir **ni clés, ni données réelles** (c'est déjà une règle d'`AGENTS.md`). Vérifiez où le fournisseur traite et conserve les données (question QT-04 / QT-07 de la spécification technique) avant d'y mettre autre chose que des spécifications et du code.
- **Questions du produit** : les décisions listées en 13.5 de la spécification fonctionnelle et en 22.2 de la technique (INIS, hébergement, non-rétention…) sont à prendre **par vous**, pas par l'agent. Il les consigne dans `QUESTIONS.md`.
- **Aucune donnée réelle avant la fin de MS-8** (sécurité, résidence des données, non-rétention).

## 7. Quand les spécifications changent

```text
1. Remplacez les fichiers de docs/spec/_sources/
2. python tools/spec.py index
3. python tools/gen_briefs.py
```
Les briefs et prompts sont régénérés. Ne les modifiez pas à la main.

## 8. Dépannage

| Problème | Que faire |
|---|---|
| L'agent ouvre les spécifications en entier | Lui rappeler le §0 d'`AGENTS.md` ; coller `PROMPT-REPRISE.md` |
| L'agent n'exécute pas de commandes | Lui faire lire `docs/spec/INDEX.md` et ouvrir seulement les lignes indiquées |
| Le contexte est saturé | `PROMPT-REPRISE.md` dans une session neuve |
| L'agent tourne en boucle sur un test | Règle d'`AGENTS.md` : après 3 tentatives différentes, il consigne et passe à la tranche suivante ; sinon l'interrompre et lire `QUESTIONS.md` |
| L'agent propose d'affaiblir un test | Refuser : c'est interdit (principe de la section 3 d'`AGENTS.md`) ; consulter la spécification |
