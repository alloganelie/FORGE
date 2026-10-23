# Jalon MS-7 — Approbation, diffusion, versions, cycle de vie

> Brief généré par `tools/gen_briefs.py` — ne pas modifier à la main. Pour tout détail : `python tools/spec.py show <ID>`.

## 1. Objectif

Approbation, diffusion, révocation, révision, suspension, reprise, annulation.

**À savoir.** ET-201 à ET-204 et ET-212 ont été réalisés en MS-4 ; ne pas les refaire.

## 2. Périmètre

- Cas d'usage : UC-015, UC-016, UC-017, UC-018, UC-019, UC-020
- Suites de tests visées : TST-10, TST-11, TST-12
- Hors périmètre de ce jalon : Différences entre versions, exceptions, livrables multiples (V2).

## 3. Exigences techniques à réaliser (23)

- **ET-205** ([F] · MVP) — `SubmitForApproval` exige une version finalisée et une approbation requise par les règles.  
  _Réalise : RF-272, RB-113 · MOD-15_
- **ET-206** ([F] · MVP) — `DecideApproval` est définitive pour la version ; le refus exige un motif.  
  _Réalise : RF-274, RB-125 · MOD-15_
- **ET-207** ([F] · MVP) — Un déclencheur de comparaison garantit que les colonnes de l'axe C ne changent pas lors d'une approbation ou d'une diffusion.  
  _Réalise : RF-273, RF-277, IV-11 · MOD-15_
- **ET-208** ([F] · MVP) — `AuthorizeDiffusion` vérifie AU-4 pour chaque destinataire et enregistre `diffusion_grants` (version, destinataires, périmètre, éléments exclus).  
  _Réalise : RF-180, RF-181 · MOD-15_
- **ET-209** ([F] · MVP) — L'accès à une version diffusée passe par la politique, la sécurité au niveau des lignes et des liens signés ; les éléments exclus sont filtrés.  
  _Réalise : RF-184, RF-278 · MOD-15, MOD-14_
- **ET-210** ([F] · MVP) — La révocation ferme l'accès dans le produit et mentionne que les copies déjà obtenues ne sont pas concernées.  
  _Réalise : RF-279 · MOD-15_
- **ET-213** ([T] · MVP) — Les interrupteurs de configuration de 2.3 existent (`approval.approver_policy`, `delivery.adapters`, `retention.policies`, `request.max_deliverables`, `revision.pin_policy`, `roles.delegation_enabled`).  
  _Réalise : PV-05, PV-27 à PV-35 · MOD-23_
- **ET-214** ([F] · MVP) — Toute décision est journalisée avec décideur, objet, portée et motif.  
  _Réalise : RT-033 · MOD-15_
- **ET-215** ([F] · MVP) — La suspension applique TR-R-19, enregistre `suspended_from` et arrête les opérations de façon coopérative.  
  _Réalise : RF-199 à RF-201 · MOD-04_
- **ET-216** ([F] · MVP) — Un instantané de travail distingue éléments validés et provisoires et conserve cartographie, décisions et empreintes d'entrées.  
  _Réalise : RF-202, RF-203 · MOD-04_
- **ET-217** ([F] · MVP) — La revalidation (A10) est un job qui calcule l'ensemble invalidé et ne replanifie que le nécessaire.  
  _Réalise : RF-206 à RF-208 · MOD-04_
- **ET-218** ([F] · MVP) — `SourcePort.fingerprint` détecte les changements de source depuis la suspension.  
  _Réalise : RF-206 · MOD-06_
- **ET-219** ([F] · MVP) — `resume_target()` est une fonction pure testée pour chaque état d'origine possible.  
  _Réalise : TR-R-20 · MOD-04_
- **ET-220** ([F] · MVP) — La synthèse de reprise (conservé, réexécuté, pourquoi) est produite par gabarit depuis l'ensemble invalidé.  
  _Réalise : RF-209 · MOD-18_
- **ET-221** ([F] · MVP) — La conservation est vérifiée avant toute reprise ; une durée expirée refuse la reprise.  
  _Réalise : RB-087, RB-088 · MOD-04_
- **ET-222** ([F] · MVP) — L'annulation exige deux étapes avec un jeton de confirmation à usage unique.  
  _Réalise : RF-210 · MOD-04_
