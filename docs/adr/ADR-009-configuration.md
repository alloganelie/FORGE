# ADR-009 — Configuration et environnements

- **Statut :** proposé (MS-0)
- **Date :** 2026-10-23
- **Références :** ET-008, ET-010, ET-016, MOD-23, ADR-016 (spécification technique)

## Contexte

Une configuration invalide doit empêcher le démarrage ; aucun secret ne doit
être dans le dépôt ; les environnements doivent être séparés.

## Décision

- Schéma Pydantic Settings (préfixe AGENT_), validé au démarrage. Une variable
  AGENT_* inconnue est refusée ; une URL de base non psycopg est refusée ;
  AGENT_SECRET_KEY est obligatoire en production.
- Quatre fichiers d'environnement : local, CI, préproduction, production.
  Les valeurs sensibles sont des placeholders ou des variables de coffre.
- L'horloge est un port injecté (Clock) ; le domaine ne lit jamais l'heure.
- Les identifiants sont des UUIDv7 générés par l'application (platform.ids).

## Conséquences

- Une faute de frappe dans une variable bloque le démarrage au lieu de passer
  inaperçue.
- Les tests peuvent injecter FixedClock et des identifiants déterministes.
- AGENT_DATABASE_URL ne contient jamais de secret réel dans le dépôt.

## Alternatives écartées

- Fichier .env unique : mélange les environnements.
- Lire datetime.now() dans le domaine : contredit ET-016.
