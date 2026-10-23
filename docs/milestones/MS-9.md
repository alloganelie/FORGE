# Jalon MS-9 — Évolutions V2

> Brief généré par `tools/gen_briefs.py` — ne pas modifier à la main. Pour tout détail : `python tools/spec.py show <ID>`.

## 1. Objectif

Livrables multiples, priorités, exceptions, propositions de règles, profil auditeur, différences entre versions, formats Excel et PowerPoint, mutation testing.

**À savoir.** Chaque élément V2 reste sous confirmation du Product Owner (QO-036 pour la diffusion exceptionnelle).

## 2. Périmètre

- Cas d'usage : UC-021, UC-022, UC-028, UC-029
- Suites de tests visées : TST-13 et suites V2
- Hors périmètre de ce jalon : —

## 3. Exigences techniques à réaliser (10)

- **ET-067** ([T] · V2) — Les lots peuvent être exportés et importés en YAML afin de pouvoir être relus et conservés par ailleurs.  
  _Réalise : RF-257 · MOD-02_
- **ET-068** ([F] · V2) — Les propositions d'évolution de règles sont stockées sans aucun effet normatif jusqu'à décision.  
  _Réalise : RF-266, GV-05 · MOD-02_
- **ET-148** ([T] · V2) — Le rendu Excel écrit des valeurs, une feuille de provenance, et des formules vivantes seulement si une règle l'exige, avec valeurs en cache vérifiées.  
  _Réalise : RF-125 · MOD-22_
- **ET-149** ([T] · V2) — Le rendu PowerPoint place les identifiants d'atomes dans les notes.  
  _Réalise : RF-125 · MOD-22_
- **ET-197** ([T] · V2) — Une archive d'audit signée du dossier complet d'une version peut être exportée.  
  _Réalise : RT-065 · MOD-14_
- **ET-211** ([F] · V2) — Les exceptions (V2) modifient la règle appliquée à un élément, jamais le résultat d'un contrôle ; elles figurent en réserve.  
  _Réalise : RF-260 à RF-263, RF-281 · MOD-15_
- **ET-228** ([F] · V2) — Le récapitulatif des différences compare les atomes par `element_key` et empreinte, et liste les sources et règles changées.  
  _Réalise : RF-194 · MOD-16_
- **ET-263** ([T] · V2) — Les évaluations et réévaluations non urgentes utilisent le traitement par lots.  
  _Réalise : BU-03 · MOD-21_
- **ET-289** ([T] · V2) — Des webhooks signés (HMAC) avec reprises sont proposés.  
  _Réalise : 13.6 · MOD-18_
- **ET-360** ([T] · V2) — Des tests de mutation couvrent la politique d'autorisation, l'évaluation de qualité et la décision de conformité.  
  _Réalise : ET-073, ET-110, ET-166 · ADR-017_

## 4. Critères d'acceptation à rendre verts (14)

Écrire d'abord un test par critère, étiqueté de son identifiant (`@pytest.mark.ca("CA-xxx")`).

- **CA-114** (RF-194, RF-197) — **Étant donné** deux versions, **quand** on les compare, **alors** les différences sont présentées et la version remplacée reste consultable.
- **CA-127** (RF-213) — **Étant donné** deux livrables dépendants, **quand** l'un est bloqué, **alors** les éléments de l'autre qui en dépendent sont bloqués.
- **CA-128** (RF-214) — **Étant donné** une incohérence entre deux documents, **quand** l'Agent la détecte, **alors** elle est signalée.
- **CA-129** (RF-216, RB-095) — **Étant donné** un livrable déjà produit, **quand** une incohérence inter-documents est détectée, **alors** il n'est pas modifié automatiquement.
- **CA-130** (RF-223) — **Étant donné** un livrable bloqué, **quand** d'autres livrables n'en dépendent pas, **alors** ils avancent.
- **CA-131** (RF-219) — **Étant donné** deux demandes concurrentes, **quand** les critères explicites tranchent, **alors** l'ordre est appliqué et motivé.
- **CA-132** (RF-221, RB-096) — **Étant donné** une urgence non validée, **quand** les priorités sont établies, **alors** elle n'est pas prise en compte.
- **CA-133** (RF-220, RB-091) — **Étant donné** des règles insuffisantes pour départager, **quand** l'Agent ordonne, **alors** il prépare les éléments d'arbitrage et sollicite la personne responsable.
- **CA-134** (RF-217, RF-218) — **Étant donné** une information modifiée utilisée par une autre production, **quand** aucun signalement ni révision n'est demandé, **alors** cette production n'est pas révisée.
- **CA-154** (RF-260 à RF-263) — **Étant donné** une exception, **quand** elle est demandée par un autre que la personne responsable, **alors** elle est refusée ; quand elle est accordée, **alors** elle est tracée, mentionnée en réserve et n'a modifié aucune règle.
- **CA-155** (RF-264, RF-265, RF-267) — **Étant donné** une correction ponctuelle d'un utilisateur, **quand** une demande ultérieure est traitée, **alors** elle n'est pas influencée par cette correction.
- **CA-156** (RF-266) — **Étant donné** une proposition d'évolution de règle, **quand** elle est faite, **alors** elle est consignée et transmise à la personne responsable, sans effet avant décision.
- **CA-194** (RF-281, RB-127 (V2)) — **Étant donné** une exception accordée sur une règle contrôlée, **quand** les contrôles s'exécutent, **alors** ils s'appliquent aux règles telles qu'exceptées, l'exception figure en réserve et aucun contrôle échoué n'est converti en réussi.
- **CA-195** (RF-280 (V2, sous réserve de QO-036)) — **Étant donné** une diffusion exceptionnelle d'une version non conforme décidée par la personne responsable, **quand** le document est rendu accessible, **alors** il porte un marquage visible, la décision et la réserve figurent dans les rapports et le statut de conformité reste Non conforme.

