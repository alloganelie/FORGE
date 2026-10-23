# FORGE — Framework for Orchestrated Report Generation and Evaluation

> **Usage du nom :** FORGE est le nom de l'infrastructure, utilisé dans le contexte de développement et affiché dans le frontend. Il n'apparaît **pas** dans les livrables, rapports ou messages générés par le système (décision PO — 2026-10-23).

---

## Présentation

FORGE est un agent de production contrôlée de livrables réglementaires.  
Il orchestre la génération, la vérification et le cycle de vie de rapports dont chaque contenu est lié à une preuve traçable.

Le produit est conçu selon trois principes non négociables :
- **Le LLM propose, le code dispose** — aucun modèle de langage ne décide ni n'écrit en base.
- **Pas de contenu sans preuve** — chaque atome d'un livrable est lié à une source vérifiable.
- **Les états ne changent que par le moteur** — jamais de mise à jour directe d'une colonne d'état.

---

## Pour l'agent de codage — lire en premier

```
AGENTS.md       <- consignes permanentes (lire systématiquement au démarrage)
CLAUDE.md       <- renvoie à AGENTS.md (pour Claude Code)
```

Protocole de démarrage (§0 d'`AGENTS.md`) :
1. Lire `AGENTS.md`
2. Lire `docs/reports/PROGRESS.md`
3. Lire `docs/milestones/MS-n.md` (le jalon courant)

Ne jamais ouvrir les fichiers `docs/spec/_sources/` en entier (≈ 585 Ko).  
Utiliser `python tools/spec.py show <ID>` pour toute précision ponctuelle.

---

## Structure du dépôt

```
AGENTS.md                          # Consignes permanentes de l'agent
README.md                          # Ce fichier
Makefile                           # Raccourcis : make check, make spec-trace...
docs/
├── spec/
│   ├── _sources/                  # Spécifications complètes (archives — ne pas ouvrir en entier)
│   ├── INDEX.md                   # Carte des sections et familles d'identifiants (avec numéros de lignes)
│   └── ids.json                   # Annuaire des 2 068 identifiants
├── CHECKLIST-PO.md                # Fiche de revue jalon pour le Product Owner
├── milestones/MS-0.md ... MS-9.md # Briefs de jalon (ce que l'agent doit lire et faire)
├── prompts/                       # Prompts prêts à l'emploi par jalon
└── reports/                       # PROGRESS.md · QUESTIONS.md · rapports et guides de démo
tools/
├── spec.py                        # Lecteur par tranches (show / section / search / refs / toc)
└── gen_briefs.py                  # Régénère briefs et prompts si les specs changent
```

---

## Jalons

| # | Jalon | Statut |
|---|---|---|
| MS-0 | Fondations (dépôt, CI, BDD, migrations, moteur d'états, traçabilité) | **Terminé — en revue PO** |
| MS-1 | Gouvernance (rôles, espaces de travail, lots de règles) | Non démarré |
| MS-2 | Demande et faisabilité | Non démarré |
| MS-3 | Sources et preuves | Non démarré |
| MS-4 | Cartographie et contradictions | Non démarré |
| MS-5 | Atomes et rendu | Non démarré |
| MS-6 | Contrôles et rapports | Non démarré |
| MS-7 | Approbation, diffusion, cycle de vie | Non démarré |
| MS-8 | Durcissement et pilote | Non démarré |
| MS-9 | Clôture | Non démarré |

---

## État MS-0

Les fondations sont en place : 23 modules et leurs frontières, configuration
validée, PostgreSQL et migrations, journal chaîné, moteur d'états généré,
TST-18, tableau de bord de traçabilité, image non root. Voir
docs/reports/MS-0-rapport.md et docs/reports/MS-0-demo.md.

## Commandes disponibles (après MS-0)

```bash
make check                    # Format · types · dépendances · tests · traçabilité
make test-acceptance          # Tests d'acceptation uniquement (@pytest.mark.ca)
make spec-trace               # Tableau de bord spec <-> tests (HTML + Markdown)
make gen-transitions          # Génère le moteur d'états depuis la spec
make verify-chain             # Vérifie les invariants du journal chaîné

# Disponibles immédiatement :
make spec ID=CA-099           # Affiche un critère d'acceptation
make toc DOC=T                # Table des matières de la spec technique
make brief MS=MS-1            # Affiche le brief d'un jalon
```

---

## Règles fondamentales (rappel)

- **Fichiers protégés** : `docs/spec/**`, `rulepacks/**`, `backend/migrations/**` déjà appliquées, `prompts/**` — modification sur demande expresse du PO uniquement.
- **Aucune donnée réelle** ni secret dans le dépôt, les tests ou les journaux.
- **Aucune logique métier** dans l'API ou l'interface.
- Toute nouvelle dépendance requiert un ADR dans `docs/adr/`.

---

*Pour le Product Owner : votre fiche de revue est dans `docs/CHECKLIST-PO.md`.*  
*Pour reprendre après interruption : coller `docs/prompts/PROMPT-REPRISE.md` dans une session neuve.*