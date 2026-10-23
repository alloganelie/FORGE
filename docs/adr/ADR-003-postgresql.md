# ADR-003 — PostgreSQL comme unique système d'enregistrement

- **Statut :** proposé (MS-0)
- **Date :** 2026-10-23
- **Références :** ET-003, ET-013, ET-018, ET-020, ET-029, ET-358, ADR-003 (spécification technique)

## Contexte

Les invariants d'états, l'immutabilité et la sécurité au niveau des lignes
doivent tenir même en cas de bogue applicatif. Les tests d'invariants ne
doivent jamais simuler la base.

## Décision

- PostgreSQL 17 avec pgvector, pgcrypto et pg_trgm.
- Migrations Alembic versionnées ; 0001_foundations crée types, tables,
  contraintes CHECK, déclencheurs et politiques RLS.
- Les tests d'intégration utilisent une base réelle (agent_test), créée et
  migrée par backend/tests/conftest.py. make check démarre le conteneur local
  si nécessaire.
- Les invariants ne sont jamais testés contre une doublure.

## Conséquences

- Les contraintes inter-axes (IV-05, IV-12, IV-14, RB-114) sont dans la base.
- Le rôle applicatif n'est pas propriétaire des tables et n'a pas DELETE.
- Le retour arrière de migration est testé sur une base temporaire.

## Alternatives écartées

- SQLite en test : ne porte ni ENUM, ni RLS, ni déclencheurs équivalents.
- Base simulée : contredit ET-358.
