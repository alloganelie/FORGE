# Jalon MS-1 — Gouvernance

> Brief généré par `tools/gen_briefs.py` — ne pas modifier à la main. Pour tout détail : `python tools/spec.py show <ID>`.

## 1. Objectif

Artefacts de gouvernance versionnés (lots de règles, modèles, registre, catalogue de contrôles), schémas, pipeline de validation, épinglage par demande, console minimale de gouvernance.

**À savoir.** Le contenu des règles métier est fourni par la personne responsable : utiliser l'Annexe C comme exemple, sans le considérer comme décision.

## 2. Périmètre

- Cas d'usage : UC-026, UC-027
- Suites de tests visées : TST-15 (partie gouvernance)
- Hors périmètre de ce jalon : Appels LLM ; interface au-delà de la console minimale (SCR-15) et des utilisateurs/rôles (SCR-17).
- 2 exigence(s) V2 comprises dans les plages sont **reportées à MS-9** (non listées ci-dessous).

## 3. Exigences techniques à réaliser (15)

- **ET-053** ([F] · MVP) — Lots de règles, modèles, registre et catalogue de contrôles sont des versions immuables après approbation dans `governance_artifact_versions`.  
  _Réalise : RF-257, RB-067 · ADR-007_
- **ET-054** ([T] · MVP) — Chaque type d'artefact a un JSON Schema versionné ; l'artefact est validé à l'ouverture et à l'approbation.  
  _Réalise : RF-254 · MOD-02_
- **ET-055** ([T] · MVP) — Le pipeline de validation (8.6, étapes 1 à 9) est implémenté en étapes composables avec rapport détaillé.  
  _Réalise : RF-254 · MOD-02_
- **ET-056** ([T] · MVP) — Les tests de règles (*étant donné / attendu*) livrés avec un lot sont exécutés à la validation.  
  _Réalise : RF-254 · MOD-02_
- **ET-057** ([F] · MVP) — L'analyse d'impact liste les demandes épinglées sur la version remplacée et les modèles et contrôles dépendants.  
  _Réalise : RF-258 · MOD-02_
- **ET-058** ([F] · MVP) — L'approbation d'un artefact exige une décision DH-07 de la personne responsable avec date d'effet ; elle n'est pas rétroactive.  
  _Réalise : RB-104, RF-254 · MOD-02, MOD-15_
- **ET-059** ([F] · MVP) — À la faisabilité, les artefacts sont épinglés ; toute lecture de règle passe par les épinglages de la demande.  
  _Réalise : RF-028, RF-185 · MOD-02_
- **ET-060** ([T] · MVP) — Les artefacts sont chargés par empreinte avec cache ; jamais par « dernière version ».  
  _Réalise : RB-068 · MOD-02_
- **ET-061** ([F] · MVP) — L'évaluateur de formules (CEL) est encapsulé ; seules les fonctions enregistrées (FM-03) existent.  
  _Réalise : RF-105 · ADR-007_
- **ET-062** ([F] · MVP) — Les calculs utilisent exclusivement l'arithmétique décimale ; un test détecte tout `float` dans le chemin de calcul.  
  _Réalise : RF-112 · MOD-10_
- **ET-063** ([F] · MVP) — Les conversions d'unités s'appuient sur des tables déclarées dans le lot ; aucune conversion implicite.  
  _Réalise : RF-096, RB-043 · MOD-10_
- **ET-064** ([F] · MVP) — Les corrections mécaniques sont des fonctions nommées du code ; le lot ne fait que les autoriser et les paramétrer.  
  _Réalise : RF-145 · MOD-13_
- **ET-065** ([F] · MVP) — La validation sémantique refuse toute valeur par défaut qui comblerait une lacune hors `on_missing` explicite.  
  _Réalise : RF-075 · MOD-02_
- **ET-066** ([T] · MVP) — Une interface d'édition d'artefacts offre validation en direct, différences entre versions et rapport d'impact.  
  _Réalise : UC-027 · MOD-02_
- **ET-121** ([F] · MVP) — Le graphe de dépendances du modèle est vérifié acyclique à la validation du modèle.  
  _Réalise : RF-054 · MOD-02_

## 4. Critères d'acceptation à rendre verts (4)

Écrire d'abord un test par critère, étiqueté de son identifiant (`@pytest.mark.ca("CA-xxx")`).

