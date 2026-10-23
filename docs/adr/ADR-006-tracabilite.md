# ADR-006 — Traçabilité spécification ↔ tests

- **Statut :** proposé (MS-0)
- **Date :** 2026-10-23
- **Références :** ET-353 à ET-356, ET-372, TT-01 à TT-05, PT-14, ADR-017 (spécification technique)

## Contexte

Le Product Owner doit pouvoir vérifier la couverture sans lire le code. Les
identifiants doivent venir des spécifications, jamais d'une saisie manuelle.

## Décision

- docs/spec/ids.json est généré par tools/spec.py index.
- Les tests portent @pytest.mark.ca("CA-xxx"), .spec("RF-xxx") ou
  .tst("TST-xx"). tools/spec_trace.py construit la matrice et lit les
  résultats du JUnit produit par pytest.
- Portes bloquantes : identifiant inconnu (ET-356), test orphelin, transition
  non citée (ET-044), CA du périmètre non vert (ET-354).
- La porte ET-355 (toute exigence RF/RB/RT couverte ou justifiée) est publiée
  dès MS-0 et devient bloquante au jalon final. Le périmètre des CA est le
  cumul des sections 4 des jalons ≤ courant ; MS-0 n'a aucun CA, les 195 CA
  sont donc « hors périmètre » et non « sans test ».
- Sorties : docs/reports/spec-trace.html (lecture PO), .md, .json, plus
  l'historique spec-trace-history.json pour mesurer la non-régression.

## Conséquences

- Un identifiant inventé fait échouer make check.
- Un test sans identifiant est un test orphelin et fait échouer la porte.
- La décision de périmètre est une hypothèse à valider par le PO (Q-003).

## Alternatives écartées

- Couverture calculée par nom de fichier : trop fragile.
- Ne pas publier les exigences non couvertes : le PO ne verrait pas la dette.
