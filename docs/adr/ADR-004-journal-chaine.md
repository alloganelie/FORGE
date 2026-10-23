# ADR-004 — Journal en ajout seul, canonisation et chaîne de hachage

- **Statut :** proposé (MS-0)
- **Date :** 2026-10-23
- **Références :** ET-021 à ET-026, RT-035, RT-036, RT-062, DC-08, ADR-004 (spécification technique)

## Contexte

Le journal doit permettre de reconstituer l'histoire et détecter toute
modification, suppression ou réordonnancement. La base doit refuser les
écritures directes.

## Décision

- ledger_events est en ajout seul : déclencheurs BEFORE UPDATE/DELETE et
  BEFORE TRUNCATE ; le rôle applicatif n'a que SELECT, INSERT.
- Le hachage est self_hash = SHA-256(canonicalise(champs + prev_hash)) selon
  RFC 8785. Les charges n'utilisent que des entiers (les flottants sont
  refusés) ; les horodatages sont des chaînes RFC 3339 UTC à microsecondes.
- request_seq est attribué sous verrou SELECT ... FOR UPDATE de la demande,
  sans trou. prev_hash est celui du dernier événement de la demande.
- Un déclencheur vérifie la continuité (request_seq, prev_hash) ; la
  vérification du self_hash est refaite par l'application (make verify-chain,
  tâche périodique ET-025).

## Conséquences

- Une suppression ou un réordonnancement est détecté ; une altération du
  contenu est détectée par recalcul.
- Les séquences globales peuvent avoir des trous après annulation de
  transaction ; seuls les request_seq sont sans trou.
- Un événement forgé avec un prev_hash correct mais un faux self_hash passe
  le déclencheur : la vérification applicative le signale comme alerte.

## Alternatives écartées

- Chaîne globale unique : la spécification exige une chaîne par demande.
- Hachage sur JSON non canonique : résultats dépendants de l'ordre des clés.
