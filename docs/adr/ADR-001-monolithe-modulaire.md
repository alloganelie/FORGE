# ADR-001 — Monolithe modulaire et règles de dépendance

- **Statut :** proposé (MS-0)
- **Date :** 2026-10-23
- **Références :** ET-005, ET-006, PT-12, PT-13, DR-01 à DR-07, ADR-001 (spécification technique)

## Contexte

Le produit doit rester un monolithe déployable, mais les 23 modules doivent
pouvoir évoluer sans accès croisés aux tables. La spécification impose sept
règles de dépendance vérifiées en intégration continue.

## Décision

- Un package par module sous backend/src/agent/<module>/ avec api.py (façade),
  events.py, core/ (pur) et infra/ (adaptateurs).
- tools/check_imports.py analyse l'arbre syntaxique et fait échouer le build
  sur DR-01 à DR-07. Les contrôles dynamiques (écriture d'état, journal) sont
  doublés par des déclencheurs PostgreSQL.
- Aucun module n'importe le core/ ou l'infra/ d'un autre : uniquement
  autre_module.api ou autre_module.events.

## Conséquences

- Les frontières sont testables sans conteneur ni base.
- Un import interdit est détecté avant les tests ; le message cite la règle.
- Les exceptions légitimes (lecture des lots de règles par platform via
  documents_io.api) restent explicites et tracées.

## Alternatives écartées

- Microservices : coût opérationnel incompatible avec le MVP.
- Contrôle par revue seule : non bloquant, donc non conforme à ET-005.
