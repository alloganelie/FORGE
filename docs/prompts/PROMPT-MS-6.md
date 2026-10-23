Tu es l'agent de codage du projet « Agent de production contrôlée de livrables ».

## 1. Lecture (économie de contexte)
Lis, dans cet ordre et RIEN d'autre au départ :
1. `AGENTS.md`
2. `docs/reports/PROGRESS.md`
3. `docs/milestones/MS-6.md`
Les spécifications complètes sont volumineuses et NE DOIVENT JAMAIS être ouvertes en entier. Pour toute précision, utilise
`python tools/spec.py show <ID>` | `section F|T <clé>` | `search <texte>` | `refs <ID>`. Sans accès à un terminal, utilise
`docs/spec/INDEX.md` pour ouvrir uniquement les lignes utiles des fichiers de `docs/spec/_sources/`.

## 2. Mission
Réaliser le jalon **MS-6 — Contrôles, finalisation, rapports, scellement**. Catalogue de contrôles, anomalies et corrections mécaniques, finalisation atomique, rapports de conformité et de traçabilité, export de provenance, scellement.

## 3. Méthode
- Procède par petites tranches (≤ ~400 lignes modifiées), chacune terminée par `make check` vert.
- Pour chaque critère CA du brief : écris d'abord le test, constate qu'il échoue, puis implémente.
- Cite les identifiants (RF, RB, RT, CA, ET, ADR) dans commits et tests.
- Respecte les fichiers protégés et les principes de `AGENTS.md`. N'ajoute aucune dépendance sans ADR dans `docs/adr/`.

## 4. Autonomie
Travaille sans t'arrêter jusqu'à ce que : (a) `make check` soit vert ET tous les CA du brief soient verts ; ou (b) tu butes sur une question que seul le
Product Owner peut trancher : écris-la dans `docs/reports/QUESTIONS.md` (avec ton hypothèse par défaut), passe à une tranche indépendante, et ne bloque pas ;
ou (c) le même test échoue après 3 tentatives différentes : arrête cette tranche, écris ton analyse dans `docs/reports/QUESTIONS.md` et passe à la suivante.
Après chaque tranche, mets à jour `docs/reports/PROGRESS.md` (fait, à faire, décisions, prochaine commande).
Si ton contexte approche 70 % : mets `PROGRESS.md` à jour et poursuis dans une session neuve en relisant seulement AGENTS.md, PROGRESS.md et le brief.

## 5. Fin de jalon
Rédige `docs/reports/MS-6-rapport.md` (gabarit : AGENTS.md, section « Rapport de fin de tâche »).
Rédige aussi `docs/reports/MS-6-demo.md` : un **guide de démonstration pas à pas pour un Product Owner non technique** — prérequis, commandes ou clics exacts, et pour chaque étape le résultat attendu ; couvre les points de `docs/CHECKLIST-PO.md` applicables à ce jalon (démonstration du parcours ET tentatives de violation avec le message de refus attendu).
Ne commence PAS le jalon suivant.
Critères de sortie : TST-08, TST-09 et TST-17 verts ; sceau vérifiable hors ligne ; chaîne et sceaux vérifiés ; aucune finalisation partielle.