- **ET-223** ([F] · MVP) — L'annulation fait passer les versions provisoires à « abandonnée » et n'affecte jamais une version finalisée.  
  _Réalise : RF-211, TR-V-03 · MOD-04_
- **ET-224** ([F] · MVP) — La commande `CreateRevisionRequest` crée une demande liée avec épinglage hérité.  
  _Réalise : RF-188, RF-195 · MOD-16_
- **ET-225** ([F] · MVP) — L'analyse d'impact d'une révision propage les changements dans les graphes d'éléments et de contrôles.  
  _Réalise : RF-191 · MOD-16_
- **ET-226** ([T] · MVP) — Les informations et atomes inchangés sont réutilisés par référence, jamais copiés en version modifiable.  
  _Réalise : RF-186, RF-187 · MOD-16_
- **ET-227** ([F] · MVP) — La numérotation de version est séquentielle, sans trou et sans réutilisation.  
  _Réalise : RB-076 · MOD-11_
- **ET-229** ([F] · MVP) — Des tests garantissent qu'un changement de règle n'affecte jamais une demande en cours ni une production antérieure.  
  _Réalise : RF-187, RF-258 · MOD-02_
- **ET-230** ([F] · MVP) — Un test garantit qu'aucune révision n'est déclenchée sans commande explicite (CA-107).  
  _Réalise : RF-190, RB-072 · MOD-16_

## 4. Critères d'acceptation à rendre verts (45)

Écrire d'abord un test par critère, étiqueté de son identifiant (`@pytest.mark.ca("CA-xxx")`).