## 5. Exigences fonctionnelles liées (28) — une ligne chacune

Résumés seulement. Pour le texte complet et le contexte : `python tools/spec.py show RF-xxx`.

- RB-091 — Si les règles ne permettent pas d'établir une priorité, l'Agent prépare les éléments d'arbitrage et sollicite la personne responsable.
- RB-095 — L'Agent ne modifie jamais automatiquement un livrable déjà produit.
- RB-096 — Une urgence non validée n'altère pas la priorité.
- RB-127 — Une exception ne transforme pas un contrôle échoué en contrôle réussi ; la conformité s'apprécie par rapport aux règles telles qu'exceptées, et l'exception est mention...
- RF-125 — L'Agent doit produire le livrable dans le format demandé parmi les formats prévus (Word, PDF, Excel, PowerPoint, CSV, Markdown), dans la mesure où le type de livrable ...
- RF-194 — L'Agent doit produire un récapitulatif des différences entre deux versions (éléments ajoutés, modifiés, supprimés ; sources et règles changées).
- RF-197 — Une version remplacée doit rester consultable et immuable.
- RF-213 — Lorsque plusieurs livrables sont demandés dans la même opération, l'Agent doit coordonner leurs dépendances.
- RF-214 — L'Agent doit vérifier la cohérence entre les différents documents.
- RF-216 — L'Agent ne doit pas modifier automatiquement un livrable déjà produit ; une révision doit être explicitement déclenchée.
- RF-217 — Les demandes sont traitées indépendamment : une modification d'information ne déclenche pas automatiquement la révision d'autres productions.
- RF-218 — Une répercussion sur une autre production n'a lieu que lorsqu'elle est explicitement signalée ou lorsqu'une révision est demandée.
- RF-219 — L'Agent doit organiser les priorités selon des critères explicites : échéances, urgence validée, importance autorisée, dépendances et ressources disponibles.
- RF-220 — Si les règles ne permettent pas d'établir une priorité, l'Agent doit préparer les éléments utiles à l'arbitrage et solliciter la personne responsable.
- RF-221 — Une urgence déclarée par un utilisateur n'est prise en compte que lorsqu'elle est validée.
- RF-223 — Dans une même opération, le statut de chaque livrable est géré individuellement : un livrable bloqué n'empêche pas ceux qui n'en dépendent pas.
- RF-257 — Les modèles et règles doivent être versionnés : chaque version est datée et porte son auteur et son motif.
- RF-260 — Seule la personne responsable peut autoriser une exception à une règle.
- RF-261 — Une exception doit être explicite, ponctuelle, motivée, limitée à une demande ou un élément, et tracée.
- RF-262 — Une exception ne modifie pas la règle et ne constitue pas un précédent.
- RF-263 — Un livrable produit avec exception doit le mentionner dans le rapport de conformité à titre de réserve.
- RF-264 — Une correction ponctuelle apportée par un utilisateur ne doit jamais devenir automatiquement une règle générale.
- RF-265 — Aucune règle, préférence ou modèle ne doit être modifié implicitement à partir de l'historique des interactions.
- RF-266 — L'utilisateur peut proposer une évolution de règle ; la proposition est consignée et transmise à la personne responsable, sans effet normatif avant décision.
- RF-267 — L'Agent doit informer l'utilisateur qu'une correction ponctuelle ne vaut que pour la demande en cours.
- RF-280 — Diffusion exceptionnelle d'une version non finalisée ou non conforme : si elle est retenue en V2 (QO-036), elle n'est possible que sur décision explicite de la personn...
- RF-281 — Une exception (RF-260 à RF-263) modifie la règle appliquée à un élément ; elle ne transforme jamais un contrôle échoué en contrôle réussi. La conformité s'apprécie par...
- RT-065 — Un audit doit pouvoir reconstituer pourquoi un livrable est ce qu'il est : règles, sources, décisions, contrôles.

## 6. À lire à la demande (ne rien lire d'autre au départ)

| Quoi | Commande | Pourquoi |
|---|---|---|
| Spéc. technique 10.13 | `python tools/spec.py section T 10.13` | Priorisation et livrables multiples (SC-01 à SC-05) |
| Spéc. fonctionnelle UC-021 | `python tools/spec.py section F UC-021` | Fiche du cas d’usage |
| Spéc. fonctionnelle UC-022 | `python tools/spec.py section F UC-022` | Fiche du cas d’usage |
| Spéc. fonctionnelle UC-028 | `python tools/spec.py section F UC-028` | Fiche du cas d’usage |
| Spéc. fonctionnelle UC-029 | `python tools/spec.py section F UC-029` | Fiche du cas d’usage |
| Spéc. fonctionnelle 9.6.4 | `python tools/spec.py section F 9.6.4` | Version non conforme et exceptions |

## 7. Critères de sortie du jalon

TST-13 vert ; suites V2 vertes.

## 8. Rappels (extraits d'AGENTS.md)

- Tests d'acceptation d'abord ; `make check` doit passer ; ne jamais affaiblir un test, une contrainte ou un déclencheur.
- Ambiguïté de spécification → question dans `docs/reports/QUESTIONS.md`, jamais d'invention.
- À la fin d'une tranche : mettre à jour `docs/reports/PROGRESS.md`.

