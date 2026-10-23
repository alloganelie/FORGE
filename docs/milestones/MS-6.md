# Jalon MS-6 — Contrôles, finalisation, rapports, scellement

> Brief généré par `tools/gen_briefs.py` — ne pas modifier à la main. Pour tout détail : `python tools/spec.py show <ID>`.

## 1. Objectif

Catalogue de contrôles, anomalies et corrections mécaniques, finalisation atomique, rapports de conformité et de traçabilité, export de provenance, scellement.

**À savoir.** La finalisation est atomique (ET-195) : tout ou rien.

## 2. Périmètre

- Cas d'usage : UC-012, UC-013, UC-014, UC-030
- Suites de tests visées : TST-08, TST-09, TST-17
- Hors périmètre de ce jalon : Approbation, diffusion, révision, suspension.
- 1 exigence(s) V2 comprises dans les plages sont **reportées à MS-9** (non listées ci-dessous).

## 3. Exigences techniques à réaliser (37)

- **ET-163** ([F] · MVP) — Un contrôle est une classe pure `Control.run(snapshot) → ControlResult` à quatre issues.  
  _Réalise : RF-142 · MOD-12_
- **ET-164** ([F] · MVP) — Le catalogue CT-01 à CT-16 est implémenté selon 10.10.  
  _Réalise : RF-128 à RF-139 · MOD-12_
- **ET-165** ([F] · MVP) — Les contrôles sont ordonnés par dépendances ; un préalable en échec rend les dépendants « non exécutables ».  
  _Réalise : RT-054 · MOD-12_
- **ET-166** ([F] · MVP) — `decide_conformity` est une fonction pure ; seul « réussi » ou « non applicable » justifié satisfait un contrôle obligatoire.  
  _Réalise : RF-141, RB-054 · MOD-12_
- **ET-167** ([F] · MVP) — Les résultats sont ajoutés, jamais modifiés ; l'historique des rejeux est conservé.  
  _Réalise : RT-057 · MOD-12_
- **ET-168** ([F] · MVP) — Un graphe contrôle → éléments permet le rejeu incrémental ; les contrôles transversaux sont toujours rejoués.  
  _Réalise : RT-056 · MOD-12_
- **ET-169** ([F] · MVP) — Un contrôle ne modifie jamais le contenu qu'il contrôle.  
  _Réalise : RT-058 · MOD-12_
- **ET-170** ([F] · MVP) — CT-12 utilise les matrices déclarées par le lot et LT-09 ; les seuils sont appliqués par le code ; aucune correction n'est proposée.  
  _Réalise : RF-139, RF-140 · MOD-12_
- **ET-171** ([F] · MVP) — CT-13 recalcule les empreintes des atomes et les rapproche des sources.  
  _Réalise : RF-123, RT-069 · MOD-12_
- **ET-172** ([F] · MVP) — Chaque contrôle déclare la classe d'anomalie (AN-1 à AN-3) de chacun de ses échecs.  
  _Réalise : RF-143 · MOD-13_
- **ET-173** ([F] · MVP) — Le registre d'autocorrections exige une postcondition vérifiable ; sans elle, aucune correction.  
  _Réalise : RF-145, AF-03 · MOD-13_
- **ET-174** ([F] · MVP) — La boucle de correction est bornée (3 itérations par défaut, paramétrable) ; au-delà, escalade vers la personne responsable.  
  _Réalise : RF-153 · MOD-13_
- **ET-175** ([F] · MVP) — Les corrections écrivent avant et après et déclenchent le rejeu des contrôles concernés.  
  _Réalise : RF-146, RF-147 · MOD-13_
- **ET-176** ([F] · MVP) — Une correction non couverte suspend l'opération et crée une demande de décision.  
  _Réalise : RF-148 · MOD-13_
- **ET-177** ([F] · MVP) — Les observations sont consignées sans aucune modification du livrable.  
  _Réalise : RF-149, RF-150 · MOD-13_