- **CA-095** (RF-173, RF-176) — **Étant donné** une approbation requise, **quand** elle est accordée, **alors** elle est rattachée à une version précise.
- **CA-096** (RF-177, RB-110) — **Étant donné** une approbation accordée, **quand** on consulte les statuts, **alors** conformité et diffusion sont inchangées.
- **CA-097** (RF-175) — **Étant donné** une demande d'approbation, **quand** l'Agent la présente, **alors** livrable, rapport de conformité, réserves, observations et décisions antérieures sont fournis.
- **CA-098** (RF-178) — **Étant donné** un refus d'approbation, **quand** il est enregistré, **alors** il porte un motif et une révision peut être demandée.
- **CA-099** (RB-113, RF-272) — **Étant donné** une version non finalisée ou non conforme, **quand** l'approbation est demandée, **alors** elle est impossible et l'Agent en explique la raison.
- **CA-100** (RF-179, RB-107) — **Étant donné** une version conforme, **quand** aucune décision humaine n'a été prise, **alors** la diffusion reste non autorisée.
- **CA-101** (RF-180) — **Étant donné** une autorisation de diffusion, **quand** on la consulte, **alors** version, destinataires et périmètre sont précisés.
- **CA-102** (RF-181, RF-184) — **Étant donné** un destinataire non autorisé, **quand** une transmission est demandée, **alors** elle n'a pas lieu.
- **CA-103** (RF-182, RB-058) — **Étant donné** des droits de diffusion incertains, **quand** la diffusion est envisagée, **alors** l'opération est suspendue jusqu'à clarification.
- **CA-104** (RF-183) — **Étant donné** une autorisation de diffusion révoquée, **quand** on consulte l'historique, **alors** la révocation est tracée.
- **CA-105** (RF-188, RB-067) — **Étant donné** une version finalisée, **quand** une révision est demandée, **alors** une nouvelle version est créée et la précédente est intacte.
- **CA-106** (RF-189, RB-071) — **Étant donné** une version approuvée, **quand** une révision est produite, **alors** la version approuvée n'est ni écrasée ni altérée.
- **CA-107** (RF-190, RB-072) — **Étant donné** une information source modifiée, **quand** aucune révision n'est demandée, **alors** aucune nouvelle version n'est créée.
- **CA-108** (RF-191) — **Étant donné** une demande de révision, **quand** l'Agent la prépare, **alors** il présente l'analyse d'impact.
- **CA-109** (RF-192) — **Étant donné** une nouvelle version, **quand** elle est produite, **alors** les contrôles applicables sont rejoués.
- **CA-110** (RF-196, RB-116) — **Étant donné** une nouvelle version, **quand** on consulte ses statuts, **alors** conformité, approbation et diffusion sont remis à zéro.
- **CA-111** (RF-187, RB-069) — **Étant donné** une règle modifiée, **quand** on consulte les livrables antérieurs, **alors** ils sont inchangés.
- **CA-112** (RF-185, RT-031) — **Étant donné** un livrable, **quand** on consulte sa traçabilité, **alors** les versions de sources, règles et modèles de sa création sont retrouvées.
- **CA-113** (RF-193, RF-198) — **Étant donné** une révision, **quand** on consulte l'historique, **alors** motif, auteur et date figurent.
- **CA-115** (RF-199 à RF-201) — **Étant donné** une demande en cours, **quand** l'utilisateur l'interrompt, **alors** les opérations s'arrêtent et la demande est Suspendue.
- **CA-116** (RF-202, RF-203) — **Étant donné** une suspension, **quand** on consulte l'état conservé, **alors** les résultats validés sont distingués des provisoires.
- **CA-117** (RF-204, RB-083) — **Étant donné** une demande Suspendue, **quand** un livrable provisoire existe, **alors** il est marqué non final.
- **CA-118** (RF-205) — **Étant donné** une demande Suspendue, **quand** les règles de conservation le permettent, **alors** l'état de travail est conservé.
- **CA-119** (RB-084, RF-200) — **Étant donné** une interruption à l'initiative de l'utilisateur, **quand** elle est enregistrée, **alors** elle vaut suspension et non annulation.
- **CA-120** (RF-212) — **Étant donné** une demande Suspendue, **quand** l'Agent décrit son statut, **alors** elle n'est jamais présentée comme finalisée.
- **CA-121** (RF-206) — **Étant donné** une reprise, **quand** elle est demandée, **alors** l'Agent vérifie sources, informations, règles et autorisations.
- **CA-122** (RF-207, RF-208) — **Étant donné** une reprise après changement d'une source, **quand** l'Agent poursuit, **alors** les éléments valides sont conservés et les éléments affectés réexécutés avec leurs contrôles.
- **CA-123** (RF-209) — **Étant donné** une reprise, **quand** elle est effectuée, **alors** l'utilisateur est informé de ce qui a changé et de ses conséquences.
- **CA-124** (RB-087, RB-088) — **Étant donné** une durée maximale de conservation fixée par la personne responsable et expirée, **quand** la reprise est demandée, **alors** elle est refusée avec un motif communicable ; sans durée fixée, la demande peut être reprise.
- **CA-125** (RF-210) — **Étant donné** une demande d'annulation définitive, **quand** l'utilisateur ne confirme pas explicitement, **alors** la demande est suspendue et non annulée.
- **CA-126** (RF-211) — **Étant donné** une annulation confirmée, **quand** une reprise est tentée, **alors** elle est impossible, les versions provisoires sont Abandonnées et le travail n'est pas présenté comme livrable.
- **CA-177** (RF-272, RB-113, RB-124) — **Étant donné** une version provisoire non conforme, **quand** l'approbation est demandée, **alors** elle est impossible et le statut de conformité reste Non conforme.
- **CA-178** (RF-273, RB-123) — **Étant donné** une version finalisée conforme, **quand** elle est approuvée ou refusée, **alors** son statut de conformité reste Conforme.
- **CA-179** (RF-274, RB-125) — **Étant donné** une version approuvée, **quand** on tente d'annuler l'approbation, **alors** c'est refusé ; sa remise en cause passe par une révision.
- **CA-180** (RF-275, RB-114) — **Étant donné** une version finalisée dont l'approbation requise est En attente, **quand** la diffusion est demandée, **alors** elle est impossible.
- **CA-181** (RF-275, RB-124) — **Étant donné** une version provisoire ou non conforme, **quand** la diffusion est demandée, **alors** elle est impossible au MVP.
- **CA-182** (RF-276, RB-126) — **Étant donné** une version dont l'approbation est Refusée, **quand** la diffusion est demandée, **alors** elle est impossible.
- **CA-183** (RF-277, RB-123) — **Étant donné** une autorisation de diffusion accordée, révoquée ou modifiée, **quand** on consulte les statuts, **alors** conformité et approbation sont inchangées.
- **CA-184** (RF-275) — **Étant donné** une version finalisée dont l'approbation est Non requise, **quand** la personne responsable autorise la diffusion et que les droits sont vérifiés, **alors** la diffusion est autorisée sans approbation.
- **CA-185** (RF-278, RB-128) — **Étant donné** une diffusion autorisée, **quand** des destinataires accèdent au livrable, **alors** seuls les destinataires désignés y accèdent dans le produit et l'Agent ne transmet rien hors du produit.
- **CA-186** (RF-279) — **Étant donné** une autorisation révoquée, **quand** un destinataire tente d'accéder au livrable, **alors** l'accès est refusé et l'Agent a mentionné que les copies déjà obtenues ne sont pas concernées.
- **CA-187** (RF-210) — **Étant donné** une demande d'annulation définitive, **quand** elle émane d'une personne autre que l'auteur ou la personne responsable, ou porte sur une demande Finalisée, **alors** elle est refusée ; **quand** l'auteur confirme explicitement sur une demande non finalisée, **alors** la demande est Annulée définitivement.
- **CA-188** (RF-211) — **Étant donné** l'annulation d'une demande de révision liée, **quand** elle est confirmée, **alors** la demande d'origine et ses versions finalisées restent inchangées.
- **CA-191** (RF-195) — **Étant donné** une révision, **quand** elle démarre, **alors** les versions d'origine de modèle, de règles et de registre sont utilisées ; des versions plus récentes ne le sont que sur décision explicite et tracée de la personne responsable.
- **CA-193** (RB-087, RT-061) — **Étant donné** qu'aucune durée de conservation n'est fixée, **quand** une demande reste suspendue, **alors** elle n'est ni supprimée ni périmée automatiquement.

