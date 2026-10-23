# ADR-005 — Machines à états générées et moteur unique

- **Statut :** proposé (MS-0)
- **Date :** 2026-10-23
- **Références :** ET-035 à ET-044, IV-01 à IV-15, TR-xx, ADR-005 (spécification technique)

## Contexte

Aucune transition ne doit exister uniquement dans le code. Les six axes (R, C,
A, D, V, E) doivent être indépendants et tout changement d'état doit passer par
un moteur unique.

## Décision

- tools/gen_transitions.py lit la spécification fonctionnelle 8.2 à 8.7 et la
  spécification technique 7.2, puis écrit rulepacks/state_machines/*.yaml.
  Chaque fichier porte les empreintes des sources ; --check échoue en cas de
  dérive.
- lifecycle/core/engine.py est pur : il reçoit la machine, l'état courant,
  l'acteur et un instantané de gardes. guards.py ne lit ni l'heure, ni la
  base, ni le hasard ; une garde inconnue refuse.
- lifecycle/infra/transitions.py applique une transition dans une
  transaction : verrou, row_version, état, state_changes, journal.
- La base refuse toute écriture d'état sans app.transition_id (DR-03).
- TST-18 : backend/tests/property/test_tst18.py (Hypothesis) vérifie IV-01 à
  IV-15 après chaque pas ; test_tst18_db.py rejoue le parcours nominal sur
  PostgreSQL réel.

## Conséquences

- TR-R-22 (révision) n'est pas une transition d'état : elle est déclarée dans
  non_transitions et testée comme commande de création d'une demande liée.
- Q-002 : la reprise depuis Reçue ou Vérification de faisabilité revient à
  l'état d'origine (hypothèse consignée).

## Alternatives écartées

- Transitions écrites à la main dans le code : contredit ET-035.
- Moteur par axe dupliqué : risque de divergence des gardes.