- **ET-178** ([F] · MVP) — Un test garantit qu'un résultat « non exécutable » n'est jamais agrégé comme « réussi ».  
  _Réalise : RB-054 · MOD-12_
- **ET-179** ([F] · MVP) — Les contrôles obligatoires proviennent du modèle et du lot ; aucun code ne peut en retirer.  
  _Réalise : RT-053 · MOD-12_
- **ET-180** ([F] · MVP) — Le catalogue est versionné ; sa version est enregistrée pour chaque exécution.  
  _Réalise : RT-060 · MOD-12_
- **ET-181** ([T] · MVP) — Un résumé des contrôles est produit pour l'utilisateur par gabarit communicable.  
  _Réalise : RF-142 · MOD-12_
- **ET-182** ([T] · MVP) — Les segments « de type instruction » détectés dans les sources créent une observation (AN-3) liée à la source.  
  _Réalise : IP-06 · MOD-13_
- **ET-183** ([F] · MVP) — La provenance est modélisée en tables ; des requêtes de remontée et de descente existent.  
  _Réalise : RT-037 · ADR-020_
- **ET-184** ([T] · MVP) — L'export W3C PROV-JSON est disponible par version.  
  _Réalise : RT-027 à RT-042 · ADR-020_
- **ET-185** ([F] · MVP) — Le rapport de conformité est un document canonique JSON, rendu en Word, PDF, HTML ou Markdown.  
  _Réalise : RF-158, RT-043 · MOD-14_
- **ET-186** ([F] · MVP) — Le rapport de traçabilité est un document canonique JSON, rendu de même ; il n'est pas une simple bibliographie.  
  _Réalise : RF-159, RF-160 · MOD-14_
- **ET-187** ([F] · MVP) — Les sources non communicables sont rédigées de façon générique dans les rapports selon les droits du lecteur.  
  _Réalise : RF-270 · MOD-14_
- **ET-188** ([F] · MVP) — Le rapport de traçabilité porte sa propre classification, éventuellement plus stricte que celle du livrable.  
  _Réalise : RT-011 · MOD-14_
- **ET-189** ([T] · MVP) — Le scellement calcule les feuilles et la racine de Merkle comme en 12.6.  
  _Réalise : RF-166, RT-062 · ADR-022_
- **ET-190** ([T] · MVP) — La signature Ed25519 est demandée à un service de gestion de clés ; l'application ne détient pas la clé privée.  
  _Réalise : SL-01 · ADR-022_
- **ET-191** ([T] · MVP) — Les clés publiques, leurs identifiants et leurs dates de validité sont conservés.  
  _Réalise : SL-02 · ADR-022_
- **ET-192** ([T] · MVP) — Un point d'accès et un outil en ligne de commande vérifient un sceau, y compris hors ligne à partir d'un export.  
  _Réalise : SL-03 · ADR-022_
- **ET-193** ([T] · MVP) — La rotation de clés est planifiée (annuelle) sans rendre un ancien sceau invérifiable.  
  _Réalise : SL-02 · ADR-022_
- **ET-194** ([T] · MVP) — La chaîne du journal et un échantillon de sceaux sont vérifiés chaque jour.  
  _Réalise : SL-04, RT-065 · MOD-19_
- **ET-195** ([F] · MVP) — La finalisation est atomique : rapports, sceau, états et événements dans une seule transaction ; pas de finalisation partielle.  
  _Réalise : RF-155 à RF-167 · MOD-14_
- **ET-196** ([F] · MVP) — Les objets de la version finalisée sont verrouillés à la finalisation.  
  _Réalise : RF-166 · ADR-010_
- **ET-198** ([T] · MVP) — Les consultations de rapports sont journalisées (qui, quoi, quand).  
  _Réalise : RT-012 · MOD-14_
- **ET-199** ([F] · MVP) — Un outil de rejeu en lecture reconstitue chronologiquement une demande à partir du journal.  
  _Réalise : RT-036 · MOD-19_