## 5. Exigences fonctionnelles liées (70) — une ligne chacune

Résumés seulement. Pour le texte complet et le contexte : `python tools/spec.py show RF-xxx`.

- IV-11 — L'approbation et la diffusion ne modifient jamais l'état de l'axe C ; seule l'exécution des contrôles le modifie.
- RB-058 — Si les droits applicables sont incertains, l'Agent suspend l'opération concernée jusqu'à clarification.
- RB-067 — Les livrables existants sont immuables.
- RB-069 — Une modification des règles ne modifie pas automatiquement les productions antérieures.
- RB-071 — Une version déjà approuvée n'est jamais écrasée silencieusement.
- RB-072 — Une révision est explicitement déclenchée ; elle n'est jamais automatique.
- RB-076 — La numérotation des versions est séquentielle, sans trou et sans réutilisation.
- RB-083 — Une demande suspendue n'est pas un livrable finalisé.
- RB-084 — Une interruption à l'initiative de l'utilisateur entraîne une suspension.
- RB-087 — Au MVP, aucune péremption automatique d'une suspension ; une durée maximale ne s'applique que si la personne responsable l'a fixée dans les règles de conservation.
- RB-088 — Lorsqu'une durée de conservation fixée est expirée, les éléments non conservables sont supprimés ou anonymisés selon les règles ; la demande ne peut plus reprendre.
- RB-107 — L'Agent n'attribue jamais à la place d'un humain un statut d'approbation, de diffusion ou d'arbitrage.
- RB-110 — Aucun de ces statuts n'est déduit automatiquement des deux autres.
- RB-113 — L'approbation ne peut porter que sur une version **finalisée**, donc conforme. Une version non conforme ne peut pas être approuvée.
- RB-114 — L'autorisation de diffusion ne peut porter que sur une version finalisée (donc conforme) dont l'approbation est « Approuvée » ou « Non requise ». La diffusion d'une ve...
- RB-116 — Une nouvelle version démarre avec des statuts remis à zéro.
- RB-123 — L'approbation et la diffusion ne modifient jamais le statut de conformité : seule l'exécution des contrôles le modifie.
- RB-124 — Une version non conforme n'a pas d'autre issue que la correction, le complément de production ou la révision ; elle ne peut être ni approuvée ni diffusée au MVP.
- RB-125 — L'approbation, comme le refus, est définitive pour sa version.
- RB-126 — Une version dont l'approbation est refusée ou en attente ne peut pas être diffusée.
- RB-128 — Au MVP, la diffusion consiste à rendre le livrable accessible dans le produit ; l'Agent ne transmet aucun livrable hors du produit.
- RF-173 — L'Agent doit gérer l'approbation humaine comme un statut distinct, lorsque les règles du type de livrable l'exigent.
- RF-175 — L'Agent doit présenter à l'approbateur le livrable, le rapport de conformité, les réserves, les observations et les décisions antérieures.
- RF-176 — Une approbation porte sur une version précise du livrable, **finalisée et conforme**.
- RF-177 — Une approbation ne vaut pas conformité et ne confère pas autorisation de diffuser.
- RF-178 — Un refus d'approbation doit être motivé et peut déclencher une révision.
- RF-179 — L'autorisation de diffusion est un statut distinct, relevant des décisions de livraison réservées à la personne responsable.
- RF-180 — L'autorisation de diffusion doit préciser la version, les destinataires ou catégories de destinataires, le périmètre et les éléments exclus.
- RF-181 — Avant toute diffusion, l'Agent doit vérifier que les restrictions de confidentialité et de diffusion sont respectées pour chaque destinataire.
- RF-182 — En cas de droits de diffusion incertains, l'Agent doit suspendre l'opération concernée jusqu'à clarification.
- RF-183 — Une autorisation de diffusion peut être révoquée ; la révocation est tracée.
- RF-184 — L'Agent ne rend un livrable accessible à un destinataire autre que le demandeur que si la diffusion est autorisée pour ce destinataire.
- RF-185 — Chaque production doit rester liée aux sources, règles et modèles utilisés au moment de sa création.
- RF-186 — Les livrables existants sont immuables.
- RF-187 — Une modification des règles ne doit pas modifier automatiquement les productions antérieures.
- RF-188 — Toute révision demandée doit donner lieu à une nouvelle version.
- RF-189 — Une version déjà approuvée ne doit jamais être écrasée silencieusement.
- RF-190 — Une révision doit être explicitement déclenchée ; l'Agent ne révise jamais un livrable de sa propre initiative.
- RF-191 — Avant une révision, l'Agent doit réaliser une analyse des impacts : éléments concernés, contrôles à rejouer, livrables liés.
- RF-192 — La nouvelle version doit faire rejouer les contrôles applicables.
- RF-193 — L'Agent doit conserver l'historique : versions, motifs de révision, auteurs, dates.
- RF-195 — Lors d'une révision, l'Agent doit utiliser par défaut les versions de modèle, de règles et de registre d'origine ; des versions plus récentes ne sont utilisées que sur...
- RF-196 — Les statuts de conformité, d'approbation et de diffusion sont propres à chaque version ; une nouvelle version ne les hérite pas.
- RF-198 — L'Agent doit enregistrer le motif de la révision (correction d'erreur, nouvelle information, changement de règle, demande de l'utilisateur).
- RF-199 — L'Agent doit pouvoir suspendre une demande à l'initiative de l'utilisateur.
- RF-200 — Une demande interrompue à l'initiative de l'utilisateur est suspendue, pour permettre une reprise ultérieure, sous réserve des règles de conservation.
- RF-201 — À la suspension, l'Agent doit arrêter les opérations.
- RF-202 — À la suspension, l'Agent doit préserver les éléments autorisés.
- RF-203 — À la suspension, l'Agent doit distinguer les résultats validés des résultats provisoires.
- RF-204 — L'Agent ne doit pas présenter un travail inachevé comme un livrable final.
- RF-205 — Une demande suspendue conserve son état de travail dans les limites des règles de conservation et des autorisations applicables.
- RF-206 — À la reprise, l'Agent doit vérifier la validité des sources, informations, règles et autorisations susceptibles d'avoir changé.
- RF-207 — À la reprise, l'Agent doit conserver les éléments toujours valides.
- RF-208 — À la reprise, l'Agent doit réexécuter les opérations affectées et les contrôles nécessaires.
- RF-209 — À la reprise, l'Agent doit informer l'utilisateur de ce qui a changé depuis la suspension et de ses conséquences.
- RF-210 — L'annulation définitive doit être distincte de la suspension. Au MVP, elle exige une action explicite et une confirmation explicite, peut être demandée par l'auteur de...
- RF-211 — Après une annulation définitive, la demande ne peut plus être reprise ; une nouvelle demande est nécessaire. Les versions provisoires deviennent « Abandonnées » ; le t...
- RF-212 — Une demande suspendue ne constitue pas un livrable finalisé.
- RF-258 — Une modification de règle ou de modèle n'affecte automatiquement ni les productions antérieures ni les demandes en cours.
- RF-272 — L'Agent ne soumet une version à l'approbation que si elle est finalisée. Une version non finalisée ou non conforme ne peut être ni soumise à l'approbation ni approuvée...
- RF-273 — Une décision d'approbation ou de refus ne modifie jamais le statut de conformité : une version Conforme reste Conforme, et aucune approbation ne peut rendre conforme u...
- RF-274 — Une approbation, comme un refus, est définitive pour sa version. Sa remise en cause passe par une révision (nouvelle version) et, pour la circulation du livrable, par ...
- RF-275 — L'Agent n'enregistre une autorisation de diffusion que pour une version finalisée dont le statut d'approbation est « Approuvée » ou « Non requise ». La diffusion d'une...
- RF-276 — Une version dont l'approbation est « En attente » ou « Refusée » ne peut pas être diffusée.
- RF-277 — Une autorisation de diffusion, sa révocation ou sa modification ne modifient jamais le statut de conformité ni le statut d'approbation de la version.
- RF-278 — Au MVP, « diffuser » signifie rendre le livrable accessible, dans le produit, aux destinataires désignés et autorisés. L'Agent ne transmet aucun livrable hors du produ...
- RF-279 — La révocation d'une autorisation de diffusion met fin à l'accessibilité du livrable dans le produit pour les destinataires concernés. Elle ne s'étend pas aux copies ob...
- RT-031 — Les versions du modèle, des règles, du registre des sources et du catalogue de contrôles utilisées sont enregistrées.
- RT-033 — Chaque décision humaine est enregistrée avec son décideur.
- RT-061 — Au MVP, aucune suppression automatique : l'historique et les états suspendus sont conservés jusqu'à décision explicite de la personne responsable, qui peut fixer des r...

