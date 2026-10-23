# AGENTS.md — consignes permanentes (à lire en premier ; une page)

Projet : **Agent de production contrôlée de livrables**. Spécifications dans `docs/spec/_sources/` (fonctionnelle **F** et technique **T**).
La spécification fonctionnelle prévaut. Tu es soumis aux mêmes principes que le produit : **ne rien inventer, ne pas décider hors règles, tout tracer.**

## 0. Protocole de lecture (économie de contexte) — OBLIGATOIRE
1. **N'ouvre jamais les fichiers maîtres en entier** (≈ 585 Ko, ≈ 160 000 jetons). Ils sont des archives de référence.
2. Au démarrage, lis uniquement : `AGENTS.md` → `docs/reports/PROGRESS.md` → `docs/milestones/MS-n.md` (le jalon courant).
3. Pour toute précision, utilise l'outil (aucune dépendance) :
   - `python tools/spec.py show CA-099 ET-021 RF-272` — lignes d'identifiants (plages : `ET-091..ET-106`) ou fiches (`UC-015`, `ADR-005`)
   - `python tools/spec.py section T 10.4` / `section F UC-005` / `section F Annexe-C` — une section
   - `python tools/spec.py search "texte"` / `refs RF-272` — recherche et mentions
   - `python tools/spec.py toc T` — table des matières avec lignes
4. Sans terminal : `docs/spec/INDEX.md` donne les lignes de chaque section ; n'ouvre que ces lignes.
5. Ne recopie pas de longs extraits des spécifications dans tes notes ou tes réponses : cite les identifiants.
6. Si ton contexte approche **70 %**, mets `docs/reports/PROGRESS.md` à jour et continue dans une session neuve en relisant seulement les trois fichiers du point 2.

## 1. Principes non négociables
1. Le LLM propose, le code dispose : aucun modèle de langage n'écrit en base, ne change un état, ne décide un droit.
2. Tout contenu d'un livrable est un **atome lié à une preuve** (CT-13). Pas de lien, pas de contenu.
3. Les états ne changent que par le **moteur de machines à états**. Jamais d'UPDATE direct d'une colonne d'état.
4. Conformité, approbation, diffusion sont **trois statuts indépendants** : n'en déduis jamais un d'un autre.
5. Le domaine pur (`core/`) n'a **aucune entrée-sortie** ; heure, hasard et I/O passent par des ports.
6. Tout appel de LLM passe par `llm_gateway.run_task` ; sorties revalidées localement ; aucun outil exposé aux modèles.
7. Les règles métier sont des **données** (`rulepacks/`), jamais du code ni du texte de prompt.
8. **Refus par défaut** : autorisations, transformations, formats, sources.
9. Les raisons communicables viennent de **gabarits** ; jamais de texte libre d'un LLM ; jamais de raison interne exposée.
10. **Aucune donnée réelle** ni secret dans le dépôt, les tests, les prompts ou les journaux (clés d'API : variables d'environnement).

## 2. Fichiers PROTÉGÉS (modification seulement sur demande expresse du Product Owner)
`docs/spec/**`, `rulepacks/**`, `backend/migrations/**` déjà appliquées, déclencheurs d'immutabilité, configuration d'intégration continue, `prompts/**` (changement = évaluation).

## 3. Méthode
- Une tranche = un morceau précis (≤ ~400 lignes modifiées), terminée par `make check` vert.
- **Tests d'acceptation d'abord** : un test par CA, étiqueté `@pytest.mark.ca("CA-xxx")` ; vérifier qu'il échoue ; puis implémenter.
- Cite les identifiants (RF, RB, RT, CA, ET, ADR) dans commits et tests.
- **Ne jamais affaiblir, ignorer ou supprimer** un test, une contrainte, un déclencheur ou une règle de dépendance pour faire passer un résultat.
- Pas de nouvelle dépendance sans ADR proposé dans `docs/adr/`. Aucune logique métier dans l'API ou l'interface.

## 4. Autonomie, blocages et reprise
- Travaille de façon autonome jusqu'à la fin du jalon (CA du brief verts + `make check` vert).
- **Question que seul le Product Owner peut trancher** → écris-la dans `docs/reports/QUESTIONS.md` avec ton hypothèse par défaut, passe à une tranche indépendante, ne bloque pas.
- **Même test en échec après 3 tentatives différentes** → arrête cette tranche, consigne l'analyse dans `QUESTIONS.md`, passe à la suivante.
- Après chaque tranche : mets à jour `docs/reports/PROGRESS.md`. À la fin du jalon : rapport `docs/reports/MS-n-rapport.md` **et** guide de démonstration `docs/reports/MS-n-demo.md` (pas à pas, pour un Product Owner non technique ; voir `docs/CHECKLIST-PO.md`). **Ne commence pas le jalon suivant.**

## 5. Commandes (à créer en MS-0 ; ensuite disponibles)
`make check` (format, types, dépendances, tests, traçabilité) · `make test-acceptance` · `make spec-trace` · `make gen-transitions` · `make verify-chain`
Toujours disponibles : `make spec ID=CA-099`, `make toc DOC=T`, `make brief MS=MS-3`.

## 6. Quand t'arrêter et demander
Exigence ambiguë, contradictoire ou manquante · une tâche semble exiger de relâcher un principe du §1 · décision d'architecture nouvelle · un fichier protégé devrait changer.

## 7. Rapport de fin de tâche (gabarit)
```text
Tâche / jalon : <titre>
Identifiants couverts : RF-…, RB-…, RT-…, CA-…, ET-…
Tests ajoutés ou modifiés : <liste>
Résultat de make check : <vert/rouge, détail>
Écarts par rapport à la spécification : <aucun | liste>
Décisions prises : <aucune | ADR proposés>
Questions ouvertes : <aucune | liste>
Risques constatés : <aucun | liste>
```

## 8. Définition de « terminé »
CA visés verts et étiquetés · identifiants cités · `make check` vert · aucun test/contrainte/déclencheur affaibli · aucune logique métier hors domaine pur · décisions et questions consignées · `PROGRESS.md` à jour.