- **ET-200** ([T] · MVP) — Des fichiers de référence (« golden ») protègent les formats de rapports contre les régressions.  
  _Réalise : — · ADR-017_

## 4. Critères d'acceptation à rendre verts (33)

Écrire d'abord un test par critère, étiqueté de son identifiant (`@pytest.mark.ca("CA-xxx")`).

- **CA-071** (RF-127, RF-141) — **Étant donné** un contrôle obligatoire échoué, **quand** l'Agent évalue la conformité, **alors** le livrable n'est pas déclaré conforme.
- **CA-072** (RF-129 à RF-138) — **Étant donné** un livrable produit, **quand** les contrôles s'exécutent, **alors** chaque contrôle du catalogue applicable (CT-01 à CT-11) est exécuté.
- **CA-073** (RF-139, RF-140) — **Étant donné** des règles méthodologiques explicites, **quand** une incohérence est détectée, **alors** elle est signalée et aucun choix méthodologique n'est modifié.
- **CA-074** (RF-142, RT-059) — **Étant donné** un contrôle, **quand** il est enregistré, **alors** résultat, éléments examinés, règle et date figurent, et aucun contrôle non exécuté n'est marqué réussi.
- **CA-075** (RB-054, RT-054) — **Étant donné** un contrôle dont une donnée préalable manque, **quand** il est évalué, **alors** son résultat est « non exécutable » et non « réussi ».
- **CA-076** (RF-141, RB-112) — **Étant donné** tous les contrôles obligatoires réussis, **quand** l'Agent conclut, **alors** la version peut être déclarée conforme.
- **CA-077** (RF-143, RF-144) — **Étant donné** une anomalie, **quand** l'Agent la traite, **alors** elle est classée et, si avérée, rattachée à une règle explicite.
- **CA-078** (RF-145 à RF-147) — **Étant donné** une règle autorisant la correction d'un défaut mécanique, **quand** le défaut est détecté, **alors** il est corrigé, tracé (avant, après, règle, date) et les contrôles concernés sont rejoués.
- **CA-079** (RF-145, RB-049) — **Étant donné** un défaut mécanique sans règle de correction, **quand** il est détecté, **alors** il n'est pas corrigé automatiquement.
- **CA-080** (RF-148) — **Étant donné** une correction exigeant une interprétation, **quand** l'Agent y est conduit, **alors** il suspend l'opération concernée et sollicite la personne habilitée.
- **CA-081** (RF-149, RF-150) — **Étant donné** une observation, **quand** elle est consignée, **alors** le livrable est inchangé.
- **CA-082** (RF-151) — **Étant donné** des observations, **quand** le rapport de conformité est produit, **alors** elles y figurent.
- **CA-083** (RF-153) — **Étant donné** des cycles de correction non convergents, **quand** la borne est atteinte, **alors** l'Agent escalade à la personne responsable.
- **CA-084** (RF-154) — **Étant donné** une correction, **quand** on consulte l'historique, **alors** les résultats de contrôle antérieurs sont conservés.
- **CA-085** (RF-155, RF-163) — **Étant donné** des contrôles obligatoires non tous réussis, **quand** l'utilisateur s'enquiert du résultat, **alors** l'Agent n'annonce ni finalisation ni conformité.
- **CA-086** (RF-156 à RF-159) — **Étant donné** des règles exigeant les trois éléments, **quand** la version est finalisée, **alors** livrable, rapport de conformité et rapport de traçabilité sont remis.
- **CA-087** (RF-160, RT-039) — **Étant donné** le rapport de traçabilité, **quand** on le lit, **alors** il présente la chaîne complète pour chaque élément significatif et non une simple bibliographie.
- **CA-088** (RF-161, RF-162) — **Étant donné** une version conforme et finalisée, **quand** l'Agent présente le statut, **alors** l'approbation et la diffusion sont présentées comme non accordées, non déduites.
- **CA-089** (RF-164, RF-172) — **Étant donné** une remise, **quand** elle est présentée, **alors** elle indique le statut, les réserves et les actions restantes.
- **CA-090** (RF-166, RB-067) — **Étant donné** une version finalisée, **quand** une modification est tentée, **alors** elle est refusée et une nouvelle version est nécessaire.
- **CA-091** (RF-167) — **Étant donné** les trois éléments remis, **quand** on les consulte, **alors** chacun renvoie à la même version précise et aux versions de modèle et de règles.
- **CA-092** (RF-168) — **Étant donné** un type de livrable n'exigeant pas le rapport de traçabilité, **quand** la remise est faite, **alors** le rapport de conformité le mentionne avec la règle concernée.
- **CA-093** (RF-169, RF-170) — **Étant donné** des informations qualifiées, des exceptions ou des décisions humaines, **quand** le rapport de conformité est produit, **alors** ils y sont mentionnés.
- **CA-094** (RF-165, RT-011) — **Étant donné** un destinataire de la remise sans droit sur certains éléments, **quand** la remise est faite, **alors** ces éléments en sont exclus.
- **CA-141** (RF-237, RB-109) — **Étant donné** un livrable finalisé, **quand** son statut est présenté, **alors** conformité, approbation et diffusion apparaissent séparément.
- **CA-169** (RT-027, RT-037) — **Étant donné** un élément significatif d'un livrable finalisé, **quand** on remonte sa chaîne, **alors** on retrouve source, référence, statut de validation et transformations.
- **CA-170** (RT-035, RT-036) — **Étant donné** une demande terminée, **quand** on consulte son historique, **alors** chaque changement d'état est horodaté avec son auteur et son motif et l'ensemble se reconstitue chronologiquement.
- **CA-171** (RT-062, RT-063, RF-271) — **Étant donné** une entrée d'historique, **quand** un utilisateur tente de la modifier ou de la supprimer, **alors** c'est refusé ; une correction s'ajoute comme entrée complémentaire.
- **CA-172** (RT-031, RT-034) — **Étant donné** un livrable, **quand** on consulte sa traçabilité, **alors** les versions de règles, de modèle, de registre et de contrôles et tous les résultats de contrôle (rejeux inclus) y figurent.
- **CA-173** (RF-268, RF-270) — **Étant donné** un lecteur sans droit sur une source, **quand** il consulte la traçabilité, **alors** il voit une mention générique à la place de la source.
- **CA-174** (RT-040, RT-041) — **Étant donné** des informations exclues, masquées ou candidates non retenues, **quand** on consulte la traçabilité, **alors** leur existence et leur motif général y figurent.
- **CA-175** (RT-064, RT-066) — **Étant donné** une suppression en fin de conservation, **quand** elle a lieu, **alors** une trace minimale (existence, date, motif général) subsiste.
- **CA-176** (RT-065) — **Étant donné** un livrable finalisé, **quand** une personne autorisée à consulter la traçabilité (l'auteur de la demande ou la personne responsable) l'examine, **alors** elle peut reconstituer pourquoi il est tel qu'il est (règles, sources, décisions, contrôles).

## 5. Exigences fonctionnelles liées (86) — une ligne chacune

Résumés seulement. Pour le texte complet et le contexte : `python tools/spec.py show RF-xxx`.

- RB-049 — Un défaut mécanique n'est corrigé automatiquement que si une règle l'autorise explicitement.
- RB-054 — Un contrôle non exécutable n'est pas un contrôle réussi.
- RB-067 — Les livrables existants sont immuables.
- RB-109 — Conformité aux contrôles, approbation humaine et autorisation de diffuser sont trois statuts distincts.
- RB-112 — La conformité exige la réussite de tous les contrôles obligatoires.
- RF-123 — L'Agent ne doit inclure aucun contenu qui ne se rattache ni à une information source, ni à un modèle, ni à une règle.
- RF-127 — Avant toute finalisation, l'Agent doit exécuter l'ensemble des contrôles obligatoires.
- RF-128 — Les contrôles obligatoires proviennent du modèle et des règles du type de livrable ; le catalogue minimal est donné en Annexe B (CT-01 à CT-12).
- RF-129 — L'Agent doit contrôler la présence des sections et champs obligatoires (CT-01).
- RF-130 — L'Agent doit contrôler l'utilisation du bon modèle et de la bonne version (CT-02).
- RF-131 — L'Agent doit contrôler la conformité des informations intégrées (CT-03).
- RF-132 — L'Agent doit contrôler la résolution des contradictions bloquantes (CT-04).
- RF-133 — L'Agent doit contrôler la validité des sources et des autorisations (CT-05).
- RF-134 — L'Agent doit contrôler la conformité des transformations éditoriales (CT-06).
- RF-135 — L'Agent doit contrôler la reproductibilité des calculs autorisés (CT-07).
- RF-136 — L'Agent doit contrôler la cohérence interne du document et la cohérence entre ses éléments (CT-08, CT-09).
- RF-137 — L'Agent doit contrôler la présence des références et traces exigées (CT-10).
- RF-138 — L'Agent doit contrôler le respect des restrictions de confidentialité et de diffusion (CT-11).
- RF-139 — Lorsque des règles explicites les définissent, l'Agent doit exécuter les contrôles méthodologiques de cohérence entre objectifs, questions, méthodes, variables, indica...
- RF-140 — L'Agent ne doit pas inventer ni modifier des choix méthodologiques pour rendre le document artificiellement cohérent.
- RF-141 — Tous les contrôles obligatoires doivent réussir avant que le livrable puisse être déclaré conforme.
- RF-142 — Chaque contrôle doit produire un résultat (réussi, échoué, non exécutable, non applicable), les éléments examinés, la règle appliquée et la date.
- RF-143 — L'Agent doit classer chaque anomalie : non-conformité avérée, incohérence établie, ou observation nécessitant une appréciation humaine.
- RF-144 — Une non-conformité avérée doit se rapporter à une règle explicite identifiée.
- RF-145 — L'Agent ne peut corriger automatiquement un défaut mécanique que si une règle l'autorise explicitement.
- RF-146 — Chaque correction automatique doit être tracée : état avant, état après, règle, date.
- RF-147 — Après une correction, l'Agent doit rejouer les contrôles concernés.
- RF-148 — Si la correction exige une interprétation ou une décision non autorisée, l'Agent doit suspendre l'opération concernée et solliciter la personne habilitée.
- RF-149 — L'Agent doit consigner comme observations les anomalies non couvertes par les règles.
- RF-150 — Une observation ne doit pas justifier, à elle seule, une modification du livrable.
- RF-151 — Les observations doivent figurer dans le rapport de conformité et être mises à disposition de la personne responsable.
- RF-153 — Le nombre de cycles correction puis contrôle doit être borné ; au-delà, l'Agent escalade à la personne responsable.
- RF-154 — Une correction ne doit jamais modifier le sens d'une information, ni effacer un résultat de contrôle antérieur : l'historique des résultats est conservé.
- RF-155 — La finalisation ne peut intervenir qu'après la réussite de tous les contrôles obligatoires.
- RF-156 — L'Agent doit produire trois éléments distincts lorsque les règles du livrable l'exigent : le livrable, le rapport de conformité, le rapport de traçabilité.
- RF-157 — Le livrable est le document final destiné à son public, avec les citations et références nécessaires à sa compréhension et à sa vérification.
- RF-158 — Le rapport de conformité doit présenter les contrôles effectués, leurs résultats, les éventuelles réserves et les conditions qui restent à satisfaire.
- RF-159 — Le rapport de traçabilité doit permettre de retrouver, pour chaque élément significatif, les sources, les références, le statut de validation, les transformations, les...
- RF-160 — Le rapport de traçabilité ne doit pas être réduit à une bibliographie.
- RF-161 — L'Agent doit distinguer explicitement la conformité aux contrôles, l'approbation humaine éventuelle et l'autorisation de diffuser.
- RF-162 — Aucun de ces trois statuts ne doit être déduit automatiquement des deux autres.
- RF-163 — L'Agent ne doit jamais annoncer qu'un livrable est final, conforme, approuvé ou diffusable avant que les contrôles ou validations correspondants aient effectivement ab...
- RF-164 — La remise doit présenter le statut de la production, les réserves éventuelles et les actions restant à effectuer.
- RF-165 — La remise doit se limiter aux éléments que le destinataire de la remise est autorisé à recevoir (le rapport de traçabilité peut contenir des informations protégées).
- RF-166 — Une version finalisée devient immuable.
- RF-167 — Les trois éléments doivent être liés entre eux, à la version précise du livrable et aux versions de modèle et de règles utilisées.
- RF-168 — Si les règles d'un type de livrable n'exigent pas certains éléments, l'Agent doit le consigner dans le rapport de conformité en citant la règle concernée.
- RF-169 — Le rapport de conformité doit mentionner explicitement les informations qualifiées (non QI-01) intégrées et toutes les réserves.
- RF-170 — Le rapport de conformité doit mentionner les décisions humaines prises, les exceptions autorisées et les observations.
- RF-172 — La remise doit indiquer les prochaines actions possibles (approbation, diffusion, révision).
- RF-237 — Les statuts de conformité, d'approbation et de diffusion doivent toujours être présentés séparément.
- RF-268 — Selon ses droits, un utilisateur ou la personne responsable doit pouvoir retrouver, pour tout élément significatif, la chaîne source, information, transformations ou c...
- RF-270 — Les consultations de traçabilité sont soumises aux restrictions de confidentialité : un lecteur sans droit sur une source voit une mention générique.
- RF-271 — L'historique de production ne peut être modifié ni supprimé par un utilisateur ; toute correction s'ajoute sous forme d'entrée complémentaire.
- RT-011 — Le rapport de traçabilité a sa propre classification et peut être plus restrictif que le livrable.
- RT-012 — Les journaux d'historique sont soumis aux mêmes restrictions d'accès que les objets qu'ils décrivent.
- RT-027 — Toute information significative d'un livrable doit être reliée à sa source, sa référence précise, son statut de validation et ses transformations.
- RT-028 — Au MVP, sont significatifs tout contenu factuel, chiffre, référence, calcul et décision, ainsi que tout élément que le modèle qualifie de significatif.
- RT-029 — Pour chaque calcul : données d'entrée, sources, méthode, unités, conventions, arrondi, résultat.
- RT-030 — Pour chaque transformation : opération, règle autorisante, état avant, état après.
- RT-031 — Les versions du modèle, des règles, du registre des sources et du catalogue de contrôles utilisées sont enregistrées.
- RT-032 — Chaque autorisation pertinente (permanente, ponctuelle, exception) est enregistrée.
- RT-033 — Chaque décision humaine est enregistrée avec son décideur.
- RT-034 — Chaque contrôle et chacun de ses résultats est enregistré, y compris lors des rejeux.
- RT-035 — Chaque changement d'état (demande, conformité, approbation, diffusion, version) est horodaté, avec son auteur (humain ou Agent) et son motif.
- RT-036 — L'historique permet de reconstituer chronologiquement ce qui s'est passé pour une demande.
- RT-037 — La traçabilité est navigable du livrable vers les sources, et des sources vers les éléments qui les utilisent.
- RT-038 — Les liens de traçabilité sont stables dans le temps.
- RT-039 — La traçabilité n'est pas une simple bibliographie.
- RT-040 — La traçabilité mentionne aussi ce qui a été exclu ou masqué (existence de l'exclusion et motif général).
- RT-041 — Les informations candidates non retenues sont consignées avec leur motif.
- RT-042 — La traçabilité est complète avant finalisation (contrôle CT-10).
- RT-043 — Le rapport de conformité doit être complet (contenu minimal en Annexe D).
- RT-053 — Les contrôles obligatoires sont définis par les modèles et règles ; l'Agent ne peut en retirer.
- RT-054 — Les contrôles respectent leurs dépendances : si un préalable échoue, les contrôles dépendants sont « non exécutables ».
- RT-056 — Après correction ou reprise, les contrôles rejoués couvrent au minimum les éléments affectés et les contrôles transversaux.
- RT-057 — Les résultats de toutes les exécutions de contrôle sont conservés, pas seulement la dernière.
- RT-058 — Un contrôle ne modifie jamais le contenu qu'il contrôle : contrôler et corriger sont deux opérations distinctes.
- RT-059 — L'Agent ne peut marquer « réussi » un contrôle qu'il n'a pas exécuté.
- RT-060 — Le catalogue de contrôles est versionné ; la version utilisée est enregistrée pour chaque production.
- RT-062 — L'historique de production est immuable : aucune entrée n'est modifiée ou supprimée par un utilisateur.
- RT-063 — Rien n'est écrasé silencieusement.
- RT-064 — La suppression en fin de conservation laisse une trace minimale (existence, date, motif général).
- RT-065 — Un audit doit pouvoir reconstituer pourquoi un livrable est ce qu'il est : règles, sources, décisions, contrôles.
- RT-066 — Les demandes suspendues ou annulées suivent les règles de conservation.
- RT-069 — Aucun contenu n'est généré sans rattachement à une source, un modèle ou une règle.

## 6. À lire à la demande (ne rien lire d'autre au départ)

| Quoi | Commande | Pourquoi |
|---|---|---|
| Spéc. technique 10.10 | `python tools/spec.py section T 10.10` | É9 Contrôles (catalogue CT) |
| Spéc. technique 10.11 | `python tools/spec.py section T 10.11` | É10 Anomalies |
| Spéc. technique 10.12 | `python tools/spec.py section T 10.12` | É11 Finalisation |
| Spéc. technique 12.4 | `python tools/spec.py section T 12.4` | Rapport de conformité |
| Spéc. technique 12.5 | `python tools/spec.py section T 12.5` | Rapport de traçabilité et PROV |
| Spéc. technique 12.6 | `python tools/spec.py section T 12.6` | Scellement |
| Spéc. technique 11.4 | `python tools/spec.py section T 11.4` | Tâche LT-09 |
| Spéc. fonctionnelle Annexe-B | `python tools/spec.py section F Annexe-B` | Catalogue de contrôles |
| Spéc. fonctionnelle Annexe-D | `python tools/spec.py section F Annexe-D` | Contenu des rapports |
| Spéc. fonctionnelle 9.4 | `python tools/spec.py section F 9.4` | Conditions de finalisation FN-01 à FN-10 |
| Spéc. fonctionnelle UC-012 | `python tools/spec.py section F UC-012` | Fiche du cas d’usage |
| Spéc. fonctionnelle UC-013 | `python tools/spec.py section F UC-013` | Fiche du cas d’usage |
| Spéc. fonctionnelle UC-014 | `python tools/spec.py section F UC-014` | Fiche du cas d’usage |
| Spéc. fonctionnelle UC-030 | `python tools/spec.py section F UC-030` | Fiche du cas d’usage |

## 7. Critères de sortie du jalon

TST-08, TST-09 et TST-17 verts ; sceau vérifiable hors ligne ; chaîne et sceaux vérifiés ; aucune finalisation partielle.

## 8. Rappels (extraits d'AGENTS.md)

- Tests d'acceptation d'abord ; `make check` doit passer ; ne jamais affaiblir un test, une contrainte ou un déclencheur.
- Ambiguïté de spécification → question dans `docs/reports/QUESTIONS.md`, jamais d'invention.
- À la fin d'une tranche : mettre à jour `docs/reports/PROGRESS.md`.