## 6. À lire à la demande (ne rien lire d'autre au départ)

| Quoi | Commande | Pourquoi |
|---|---|---|
| Spéc. fonctionnelle 9.6 | `python tools/spec.py section F 9.6` | Approbation et diffusion : possibilités, conditions, effets |
| Spéc. technique 10.12 | `python tools/spec.py section T 10.12` | É11 (approbation, diffusion) |
| Spéc. technique 10.13 | `python tools/spec.py section T 10.13` | Suspension, reprise (A10), révision, annulation |
| Spéc. technique 7.4 | `python tools/spec.py section T 7.4` | Application d'une transition |
| Spéc. fonctionnelle UC-015 | `python tools/spec.py section F UC-015` | Fiche du cas d’usage |
| Spéc. fonctionnelle UC-016 | `python tools/spec.py section F UC-016` | Fiche du cas d’usage |
| Spéc. fonctionnelle UC-017 | `python tools/spec.py section F UC-017` | Fiche du cas d’usage |
| Spéc. fonctionnelle UC-018 | `python tools/spec.py section F UC-018` | Fiche du cas d’usage |
| Spéc. fonctionnelle UC-019 | `python tools/spec.py section F UC-019` | Fiche du cas d’usage |
| Spéc. fonctionnelle UC-020 | `python tools/spec.py section F UC-020` | Fiche du cas d’usage |

## 7. Critères de sortie du jalon

TST-10, TST-11 et TST-12 verts ; tests de reprise après crash ; l'approbation et la diffusion ne modifient jamais la conformité.

## 8. Rappels (extraits d'AGENTS.md)

- Tests d'acceptation d'abord ; `make check` doit passer ; ne jamais affaiblir un test, une contrainte ou un déclencheur.
- Ambiguïté de spécification → question dans `docs/reports/QUESTIONS.md`, jamais d'invention.
- À la fin d'une tranche : mettre à jour `docs/reports/PROGRESS.md`.

