# ADR-010 — Schémas JSON et évaluateur CEL encapsulé

- **Statut :** proposé (MS-1)
- **Date :** 2026-10-23
- **Références :** ET-054, ET-055, ET-061, ET-062, RF-105, RF-254, ADR-007 (spécification technique)

## Contexte

Chaque type d'artefact de gouvernance doit être validé contre un JSON Schema
versionné (ET-054). Les formules des lots doivent être évaluées sans effet de
bord, avec des fonctions enregistrées uniquement (FM-01, FM-03), et tous les
calculs doivent rester en arithmétique décimale (ET-062, FM-02).

## Décision

- Ajouter la dépendance **jsonschema** (draft 2020-12) pour l'étape 1 du
  pipeline. Les schémas sont versionnés dans
  backend/src/agent/governance/schemas/v1/.
- Implémenter un évaluateur CEL **restreint et encapsulé** dans
  transform/core/cel.py : littéraux, identifiants, appels de fonctions
  enregistrées, opérateurs arithmétiques et de comparaison, listes. Il n'utilise
  ni eval ni exécution dynamique. Toute fonction hors FM-03 est refusée au
  moment de la compilation.
- Les nombres sont des decimal.Decimal avec un contexte explicite (précision et
  arrondi). Aucun float n'est accepté dans le chemin de calcul ; un contrôle
  AST dédié échoue si le mot-clé float apparaît dans transform/core.
- L'évaluateur est remplaçable derrière le port compile_expression/evaluate ;
  un moteur CEL externe pourra le remplacer sans changer les lots.

## Conséquences

- Une formule inconnue, une fonction non enregistrée ou une unité non déclarée
  font échouer la validation du lot.
- Le sous-ensemble CEL est volontairement limité : pas de compréhension de
  liste, pas de macro, pas d'accès réseau. Une formule hors sous-ensemble est
  refusée, jamais approximée.
- La dépendance jsonschema est une dépendance de production, verrouillée dans
  uv.lock.

## Alternatives écartées

- Valider à la main : ne satisfait pas ET-054 (JSON Schema versionné).
- Utiliser un moteur CEL complet avec fonctions personnalisées : coût
  d'intégration élevé pour le MVP ; le port permet un remplacement ultérieur.
- Utiliser float : interdit par FM-02 et ET-062.