- **CA-150** (RF-250, RF-252) — **Étant donné** une modification du registre permanent, **quand** elle est tentée par un autre que la personne responsable, **alors** elle est refusée ; quand elle est faite par la personne responsable, **alors** le registre est versionné et les productions antérieures restent liées à l'ancien.
- **CA-151** (RF-251) — **Étant donné** une source du registre, **quand** on la consulte, **alors** ses autorisations aux quatre niveaux figurent.
- **CA-152** (RF-254, RF-258, RF-259) — **Étant donné** une modification de règle, de modèle ou de préférence, **quand** elle est tentée par un utilisateur ordinaire, **alors** elle est refusée ; faite par la personne responsable, **alors** elle est versionnée sans effet sur les productions antérieures ni sur les demandes en cours.
- **CA-153** (RF-255, RF-256) — **Étant donné** un exemple contredisant une règle, **quand** l'Agent produit, **alors** il applique la règle et signale l'incohérence comme observation.

## 5. Exigences fonctionnelles liées (21) — une ligne chacune

Résumés seulement. Pour le texte complet et le contexte : `python tools/spec.py show RF-xxx`.

- RB-043 — La conversion d'unités, de dates ou de formats n'est faite que selon des règles explicites.
- RB-067 — Les livrables existants sont immuables.
- RB-068 — Chaque production reste liée aux sources, règles et modèles utilisés au moment de sa création.
- RB-104 — Un changement de règle approuvé a une date d'effet explicite et n'est pas rétroactif.
- RF-028 — L'Agent doit déterminer les versions applicables du modèle, des règles et du registre des sources, et les figer pour la demande.
- RF-054 — Pour chaque ligne, l'Agent doit préciser les dépendances susceptibles de bloquer l'élément.
- RF-075 — L'Agent ne doit pas combler une lacune par une déduction, une estimation, une valeur par défaut ou un contenu plausible qui ne provient pas d'une source ou d'une règle.
- RF-096 — L'Agent peut convertir des formats de dates, d'unités ou de fichiers selon des règles explicites (TF-04).
- RF-105 — L'Agent ne doit effectuer aucun calcul ni aucune transformation numérique sans méthode explicitement définie.
- RF-112 — Un calcul doit être reproductible : mêmes entrées et même méthode donnent le même résultat.
- RF-145 — L'Agent ne peut corriger automatiquement un défaut mécanique que si une règle l'autorise explicitement.
- RF-185 — Chaque production doit rester liée aux sources, règles et modèles utilisés au moment de sa création.
- RF-250 — Le registre permanent des sources n'est modifié que par la personne responsable, selon une procédure explicite.
- RF-251 — Chaque source du registre porte ses autorisations aux quatre niveaux, ses conditions, ses périodes de validité et ses restrictions.
- RF-252 — Les modifications du registre sont versionnées et datées ; les productions antérieures conservent le registre en vigueur à leur création.
- RF-254 — Les modèles et les règles ne sont créés ou modifiés que par une procédure explicite et par une personne habilitée.
- RF-255 — Les règles et exigences formelles prévalent sur les exemples documentaires.
- RF-256 — Lorsqu'un exemple contredit une règle, l'Agent applique la règle et signale l'incohérence comme observation à la personne responsable.
- RF-257 — Les modèles et règles doivent être versionnés : chaque version est datée et porte son auteur et son motif.
- RF-258 — Une modification de règle ou de modèle n'affecte automatiquement ni les productions antérieures ni les demandes en cours.
- RF-259 — Les préférences suivent la même procédure explicite que les règles et les modèles.

## 6. À lire à la demande (ne rien lire d'autre au départ)

| Quoi | Commande | Pourquoi |
|---|---|---|
| Spéc. technique 8 | `python tools/spec.py section T 8` | Moteur de règles et gouvernance |
| Spéc. technique 6.4 | `python tools/spec.py section T 6.4` | Tables de gouvernance et d'épinglage |
| Spéc. fonctionnelle UC-026 | `python tools/spec.py section F UC-026` | Registre des sources |
| Spéc. fonctionnelle UC-027 | `python tools/spec.py section F UC-027` | Modèles, règles, préférences |
| Spéc. technique Annexe-C | `python tools/spec.py section T Annexe-C` | Exemple de lot de règles (illustratif) |
| Spéc. fonctionnelle 7.10 | `python tools/spec.py section F 7.10` | Règles de gouvernance (RB-097 à RB-108) |

## 7. Critères de sortie du jalon

TST-15 (gouvernance) vert ; un lot de règles d'exemple approuvé de bout en bout ; épinglage et non-rétroactivité testés.

## 8. Rappels (extraits d'AGENTS.md)

- Tests d'acceptation d'abord ; `make check` doit passer ; ne jamais affaiblir un test, une contrainte ou un déclencheur.
- Ambiguïté de spécification → question dans `docs/reports/QUESTIONS.md`, jamais d'invention.
- À la fin d'une tranche : mettre à jour `docs/reports/PROGRESS.md`.

