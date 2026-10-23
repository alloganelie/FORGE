# Spécification fonctionnelle — Agent de production contrôlée de livrables

| Champ | Valeur |
|---|---|
| Nom de travail du produit | Agent de production contrôlée de livrables (« l'Agent ») |
| Version du document | 0.2 — corrigée après revue (états, profils, règles MVP, approbation et diffusion) |
| Date | 20 octobre 2026 |
| Statut | Brouillon à valider |
| Document source | *Cahier de cadrage fonctionnel — Agent de production contrôlée de livrables* (« le cahier ») |
| Langue | Français |
| Nature | Spécification fonctionnelle. **Aucune architecture technique** n'est proposée ni présupposée. |

---

## Table des matières

0. Préambule et conventions
1. Vision et périmètre fonctionnel
2. Profils d'utilisateurs et responsabilités
3. Modèle conceptuel métier (objets, taxonomies, glossaire)
4. Cas d'usage (catalogue et fiches détaillées)
5. Parcours fonctionnels détaillés
6. Exigences fonctionnelles (RF)
7. Règles métier (RB)
8. États fonctionnels et transitions
9. Règles de blocage, de reprise, de révision et de finalisation
10. Exigences transverses : confidentialité, traçabilité, conformité, contrôle qualité (RT)
11. Critères d'acceptation (CA)
12. Cas limites et scénarios d'erreur (CL)
13. MVP, évolutions ultérieures et points à arbitrer
- Annexe A — Matrice de couverture du cahier
- Annexe B — Catalogue des contrôles (CT)
- Annexe C — Catalogue des motifs de blocage (MB)
- Annexe D — Contenu minimal des rapports
- Annexe E — Registre des propositions à valider (PV)
- Annexe F — Matrice cas d'usage × exigences

---

## 0. Préambule et conventions

### 0.1 Objet du document

Ce document définit **ce que le produit doit faire**, dans quelles conditions, avec quelles limites, quelles responsabilités et quels résultats vérifiables. Il sert de référence commune au produit, aux utilisateurs, aux tests d'acceptation et à une future conception technique, **sans préjuger de cette dernière**.

### 0.2 Ce que ce document n'est pas

- Ce n'est pas une architecture : aucun langage, framework, base de données, modèle de langage, service, protocole ou outil d'infrastructure n'est choisi.
- Ce n'est pas une conception de workflow technique, de microservices, d'agents spécialisés ou d'orchestration.
- Ce n'est pas un jeu de règles métier de contenu (règles éditoriales d'un type de livrable particulier) : ces règles seront fournies par la personne responsable, type de livrable par type de livrable. La spécification définit **comment l'Agent se comporte face à ces règles**, pas leur contenu.

### 0.3 Statut des exigences : décidé ou proposé

Chaque exigence, règle ou critère porte l'un des statuts suivants. **Une proposition n'est jamais une décision acquise.**

| Marqueur | Signification | Portée |
|---|---|---|
| **[D]** | **Décidé** : posé explicitement par le cahier, ou conséquence directe et nécessaire de ce qu'il pose. La colonne « Cahier » donne la référence. | Engage le produit. |
| **[P]** | **Proposition** : introduite dans cette spécification pour la compléter. | N'engage pas tant qu'elle n'est pas validée (voir Annexe E). |
| **[Q]** | **Question ouverte** : le sujet exige une décision qui n'a pas été prise. Renvoie à un identifiant QO-xxx (section 13). | Comportement par défaut proposé, à confirmer. |

Lorsqu'une exigence mêle une partie décidée et un complément proposé, elle est scindée ou le complément est signalé dans sa formulation.

### 0.4 Identifiants stables

| Préfixe | Objet | Exemple |
|---|---|---|
| **GP** | Garantie produit | GP-01 |
| **HY** | Hypothèse ou dépendance | HY-001 |
| **PU** | Profil d'utilisateur ou d'acteur | PU-01 |
| **OB** | Objet métier | OB-01 |
| **QI** | Statut de qualité d'une information | QI-01 |
| **LC** | Statut d'une ligne de cartographie | LC-01 |
| **TF** | Type de transformation | TF-01 |
| **UC** | Cas d'usage | UC-001 |
| **PA** | Parcours fonctionnel | PA-01 |
| **RF** | Exigence fonctionnelle | RF-001 |
| **RB** | Règle métier | RB-001 |
| **RT** | Exigence transverse | RT-001 |
| **ST** | État fonctionnel | ST-R-01 |
| **TR** | Transition d'état | TR-R-01 |
| **IV** | Invariant d'état | IV-01 |
| **CT** | Contrôle du catalogue | CT-01 |
| **MB** | Motif de blocage | MB-01 |
| **CA** | Critère d'acceptation | CA-001 |
| **CL** | Cas limite ou scénario d'erreur | CL-001 |
| **QO** | Question ouverte | QO-001 |
| **PV** | Proposition à valider | PV-01 |

Préfixes complémentaires : **IN** interprétation, **HP** hors périmètre, **IND** indicateur, **RP** principe de responsabilité, **AU** niveau d'autorisation, **AN** classe d'anomalie, **RC** résultat de contrôle, **DH** type de décision humaine, **ES** cas d'escalade, **FN** condition de finalisation, **OB** objet métier.

Les identifiants sont **stables** : un identifiant n'est jamais réutilisé. Une exigence abandonnée est marquée « retirée », jamais renumérotée.

### 0.5 Priorités

| Priorité | Signification |
|---|---|
| **MVP** | Indispensable à un premier produit utilisable et digne de confiance. |
| **V2** | Évolution ultérieure proche, après validation du MVP. |
| **V3** | Évolution ultérieure plus lointaine. |
| **ARB** | Priorité dépendante d'un arbitrage (voir questions ouvertes). |

### 0.6 Références au cahier

La colonne « Cahier » renvoie aux sections du cahier : **§1** Mission, **§2** Objectif principal, **§3.x** Principes fondamentaux, **§4** Modèle de fonctionnement, **§5-É1 à §5-É11** Étapes du cycle fonctionnel, **§6.x** Règles de gestion particulières, **§7** Interaction avec l'utilisateur, **§8** Gestion des utilisateurs et responsabilités, **§9** Formats et types de livrables, **§10** États fonctionnels, **§11–12** Mission de la spécification et limites.

### 0.7 Interprétations retenues

| Réf. | Interprétation | Statut |
|---|---|---|
| IN-01 | Dans le cahier, « personne habilitée » (§3.2, §3.6) et « personne responsable » (§8) désignent la même personne, sauf règle explicite contraire. | [P] |
| IN-02 | « Élément significatif » désigne toute information, tout calcul, toute section, tout champ ou tout tableau dont les règles du type de livrable exigent la traçabilité. Sa définition précise est une question ouverte (QO-018). | [Q] |
| IN-03 | « Règles » désigne l'ensemble des règles générales et des règles propres à chaque type de livrable, y compris les règles éditoriales, de sélection, de transformation, de calcul, de contrôle, de validité, de priorité, de confidentialité et de conservation. | [D] |
| IN-04 | « Demande » désigne l'unité de travail soumise par un utilisateur. Au MVP, une demande vise un seul livrable (RF-008) ; le traitement coordonné de plusieurs livrables relève de la V2 (§6.6). | [P] |

---

## 1. Vision et périmètre fonctionnel

### 1.1 Mission

L'Agent produit des **livrables documentaires** à partir d'informations préalablement mobilisées, vérifiées et mises à sa disposition. Il organise, sélectionne, structure et présente les informations disponibles selon des critères, des règles éditoriales et des formats définis (§1).

L'Agent est un **exécutant documentaire intelligent, rigoureux, traçable et soumis à des règles explicites**. Il n'est pas un consultant autonome qui prendrait librement des décisions de fond (§1).

### 1.2 Garanties produit

Les garanties suivantes résument ce que le produit s'engage à tenir en toutes circonstances. Chacune est déclinée en exigences vérifiables.

| ID | Garantie | Cahier | Statut |
|---|---|---|---|
| GP-01 | **Rien n'est inventé.** Aucun fait, chiffre, référence, résultat, décision ou justification n'est fabriqué pour combler une lacune. | §3.1 | [D] |
| GP-02 | **Rien n'est décidé hors règles.** Toute décision substantielle non couverte par les règles est renvoyée à la personne habilitée. | §3.2 | [D] |
| GP-03 | **Tout est traçable.** Toute information significative d'un livrable est reliée à sa source, à son statut de validation et à ses transformations. | §3.4 | [D] |
| GP-04 | **Les droits sont respectés séparément.** Accès, utilisation, intégration et diffusion sont quatre autorisations distinctes. | §3.5 | [D] |
| GP-05 | **Rien n'est annoncé réussi avant d'avoir réussi.** Aucune conformité, approbation ou autorisation n'est affirmée avant que les contrôles ou validations requis aient abouti. | §7, §5-É11 | [D] |
| GP-06 | **Conformité, approbation et diffusion sont trois statuts indépendants.** Aucun ne se déduit des deux autres. | §5-É11 | [D] |
| GP-07 | **Rien ne s'apprend sans procédure.** Une correction ponctuelle ne devient jamais une règle générale. | §3.6 | [D] |
| GP-08 | **L'historique est immuable.** Les livrables existants ne sont jamais modifiés ni écrasés silencieusement ; toute révision crée une nouvelle version. | §6.8 | [D] |

### 1.3 Positionnement par rapport à INIS

Le produit s'inspire de certains principes du projet INIS (traçabilité, provenance, respect des autorisations, vérification, interdiction d'inventer) mais **est un agent distinct** (§1).

| Dimension | INIS | Agent de production contrôlée de livrables |
|---|---|---|
| Finalité | Mobiliser, vérifier, transformer et transmettre des informations. | Exploiter ces informations de façon contrôlée pour produire des livrables conformes à des exigences prédéfinies. |
| Sortie principale | Informations mobilisées, vérifiées, transmises. | Livrable, rapport de conformité, rapport de traçabilité. |
| Relation | Source **prioritaire** de l'Agent, sans être nécessairement l'unique source autorisée. | Consommateur d'INIS parmi d'autres sources autorisées. |
| Fiabilité | Une information issue d'INIS n'est **pas automatiquement fiable** pour l'Agent. | L'Agent évalue lui-même la qualité et l'utilisabilité de chaque information. |

### 1.4 Périmètre inclus

| Domaine fonctionnel | Description | Cahier |
|---|---|---|
| Gestion des demandes | Réception, compréhension, clarification, suivi, suspension, reprise, annulation. | §5-É1, §6.9, §6.11 |
| Faisabilité | Vérification préalable des modèles, règles, informations, autorisations, exigences. | §5-É2 |
| Mobilisation | Recherche d'informations dans les sources autorisées (INIS prioritaire). | §5-É3 |
| Cartographie | Correspondance structurée entre exigences du livrable et informations disponibles. | §5-É4 |
| Qualité de l'information | Classement des informations selon des statuts de qualité explicites. | §5-É5 |
| Transformation | Opérations éditoriales, structurelles et calculatoires autorisées. | §5-É6, §6.1 |
| Lacunes et contradictions | Détection, recherche alternative, application des règles de priorité, blocage ciblé. | §5-É7 |
| Production | Assemblage du livrable selon modèle et règles. | §5-É8 |
| Contrôle qualité | Contrôles obligatoires de conformité et de cohérence. | §5-É9 |
| Anomalies | Classement, correction mécanique autorisée, observations. | §5-É10 |
| Finalisation et remise | Livrable, rapport de conformité, rapport de traçabilité. | §5-É11 |
| Approbation et diffusion | Statuts distincts, soumis aux décisions humaines. | §5-É11, §8 |
| Versions et révisions | Immutabilité, nouvelle version à chaque révision, historique. | §6.8 |
| Livrables multiples et priorités | Coordination, cohérence, arbitrage de demandes concurrentes. | §6.6, §6.7, §6.10 |
| Gouvernance | Règles, modèles, registre des sources, exceptions, arbitrages par la personne responsable. | §3.6, §8 |
| Confidentialité et données sensibles | Droits distincts, minimisation, masquage, explications limitées. | §3.5, §6.3, §6.4 |

### 1.5 Hors périmètre

| Réf. | Hors périmètre | Justification |
|---|---|---|
| HP-01 | Toute architecture ou décision technique. | §12 |
| HP-02 | Décisions de fond non couvertes par les règles (choix méthodologique, choix d'un indicateur, modification d'une définition, résolution libre d'une contradiction). | §3.2 |
| HP-03 | Modification autonome des règles, préférences, modèles ou registre des sources. | §3.6 |
| HP-04 | Substitution à INIS (mobilisation et vérification initiales comme fonction première). | §1 |
| HP-05 | Définition du **contenu** des règles éditoriales de chaque type de livrable (fournies par la personne responsable). | §4 |
| HP-06 | Autorisation de diffuser, approbation humaine et arbitrages : l'Agent les prépare et les enregistre, il ne les décide pas. | §5-É11, §8 |
| HP-07 | Pilotage du livrable après sa remise (suivi de lecture, retours des destinataires). | Non traité par le cahier ; à arbitrer. |

### 1.6 Hypothèses et dépendances

| ID | Hypothèse ou dépendance | Statut |
|---|---|---|
| HY-001 | INIS est disponible comme source prioritaire d'informations, avec leur provenance et, lorsque c'est possible, leur statut de validation. Le contrat fonctionnel exact avec INIS est à définir (QO-003). | [Q] |
| HY-002 | Un registre permanent des sources autorisées existe ou sera constitué par la personne responsable (QO-004). | [Q] |
| HY-003 | Les modèles documentaires et les règles de chaque type de livrable seront fournis et maintenus par la personne responsable (QO-001). | [Q] |
| HY-004 | L'identité des utilisateurs et leurs droits d'accès sont connus du produit au moment de la demande ; leur définition relève de la gouvernance (QO-007). | [Q] |
| HY-005 | Une et une seule personne responsable est désignée (§8). Au MVP, aucune suppléance n'est prévue (RB-108) ; la suppléance est reportée (QO-008). | [D] / [P] |
| HY-006 | Les échanges et livrables sont rédigés principalement en français. La politique de langues est à confirmer (QO-013). | [P] |
| HY-007 | Les règles de conservation sont définies par la personne responsable. Au MVP, aucune suppression ni péremption automatique tant qu'elle n'a pas fixé de durée (RB-087, RT-061). | [P] |

### 1.7 Indicateurs de réussite fonctionnelle

Ces indicateurs permettent de vérifier que le produit tient ses garanties. Ils sont **proposés**.

| ID | Indicateur | Cible | Statut |
|---|---|---|---|
| IND-01 | Éléments significatifs de livrables finalisés dotés d'une chaîne de traçabilité complète | 100 % | [P] |
| IND-02 | Faits, chiffres ou références présents dans un livrable finalisé sans source identifiée | 0 | [P] |
| IND-03 | Livrables finalisés dont tous les contrôles obligatoires ont réussi | 100 % | [P] |
| IND-04 | Annonces de réussite, conformité ou approbation émises avant l'aboutissement des contrôles ou validations | 0 | [P] |
| IND-05 | Cas où un statut (conformité, approbation, diffusion) est déduit d'un autre | 0 | [P] |
| IND-06 | Décisions substantielles prises par l'Agent hors règles | 0 | [P] |
| IND-07 | Versions finalisées modifiées ou écrasées silencieusement | 0 | [P] |
| IND-08 | Questions de clarification dont la réponse était déterminable par le contexte autorisé et les règles | Tendre vers 0 | [P] |

### 1.8 Contraintes de mission (§12)

- Pas d'architecture technique à ce stade.
- Pas de conception prématurée de microservices, d'agents spécialisés, de workflows techniques ou de mécanismes d'orchestration.
- Une information manquante pour définir une exigence est consignée comme question ouverte, en distinguant **bloquantes** et **reportables** (section 13).

---

## 2. Profils d'utilisateurs et responsabilités

### 2.1 Profils

| ID | Profil | Nature | Responsabilités | Cahier | Statut |
|---|---|---|---|---|---|
| PU-01 | **Utilisateur ordinaire autorisé** | Humain | Soumettre des demandes, fournir des informations, répondre aux clarifications, suivre l'avancement, dans la limite des droits d'accès applicables. | §8 | [D] |
| PU-02 | **Personne responsable** | Humain, **unique** | Arbitrer les décisions sensibles ; résoudre les conflits non résolubles par les règles ; autoriser les exceptions ; approuver les changements de règles, préférences, modèles et registre ; prendre les décisions de livraison qui lui sont réservées. | §8, §3.2, §3.6 | [D] |
| PU-03 | **Destinataire du livrable** | Humain ou organisation, pas nécessairement utilisateur du produit | Reçoit le livrable (et éventuellement les rapports) si la diffusion est autorisée ; ses droits conditionnent ce qu'il peut recevoir. | §6.3, §6.4 | [P] |
| PU-04 | **Source d'information** | Système ou ressource (dont INIS) | Fournit des informations, avec leur provenance, selon ses propres autorisations. | §5-É3 | [D] |
| PU-05 | **Auditeur** (profil dédié) | Humain | Évolution V2 : consulte en lecture seule la traçabilité et l'historique de demandes dont il n'est pas l'auteur, sans pouvoir les modifier. Il n'est pas nécessaire au MVP : la consultation de la traçabilité par l'auteur d'une demande et par la personne responsable relève d'un droit d'accès (UC-030). | §5-É11 | [P] (V2) |

**Priorité des profils.** PU-01, PU-02 et PU-04 : MVP. PU-03 : MVP, en tant qu'acteur dont les droits conditionnent la diffusion ; il n'est pas nécessairement utilisateur du produit. PU-05 : V2.

### 2.2 Principes de répartition des responsabilités

| ID | Principe | Cahier | Statut |
|---|---|---|---|
| RP-01 | Deux niveaux de responsabilité : utilisateurs ordinaires et personne responsable unique. | §8 | [D] |
| RP-02 | L'accès partagé aux actions ordinaires ne supprime pas les restrictions de confidentialité, les autorisations propres aux sources ni les limites de diffusion. | §8 | [D] |
| RP-03 | L'Agent n'exerce jamais à la place d'un humain une décision qui lui est réservée (arbitrage, exception, approbation, autorisation de diffuser, changement de règle). | §3.2, §5-É11 | [D] |
| RP-04 | Un utilisateur ordinaire peut **proposer** une évolution de règle ou de modèle ; seule la personne responsable peut la décider. | §3.6 | [P] |
| RP-05 | Aucune délégation implicite : toute délégation de décision (suppléance) devrait être explicite et tracée. **Aucune suppléance n'est prévue au MVP** (RB-108). | §8 | [P] |
| RP-06 | Chaque décision humaine est enregistrée avec l'identité du décideur, la date, l'objet, le périmètre et le motif. | §3.4 | [P] |

### 2.3 Matrice des droits

Légende : **✔** autorisé · **◐** autorisé sous réserve des droits d'accès applicables à la demande, au livrable et aux sources · **✖** non autorisé · **?** à arbitrer.

| Action | Utilisateur ordinaire (PU-01) | Personne responsable (PU-02) | Destinataire (PU-03) | Cahier | Statut |
|---|---|---|---|---|---|
| Soumettre une demande | ◐ | ✔ | ✖ | §8 | [D] |
| Fournir des informations, répondre aux clarifications | ◐ | ✔ | ✖ | §8 | [D] |
| Suivre l'avancement d'une demande | ◐ | ✔ | ✖ | §7, §8 | [D] |
| Consulter le livrable finalisé | ◐ | ✔ | ◐ (si diffusion autorisée) | §5-É11 | [P] |
| Consulter le rapport de conformité | ◐ | ✔ | ? | §5-É11 | [P] |
| Consulter le rapport de traçabilité | ◐ | ✔ | ✖ par défaut | §6.4 | [P] |
| Suspendre sa propre demande | ◐ | ✔ | ✖ | §6.11 | [D] |
| Reprendre une demande suspendue | ◐ | ✔ | ✖ | §6.9 | [D] |
| Annuler définitivement une demande (non finalisée) | ◐ (sa propre demande) | ✔ | ✖ | §6.11 | [P] |
| Demander une révision (nouvelle version) | ◐ | ✔ | ✖ | §6.8 | [D] |
| Signaler une correction ponctuelle | ◐ | ✔ | ✖ | §3.6 | [D] |
| Proposer une évolution de règle ou de modèle | ◐ | ✔ | ✖ | §3.6 | [P] |
| Modifier règles, préférences, modèles | ✖ | ✔ | ✖ | §3.6, §8 | [D] |
| Modifier le registre permanent des sources | ✖ | ✔ | ✖ | §5-É3 | [D] |
| Autoriser ponctuellement une source | ✖ | ✔ | ✖ | §5-É3 | [D] |
| Arbitrer une décision non couverte | ✖ | ✔ | ✖ | §3.2, §8 | [D] |
| Résoudre une contradiction irrésolue par les règles | ✖ | ✔ | ✖ | §8 | [D] |
| Autoriser une exception | ✖ | ✔ | ✖ | §8 | [D] |
| Approuver un livrable (version finalisée) | ✖ | ✔ | ✖ | §5-É11 | [P] |
| Autoriser la diffusion (version finalisée) | ✖ | ✔ | ✖ | §8 | [D] |
| Arbitrer des priorités concurrentes | ✖ | ✔ | ✖ | §6.7 | [D] |
| Consulter l'historique et les versions | ◐ | ✔ | ✖ | §6.8 | [P] |

### 2.4 Visibilité

- Chaque profil ne voit que ce que ses droits permettent, y compris l'état d'avancement et les motifs de blocage (§7). [D]
- Au MVP, une demande, son livrable et sa traçabilité ne sont accessibles qu'à son auteur et à la personne responsable (RT-016). La visibilité entre utilisateurs ordinaires est reportée (QO-027). [P]
- Au MVP, **consulter la traçabilité et l'historique est un droit d'accès**, attribué à l'auteur de la demande et à la personne responsable (UC-030) ; cela ne requiert aucun profil dédié. Le profil d'auditeur (PU-05) est une évolution V2 qui ajoute la consultation en lecture seule de demandes dont l'auditeur n'est pas l'auteur. [P]

---
## 3. Modèle conceptuel métier

Cette section décrit les objets du métier **tels que l'utilisateur et la personne responsable les comprennent**. Elle ne décrit ni une structure de données ni un schéma technique.

### 3.1 Objets métier

| ID | Objet | Définition | Attributs fonctionnels principaux | Statut |
|---|---|---|---|---|
| OB-01 | **Demande** | Unité de travail soumise en langage naturel. | Identifiant, auteur, date, texte d'origine, type de livrable identifié, finalité, contraintes, paramètres, état, priorité. | [D] |
| OB-02 | **Livrable** | Document produit pour répondre à une demande. Distinct de son format de fichier. | Type, format, destinataires prévus, versions. | [D] |
| OB-03 | **Version de livrable** | Instance immuable d'un livrable une fois finalisée. | Numéro, statut de version, statuts de conformité, d'approbation et de diffusion, modèle et règles utilisés, motif de création. | [D] |
| OB-04 | **Type de livrable** | Catégorie de livrable (protocole de recherche, rapport de suivi-évaluation, etc.). | Modèle(s) associé(s), règles propres, formats autorisés, contrôles obligatoires, éléments de sortie exigés. | [D] |
| OB-05 | **Modèle documentaire** | Structure réutilisable d'un type de livrable. | Sections, champs, tableaux attendus, caractère obligatoire, exemples, version. | [D] |
| OB-06 | **Règle** | Prescription explicite encadrant le comportement de l'Agent. | Catégorie, portée, version, date d'effet, auteur de la décision. | [D] |
| OB-07 | **Exigence de livrable** | Élément attendu par le modèle ou la demande (section, champ, tableau, critère). | Caractère obligatoire ou facultatif, information nécessaire, transformations autorisées. | [D] |
| OB-08 | **Instruction de demande** | Paramètres propres à une demande (contexte, finalité, contraintes, paramètres particuliers). | Valeur, origine (utilisateur, contexte, règle). | [D] |
| OB-09 | **Source** | Ressource d'où proviennent des informations (INIS ou autre). | Identité, niveaux d'autorisation, conditions, restrictions, périodes de validité. | [D] |
| OB-10 | **Registre permanent des sources** | Liste versionnée des sources autorisées de façon permanente. | Sources, autorisations aux quatre niveaux, versions. | [D] |
| OB-11 | **Autorisation** | Droit relatif à une source, une information ou un livrable. Quatre niveaux : accès, utilisation, intégration, diffusion. Peut être permanente ou ponctuelle. | Niveau, bénéficiaire, objet, périmètre, durée, origine. | [D] |
| OB-12 | **Information** | Unité d'information mobilisée ou fournie. | Contenu, source, référence, date de consultation, période de référence, statut de qualité, usage prévu, classification de confidentialité. | [D] |
| OB-13 | **Cartographie** | Correspondance structurée exigences ↔ informations pour une demande. | Lignes, version, état global (ce qui est produisible, à clarifier, bloqué). | [D] |
| OB-14 | **Ligne de cartographie** | Correspondance pour un élément significatif. | Exigence, information nécessaire, information disponible, source, statut de validation, transformations, manques, contradictions, dépendances, statut de ligne. | [D] |
| OB-15 | **Lacune** | Information manquante pour une exigence. | Exigence concernée, recherches effectuées, état (ouverte, résolue, bloquante). | [D] |
| OB-16 | **Contradiction** | Divergence entre informations destinées au même élément. | Informations en conflit, règles examinées, état (résolue par règle, irrésolue, arbitrée). | [D] |
| OB-17 | **Transformation** | Opération autorisée appliquée à une information. | Type (TF), règle autorisante, entrée, sortie, date. | [D] |
| OB-18 | **Donnée dérivée** | Résultat d'un calcul autorisé. | Entrées et sources, formule ou méthode, unités et conventions, arrondi, résultat. | [D] |
| OB-19 | **Contrôle** | Vérification obligatoire ou informative. | Nature, règle, résultat (réussi, échoué, non exécutable, non applicable), éléments examinés, date. | [D] |
| OB-20 | **Anomalie** | Écart relevé. Trois classes : non-conformité avérée, incohérence établie, observation. | Classe, règle concernée, élément, traitement, état. | [D] |
| OB-21 | **Décision humaine** | Arbitrage, autorisation, exception, approbation, changement de règle. | Décideur, date, objet, périmètre, motif, éléments impactés. | [D] |
| OB-22 | **Rapport de conformité** | Présente les contrôles, résultats, réserves et conditions restantes. | Version de livrable concernée, contenu minimal (Annexe D). | [D] |
| OB-23 | **Rapport de traçabilité** | Permet de retrouver pour chaque élément significatif sources, références, statuts, transformations, règles, calculs, autorisations, historique. | Version concernée, contenu minimal (Annexe D). | [D] |
| OB-24 | **Historique de production** | Journal ordonné et immuable de tout ce qui s'est passé pour une demande. | Événements, auteurs (humain ou Agent), dates, motifs. | [D] |
| OB-25 | **État de travail suspendu** | Ensemble conservé d'une demande suspendue. | Éléments validés, éléments provisoires, cartographie, décisions, conditions de reprise. | [D] |
| OB-26 | **Élément du livrable** | Section, champ, tableau, annexe ou contenu significatif du livrable. | Statut d'élément, lignes de cartographie liées, statut de contrôle. | [P] |
| OB-27 | **Exemple documentaire** | Illustration du résultat attendu dans un modèle. Ne prévaut jamais sur une règle. | Modèle de rattachement. | [D] |
| OB-28 | **Priorité de demande** | Rang d'une demande par rapport aux autres. | Critères appliqués, justification. | [D] |

### 3.2 Relations structurantes

- Une **demande** vise un ou plusieurs **livrables** (QO-026) d'un **type** donné, qui s'appuie sur un **modèle** et des **règles** dont les **versions sont figées** pour cette demande (§6.8).
- Un **livrable** a une ou plusieurs **versions**. Chaque version a ses propres statuts de **conformité**, d'**approbation** et de **diffusion**.
- Une **cartographie** relie des **exigences** à des **informations**, chaque information ayant une **source**, un **statut de qualité** et des **transformations** éventuelles.
- Une **version finalisée** est accompagnée, selon les règles du type, d'un **rapport de conformité** et d'un **rapport de traçabilité**, tous deux liés à cette version précise.
- Une **décision humaine** est toujours liée à un objet précis (contradiction, exception, source, approbation, diffusion, règle) et à une demande.
- Les **règles** prévalent sur les **exemples** des modèles (§3.3).

### 3.3 Taxonomies

#### 3.3.1 Statuts de qualité d'une information (QI)

Le statut est évalué **pour un usage prévu et une période de référence** : une même information peut être « vérifiée et utilisable » pour une analyse historique et « hors période de validité » pour décrire la situation actuelle (§6.2).

| ID | Statut | Définition | Peut être présentée comme fait établi ? | Cahier |
|---|---|---|---|---|
| QI-01 | **Vérifiée et utilisable** | Vérifiée selon les critères explicites ; utilisable pour l'usage prévu ; dans sa période de validité ; autorisée. | **Oui** | §5-É5 |
| QI-02 | **Candidate** | Plausible mais nécessitant une vérification supplémentaire. | Non | §5-É5 |
| QI-03 | **Incertaine** | Fiabilité ou pertinence douteuse. | Non | §5-É5 |
| QI-04 | **Contradictoire** | En conflit avec une autre information pour le même élément. | Non | §5-É5 |
| QI-05 | **Hors période de validité** | Valide pour une autre période que celle visée. | Non (pour la période visée) | §5-É5, §6.2 |
| QI-06 | **Interdite ou non autorisée pour l'usage prévu** | Accès, utilisation, intégration ou diffusion non permis pour l'usage visé. | Non, et exclue du livrable | §5-É5 |
| QI-07 | **Absente** | Aucune information disponible pour l'exigence. | Sans objet | §5-É5 |

Règle structurante : **seule QI-01 peut être présentée comme un fait établi.** Les autres statuts déclenchent vérification, clarification, arbitrage, blocage ou exclusion selon les règles (RB-018, RB-019).

#### 3.3.2 Statuts d'une ligne de cartographie (LC)

Le cahier distingue trois issues : ce qui peut être produit, ce qui doit être clarifié, ce qui reste bloqué (§5-É4). Les statuts suivants les déclinent.

| ID | Statut | Signification | Issue | Statut de la définition |
|---|---|---|---|---|
| LC-01 | **Satisfaite** | Information QI-01 disponible, transformations autorisées, aucune dépendance bloquante. | Peut être produit | [P] |
| LC-02 | **Partielle** | Une partie seulement des informations nécessaires est satisfaite. | À clarifier ou bloqué selon le caractère obligatoire | [P] |
| LC-03 | **À clarifier** | Ambiguïté, correspondance incertaine, information candidate ou incertaine en cours de vérification. | À clarifier | [P] |
| LC-04 | **Bloquée** | Information obligatoire absente, contradictoire irrésolue, non autorisée ; méthode non définie ; décision requise. | Bloqué | [P] |
| LC-05 | **Non applicable** | Exigence sans objet pour cette demande selon les règles. | — | [P] |

#### 3.3.3 Types de transformation autorisables (TF)

Chacune n'est permise **que si une règle explicite l'autorise** (§5-É6, §6.1).

| ID | Transformation | Cahier |
|---|---|---|
| TF-01 | Extraire des informations d'un document | §5-É6 |
| TF-02 | Réorganiser des paragraphes ou des tableaux | §5-É6 |
| TF-03 | Associer des champs sources à des champs cibles | §5-É6 |
| TF-04 | Convertir des formats de dates, d'unités ou de fichiers | §5-É6 |
| TF-05 | Corriger des erreurs grammaticales ou typographiques | §5-É6 |
| TF-06 | Reformuler fidèlement un contenu | §5-É6 |
| TF-07 | Appliquer des formules et méthodes de calcul autorisées | §5-É6, §6.1 |
| TF-08 | Insérer des informations dans les sections prévues | §5-É6 |
| TF-09 | Générer les tableaux et annexes exigés | §5-É6 |

#### 3.3.4 Niveaux d'autorisation (AU)

| ID | Niveau | Question à laquelle il répond | Cahier |
|---|---|---|---|
| AU-1 | **Accès** | Puis-je consulter cette source ? | §3.5, §6.4 |
| AU-2 | **Utilisation** | Puis-je utiliser le contenu de cette source (analyser, transformer) ? | §3.5, §6.4 |
| AU-3 | **Intégration** | Puis-je intégrer ce contenu dans un livrable ? | §3.5, §6.4 |
| AU-4 | **Diffusion** | Puis-je diffuser le livrable qui le contient, à ces destinataires ? | §3.5, §6.4 |

Chaque niveau est évalué séparément. Un droit supérieur n'implique pas un droit inférieur et réciproquement. [D]

#### 3.3.5 Classes d'anomalies (AN)

| ID | Classe | Traitement | Cahier |
|---|---|---|---|
| AN-1 | **Non-conformité avérée** par rapport à une règle explicite | Correction mécanique si une règle l'autorise ; sinon suspension et décision humaine. | §5-É10 |
| AN-2 | **Incohérence établie** | Idem. | §5-É10 |
| AN-3 | **Observation ou anomalie potentielle** nécessitant une appréciation humaine | Consignée ; ne justifie pas à elle seule une modification. | §5-É10 |

#### 3.3.6 Résultats de contrôle (RC)

| ID | Résultat | Signification | Statut |
|---|---|---|---|
| RC-1 | **Réussi** | Le contrôle a été exécuté et le critère est satisfait. | [P] |
| RC-2 | **Échoué** | Le contrôle a été exécuté et le critère n'est pas satisfait. | [P] |
| RC-3 | **Non exécutable** | Les données ou règles nécessaires manquent. N'est **pas** un succès. | [P] |
| RC-4 | **Non applicable** | Le contrôle ne s'applique pas à ce livrable selon les règles. | [P] |

#### 3.3.7 Types de décision humaine (DH)

| ID | Type | Cahier |
|---|---|---|
| DH-01 | Arbitrage d'une contradiction irrésolue | §5-É7, §8 |
| DH-02 | Décision sur un point non couvert par les règles | §3.2, §6.5 |
| DH-03 | Autorisation d'une exception | §8 |
| DH-04 | Autorisation ponctuelle d'une source | §5-É3 |
| DH-05 | Approbation d'un livrable | §5-É11 |
| DH-06 | Autorisation de diffusion | §5-É11, §8 |
| DH-07 | Changement de règle, préférence, modèle ou registre | §3.6, §8 |
| DH-08 | Arbitrage de priorité | §6.7 |
| DH-09 | Annulation définitive (auteur de la demande ou personne responsable) | §6.11 |
| DH-10 | Autorisation d'une correction non couverte par une règle | §5-É10 |

### 3.4 Glossaire

| Terme | Définition |
|---|---|
| **Agent** | Le produit décrit par cette spécification. |
| **Annulation définitive** | Arrêt irréversible d'une demande non finalisée, distinct de la suspension. Règle MVP : action explicite et confirmée de l'auteur de la demande ou de la personne responsable (RF-210). |
| **Approbation** | Décision humaine d'accepter une version de livrable. Statut distinct de la conformité et de la diffusion. |
| **Blocage** | Impossibilité de produire ou finaliser un élément tant qu'une cause n'est pas levée. Local par défaut. |
| **Cartographie** | Correspondance structurée entre exigences du livrable et informations disponibles. |
| **Conformité** | Réussite de tous les contrôles obligatoires pour une version donnée. N'est ni une approbation ni une autorisation de diffuser. |
| **Contradiction** | Divergence entre informations destinées au même élément, après prise en compte de la portée et de la période. |
| **Correction mécanique** | Correction d'un défaut ne nécessitant aucune interprétation, autorisée explicitement par une règle. |
| **Diffusion** | Transmission d'un livrable à des destinataires. Son autorisation est un statut distinct. |
| **Donnée dérivée** | Résultat d'un calcul autorisé. |
| **Élément significatif** | Élément dont la traçabilité est exigée (QO-018). |
| **Exception** | Dérogation explicite, ponctuelle et tracée à une règle, accordée par la personne responsable. |
| **Exemple documentaire** | Illustration d'un résultat attendu, subordonnée aux règles. |
| **Information candidate** | Information plausible mais non encore vérifiée. |
| **Instruction de demande** | Précision propre à une demande, sans portée normative. |
| **Lacune** | Information manquante pour une exigence. |
| **Livrable** | Document produit, distinct de son format. |
| **Modèle documentaire** | Structure réutilisable d'un type de livrable. |
| **Motif communicable** | Explication d'un blocage ou refus qu'un interlocuteur donné a le droit de recevoir, sans révéler d'information protégée. |
| **Observation** | Anomalie potentielle consignée, nécessitant une appréciation humaine. |
| **Personne responsable** | Personne unique habilitée à arbitrer, autoriser les exceptions, approuver les changements de règles et prendre les décisions de livraison réservées. |
| **Provenance** | Origine d'une information : source, référence, date. |
| **Règle** | Prescription explicite encadrant l'Agent. |
| **Réserve** | Limite ou condition restante mentionnée dans le rapport de conformité sans empêcher la conformité. |
| **Révision** | Nouvelle version d'un livrable issue d'une demande explicite. |
| **Source** | Ressource d'informations (INIS ou autre). |
| **Suspension** | Interruption d'une demande avec conservation de l'état de travail. Distincte de l'annulation. |
| **Traçabilité** | Capacité de relier tout élément significatif à ses sources, statut, transformations, règles, calculs et autorisations. |
| **Usage prévu** | Finalité pour laquelle une information est utilisée dans un livrable. |
| **Utilisateur ordinaire autorisé** | Utilisateur pouvant soumettre des demandes et suivre l'avancement sous réserve de ses droits. |
| **Validité temporelle** | Période durant laquelle une information peut être utilisée pour un usage donné. |
| **Version figée** | Version du modèle, des règles et du registre en vigueur à la création d'une production, qui lui reste liée. |

---
## 4. Cas d'usage

### 4.1 Catalogue

| ID | Cas d'usage | Acteur principal | Étape du cycle | Priorité |
|---|---|---|---|---|
| UC-001 | Soumettre une demande de livrable | PU-01 | É1 | MVP |
| UC-002 | Clarifier la demande | PU-01 | É1 | MVP |
| UC-003 | Vérifier la faisabilité | Agent | É2 | MVP |
| UC-004 | Mobiliser les informations auprès des sources autorisées | Agent | É3 | MVP |
| UC-005 | Établir la cartographie exigences / informations | Agent | É4 | MVP |
| UC-006 | Évaluer la qualité des informations | Agent | É5 | MVP |
| UC-007 | Traiter une lacune d'information | Agent | É7 | MVP |
| UC-008 | Traiter une contradiction | Agent, PU-02 | É7 | MVP |
| UC-009 | Organiser et transformer les informations | Agent | É6 | MVP |
| UC-010 | Calculer une donnée dérivée | Agent | É6, §6.1 | MVP |
| UC-011 | Produire le livrable | Agent | É8 | MVP |
| UC-012 | Exécuter les contrôles qualité | Agent | É9 | MVP |
| UC-013 | Traiter les anomalies | Agent, PU-02 | É10 | MVP |
| UC-014 | Finaliser et remettre le livrable et ses rapports | Agent | É11 | MVP |
| UC-015 | Approuver un livrable | PU-02 | É11 | MVP |
| UC-016 | Autoriser la diffusion d'un livrable | PU-02 | É11 | MVP |
| UC-017 | Réviser un livrable (nouvelle version) | PU-01, PU-02 | §6.8 | MVP |
| UC-018 | Suspendre une demande | PU-01, Agent | §6.9, §6.11 | MVP |
| UC-019 | Reprendre une demande suspendue | PU-01 | §6.9 | MVP |
| UC-020 | Annuler définitivement une demande | PU-01 (auteur) ou PU-02 | §6.11 | MVP |
| UC-021 | Coordonner des livrables multiples | Agent | §6.6 | V2 |
| UC-022 | Prioriser des demandes concurrentes | Agent, PU-02 | §6.7 | V2 |
| UC-023 | Suivre l'avancement d'une demande | PU-01 | §7 | MVP |
| UC-024 | Arbitrer une décision non couverte | PU-02 | §3.2, §6.5 | MVP |
| UC-025 | Autoriser ponctuellement une source | PU-02 | É3 | MVP |
| UC-026 | Gérer le registre permanent des sources | PU-02 | É3 | MVP (minimal) |
| UC-027 | Gérer modèles, règles et préférences | PU-02 | §3.6 | MVP |
| UC-028 | Gérer une exception | PU-02 | §8 | V2 |
| UC-029 | Traiter une correction ponctuelle ou une proposition de règle | PU-01, PU-02 | §3.6 | V2 |
| UC-030 | Consulter la traçabilité et l'historique | PU-01 (auteur), PU-02 | É11 | MVP |
| UC-031 | Appliquer la minimisation et le masquage des données sensibles | Agent | §6.3 | MVP |

### 4.2 Vue d'ensemble : cycle de production et cas d'usage

| Étape du cycle (cahier) | Cas d'usage | État de la demande typique (section 8) | Points de blocage possibles |
|---|---|---|---|
| É1 Réception et compréhension | UC-001, UC-002 | Reçue, En clarification | Ambiguïté significative |
| É2 Vérification de la faisabilité | UC-003 | En vérification de faisabilité | MB-01, MB-06, MB-14 |
| É3 Mobilisation des informations | UC-004, UC-025, UC-026 | En production | Source non autorisée, indisponible |
| É4 Cartographie | UC-005 | En production | Lignes bloquées |
| É5 Qualité des informations | UC-006 | En production | Information non vérifiable |
| É6 Organisation et transformation | UC-009, UC-010, UC-031 | En production | Méthode non définie, correspondance incertaine |
| É7 Lacunes et contradictions | UC-007, UC-008 | En production, Bloquée, En attente de décision | Lacune obligatoire, contradiction irrésolue |
| É8 Production | UC-011 | En production | Conditions de production non satisfaites |
| É9 Contrôle qualité | UC-012 | En contrôle qualité | Contrôle obligatoire échoué |
| É10 Anomalies | UC-013 | En contrôle qualité, En attente de décision | Correction non autorisée |
| É11 Finalisation et remise | UC-014, UC-015, UC-016 | Finalisée | Approbation ou diffusion non accordée |

---

### 4.3 Fiches de cas d'usage

Chaque fiche précise acteurs, déclencheur, préconditions, entrées, parcours nominal, variantes et erreurs, sorties, postconditions et liens avec les exigences. Les plages d'exigences renvoient aux sections 6, 7, 10 et 11.

#### UC-001 — Soumettre une demande de livrable

- **Acteurs** : utilisateur ordinaire autorisé (principal), personne responsable ; Agent.
- **Déclencheur** : l'utilisateur formule en langage naturel la demande d'un livrable.
- **Préconditions** : utilisateur identifié et autorisé à soumettre ce type de demande ; au moins un type de livrable est configuré.
- **Entrées** : texte de la demande ; informations ou pièces fournies ; contraintes exprimées (échéance, destinataires, format, période de référence).
- **Parcours nominal** :
  1. L'utilisateur formule sa demande.
  2. L'Agent enregistre la demande (identifiant stable, auteur, date, texte d'origine) : état **Reçue**.
  3. L'Agent identifie type de livrable, objectif, contexte, finalité, contraintes, paramètres.
  4. L'Agent détermine les paramètres déductibles du contexte autorisé et des règles.
  5. L'Agent reformule sa compréhension si nécessaire.
  6. S'il subsiste une ambiguïté significative, passage à UC-002 ; sinon à UC-003.
- **Variantes et erreurs** : utilisateur non autorisé → refus avec motif communicable (CL-001) ; type de livrable non reconnu → signalé en UC-003 (MB-01) ; plusieurs livrables demandés → au MVP, l'Agent propose de scinder en demandes distinctes et indépendantes (RF-008, CL-064) ; le traitement coordonné relève de UC-021 (V2) ; demande incompréhensible → question ciblée (UC-002).
- **Sorties** : demande enregistrée ; compréhension reformulée.
- **Postconditions** : la demande existe ; aucun contenu de livrable n'a été produit ; état **Reçue** puis **En clarification** ou **En vérification de faisabilité**.
- **Liens** : RF-001 à RF-010 ; RB-118, RB-119 ; CA-001 à CA-004, CA-189. **Priorité** : MVP.

#### UC-002 — Clarifier la demande

- **Acteurs** : utilisateur ordinaire ; Agent.
- **Déclencheur** : une ambiguïté restante a une incidence significative sur la conformité ou la validité du livrable.
- **Préconditions** : demande à l'état Reçue ou en cours d'analyse.
- **Entrées** : ambiguïtés identifiées ; contexte autorisé ; règles applicables.
- **Parcours nominal** :
  1. L'Agent vérifie qu'il ne peut pas déterminer le paramètre par le contexte autorisé et les règles.
  2. Il formule une question ciblée en indiquant pourquoi la réponse est nécessaire.
  3. La demande passe à **En clarification**.
  4. L'utilisateur répond ; l'Agent enregistre la réponse comme information fournie.
  5. L'Agent réévalue ; s'il reste une ambiguïté significative, nouvelle question ; sinon passage à UC-003.
- **Variantes et erreurs** : pas de réponse → l'élément dépendant reste en attente, l'Agent ne choisit pas à la place de l'utilisateur pour un choix substantiel (CL-002) ; réponse contradictoire avec une règle → la règle prévaut, signalement (CL-003) ; plusieurs ambiguïtés → hiérarchisation des questions (bloquantes d'abord).
- **Sorties** : paramètres précisés ; questions restantes.
- **Postconditions** : paramètres nécessaires connus ou éléments dépendants identifiés comme en attente.
- **Liens** : RF-011 à RF-018 ; RB-118, RB-119 ; CA-005 à CA-010, CA-190. **Priorité** : MVP.

#### UC-003 — Vérifier la faisabilité

- **Acteurs** : Agent.
- **Déclencheur** : paramètres suffisamment connus.
- **Préconditions** : demande comprise.
- **Entrées** : demande ; modèles ; règles ; registre des sources ; droits des acteurs.
- **Parcours nominal** :
  1. L'Agent vérifie l'existence d'un modèle et de règles applicables.
  2. Il vérifie la disponibilité des informations nécessaires.
  3. Il vérifie les autorisations d'accès et d'utilisation.
  4. Il identifie les exigences obligatoires du livrable.
  5. Il recense les contradictions déjà identifiées.
  6. Il vérifie les conditions préalables à la production.
  7. Il fige les versions de modèle, règles et registre pour la demande.
  8. Il produit un diagnostic de faisabilité : réalisable, à clarifier, bloqué, avec motifs communicables.
- **Variantes et erreurs** : modèle absent → blocage (MB-01), aucune structure improvisée (CL-004) ; condition indispensable non satisfaite → blocage de la partie concernée, diagnostic poursuivi (CL-005) ; droits incertains → suspension de l'opération concernée (CL-006).
- **Sorties** : diagnostic de faisabilité ; versions figées.
- **Postconditions** : état **En production** si faisable, au moins pour une partie ; sinon **Bloquée** ou **En attente d'une décision humaine**.
- **Liens** : RF-019 à RF-030 ; RB-013, RB-057, RB-058, RB-077, RB-078 ; CA-011 à CA-020. **Priorité** : MVP.

#### UC-004 — Mobiliser les informations auprès des sources autorisées

- **Acteurs** : Agent ; sources (PU-04) ; personne responsable pour les autorisations ponctuelles.
- **Déclencheur** : faisabilité acquise, au moins partiellement.
- **Préconditions** : registre des sources disponible ; droits d'accès (AU-1) établis.
- **Entrées** : exigences du livrable ; sources autorisées ; critères de recherche issus des règles.
- **Parcours nominal** :
  1. L'Agent interroge INIS en priorité.
  2. Pour chaque information, il enregistre source, référence, date de consultation, période de référence et statut attribué par la source.
  3. Si une information obligatoire est absente d'INIS, il consulte les autres sources explicitement autorisées.
  4. Il conserve les informations dans leur forme d'origine.
  5. Il consigne chaque interrogation, y compris infructueuse.
- **Variantes et erreurs** : source indisponible → signalement, poursuite auprès des autres sources, pas de conclusion à l'absence (CL-007) ; source non autorisée → jamais consultée ; demande d'autorisation ponctuelle (UC-025) ; méthode de recherche non définie par les règles → décision non couverte (UC-024).
- **Sorties** : informations mobilisées avec provenance ; journal des interrogations.
- **Postconditions** : informations disponibles pour la cartographie ; lacunes consignées.
- **Liens** : RF-031 à RF-044 ; RB-013 à RB-016 ; RT-003, RT-004 ; CA-021 à CA-030. **Priorité** : MVP.

#### UC-005 — Établir la cartographie exigences / informations

- **Acteurs** : Agent.
- **Déclencheur** : informations mobilisées.
- **Préconditions** : exigences du livrable connues ; informations mobilisées.
- **Entrées** : modèle ; informations ; règles.
- **Parcours nominal** :
  1. Pour chaque section, champ, tableau ou élément significatif, l'Agent crée une ligne.
  2. Il renseigne exigence, information nécessaire, information disponible, source et référence, statut de validation, transformations, manques, contradictions, incertitudes, dépendances.
  3. Il attribue un statut de ligne (LC).
  4. Il établit la synthèse : ce qui peut être produit, ce qui doit être clarifié, ce qui reste bloqué.
- **Variantes et erreurs** : correspondance incertaine → ligne **À clarifier**, jamais résolue arbitrairement (CL-008) ; changement en cours de production → mise à jour versionnée.
- **Sorties** : cartographie versionnée ; synthèse.
- **Postconditions** : la rédaction ne peut commencer que sur la base de cette cartographie.
- **Liens** : RF-045 à RF-058 ; RB-023 à RB-025 ; CA-031 à CA-040. **Priorité** : MVP.

#### UC-006 — Évaluer la qualité des informations

- **Acteurs** : Agent.
- **Déclencheur** : cartographie établie ou mise à jour.
- **Préconditions** : critères d'évaluation définis par les règles (QO-029).
- **Entrées** : informations ; critères ; règles de validité temporelle ; usage prévu.
- **Parcours nominal** :
  1. L'Agent évalue chaque information selon les critères explicites.
  2. Il lui attribue un statut QI pour l'usage et la période visés.
  3. Pour toute information incertaine ou candidate, il cherche à la vérifier auprès de sources autorisées.
  4. Tant que la vérification n'aboutit pas, l'information n'est pas présentée comme un fait établi.
  5. Il enregistre critères appliqués, résultat, sources de vérification et date.
- **Variantes et erreurs** : information d'INIS à fiabilité non établie → traitée comme candidate (CL-009) ; information ancienne → évaluée selon la période visée (CL-010) ; critères absents → décision non couverte.
- **Sorties** : statut QI par information ; vérifications effectuées.
- **Postconditions** : les lignes de cartographie reflètent les statuts ; seules les informations QI-01 sont utilisables comme faits établis.
- **Liens** : RF-059 à RF-072 ; RB-016 à RB-022 ; CA-041 à CA-044. **Priorité** : MVP.

#### UC-007 — Traiter une lacune d'information

- **Acteurs** : Agent ; utilisateur ordinaire.
- **Déclencheur** : une exigence n'a pas d'information disponible.
- **Préconditions** : cartographie établie.
- **Entrées** : lacune ; sources alternatives autorisées.
- **Parcours nominal** :
  1. L'Agent consigne la lacune et identifie les éléments dépendants.
  2. Il recherche l'information auprès d'autres sources autorisées.
  3. Si elle est trouvée, elle suit UC-006.
  4. Sinon, si elle est obligatoire, les éléments dépendants restent **bloqués** ; si elle est facultative, la règle du modèle s'applique.
  5. L'Agent peut demander l'information à l'utilisateur sous forme ciblée.
- **Variantes et erreurs** : tentation de combler par estimation ou valeur par défaut → interdit (CL-011) ; lacune résolue → historique conservé.
- **Sorties** : lacune résolue ou bloquante ; éléments dépendants identifiés.
- **Postconditions** : aucun contenu fabriqué ; blocage ciblé.
- **Liens** : RF-073 à RF-080 ; RB-001, RB-002, RB-027 à RB-029 ; CA-045 à CA-047. **Priorité** : MVP.

#### UC-008 — Traiter une contradiction

- **Acteurs** : Agent ; personne responsable.
- **Déclencheur** : deux informations ou plus divergent pour le même élément.
- **Préconditions** : informations évaluées.
- **Entrées** : informations en conflit ; règles de priorité (QO-005) ; contexte, provenance, portée, période.
- **Parcours nominal** :
  1. L'Agent vérifie si la divergence s'explique par la portée ou la période.
  2. Il applique les règles de priorité explicites.
  3. Si une règle tranche, il enregistre le résultat et la règle appliquée.
  4. Sinon, il identifie les éléments dépendants ; si l'information est indispensable, ils restent **bloqués**.
  5. Il constitue un dossier d'arbitrage et sollicite la personne responsable (UC-024).
  6. Les opérations indépendantes se poursuivent si les règles le permettent.
- **Variantes et erreurs** : information la plus récente ≠ gagnante par défaut (CL-012) ; arbitrage reçu → décision tracée, portée limitée à la demande (CL-013).
- **Sorties** : contradiction résolue, arbitrée ou bloquante.
- **Postconditions** : aucune contradiction masquée ni tranchée librement.
- **Liens** : RF-081 à RF-090 ; RB-030 à RB-036 ; CA-048 à CA-052. **Priorité** : MVP.

#### UC-009 — Organiser et transformer les informations

- **Acteurs** : Agent.
- **Déclencheur** : informations évaluées, lignes produisibles.
- **Préconditions** : transformations autorisées par des règles explicites.
- **Entrées** : informations QI-01 ; règles de transformation ; modèle.
- **Parcours nominal** :
  1. L'Agent organise les informations selon le modèle.
  2. Il applique uniquement les transformations TF-01 à TF-09 autorisées.
  3. Il trace chaque transformation : opération, règle, entrée, sortie.
  4. Il vérifie que le sens, la portée et les nuances sont préservés.
- **Variantes et erreurs** : transformation non couverte → refusée, décision non couverte (CL-014) ; correspondance incertaine → ligne À clarifier ; hypothèse jamais transformée en fait (CL-015).
- **Sorties** : contenu organisé et transformé ; traces.
- **Postconditions** : chaque transformation est rattachée à une règle.
- **Liens** : RF-091 à RF-104 ; RB-023 à RB-025, RB-043 ; RT-030 ; CA-053 à CA-058. **Priorité** : MVP.

#### UC-010 — Calculer une donnée dérivée

- **Acteurs** : Agent.
- **Déclencheur** : une exigence requiert un calcul.
- **Préconditions** : méthode de calcul explicitement définie ; données d'entrée utilisables.
- **Entrées** : données d'entrée avec sources ; formule ou méthode ; unités, conventions, arrondi.
- **Parcours nominal** :
  1. L'Agent vérifie que la méthode est définie.
  2. Il exécute le calcul et conserve entrées, sources, méthode, unités, conventions, arrondi, résultat.
  3. Il marque le résultat comme **dérivé**.
  4. Il vérifie la reproductibilité.
- **Variantes et erreurs** : méthode non définie → clarification ou blocage (CL-016) ; entrées de statut faible → résultat de statut au plus égal (CL-017).
- **Sorties** : donnée dérivée tracée.
- **Postconditions** : le calcul peut être rejoué à l'identique.
- **Liens** : RF-105 à RF-114 ; RB-037 à RB-044 ; CA-059 à CA-062. **Priorité** : MVP.

#### UC-011 — Produire le livrable

- **Acteurs** : Agent.
- **Déclencheur** : conditions de production satisfaites, au moins pour une partie.
- **Préconditions** : cartographie, informations, transformations disponibles.
- **Entrées** : modèle ; règles ; informations ; autorisations ; format demandé.
- **Parcours nominal** :
  1. L'Agent assemble le livrable selon modèle, règles de sélection et d'intégration, règles éditoriales, calcul et transformation, présentation, confidentialité et diffusion.
  2. Il insère les citations et références nécessaires.
  3. Il lie chaque élément significatif à ses lignes de cartographie.
  4. Il produit dans le format demandé, si autorisé pour le type.
- **Variantes et erreurs** : éléments bloqués → version **provisoire** avec emplacements identifiés et motifs, jamais de contenu inventé (CL-018) ; format non autorisé → blocage ou proposition des formats permis (CL-019) ; suppression d'un élément obligatoire → interdite sans autorisation explicite.
- **Sorties** : version provisoire ou complète du livrable.
- **Postconditions** : le livrable n'est pas encore conforme ; il passe en contrôle qualité.
- **Liens** : RF-115 à RF-126 ; RB-075 ; CA-063 à CA-070. **Priorité** : MVP.

#### UC-012 — Exécuter les contrôles qualité

- **Acteurs** : Agent.
- **Déclencheur** : production terminée, ou reprise après correction.
- **Préconditions** : catalogue de contrôles applicable (Annexe B).
- **Entrées** : version de livrable ; contrôles obligatoires ; règles.
- **Parcours nominal** :
  1. L'Agent exécute tous les contrôles obligatoires.
  2. Il enregistre pour chacun résultat, éléments examinés, règle, date.
  3. Il traite les échecs via UC-013.
  4. Si tous les contrôles obligatoires ont réussi, la version peut être déclarée **conforme**.
- **Variantes et erreurs** : contrôle non exécutable → ne vaut pas réussite (CL-020) ; contrôle méthodologique sans règle explicite → non applicable ; interdiction de modifier les choix méthodologiques pour obtenir la cohérence (CL-021).
- **Sorties** : résultats de contrôle ; statut de conformité.
- **Postconditions** : conformité attribuée uniquement si tous les contrôles obligatoires ont réussi.
- **Liens** : RF-127 à RF-142 ; RB-045 à RB-047, RB-053 à RB-055, RB-112 ; RT-053 à RT-060 ; CA-071 à CA-076. **Priorité** : MVP.

#### UC-013 — Traiter les anomalies

- **Acteurs** : Agent ; personne responsable.
- **Déclencheur** : un contrôle échoue ou une anomalie est détectée.
- **Préconditions** : résultats de contrôle disponibles.
- **Entrées** : anomalies ; règles de correction automatique autorisée.
- **Parcours nominal** :
  1. L'Agent classe l'anomalie (AN-1, AN-2, AN-3).
  2. Si une règle autorise explicitement la correction mécanique, il corrige, trace, puis rejoue les contrôles concernés.
  3. Sinon, si la correction exige interprétation ou décision, il suspend l'opération concernée et sollicite la personne habilitée.
  4. Les anomalies non couvertes par les règles sont consignées comme observations.
- **Variantes et erreurs** : boucle de correction non convergente → escalade (CL-022) ; observation non justifiant modification (CL-023).
- **Sorties** : anomalies classées ; corrections tracées ; observations consignées.
- **Postconditions** : aucune correction sans règle ; contrôles rejoués après correction.
- **Liens** : RF-143 à RF-154 ; RB-048 à RB-052, RB-056 ; CA-077 à CA-084. **Priorité** : MVP.

#### UC-014 — Finaliser et remettre le livrable et ses rapports

- **Acteurs** : Agent ; demandeur.
- **Déclencheur** : tous les contrôles obligatoires ont réussi.
- **Préconditions** : version conforme.
- **Entrées** : version conforme ; résultats de contrôle ; traçabilité.
- **Parcours nominal** :
  1. L'Agent produit le livrable final, le rapport de conformité et le rapport de traçabilité, selon les règles du type.
  2. Il lie les trois éléments entre eux et à la version précise.
  3. Il rend la version immuable.
  4. Il présente clairement le statut : conformité acquise, approbation et diffusion non déduites.
  5. Il indique les actions restantes.
- **Variantes et erreurs** : rapport non exigé par les règles → mention dans le rapport de conformité (CL-024) ; tentative d'annoncer la réussite trop tôt → interdite (CL-025).
- **Sorties** : livrable, rapport de conformité, rapport de traçabilité.
- **Postconditions** : version finalisée immuable ; statut d'approbation Non soumise (ou Non requise, simple constat que les règles du type n'exigent pas d'approbation) ; statut de diffusion Non autorisée ; aucun des deux n'est déduit de la conformité.
- **Liens** : RF-155 à RF-172 ; RB-109 à RB-112, RB-117 ; RT-043 à RT-052 ; CA-085 à CA-094. **Priorité** : MVP.

#### UC-015 — Approuver un livrable

- **Acteurs** : personne responsable (approbateur unique au MVP, RF-174) ; Agent.
- **Déclencheur** : une version est finalisée et les règles du type de livrable exigent une approbation.
- **Préconditions** : version à l'état **Finalisée** (donc Conforme, IV-05) ; statut d'approbation Non soumise.
- **Entrées** : version ; rapport de conformité ; réserves ; observations ; décisions antérieures.
- **Parcours nominal** :
  1. L'Agent vérifie que la version est finalisée et conforme, puis la soumet à l'approbateur (statut En attente d'approbation).
  2. L'Agent présente le dossier d'approbation (Annexe D.5).
  3. La personne responsable approuve ou refuse, avec un motif en cas de refus.
  4. L'Agent enregistre la décision, liée à la version précise.
- **Variantes et erreurs** : approbation sollicitée pour une version non finalisée ou non conforme → **impossible** ; l'Agent explique qu'il faut d'abord corriger ou réviser (CL-027) ; refus → motif consigné, version intacte, diffusion impossible pour cette version, révision possible (UC-017, CL-026) ; erreur découverte après approbation → l'approbation n'est pas révoquée, une révision crée une nouvelle version (CL-063) ; approbation non exigée par les règles → statut Non requise, ce cas d'usage n'est pas déclenché.
- **Sorties** : statut d'approbation de la version.
- **Postconditions** : approbation (ou refus) définitive pour cette version ; **statut de conformité inchangé** ; statut de diffusion inchangé (RF-273, RF-277).
- **Liens** : RF-173 à RF-178, RF-272 à RF-274 ; RB-109 à RB-113, RB-123 à RB-126 ; CA-095 à CA-099, CA-177 à CA-179. **Priorité** : MVP.

#### UC-016 — Autoriser la diffusion d'un livrable

- **Acteurs** : personne responsable ; Agent ; destinataires (PU-03).
- **Déclencheur** : demande de diffusion ou décision de livraison pour une version finalisée.
- **Préconditions** : version **Finalisée** (donc Conforme) ; statut d'approbation « Approuvée » ou « Non requise » ; destinataires désignés.
- **Entrées** : version ; destinataires ; périmètre ; restrictions applicables.
- **Parcours nominal** :
  1. L'Agent vérifie les prérequis (version finalisée, approbation obtenue ou non requise).
  2. Il vérifie les restrictions de confidentialité et de diffusion (AU-4) pour chaque destinataire.
  3. La personne responsable autorise la diffusion pour une version, des destinataires, un périmètre et des éléments exclus précisés.
  4. L'Agent enregistre l'autorisation et rend le livrable accessible, dans le produit, aux seuls destinataires désignés ; il ne transmet rien hors du produit (RF-278).
- **Variantes et erreurs** : version provisoire ou non conforme → **impossible** au MVP (CL-061) ; approbation requise en attente ou refusée → impossible (CL-062) ; droits incertains → suspension de l'opération concernée (CL-028) ; révocation → l'accessibilité cesse dans le produit, les copies déjà obtenues ne sont pas concernées et l'Agent le mentionne (CL-029) ; *V2, sous réserve de QO-036 : diffusion exceptionnelle d'une version non conforme (RF-280).*
- **Sorties** : statut de diffusion de la version.
- **Postconditions** : **conformité et approbation inchangées** (RF-277) ; aucun accès pour un destinataire non autorisé.
- **Liens** : RF-179 à RF-184, RF-275 à RF-279 (RF-280 en V2) ; RB-057, RB-058, RB-114, RB-115, RB-126, RB-128 ; CA-100 à CA-104, CA-180 à CA-186. **Priorité** : MVP.

#### UC-017 — Réviser un livrable (nouvelle version)

- **Acteurs** : utilisateur ordinaire ou personne responsable (demandeur de la révision) ; Agent.
- **Déclencheur** : demande **explicite** de révision d'un livrable existant (correction, nouvelle information, changement de règle voulu, retour d'approbation).
- **Préconditions** : au moins une version finalisée ; droits du demandeur sur le livrable.
- **Entrées** : version de référence ; motif de révision ; modifications souhaitées.
- **Parcours nominal** :
  1. L'Agent enregistre la demande de révision et son motif.
  2. Il réalise l'analyse d'impact : éléments concernés, contrôles à rejouer, livrables liés.
  3. Il détermine les versions de modèle, règles et registre à utiliser (d'origine par défaut, QO-032).
  4. Il crée une **nouvelle version** sans toucher à la précédente.
  5. Il rejoue les contrôles applicables et suit le cycle (UC-012 à UC-014).
  6. Il produit un récapitulatif des différences avec la version précédente.
- **Variantes et erreurs** : version déjà approuvée → jamais écrasée silencieusement (CL-030) ; règles modifiées depuis → pas d'application automatique (CL-031).
- **Sorties** : nouvelle version ; analyse d'impact ; différences.
- **Postconditions** : version précédente intacte et consultable ; statuts de la nouvelle version propres (conformité, approbation, diffusion remis à zéro).
- **Liens** : RF-185 à RF-198 ; RB-067 à RB-076 ; CA-105 à CA-114, CA-191. **Priorité** : MVP.

#### UC-018 — Suspendre une demande

- **Acteurs** : utilisateur ordinaire (initiative), personne responsable ; Agent.
- **Déclencheur** : interruption à l'initiative de l'utilisateur, ou attente prolongée imposant une mise en suspens.
- **Préconditions** : demande non finalisée et non annulée.
- **Entrées** : demande en cours ; règles de conservation.
- **Parcours nominal** :
  1. L'Agent arrête les opérations en cours.
  2. Il préserve les éléments autorisés à l'être.
  3. Il distingue les résultats validés des résultats provisoires.
  4. Il passe la demande à **Suspendue**.
  5. Il communique ce qui est conservé et les conditions de reprise.
- **Variantes et erreurs** : interruption pendant un calcul ou un contrôle → l'opération en cours est considérée comme non aboutie (CL-032) ; travail inachevé → jamais présenté comme livrable final.
- **Sorties** : état de travail suspendu.
- **Postconditions** : demande Suspendue ; non finalisée.
- **Liens** : RF-199 à RF-205 ; RB-081, RB-083, RB-084, RB-086 ; CA-115 à CA-120. **Priorité** : MVP.

#### UC-019 — Reprendre une demande suspendue

- **Acteurs** : utilisateur ordinaire, personne responsable ; Agent.
- **Déclencheur** : demande de reprise.
- **Préconditions** : demande Suspendue ; conservation encore valable.
- **Entrées** : état de travail suspendu.
- **Parcours nominal** :
  1. L'Agent vérifie la validité des sources, informations, règles et autorisations susceptibles d'avoir changé.
  2. Il conserve les éléments toujours valides.
  3. Il réexécute les opérations affectées et les contrôles nécessaires.
  4. Il informe l'utilisateur de ce qui a changé et de ses conséquences.
  5. La demande retrouve l'état correspondant à l'avancement réel.
- **Variantes et erreurs** : source ou règle modifiée pendant la suspension (CL-033) ; conservation expirée → reprise impossible (CL-034).
- **Sorties** : demande reprise ; synthèse des changements.
- **Postconditions** : aucun élément devenu invalide n'est réutilisé.
- **Liens** : RF-206 à RF-209 ; RB-082, RB-087, RB-088 ; RT-009 ; CA-121 à CA-124, CA-193. **Priorité** : MVP.

#### UC-020 — Annuler définitivement une demande

- **Acteurs** : auteur de la demande ou personne responsable ; Agent.
- **Déclencheur** : demande explicite d'annulation définitive.
- **Préconditions** : demande non Finalisée (de l'état Reçue à l'état Suspendue).
- **Parcours nominal** :
  1. L'Agent distingue annulation définitive (irréversible) et suspension (reprise possible), et demande une confirmation explicite.
  2. Après confirmation, il arrête toute opération.
  3. Il passe la demande à **Annulée définitivement** et ses versions provisoires à **Abandonnée**.
  4. Il conserve le travail réalisé selon les règles de conservation (aucune suppression automatique au MVP), sans le présenter comme un livrable.
- **Variantes et erreurs** : absence de confirmation → la demande est suspendue et non annulée (CL-035) ; demande émanant d'une personne autre que l'auteur ou la personne responsable → refusée ; demande Finalisée → annulation impossible, les versions finalisées, approuvées ou diffusées restent inchangées (CL-036) ; annulation d'une demande de révision liée → sans effet sur la demande d'origine.
- **Sorties** : demande annulée ; trace de l'annulation.
- **Postconditions** : reprise impossible ; une nouvelle demande est nécessaire.
- **Liens** : RF-210 à RF-212 ; RB-085, RB-088 ; CA-125, CA-126, CA-187, CA-188. **Priorité** : MVP. **Statut** : [P] (PV-13).

#### UC-021 — Coordonner des livrables multiples

- **Acteurs** : Agent.
- **Déclencheur** : plusieurs livrables demandés dans la même opération.
- **Préconditions** : cadre de la « même opération » défini (QO-026).
- **Parcours nominal** :
  1. L'Agent identifie les dépendances entre livrables.
  2. Il gère chaque livrable individuellement (statuts propres).
  3. Il vérifie la cohérence entre les documents.
  4. Il évalue les conséquences des changements sur les éléments concernés.
- **Variantes et erreurs** : livrable dépendant d'un livrable bloqué (CL-037) ; incohérence entre documents → AN-2 ou AN-3, sans modification automatique d'un livrable déjà produit (CL-038).
- **Sorties** : livrables coordonnés ; synthèse de cohérence.
- **Postconditions** : aucun livrable produit modifié sans révision explicite.
- **Liens** : RF-213 à RF-218 ; RB-094, RB-095 ; CA-127 à CA-130. **Priorité** : V2.

#### UC-022 — Prioriser des demandes concurrentes

- **Acteurs** : Agent ; personne responsable.
- **Déclencheur** : plusieurs demandes se disputent les mêmes ressources ou échéances.
- **Entrées** : échéances ; urgences validées ; importance autorisée ; dépendances ; ressources disponibles.
- **Parcours nominal** :
  1. L'Agent applique les critères explicites.
  2. S'ils permettent de trancher, il ordonne les demandes et informe chaque demandeur.
  3. Sinon, il prépare les éléments d'arbitrage et sollicite la personne responsable.
- **Variantes et erreurs** : urgence déclarée mais non validée → ignorée (CL-039) ; règles insuffisantes (CL-040).
- **Sorties** : ordre de traitement ; justification communicable.
- **Postconditions** : aucune priorité implicite.
- **Liens** : RF-219 à RF-224 ; RB-089 à RB-091, RB-096 ; CA-131 à CA-134. **Priorité** : V2.

#### UC-023 — Suivre l'avancement d'une demande

- **Acteurs** : utilisateur ordinaire, personne responsable.
- **Déclencheur** : l'utilisateur demande où en est sa demande, ou l'Agent l'informe d'un changement.
- **Préconditions** : droits de suivi sur la demande.
- **Parcours nominal** :
  1. L'Agent présente les étapes terminées, en cours, les motifs communicables, les éléments attendus et la prochaine action.
  2. Il distingue tâches terminées, suspendues, bloquées, en attente de décision, finalisées.
  3. Il présente séparément conformité, approbation et diffusion.
  4. Il n'expose aucune information protégée.
- **Variantes et erreurs** : utilisateur sans droit sur certaines sources → motif général (CL-041).
- **Sorties** : message d'état.
- **Postconditions** : aucune annonce de réussite avant contrôle ou validation.
- **Liens** : RF-225 à RF-238 ; RB-064, RB-065, RB-117, RB-120, RB-122 ; CA-135 à CA-144. **Priorité** : MVP.

#### UC-024 — Arbitrer une décision non couverte

- **Acteurs** : personne responsable ; Agent.
- **Déclencheur** : une décision substantielle est nécessaire et n'est pas couverte par les règles.
- **Parcours nominal** :
  1. L'Agent suspend l'opération concernée et poursuit les tâches de diagnostic ou indépendantes.
  2. Il formule la demande de décision : question, contexte, options issues des règles, conséquences, urgence.
  3. La personne responsable décide.
  4. L'Agent enregistre la décision (décideur, date, objet, périmètre, motif) et reprend l'opération.
- **Variantes et erreurs** : personne responsable indisponible (CL-042) ; décision hors périmètre de la demande → passe par UC-027.
- **Sorties** : décision tracée.
- **Postconditions** : la décision vaut pour l'objet et la demande, pas comme règle générale.
- **Liens** : RF-239 à RF-244 ; RB-003 à RB-005, RB-033, RB-097, RB-098, RB-106 à RB-108 ; CA-145 à CA-147, CA-192. **Priorité** : MVP.

#### UC-025 — Autoriser ponctuellement une source

- **Acteurs** : personne responsable ; Agent.
- **Déclencheur** : une information obligatoire est absente des sources permanentes et une source non inscrite pourrait la fournir.
- **Parcours nominal** :
  1. L'Agent sollicite l'autorisation en précisant source, demande, niveaux requis.
  2. La personne responsable accorde (ou non) l'autorisation, par niveau (AU-1 à AU-4), pour une demande et une durée.
  3. L'Agent enregistre l'autorisation ; le registre permanent n'est **pas** modifié.
- **Variantes et erreurs** : accès accordé sans intégration (CL-043).
- **Sorties** : autorisation ponctuelle tracée.
- **Postconditions** : la source n'est utilisable que dans le périmètre accordé.
- **Liens** : RF-245 à RF-249 ; RB-013, RB-014 ; CA-148, CA-149. **Priorité** : MVP.

#### UC-026 — Gérer le registre permanent des sources

- **Acteurs** : personne responsable.
- **Déclencheur** : ajout, modification ou retrait d'une source permanente.
- **Parcours nominal** :
  1. La personne responsable applique la procédure explicite de modification.
  2. L'Agent versionne le registre et date la modification.
  3. Les productions antérieures conservent le registre en vigueur à leur création.
- **Variantes et erreurs** : retrait d'une source pendant des demandes en cours (CL-044).
- **Sorties** : nouvelle version du registre.
- **Postconditions** : aucune modification implicite.
- **Liens** : RF-250 à RF-253 ; CA-150, CA-151. **Priorité** : MVP (minimal).

#### UC-027 — Gérer modèles, règles et préférences

- **Acteurs** : personne responsable.
- **Déclencheur** : besoin de créer ou modifier un modèle, une règle ou une préférence.
- **Parcours nominal** :
  1. La personne responsable engage la procédure explicite.
  2. L'Agent présente l'analyse d'impact (demandes en cours, productions liées).
  3. La modification est approuvée avec une date d'effet explicite, puis versionnée.
- **Variantes et erreurs** : exemple contredisant une règle → la règle prévaut, observation signalée (CL-045) ; modification pendant une demande en cours → sans effet automatique (CL-046).
- **Sorties** : nouvelle version de modèle ou de règle.
- **Postconditions** : productions antérieures inchangées.
- **Liens** : RF-254 à RF-259 ; RB-006, RB-010, RB-011, RB-103 à RB-105 ; CA-152, CA-153. **Priorité** : MVP.

#### UC-028 — Gérer une exception

- **Acteurs** : personne responsable.
- **Déclencheur** : besoin de déroger ponctuellement à une règle.
- **Parcours nominal** :
  1. L'Agent explique la règle concernée et la conséquence de la dérogation.
  2. La personne responsable accorde l'exception, ponctuelle et motivée.
  3. L'Agent applique l'exception à l'élément visé et la mentionne en réserve dans le rapport de conformité.
- **Variantes et erreurs** : exception sur une restriction de droits de tiers (CL-047).
- **Sorties** : exception tracée.
- **Postconditions** : aucun précédent créé.
- **Liens** : RF-260 à RF-263, RF-281 ; RB-101, RB-127 ; CA-154, CA-194. **Priorité** : V2.

#### UC-029 — Traiter une correction ponctuelle ou une proposition de règle

- **Acteurs** : utilisateur ordinaire ; personne responsable ; Agent.
- **Déclencheur** : l'utilisateur corrige un résultat ou suggère une règle.
- **Parcours nominal** :
  1. L'Agent applique la correction à la demande en cours si elle est compatible avec les règles.
  2. Il informe l'utilisateur que la correction ne vaut que pour cette demande.
  3. Si l'utilisateur propose une évolution de règle, l'Agent la consigne et la transmet à la personne responsable, sans effet avant décision.
- **Variantes et erreurs** : insistance pour généraliser (CL-048).
- **Sorties** : correction appliquée localement ; proposition consignée.
- **Postconditions** : aucune règle modifiée implicitement.
- **Liens** : RF-264 à RF-267 ; RB-010, RB-102 ; CA-155, CA-156. **Priorité** : V2.

#### UC-030 — Consulter la traçabilité et l'historique

- **Acteurs** : utilisateur ordinaire (auteur de la demande, sous réserve de ses droits), personne responsable. *Extension V2 : profil d'auditeur dédié (PU-05), en lecture seule, pour des demandes dont il n'est pas l'auteur.*
- **Déclencheur** : demande de consultation.
- **Parcours nominal** :
  1. L'Agent restitue, selon les droits, la chaîne source → information → transformations et calculs → élément du livrable.
  2. Il restitue l'historique (états, décisions, versions, contrôles).
  3. Les éléments protégés sont remplacés par une mention générique.
- **Variantes et erreurs** : lecteur sans droit sur une source (CL-049).
- **Sorties** : traçabilité et historique consultés.
- **Postconditions** : aucune modification possible de l'historique.
- **Liens** : RF-268 à RF-271 ; RT-027 à RT-042, RT-061 à RT-068 ; CA-169 à CA-176. **Priorité** : MVP.

#### UC-031 — Appliquer la minimisation et le masquage des données sensibles

- **Acteurs** : Agent.
- **Déclencheur** : insertion d'informations dans un livrable.
- **Préconditions** : règles de minimisation applicables (QO-014).
- **Parcours nominal** :
  1. L'Agent identifie les données personnelles et sensibles.
  2. Il ne reprend que les données nécessaires, autorisées pour l'usage et permises pour les destinataires.
  3. Il masque ou exclut les autres selon les règles, et trace l'opération.
- **Variantes et erreurs** : masquage rendant un élément obligatoire incohérent (CL-050) ; reconstitution par recoupement (CL-051) ; cas non couvert → décision non couverte.
- **Sorties** : contenu minimisé ; trace.
- **Postconditions** : aucune donnée non permise dans le livrable pour ses destinataires.
- **Liens** : RT-017 à RT-026 ; RB-060, RB-061, RB-066 ; CA-157 à CA-168. **Priorité** : MVP.

---

## 5. Parcours fonctionnels détaillés

Les parcours décrivent des scénarios de bout en bout. Ils s'appuient sur les cas d'usage et les états de la section 8.

### PA-01 — Parcours nominal : livrable produit sans blocage

| # | Étape | Cas d'usage | État de la demande | Remarque |
|---|---|---|---|---|
| 1 | L'utilisateur soumet sa demande. | UC-001 | Reçue | — |
| 2 | L'Agent déduit les paramètres du contexte et des règles. | UC-001 | Reçue | Aucune question inutile. |
| 3 | Faisabilité acquise ; versions de modèle et règles figées. | UC-003 | En vérification de faisabilité | — |
| 4 | Mobilisation auprès d'INIS puis des sources autorisées. | UC-004 | En production | — |
| 5 | Cartographie et évaluation de la qualité. | UC-005, UC-006 | En production | Toutes les lignes produisibles. |
| 6 | Transformations et calculs autorisés. | UC-009, UC-010 | En production | Tout est tracé. |
| 7 | Production du livrable. | UC-011 | En production | — |
| 8 | Contrôles obligatoires : tous réussis. | UC-012 | En contrôle qualité | Conformité acquise. |
| 9 | Finalisation : livrable, rapport de conformité, rapport de traçabilité. | UC-014 | Finalisée | Approbation et diffusion **non** déduites. |
| 10 | Approbation si requise ; autorisation de diffusion. | UC-015, UC-016 | Finalisée | Décisions humaines distinctes. |

### PA-02 — Information obligatoire absente d'INIS

1. L'Agent interroge INIS : information absente (lacune consignée).
2. Il recherche l'information dans les autres sources du registre permanent.
3. Si trouvée : évaluation de qualité (UC-006) ; si QI-01, la ligne devient satisfaite.
4. Si non trouvée : il demande à la personne responsable une autorisation ponctuelle d'une source (UC-025), ou demande l'information à l'utilisateur (UC-007).
5. Si toujours indisponible : les éléments dépendants restent **bloqués** ; le reste de la production continue.
6. La demande n'est pas finalisable tant que les éléments obligatoires sont bloqués.

États traversés : En production → (blocage partiel) → En production / En attente d'une décision humaine.

### PA-03 — Contradiction non tranchée par les règles

1. L'Agent détecte deux informations incompatibles pour le même élément.
2. Il vérifie si la divergence s'explique par la portée ou la période.
3. Il applique les règles de priorité : aucune ne tranche.
4. Il identifie les éléments dépendants ; l'information est indispensable : ils sont **bloqués**.
5. Il constitue le dossier d'arbitrage et sollicite la personne responsable.
6. Pendant l'attente, les opérations indépendantes se poursuivent.
7. La personne responsable arbitre ; la décision est tracée, limitée à la demande.
8. Les éléments débloqués reprennent ; les contrôles concernés sont exécutés.

### PA-04 — Décision non couverte par les règles

1. L'Agent constate qu'un choix méthodologique est nécessaire (par exemple choisir un indicateur) et qu'aucune règle ne le couvre.
2. Il suspend l'opération concernée ; il ne choisit pas.
3. Il poursuit le diagnostic et les vérifications autorisées.
4. Il formule la question à la personne habilitée.
5. La décision est enregistrée ; si elle doit valoir pour l'avenir, la personne responsable engage une procédure de changement de règle (UC-027).

### PA-05 — Suspension et reprise

1. L'utilisateur interrompt sa demande en cours de production.
2. L'Agent arrête les opérations, préserve l'état, distingue validé et provisoire : **Suspendue**.
3. Des semaines plus tard, l'utilisateur demande la reprise.
4. L'Agent vérifie ce qui a changé (sources, informations, règles, autorisations).
5. Il conserve ce qui est valide, réexécute ce qui est affecté, rejoue les contrôles nécessaires.
6. Il informe l'utilisateur des changements et reprend le cycle.

### PA-06 — Révision d'un livrable approuvé

1. L'utilisateur demande explicitement une révision d'une version approuvée.
2. L'Agent réalise l'analyse d'impact.
3. Il crée une nouvelle version ; la version approuvée n'est ni modifiée ni écrasée.
4. La nouvelle version suit le cycle complet de contrôle ; ses statuts (conformité, approbation, diffusion) partent de zéro.
5. Un récapitulatif des différences est produit.
6. La version précédente reste consultable.

### PA-07 — Livrables multiples avec dépendances (V2)

1. Plusieurs livrables sont demandés dans la même opération.
2. L'Agent identifie les dépendances (par exemple un tableau de suivi qui reprend les indicateurs d'un protocole).
3. Chaque livrable suit son propre cycle et ses propres statuts.
4. Un livrable dépendant d'un livrable bloqué est bloqué pour la partie concernée.
5. L'Agent vérifie la cohérence entre documents ; les incohérences sont signalées, jamais corrigées dans un livrable déjà produit sans révision explicite.

### PA-08 — Demandes concurrentes (V2)

1. Deux demandes se disputent la même échéance.
2. L'Agent applique les critères : échéance, urgence validée, importance autorisée, dépendances, ressources.
3. Si les critères tranchent, il ordonne et informe les demandeurs avec un motif communicable.
4. Sinon, il prépare les éléments d'arbitrage pour la personne responsable.

### PA-09 — Accès ou diffusion restreints

1. L'Agent identifie qu'une source n'est pas accessible à l'interlocuteur.
2. Il bloque l'élément concerné.
3. Il explique le blocage en termes généraux, sans révéler l'existence, l'identité ou le contenu de la source protégée.
4. La personne responsable, qui a les droits, peut lever le blocage (autorisation ponctuelle ou arbitrage).

### PA-10 — Correction mécanique autorisée

1. Un contrôle détecte une non-conformité avérée (par exemple un format de date contraire à la règle).
2. Une règle autorise explicitement la correction mécanique de ce défaut.
3. L'Agent corrige, trace (avant, après, règle) et rejoue les contrôles concernés.
4. Si le contrôle réussit, le cycle se poursuit ; sinon, escalade (borne du nombre de cycles).

---
## 6. Exigences fonctionnelles (RF)

Les exigences sont formulées au présent de l'obligation : « l'Agent doit… ». Chaque ligne précise sa référence au cahier, son statut ([D] décidé, [P] proposition, [Q] question ouverte) et sa priorité.

### 6.A — Réception et compréhension de la demande (UC-001)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RF-001 | L'Agent doit accepter toute demande de livrable formulée en langage naturel par un utilisateur autorisé. | §5-É1, §7 | [D] | MVP |
| RF-002 | L'Agent doit enregistrer chaque demande dès sa réception avec un identifiant stable, l'auteur, la date et l'heure, et le texte d'origine inchangé. | §3.4 | [P] | MVP |
| RF-003 | L'Agent doit identifier le type de livrable demandé et le distinguer de son format de fichier. | §5-É1, §9 | [D] | MVP |
| RF-004 | L'Agent doit identifier l'objectif, le contexte, la finalité et les contraintes exprimés dans la demande. | §5-É1 | [D] | MVP |
| RF-005 | L'Agent doit identifier les paramètres nécessaires à la production (destinataires, échéance, période de référence, format de sortie, périmètre). | §5-É1 | [D] | MVP |
| RF-006 | L'Agent doit déterminer les paramètres à partir du contexte autorisé et des règles applicables avant de les demander à l'utilisateur. | §5-É1 | [D] | MVP |
| RF-007 | L'Agent doit distinguer les instructions propres à la demande des règles permanentes, et ne jamais traiter une instruction ponctuelle comme une modification de règle. | §4, §3.6 | [D] | MVP |
| RF-008 | L'Agent doit détecter une demande portant sur plusieurs livrables. Au MVP, il n'effectue pas de traitement coordonné : il informe l'utilisateur et propose, sur confirmation, de traiter chaque livrable par une demande distincte et indépendante. Le traitement coordonné relève de la V2 (RF-213 à RF-215). | §6.6 | [P] | MVP |
| RF-009 | L'Agent doit vérifier que l'utilisateur est autorisé à soumettre ce type de demande avant tout traitement de fond. | §8 | [D] | MVP |
| RF-010 | L'Agent doit reformuler sa compréhension de la demande, implicitement ou explicitement, lorsque cette reformulation est nécessaire à la validation de la compréhension. | §7 | [D] | MVP |

### 6.B — Clarification (UC-002)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RF-011 | L'Agent ne doit poser une question que lorsqu'une ambiguïté restante a une incidence significative sur la conformité ou la validité du livrable. | §5-É1 | [D] | MVP |
| RF-012 | L'Agent ne doit pas poser une question dont la réponse peut être déterminée par le contexte autorisé et les règles. | §5-É1 | [D] | MVP |
| RF-013 | L'Agent doit poser des questions ciblées plutôt que présenter systématiquement de longs formulaires. | §7 | [D] | MVP |
| RF-014 | L'Agent doit indiquer, pour chaque question, en quoi la réponse conditionne le livrable. | §7 | [P] | MVP |
| RF-015 | L'Agent doit hiérarchiser les questions : les bloquantes d'abord ; les non bloquantes sont regroupées ou différées. | §7 | [P] | MVP |
| RF-016 | La demande doit passer à l'état En clarification dès qu'une question est posée ; l'Agent peut poursuivre les opérations indépendantes de la réponse. | §5-É7 (par analogie) | [P] | MVP |
| RF-017 | Une réponse de l'utilisateur doit être enregistrée comme information fournie par l'utilisateur, source identifiée de statut initial QI-02 (candidate), et jamais comme une règle. Elle ne devient QI-01 que si une règle du type de livrable l'autorise pour cette catégorie d'information, ou sur décision explicite de la personne responsable pour la demande. | §6.10, §8 | [P] | MVP |
| RF-018 | Si l'utilisateur ne répond pas ou si sa réponse reste ambiguë, l'Agent ne doit pas faire à sa place un choix substantiel ; l'élément dépendant reste en attente ou bloqué. | §3.2 | [D] | MVP |

### 6.C — Vérification de la faisabilité (UC-003)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RF-019 | Avant toute production, l'Agent doit vérifier l'existence d'un modèle documentaire et de règles applicables au type de livrable. | §5-É2 | [D] | MVP |
| RF-020 | L'Agent doit vérifier la disponibilité des informations nécessaires. | §5-É2 | [D] | MVP |
| RF-021 | L'Agent doit vérifier les autorisations d'accès et d'utilisation. | §5-É2 | [D] | MVP |
| RF-022 | L'Agent doit identifier les exigences obligatoires du livrable. | §5-É2 | [D] | MVP |
| RF-023 | L'Agent doit recenser les contradictions déjà identifiées. | §5-É2 | [D] | MVP |
| RF-024 | L'Agent doit vérifier les conditions préalables à la production. | §5-É2 | [D] | MVP |
| RF-025 | Si une condition indispensable n'est pas satisfaite, l'Agent doit bloquer la partie concernée et expliquer le motif communicable. | §5-É2 | [D] | MVP |
| RF-026 | L'Agent peut exécuter les opérations de diagnostic ou de vérification qui restent autorisées malgré un blocage. | §5-É2, §6.5 | [D] | MVP |
| RF-027 | L'Agent doit produire un diagnostic de faisabilité structuré distinguant ce qui est réalisable, ce qui doit être clarifié et ce qui est bloqué, avec les motifs. | §5-É4 (par analogie) | [P] | MVP |
| RF-028 | L'Agent doit déterminer les versions applicables du modèle, des règles et du registre des sources, et les figer pour la demande. | §6.8 | [D] | MVP |
| RF-029 | Lorsqu'aucun modèle n'existe pour le type demandé, l'Agent ne doit pas improviser de structure ; il bloque et sollicite la personne responsable. | §3.2, §6.5 | [D] | MVP |
| RF-030 | L'Agent doit pouvoir réaliser, à la demande de l'utilisateur, un diagnostic de faisabilité sans produire le livrable. | §5-É2 (par analogie) | [P] | V2 |

### 6.D — Mobilisation des informations et sources (UC-004, UC-025, UC-026)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RF-031 | L'Agent doit rechercher les informations nécessaires uniquement dans les sources autorisées. | §5-É3 | [D] | MVP |
| RF-032 | L'Agent doit interroger INIS en priorité pour les informations qu'INIS peut fournir. | §5-É3 | [D] | MVP |
| RF-033 | Lorsqu'une information obligatoire est absente d'INIS, l'Agent peut consulter d'autres sources explicitement autorisées. | §5-É3 | [D] | MVP |
| RF-034 | L'Agent ne doit jamais consulter une source non autorisée, même si elle paraît pertinente. | §3.5, §5-É3 | [D] | MVP |
| RF-035 | Les sources autorisées sont celles du registre permanent ou celles autorisées ponctuellement par la personne responsable. | §5-É3 | [D] | MVP |
| RF-036 | Une autorisation ponctuelle ne doit pas modifier le registre permanent. | §5-É3 | [D] | MVP |
| RF-037 | L'autorisation de consulter une source ne vaut ni validité ni droit d'utilisation de toutes les informations qu'elle contient ; l'Agent doit évaluer chaque information. | §5-É3 | [D] | MVP |
| RF-038 | L'Agent doit distinguer, pour chaque source, les niveaux d'autorisation d'accès, d'utilisation, d'intégration et de diffusion. | §3.5 | [D] | MVP |
| RF-039 | L'Agent doit enregistrer, pour chaque information mobilisée : source, référence précise, date de consultation et, lorsqu'ils sont disponibles, période de référence et statut de validation attribué par la source. | §3.4 | [D] | MVP |
| RF-040 | L'Agent doit conserver les informations mobilisées dans leur forme d'origine, distincte des versions transformées. | §3.4 | [P] | MVP |
| RF-041 | L'Agent ne doit pas inventer de méthode de recherche ; il applique les méthodes et critères définis par les règles. | §3.2 | [D] | MVP |
| RF-042 | Lorsqu'une source est indisponible, l'Agent doit le signaler, poursuivre auprès des autres sources autorisées et ne pas conclure à l'absence de l'information. | §5-É3 | [P] | MVP |
| RF-043 | Les informations fournies directement par l'utilisateur ou par pièces jointes doivent être traitées comme des informations à source identifiée (« fournie par l'utilisateur »), soumises aux mêmes évaluations de qualité et d'autorisation, avec le statut initial défini en RF-017. | §8 | [P] | MVP |
| RF-044 | L'Agent doit tenir un journal des interrogations de sources (source, objet, résultat, date), y compris les consultations infructueuses. | §3.4 | [P] | MVP |

### 6.E — Cartographie des exigences et des informations (UC-005)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RF-045 | Avant toute rédaction, l'Agent doit établir une correspondance structurée entre les exigences du livrable et les informations disponibles. | §5-É4 | [D] | MVP |
| RF-046 | La cartographie doit couvrir chaque section, champ, tableau ou élément significatif exigé. | §5-É4 | [D] | MVP |
| RF-047 | Pour chaque ligne, l'Agent doit préciser l'exigence à satisfaire. | §5-É4 | [D] | MVP |
| RF-048 | Pour chaque ligne, l'Agent doit préciser l'information nécessaire. | §5-É4 | [D] | MVP |
| RF-049 | Pour chaque ligne, l'Agent doit préciser l'information effectivement disponible. | §5-É4 | [D] | MVP |
| RF-050 | Pour chaque ligne, l'Agent doit préciser la source et la référence correspondantes. | §5-É4 | [D] | MVP |
| RF-051 | Pour chaque ligne, l'Agent doit préciser le statut de validation. | §5-É4 | [D] | MVP |
| RF-052 | Pour chaque ligne, l'Agent doit préciser les transformations éventuellement nécessaires. | §5-É4 | [D] | MVP |
| RF-053 | Pour chaque ligne, l'Agent doit préciser les informations manquantes, les contradictions et les incertitudes. | §5-É4 | [D] | MVP |
| RF-054 | Pour chaque ligne, l'Agent doit préciser les dépendances susceptibles de bloquer l'élément. | §5-É4 | [D] | MVP |
| RF-055 | À l'issue de la cartographie, l'Agent doit déterminer et présenter ce qui peut être produit, ce qui doit être clarifié et ce qui reste bloqué. | §5-É4 | [D] | MVP |
| RF-056 | Une correspondance incertaine entre une information source et un champ cible doit être signalée et non résolue arbitrairement. | §5-É6 | [D] | MVP |
| RF-057 | La cartographie doit être mise à jour à chaque changement qui l'affecte (nouvelle information, résolution, décision) et conserver ses versions successives. | §6.8 | [P] | MVP |
| RF-058 | La cartographie doit être consultable, selon les droits, par l'utilisateur et par la personne responsable, et faire partie des éléments de traçabilité. | §5-É11 | [P] | MVP |

### 6.F — Qualité des informations (UC-006)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RF-059 | L'Agent doit évaluer chaque information selon des critères explicites définis par les règles. | §5-É5 | [D] | MVP |
| RF-060 | L'Agent doit classer chaque information dans l'un des statuts QI-01 à QI-07. | §5-É5 | [D] | MVP |
| RF-061 | L'Agent ne doit pas considérer une information issue d'INIS comme automatiquement fiable. | §5-É5 | [D] | MVP |
| RF-062 | Lorsque la fiabilité ou la pertinence d'une information est incertaine, l'Agent doit chercher à la vérifier auprès de sources autorisées. | §5-É5 | [D] | MVP |
| RF-063 | Tant que la vérification n'a pas abouti, l'Agent ne doit pas présenter l'information comme un fait établi. | §5-É5 | [D] | MVP |
| RF-064 | L'Agent doit évaluer le statut de qualité en fonction de l'usage prévu et de la période de référence. | §6.2 | [D] | MVP |
| RF-065 | L'Agent doit appliquer les règles de validité propres à chaque catégorie d'information. | §6.2 | [D] | MVP |
| RF-066 | L'Agent ne doit pas privilégier systématiquement l'information la plus récente. | §5-É7 | [D] | MVP |
| RF-067 | Une information ancienne peut être retenue pour une analyse historique ; elle ne doit pas être utilisée pour décrire la situation actuelle. | §6.2 | [D] | MVP |
| RF-068 | L'Agent doit exclure du livrable les informations interdites ou non autorisées pour l'usage prévu. | §5-É5 | [D] | MVP |
| RF-069 | Lorsque les règles permettent d'intégrer une information non QI-01, l'Agent doit la qualifier explicitement dans le livrable. | §5-É5 | [P] | MVP |
| RF-070 | L'Agent doit enregistrer, pour chaque évaluation, les critères appliqués, le résultat, les sources de vérification et la date. | §3.4 | [P] | MVP |
| RF-071 | L'Agent doit réévaluer le statut d'une information lorsque la source, la règle, la période ou l'usage prévu change. | §6.9 | [P] | MVP |
| RF-072 | L'Agent doit signaler à l'utilisateur, avec un motif communicable, les informations de statut autre que QI-01 qui affectent des éléments obligatoires. | §7 | [P] | MVP |

### 6.G — Gestion des lacunes (UC-007)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RF-073 | L'Agent doit détecter et consigner toute information manquante pour une exigence du livrable. | §3.1, §5-É7 | [D] | MVP |
| RF-074 | Pour toute information manquante, l'Agent doit rechercher une source alternative lorsque cette recherche est autorisée. | §5-É7 | [D] | MVP |
| RF-075 | L'Agent ne doit pas combler une lacune par une déduction, une estimation, une valeur par défaut ou un contenu plausible qui ne provient pas d'une source ou d'une règle. | §3.1 | [D] | MVP |
| RF-076 | Si une information obligatoire demeure indisponible, les éléments qui en dépendent restent bloqués. | §3.1 | [D] | MVP |
| RF-077 | Si l'information manquante est facultative, l'Agent applique la règle du modèle (omission signalée ou mention d'indisponibilité). | §4 | [P] | MVP |
| RF-078 | L'Agent doit identifier les éléments dépendant de l'information manquante. | §5-É4 | [D] | MVP |
| RF-079 | L'Agent doit formuler une lacune à l'utilisateur sous forme de demande ciblée précisant l'information attendue et son usage. | §7 | [P] | MVP |
| RF-080 | L'Agent doit conserver l'historique d'une lacune résolue : recherches effectuées et résolution. | §3.4 | [P] | MVP |

### 6.H — Gestion des contradictions (UC-008)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RF-081 | L'Agent doit détecter les contradictions entre informations destinées au même élément. | §5-É7 | [D] | MVP |
| RF-082 | L'Agent doit appliquer les règles de priorité explicites pour résoudre une contradiction. | §5-É7 | [D] | MVP |
| RF-083 | L'Agent doit tenir compte du contexte, de la provenance, de la portée et de la période de référence des informations. | §5-É7 | [D] | MVP |
| RF-084 | L'Agent ne doit pas résoudre librement une contradiction non couverte par les règles. | §3.2 | [D] | MVP |
| RF-085 | Si la contradiction demeure irrésolue, l'Agent doit identifier les éléments qui en dépendent. | §5-É7 | [D] | MVP |
| RF-086 | Si l'information est indispensable, les éléments dépendants restent bloqués jusqu'à résolution. | §5-É7 | [D] | MVP |
| RF-087 | Les opérations indépendantes de la contradiction peuvent se poursuivre si les règles le permettent. | §5-É7 | [D] | MVP |
| RF-088 | L'Agent doit préparer pour la personne responsable un dossier d'arbitrage : informations en conflit, sources, contexte, portée, période, règles examinées, éléments impactés. L'Agent ne tranche pas. | §3.2, §8 | [P] | MVP |
| RF-089 | La résolution par la personne responsable doit être enregistrée comme décision tracée, avec date, motif et périmètre (la demande concernée uniquement). | §3.4 | [P] | MVP |
| RF-090 | Lorsqu'une divergence s'explique par une différence de portée ou de période reconnue par les règles, l'Agent doit la documenter comme telle plutôt que la traiter comme une contradiction. | §5-É7 | [P] | MVP |

### 6.I — Organisation et transformation des informations (UC-009, UC-031)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RF-091 | L'Agent doit organiser les informations disponibles selon le modèle documentaire et les règles applicables. | §5-É6 | [D] | MVP |
| RF-092 | L'Agent ne doit appliquer que les transformations éditoriales, structurelles et calculatoires autorisées. | §2, §5-É6 | [D] | MVP |
| RF-093 | L'Agent peut extraire des informations d'un document, lorsqu'une règle l'autorise (TF-01). | §5-É6 | [D] | MVP |
| RF-094 | L'Agent peut réorganiser des paragraphes ou des tableaux, lorsqu'une règle l'autorise (TF-02). | §5-É6 | [D] | MVP |
| RF-095 | L'Agent peut associer des champs sources à des champs cibles, lorsqu'une règle l'autorise (TF-03). | §5-É6 | [D] | MVP |
| RF-096 | L'Agent peut convertir des formats de dates, d'unités ou de fichiers selon des règles explicites (TF-04). | §5-É6 | [D] | MVP |
| RF-097 | L'Agent peut corriger des erreurs grammaticales ou typographiques lorsque cela est autorisé (TF-05). | §5-É6 | [D] | MVP |
| RF-098 | L'Agent peut reformuler fidèlement un contenu, lorsqu'une règle l'autorise (TF-06). | §5-É6 | [D] | MVP |
| RF-099 | L'Agent doit insérer les informations dans les sections prévues (TF-08). | §5-É6 | [D] | MVP |
| RF-100 | L'Agent doit générer les tableaux et annexes exigés (TF-09). | §5-É6 | [D] | MVP |
| RF-101 | L'Agent ne doit pas modifier le sens des informations, inventer des relations entre données ni transformer une hypothèse en fait établi. | §5-É6 | [D] | MVP |
| RF-102 | L'Agent doit tracer chaque transformation : opération, règle autorisante, entrée, sortie. | §3.4 | [D] | MVP |
| RF-103 | Une reformulation fidèle doit préserver le sens, la portée et les nuances (modalité, incertitude, conditions, périmètre). | §5-É6 | [P] | MVP |
| RF-104 | Une transformation non couverte par une règle explicite doit être refusée et traitée comme une décision non autorisée. | §3.2 | [D] | MVP |

### 6.J — Calculs et données dérivées (UC-010)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RF-105 | L'Agent ne doit effectuer aucun calcul ni aucune transformation numérique sans méthode explicitement définie. | §6.1 | [D] | MVP |
| RF-106 | Pour chaque résultat dérivé, l'Agent doit conserver les données d'entrée et leurs sources. | §6.1 | [D] | MVP |
| RF-107 | Pour chaque résultat dérivé, l'Agent doit conserver la formule ou la méthode. | §6.1 | [D] | MVP |
| RF-108 | Pour chaque résultat dérivé, l'Agent doit conserver les unités et conventions applicables. | §6.1 | [D] | MVP |
| RF-109 | Pour chaque résultat dérivé, l'Agent doit conserver les règles d'arrondi éventuelles. | §6.1 | [D] | MVP |
| RF-110 | Pour chaque résultat dérivé, l'Agent doit conserver le résultat. | §6.1 | [D] | MVP |
| RF-111 | Si la méthode nécessaire n'est pas définie, l'Agent doit demander une clarification ou bloquer l'élément concerné. | §6.1 | [D] | MVP |
| RF-112 | Un calcul doit être reproductible : mêmes entrées et même méthode donnent le même résultat. | §5-É9 | [D] | MVP |
| RF-113 | Un résultat dérivé ne doit pas avoir un statut de qualité supérieur au plus faible de ses entrées. | §5-É5 | [P] | MVP |
| RF-114 | Un résultat dérivé doit être identifié comme tel dans le livrable et dans la traçabilité, et ne jamais être présenté comme une donnée source. | §3.4 | [P] | MVP |

### 6.K — Production du livrable (UC-011)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RF-115 | L'Agent ne doit produire le livrable que lorsque les conditions nécessaires sont satisfaites. | §5-É8 | [D] | MVP |
| RF-116 | L'Agent doit produire le livrable conformément au modèle, aux règles de sélection et d'intégration, aux règles éditoriales, aux règles de calcul et de transformation, aux exigences de présentation et aux autorisations de confidentialité et de diffusion. | §5-É8 | [D] | MVP |
| RF-117 | Les sections, champs et éléments obligatoires ne doivent être ni supprimés ni modifiés sans autorisation explicite. | §5-É8 | [D] | MVP |
| RF-118 | Les adaptations de présentation ne sont permises que dans les limites prévues. | §5-É8 | [D] | MVP |
| RF-119 | L'Agent peut produire les éléments non bloqués avant la résolution des blocages, sous forme **provisoire** clairement marquée, jamais présentée comme livrable final. | §5-É7, §6.11 | [P] | MVP |
| RF-120 | Les éléments bloqués doivent apparaître comme tels dans une version provisoire (emplacement identifié et motif), sans contenu inventé. | §3.1 | [P] | MVP |
| RF-121 | Le livrable doit inclure les citations et références nécessaires à sa compréhension et à sa vérification. | §5-É11 | [D] | MVP |
| RF-122 | Chaque élément significatif du livrable doit être relié à ses lignes de cartographie et à ses sources. | §3.4 | [D] | MVP |
| RF-123 | L'Agent ne doit inclure aucun contenu qui ne se rattache ni à une information source, ni à un modèle, ni à une règle. | §3.1 | [D] | MVP |
| RF-124 | L'Agent doit appliquer les règles de minimisation, de masquage et d'exclusion lors de l'insertion des informations. | §6.3 | [D] | MVP |
| RF-125 | L'Agent doit produire le livrable dans le format demandé parmi les formats prévus (Word, PDF, Excel, PowerPoint, CSV, Markdown), dans la mesure où le type de livrable l'autorise. | §9 | [D] | MVP |
| RF-126 | Si le format demandé n'est pas autorisé pour le type de livrable, l'Agent doit bloquer ou proposer les formats autorisés, sans dégrader silencieusement le contenu. | §9 | [P] | MVP |

### 6.L — Contrôle qualité (UC-012)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RF-127 | Avant toute finalisation, l'Agent doit exécuter l'ensemble des contrôles obligatoires. | §5-É9 | [D] | MVP |
| RF-128 | Les contrôles obligatoires proviennent du modèle et des règles du type de livrable ; le catalogue minimal est donné en Annexe B (CT-01 à CT-12). | §5-É9 | [D] | MVP |
| RF-129 | L'Agent doit contrôler la présence des sections et champs obligatoires (CT-01). | §5-É9 | [D] | MVP |
| RF-130 | L'Agent doit contrôler l'utilisation du bon modèle et de la bonne version (CT-02). | §5-É9 | [D] | MVP |
| RF-131 | L'Agent doit contrôler la conformité des informations intégrées (CT-03). | §5-É9 | [D] | MVP |
| RF-132 | L'Agent doit contrôler la résolution des contradictions bloquantes (CT-04). | §5-É9 | [D] | MVP |
| RF-133 | L'Agent doit contrôler la validité des sources et des autorisations (CT-05). | §5-É9 | [D] | MVP |
| RF-134 | L'Agent doit contrôler la conformité des transformations éditoriales (CT-06). | §5-É9 | [D] | MVP |
| RF-135 | L'Agent doit contrôler la reproductibilité des calculs autorisés (CT-07). | §5-É9 | [D] | MVP |
| RF-136 | L'Agent doit contrôler la cohérence interne du document et la cohérence entre ses éléments (CT-08, CT-09). | §5-É9 | [D] | MVP |
| RF-137 | L'Agent doit contrôler la présence des références et traces exigées (CT-10). | §5-É9 | [D] | MVP |
| RF-138 | L'Agent doit contrôler le respect des restrictions de confidentialité et de diffusion (CT-11). | §5-É9 | [D] | MVP |
| RF-139 | Lorsque des règles explicites les définissent, l'Agent doit exécuter les contrôles méthodologiques de cohérence entre objectifs, questions, méthodes, variables, indicateurs, outils de collecte, résultats attendus et calendrier (CT-12). | §5-É9 | [D] | MVP |
| RF-140 | L'Agent ne doit pas inventer ni modifier des choix méthodologiques pour rendre le document artificiellement cohérent. | §5-É9 | [D] | MVP |
| RF-141 | Tous les contrôles obligatoires doivent réussir avant que le livrable puisse être déclaré conforme. | §5-É9 | [D] | MVP |
| RF-142 | Chaque contrôle doit produire un résultat (réussi, échoué, non exécutable, non applicable), les éléments examinés, la règle appliquée et la date. | §5-É9 | [P] | MVP |

### 6.M — Traitement des anomalies (UC-013)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RF-143 | L'Agent doit classer chaque anomalie : non-conformité avérée, incohérence établie, ou observation nécessitant une appréciation humaine. | §5-É10 | [D] | MVP |
| RF-144 | Une non-conformité avérée doit se rapporter à une règle explicite identifiée. | §5-É10 | [D] | MVP |
| RF-145 | L'Agent ne peut corriger automatiquement un défaut mécanique que si une règle l'autorise explicitement. | §5-É10 | [D] | MVP |
| RF-146 | Chaque correction automatique doit être tracée : état avant, état après, règle, date. | §5-É10 | [D] | MVP |
| RF-147 | Après une correction, l'Agent doit rejouer les contrôles concernés. | §5-É10 | [D] | MVP |
| RF-148 | Si la correction exige une interprétation ou une décision non autorisée, l'Agent doit suspendre l'opération concernée et solliciter la personne habilitée. | §5-É10 | [D] | MVP |
| RF-149 | L'Agent doit consigner comme observations les anomalies non couvertes par les règles. | §5-É10 | [D] | MVP |
| RF-150 | Une observation ne doit pas justifier, à elle seule, une modification du livrable. | §5-É10 | [D] | MVP |
| RF-151 | Les observations doivent figurer dans le rapport de conformité et être mises à disposition de la personne responsable. | §5-É11 | [P] | MVP |
| RF-152 | Les incohérences établies non corrigeables mécaniquement doivent être soumises à une décision humaine ; l'Agent ne doit pas les masquer. | §5-É9, §5-É10 | [D] | MVP |
| RF-153 | Le nombre de cycles correction puis contrôle doit être borné ; au-delà, l'Agent escalade à la personne responsable. | §5-É10 | [P] | MVP |
| RF-154 | Une correction ne doit jamais modifier le sens d'une information, ni effacer un résultat de contrôle antérieur : l'historique des résultats est conservé. | §3.4, §6.8 | [P] | MVP |

### 6.N — Finalisation, rapports et remise (UC-014)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RF-155 | La finalisation ne peut intervenir qu'après la réussite de tous les contrôles obligatoires. | §5-É9, §5-É11 | [D] | MVP |
| RF-156 | L'Agent doit produire trois éléments distincts lorsque les règles du livrable l'exigent : le livrable, le rapport de conformité, le rapport de traçabilité. | §5-É11 | [D] | MVP |
| RF-157 | Le livrable est le document final destiné à son public, avec les citations et références nécessaires à sa compréhension et à sa vérification. | §5-É11 | [D] | MVP |
| RF-158 | Le rapport de conformité doit présenter les contrôles effectués, leurs résultats, les éventuelles réserves et les conditions qui restent à satisfaire. | §5-É11 | [D] | MVP |
| RF-159 | Le rapport de traçabilité doit permettre de retrouver, pour chaque élément significatif, les sources, les références, le statut de validation, les transformations, les règles appliquées, les calculs éventuels, les autorisations pertinentes et l'historique de production. | §5-É11 | [D] | MVP |
| RF-160 | Le rapport de traçabilité ne doit pas être réduit à une bibliographie. | §5-É11 | [D] | MVP |
| RF-161 | L'Agent doit distinguer explicitement la conformité aux contrôles, l'approbation humaine éventuelle et l'autorisation de diffuser. | §5-É11 | [D] | MVP |
| RF-162 | Aucun de ces trois statuts ne doit être déduit automatiquement des deux autres. | §5-É11 | [D] | MVP |
| RF-163 | L'Agent ne doit jamais annoncer qu'un livrable est final, conforme, approuvé ou diffusable avant que les contrôles ou validations correspondants aient effectivement abouti. | §7 | [D] | MVP |
| RF-164 | La remise doit présenter le statut de la production, les réserves éventuelles et les actions restant à effectuer. | §2 (10) | [D] | MVP |
| RF-165 | La remise doit se limiter aux éléments que le destinataire de la remise est autorisé à recevoir (le rapport de traçabilité peut contenir des informations protégées). | §6.4 | [P] | MVP |
| RF-166 | Une version finalisée devient immuable. | §6.8 | [D] | MVP |
| RF-167 | Les trois éléments doivent être liés entre eux, à la version précise du livrable et aux versions de modèle et de règles utilisées. | §6.8 | [P] | MVP |
| RF-168 | Si les règles d'un type de livrable n'exigent pas certains éléments, l'Agent doit le consigner dans le rapport de conformité en citant la règle concernée. | §5-É11 | [P] | MVP |
| RF-169 | Le rapport de conformité doit mentionner explicitement les informations qualifiées (non QI-01) intégrées et toutes les réserves. | §5-É11 | [P] | MVP |
| RF-170 | Le rapport de conformité doit mentionner les décisions humaines prises, les exceptions autorisées et les observations. | §5-É11 | [P] | MVP |
| RF-171 | Un livrable provisoire doit être explicitement marqué comme non finalisé, quel que soit son format. | §6.11 | [D] | MVP |
| RF-172 | La remise doit indiquer les prochaines actions possibles (approbation, diffusion, révision). | §7 | [P] | MVP |

### 6.O — Approbation et diffusion (UC-015, UC-016)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RF-173 | L'Agent doit gérer l'approbation humaine comme un statut distinct, lorsque les règles du type de livrable l'exigent. | §5-É11 | [D] | MVP |
| RF-174 | Au MVP, l'approbation est donnée par la personne responsable seule, lorsque les règles du type de livrable l'exigent. D'autres approbateurs désignés par les règles relèvent de la V2. | §8 | [P] | MVP |
| RF-175 | L'Agent doit présenter à l'approbateur le livrable, le rapport de conformité, les réserves, les observations et les décisions antérieures. | §5-É11 | [P] | MVP |
| RF-176 | Une approbation porte sur une version précise du livrable, **finalisée et conforme**. | §6.8, §5-É11 | [D] / [P] | MVP |
| RF-177 | Une approbation ne vaut pas conformité et ne confère pas autorisation de diffuser. | §5-É11 | [D] | MVP |
| RF-178 | Un refus d'approbation doit être motivé et peut déclencher une révision. | §6.8 | [P] | MVP |
| RF-179 | L'autorisation de diffusion est un statut distinct, relevant des décisions de livraison réservées à la personne responsable. | §8 | [D] | MVP |
| RF-180 | L'autorisation de diffusion doit préciser la version, les destinataires ou catégories de destinataires, le périmètre et les éléments exclus. | §6.4 | [P] | MVP |
| RF-181 | Avant toute diffusion, l'Agent doit vérifier que les restrictions de confidentialité et de diffusion sont respectées pour chaque destinataire. | §6.3, §6.4 | [D] | MVP |
| RF-182 | En cas de droits de diffusion incertains, l'Agent doit suspendre l'opération concernée jusqu'à clarification. | §6.4 | [D] | MVP |
| RF-183 | Une autorisation de diffusion peut être révoquée ; la révocation est tracée. | §3.4 | [P] | MVP |
| RF-184 | L'Agent ne rend un livrable accessible à un destinataire autre que le demandeur que si la diffusion est autorisée pour ce destinataire. | §5-É11 | [P] | MVP |

#### Enchaînement des décisions et effets sur la conformité (compléments v0.2)

L'approbation et la diffusion sont **deux décisions distinctes** ; chacune est traitée séparément (voir aussi 9.6).

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RF-272 | L'Agent ne soumet une version à l'approbation que si elle est finalisée. Une version non finalisée ou non conforme ne peut être ni soumise à l'approbation ni approuvée ; l'Agent explique qu'elle doit d'abord être corrigée ou révisée. | §5-É11 | [P] | MVP |
| RF-273 | Une décision d'approbation ou de refus ne modifie jamais le statut de conformité : une version Conforme reste Conforme, et aucune approbation ne peut rendre conforme une version non conforme. | §5-É11 | [P] | MVP |
| RF-274 | Une approbation, comme un refus, est définitive pour sa version. Sa remise en cause passe par une révision (nouvelle version) et, pour la circulation du livrable, par la révocation de la diffusion. | §6.8 | [P] | MVP |
| RF-275 | L'Agent n'enregistre une autorisation de diffusion que pour une version finalisée dont le statut d'approbation est « Approuvée » ou « Non requise ». La diffusion d'une version provisoire ou non conforme est impossible au MVP. | §5-É11 | [P] | MVP |
| RF-276 | Une version dont l'approbation est « En attente » ou « Refusée » ne peut pas être diffusée. | §5-É11 | [P] | MVP |
| RF-277 | Une autorisation de diffusion, sa révocation ou sa modification ne modifient jamais le statut de conformité ni le statut d'approbation de la version. | §5-É11 | [P] | MVP |
| RF-278 | Au MVP, « diffuser » signifie rendre le livrable accessible, dans le produit, aux destinataires désignés et autorisés. L'Agent ne transmet aucun livrable hors du produit ; la transmission hors produit relève de la personne responsable, l'autorisation enregistrée en constituant la trace. La consultation d'une version provisoire par l'auteur de la demande et la personne responsable n'est pas une diffusion. | §5-É11 | [P] | MVP |
| RF-279 | La révocation d'une autorisation de diffusion met fin à l'accessibilité du livrable dans le produit pour les destinataires concernés. Elle ne s'étend pas aux copies obtenues avant la révocation ; l'Agent le mentionne au moment de la révocation. | §5-É11 | [P] | MVP |
| RF-280 | Diffusion exceptionnelle d'une version non finalisée ou non conforme : si elle est retenue en V2 (QO-036), elle n'est possible que sur décision explicite de la personne responsable, avec marquage visible dans le document et mention en réserve dans les rapports, sans effet sur le statut de conformité, qui reste « Non conforme ». | §5-É11 | [Q] (QO-036) | V2 |
| RF-281 | Une exception (RF-260 à RF-263) modifie la règle appliquée à un élément ; elle ne transforme jamais un contrôle échoué en contrôle réussi. La conformité s'apprécie par rapport aux règles telles qu'exceptées, et l'exception figure en réserve. | §8, §5-É9 | [P] | V2 |

### 6.P — Versions, historique et révision (UC-017)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RF-185 | Chaque production doit rester liée aux sources, règles et modèles utilisés au moment de sa création. | §6.8 | [D] | MVP |
| RF-186 | Les livrables existants sont immuables. | §6.8 | [D] | MVP |
| RF-187 | Une modification des règles ne doit pas modifier automatiquement les productions antérieures. | §6.8 | [D] | MVP |
| RF-188 | Toute révision demandée doit donner lieu à une nouvelle version. | §6.8 | [D] | MVP |
| RF-189 | Une version déjà approuvée ne doit jamais être écrasée silencieusement. | §6.8 | [D] | MVP |
| RF-190 | Une révision doit être explicitement déclenchée ; l'Agent ne révise jamais un livrable de sa propre initiative. | §6.6 | [D] | MVP |
| RF-191 | Avant une révision, l'Agent doit réaliser une analyse des impacts : éléments concernés, contrôles à rejouer, livrables liés. | §6.8 | [D] | MVP |
| RF-192 | La nouvelle version doit faire rejouer les contrôles applicables. | §6.8 | [D] | MVP |
| RF-193 | L'Agent doit conserver l'historique : versions, motifs de révision, auteurs, dates. | §6.8 | [D] | MVP |
| RF-194 | L'Agent doit produire un récapitulatif des différences entre deux versions (éléments ajoutés, modifiés, supprimés ; sources et règles changées). | §6.8 | [P] | V2 |
| RF-195 | Lors d'une révision, l'Agent doit utiliser par défaut les versions de modèle, de règles et de registre d'origine ; des versions plus récentes ne sont utilisées que sur décision explicite et tracée de la personne responsable. | §6.8 | [P] | MVP |
| RF-196 | Les statuts de conformité, d'approbation et de diffusion sont propres à chaque version ; une nouvelle version ne les hérite pas. | §5-É11 | [P] | MVP |
| RF-197 | Une version remplacée doit rester consultable et immuable. | §6.8 | [D] | MVP |
| RF-198 | L'Agent doit enregistrer le motif de la révision (correction d'erreur, nouvelle information, changement de règle, demande de l'utilisateur). | §6.8 | [P] | MVP |

### 6.Q — Suspension, reprise et annulation (UC-018, UC-019, UC-020)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RF-199 | L'Agent doit pouvoir suspendre une demande à l'initiative de l'utilisateur. | §6.11 | [D] | MVP |
| RF-200 | Une demande interrompue à l'initiative de l'utilisateur est suspendue, pour permettre une reprise ultérieure, sous réserve des règles de conservation. | §6.11 | [D] | MVP |
| RF-201 | À la suspension, l'Agent doit arrêter les opérations. | §6.11 | [D] | MVP |
| RF-202 | À la suspension, l'Agent doit préserver les éléments autorisés. | §6.11 | [D] | MVP |
| RF-203 | À la suspension, l'Agent doit distinguer les résultats validés des résultats provisoires. | §6.11 | [D] | MVP |
| RF-204 | L'Agent ne doit pas présenter un travail inachevé comme un livrable final. | §6.11 | [D] | MVP |
| RF-205 | Une demande suspendue conserve son état de travail dans les limites des règles de conservation et des autorisations applicables. | §6.9 | [D] | MVP |
| RF-206 | À la reprise, l'Agent doit vérifier la validité des sources, informations, règles et autorisations susceptibles d'avoir changé. | §6.9 | [D] | MVP |
| RF-207 | À la reprise, l'Agent doit conserver les éléments toujours valides. | §6.9 | [D] | MVP |
| RF-208 | À la reprise, l'Agent doit réexécuter les opérations affectées et les contrôles nécessaires. | §6.9 | [D] | MVP |
| RF-209 | À la reprise, l'Agent doit informer l'utilisateur de ce qui a changé depuis la suspension et de ses conséquences. | §7 | [P] | MVP |
| RF-210 | L'annulation définitive doit être distincte de la suspension. Au MVP, elle exige une action explicite et une confirmation explicite, peut être demandée par l'auteur de la demande ou par la personne responsable, et ne s'applique qu'à une demande non finalisée. | §6.11 | [P] | MVP |
| RF-211 | Après une annulation définitive, la demande ne peut plus être reprise ; une nouvelle demande est nécessaire. Les versions provisoires deviennent « Abandonnées » ; le travail réalisé est conservé selon les règles de conservation et n'est jamais présenté comme un livrable. Les versions finalisées restent inchangées. | §6.11 | [P] | MVP |
| RF-212 | Une demande suspendue ne constitue pas un livrable finalisé. | §6.9 | [D] | MVP |

### 6.R — Livrables multiples, priorités et indépendance des demandes (UC-021, UC-022)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RF-213 | Lorsque plusieurs livrables sont demandés dans la même opération, l'Agent doit coordonner leurs dépendances. | §6.6 | [D] | V2 |
| RF-214 | L'Agent doit vérifier la cohérence entre les différents documents. | §6.6 | [D] | V2 |
| RF-215 | L'Agent doit évaluer les conséquences d'un changement sur les éléments concernés. | §6.6 | [D] | V2 |
| RF-216 | L'Agent ne doit pas modifier automatiquement un livrable déjà produit ; une révision doit être explicitement déclenchée. | §6.6 | [D] | MVP |
| RF-217 | Les demandes sont traitées indépendamment : une modification d'information ne déclenche pas automatiquement la révision d'autres productions. | §6.10 | [D] | MVP |
| RF-218 | Une répercussion sur une autre production n'a lieu que lorsqu'elle est explicitement signalée ou lorsqu'une révision est demandée. | §6.10 | [D] | MVP |
| RF-219 | L'Agent doit organiser les priorités selon des critères explicites : échéances, urgence validée, importance autorisée, dépendances et ressources disponibles. | §6.7 | [D] | V2 |
| RF-220 | Si les règles ne permettent pas d'établir une priorité, l'Agent doit préparer les éléments utiles à l'arbitrage et solliciter la personne responsable. | §6.7 | [D] | V2 |
| RF-221 | Une urgence déclarée par un utilisateur n'est prise en compte que lorsqu'elle est validée. | §6.7 | [D] | V2 |
| RF-222 | L'Agent doit informer chaque demandeur de la position de sa demande et du motif communicable de l'ordre de traitement. | §7 | [P] | V2 |
| RF-223 | Dans une même opération, le statut de chaque livrable est géré individuellement : un livrable bloqué n'empêche pas ceux qui n'en dépendent pas. | §6.6 | [P] | V2 |
| RF-224 | L'Agent peut signaler, sans déclencher de révision, qu'une information modifiée a pu être utilisée dans d'autres productions, lorsqu'une règle de signalement l'autorise. Les modalités sont à définir. | §6.10 | [Q] (QO-020) | V2 |

### 6.S — Interaction et suivi (UC-023)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RF-225 | L'utilisateur doit pouvoir formuler sa demande en langage naturel sans connaître la structure interne (modèles, règles, étapes). | §7 | [D] | MVP |
| RF-226 | L'utilisateur autorisé doit pouvoir obtenir à tout moment l'état de sa demande. | §7 | [D] | MVP |
| RF-227 | L'Agent doit indiquer les étapes terminées. | §7 | [D] | MVP |
| RF-228 | L'Agent doit indiquer les étapes en cours. | §7 | [D] | MVP |
| RF-229 | L'Agent doit indiquer les motifs communicables des blocages. | §7 | [D] | MVP |
| RF-230 | L'Agent doit indiquer les éléments attendus (de l'utilisateur, de la personne responsable ou d'un tiers). | §7 | [D] | MVP |
| RF-231 | L'Agent doit indiquer la prochaine action. | §7 | [D] | MVP |
| RF-232 | L'Agent doit distinguer les tâches terminées, suspendues, bloquées, en attente de décision et finalisées. | §7 | [D] | MVP |
| RF-233 | L'Agent doit permettre de suivre l'avancement sans exposer d'informations protégées. | §7 | [D] | MVP |
| RF-234 | L'Agent doit expliquer les blocages selon les droits d'accès de l'interlocuteur. | §7 | [D] | MVP |
| RF-235 | L'Agent ne doit jamais annoncer la réussite d'une opération avant que les contrôles ou validations requis aient effectivement abouti (voir aussi RF-163). | §7 | [D] | MVP |
| RF-236 | Les messages d'état doivent utiliser le vocabulaire des états fonctionnels (section 8) sans le confondre avec les étapes internes de production. | §10 | [D] | MVP |
| RF-237 | Les statuts de conformité, d'approbation et de diffusion doivent toujours être présentés séparément. | §10, §5-É11 | [D] | MVP |
| RF-238 | L'utilisateur doit pouvoir consulter, selon ses droits, l'historique des échanges et des décisions de sa demande. | §6.8 | [P] | MVP |

### 6.T — Gouvernance : décisions, sources, règles, exceptions (UC-024 à UC-030)

#### Arbitrage et décisions non couvertes (UC-024)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RF-239 | Lorsqu'une décision substantielle non couverte par les règles est nécessaire, l'Agent doit suspendre l'opération concernée et solliciter la personne habilitée. | §3.2, §6.5 | [D] | MVP |
| RF-240 | L'Agent doit formuler la demande de décision de façon autonome et exploitable : question, contexte, options issues des règles, conséquences sur le livrable, urgence. | §6.7 | [P] | MVP |
| RF-241 | Une décision réservée n'est valable que si elle est prise par la personne responsable ; l'Agent doit en vérifier l'identité. | §8 | [D] | MVP |
| RF-242 | Chaque décision doit être enregistrée : décideur, date, objet, périmètre, motif, éléments impactés. | §3.4 | [P] | MVP |
| RF-243 | La portée d'une décision est limitée à son objet et à sa demande, sauf passage par la procédure de changement de règle. | §3.6 | [D] | MVP |
| RF-244 | Pendant l'attente d'une décision, l'Agent poursuit les tâches de diagnostic, de vérification ou indépendantes qui restent autorisées. | §6.5 | [D] | MVP |

#### Autorisation ponctuelle de source (UC-025)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RF-245 | La personne responsable peut autoriser ponctuellement une source absente du registre permanent. | §5-É3 | [D] | MVP |
| RF-246 | Une autorisation ponctuelle doit préciser la source, la demande concernée, les niveaux accordés (accès, utilisation, intégration, diffusion) et la durée. | §3.5 | [P] | MVP |
| RF-247 | Une autorisation ponctuelle ne modifie pas le registre permanent. | §5-É3 | [D] | MVP |
| RF-248 | Une autorisation ponctuelle doit figurer dans le rapport de traçabilité des productions concernées. | §5-É11 | [P] | MVP |
| RF-249 | Une autorisation ponctuelle prend fin avec la demande ou à la durée fixée, et n'est pas reconduite automatiquement pour d'autres demandes. | §5-É3 | [P] | MVP |

#### Registre permanent des sources (UC-026)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RF-250 | Le registre permanent des sources n'est modifié que par la personne responsable, selon une procédure explicite. | §3.6, §5-É3 | [D] | MVP |
| RF-251 | Chaque source du registre porte ses autorisations aux quatre niveaux, ses conditions, ses périodes de validité et ses restrictions. | §3.5 | [P] | MVP |
| RF-252 | Les modifications du registre sont versionnées et datées ; les productions antérieures conservent le registre en vigueur à leur création. | §6.8 | [D] | MVP |
| RF-253 | L'Agent doit pouvoir lister, selon les droits de l'interlocuteur, les sources autorisées pour un type de livrable donné. | §7 | [P] | V2 |

#### Modèles, règles et préférences (UC-027)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RF-254 | Les modèles et les règles ne sont créés ou modifiés que par une procédure explicite et par une personne habilitée. | §3.6 | [D] | MVP |
| RF-255 | Les règles et exigences formelles prévalent sur les exemples documentaires. | §3.3 | [D] | MVP |
| RF-256 | Lorsqu'un exemple contredit une règle, l'Agent applique la règle et signale l'incohérence comme observation à la personne responsable. | §3.3 | [P] | MVP |
| RF-257 | Les modèles et règles doivent être versionnés : chaque version est datée et porte son auteur et son motif. | §6.8 | [D] | MVP |
| RF-258 | Une modification de règle ou de modèle n'affecte automatiquement ni les productions antérieures ni les demandes en cours. | §6.8 | [D] | MVP |
| RF-259 | Les préférences suivent la même procédure explicite que les règles et les modèles. | §3.6 | [D] | MVP |

#### Exceptions (UC-028)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RF-260 | Seule la personne responsable peut autoriser une exception à une règle. | §8 | [D] | V2 |
| RF-261 | Une exception doit être explicite, ponctuelle, motivée, limitée à une demande ou un élément, et tracée. | §8 | [P] | V2 |
| RF-262 | Une exception ne modifie pas la règle et ne constitue pas un précédent. | §3.6 | [D] | V2 |
| RF-263 | Un livrable produit avec exception doit le mentionner dans le rapport de conformité à titre de réserve. | §5-É11 | [P] | V2 |

#### Corrections ponctuelles et absence d'apprentissage normatif implicite (UC-029)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RF-264 | Une correction ponctuelle apportée par un utilisateur ne doit jamais devenir automatiquement une règle générale. | §3.6 | [D] | V2 |
| RF-265 | Aucune règle, préférence ou modèle ne doit être modifié implicitement à partir de l'historique des interactions. | §3.6 | [D] | MVP |
| RF-266 | L'utilisateur peut proposer une évolution de règle ; la proposition est consignée et transmise à la personne responsable, sans effet normatif avant décision. | §3.6 | [P] | V2 |
| RF-267 | L'Agent doit informer l'utilisateur qu'une correction ponctuelle ne vaut que pour la demande en cours. | §3.6 | [P] | V2 |

#### Consultation de la traçabilité et de l'historique (UC-030)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RF-268 | Selon ses droits, un utilisateur ou la personne responsable doit pouvoir retrouver, pour tout élément significatif, la chaîne source, information, transformations ou calculs, élément du livrable. | §5-É11 | [D] | MVP |
| RF-269 | Selon ses droits, un utilisateur doit pouvoir consulter l'historique complet d'une demande (états, décisions, versions, contrôles). | §6.8 | [P] | MVP |
| RF-270 | Les consultations de traçabilité sont soumises aux restrictions de confidentialité : un lecteur sans droit sur une source voit une mention générique. | §6.4 | [D] | MVP |
| RF-271 | L'historique de production ne peut être modifié ni supprimé par un utilisateur ; toute correction s'ajoute sous forme d'entrée complémentaire. | §6.8 | [P] | MVP |

---
## 7. Règles métier (RB)

Les règles métier expriment les **invariants du domaine** que toute exigence fonctionnelle doit respecter. Elles s'appliquent quelle que soit la façon dont le produit sera réalisé.

### 7.1 Principes fondamentaux (RB-001 à RB-012)

| ID | Règle | Cahier | Statut |
|---|---|---|---|
| RB-001 | **Aucune invention.** L'Agent ne fabrique ni fait, ni chiffre, ni référence, ni résultat, ni décision, ni justification pour combler une lacune. | §3.1 | [D] |
| RB-002 | Une information manquante est signalée et recherchée auprès d'autres sources expressément autorisées. Si elle reste indisponible et qu'elle est obligatoire, les éléments qui en dépendent restent bloqués. | §3.1 | [D] |
| RB-003 | **Séparation information / décision.** L'Agent sélectionne et organise selon des règles établies ; il ne prend aucune décision substantielle non couverte par ces règles. | §3.2 | [D] |
| RB-004 | L'Agent ne doit pas inventer une méthode de recherche, choisir arbitrairement un indicateur, modifier une définition ni résoudre librement une contradiction. | §3.2 | [D] |
| RB-005 | Lorsqu'une décision non autorisée est nécessaire, l'Agent suspend l'opération concernée et sollicite la personne habilitée. | §3.2 | [D] |
| RB-006 | Les règles applicables et les exigences formelles prévalent sur les exemples documentaires, qui ne peuvent contredire une règle explicite. | §3.3 | [D] |
| RB-007 | **Traçabilité.** Toute information significative d'un livrable peut être reliée à sa source, à son statut de validation et aux transformations appliquées. | §3.4 | [D] |
| RB-008 | Les calculs et informations dérivées conservent leurs données d'entrée et leurs méthodes de production. | §3.4 | [D] |
| RB-009 | L'accès à une source, le droit d'utiliser son contenu, le droit de l'intégrer dans un livrable et le droit de diffuser ce livrable sont quatre autorisations distinctes, chacune respectée. | §3.5 | [D] |
| RB-010 | **Pas d'apprentissage normatif implicite.** Une correction ponctuelle ne devient pas automatiquement une règle générale. | §3.6 | [D] |
| RB-011 | Une règle, une préférence ou un modèle n'est modifié que par une procédure explicite et par une personne habilitée. | §3.6 | [D] |
| RB-012 | L'Agent se comporte comme un exécutant documentaire, non comme un consultant autonome. | §1 | [D] |

### 7.2 Qualité de l'information et sources (RB-013 à RB-026)

| ID | Règle | Cahier | Statut |
|---|---|---|---|
| RB-013 | Les sources utilisables sont celles du registre permanent et celles autorisées ponctuellement par la personne responsable. | §5-É3 | [D] |
| RB-014 | Une autorisation ponctuelle ne modifie pas le registre permanent. | §5-É3 | [D] |
| RB-015 | L'autorisation de consulter une source ne signifie pas que toutes ses informations sont valides ou utilisables. | §5-É3 | [D] |
| RB-016 | INIS est une source prioritaire, sans être l'unique source ; une information issue d'INIS n'est pas automatiquement fiable. | §5-É3, §5-É5 | [D] |
| RB-017 | À un instant donné, une information a un seul statut de qualité (QI) pour un usage prévu et une période de référence donnés. | §5-É5 | [P] |
| RB-018 | Seule une information QI-01 peut être présentée comme un fait établi. | §5-É5 | [D] |
| RB-019 | Pour toute information candidate ou incertaine, l'Agent tente de la vérifier auprès de sources autorisées ; tant que la vérification n'aboutit pas, elle n'est pas présentée comme un fait établi. | §5-É5 | [D] |
| RB-020 | La validité temporelle d'une information dépend de règles propres à chaque catégorie, de la période de référence, de la date d'application et de l'usage prévu. | §6.2 | [D] |
| RB-021 | Une information ancienne peut rester valide pour une analyse historique sans être utilisable pour décrire la situation actuelle. | §6.2 | [D] |
| RB-022 | L'information la plus récente n'est pas systématiquement prioritaire. | §5-É7 | [D] |
| RB-023 | Une correspondance incertaine entre une information source et un champ cible est signalée, non résolue arbitrairement. | §5-É6 | [D] |
| RB-024 | Une hypothèse n'est jamais transformée en fait établi. | §5-É6 | [D] |
| RB-025 | L'Agent n'invente aucune relation entre des données. | §5-É6 | [D] |
| RB-026 | Une information fournie par l'utilisateur est traitée comme une source identifiée, soumise aux mêmes évaluations ; son statut initial est QI-02 (RF-017). | §8 | [P] |

### 7.3 Lacunes et contradictions (RB-027 à RB-036)

| ID | Règle | Cahier | Statut |
|---|---|---|---|
| RB-027 | Toute lacune déclenche une recherche d'information alternative, lorsque celle-ci est autorisée. | §5-É7 | [D] |
| RB-028 | Une lacune obligatoire irrésolue bloque les éléments qui en dépendent. | §3.1 | [D] |
| RB-029 | Une lacune facultative est traitée selon la règle prévue au modèle. | §4 | [P] |
| RB-030 | Une contradiction est traitée par les règles de priorité explicites, en tenant compte du contexte, de la provenance, de la portée et de la période de référence. | §5-É7 | [D] |
| RB-031 | Une contradiction irrésolue bloque les éléments dépendants lorsque l'information est indispensable. | §5-É7 | [D] |
| RB-032 | Les opérations indépendantes d'une contradiction ou d'une lacune se poursuivent si les règles le permettent. | §5-É7 | [D] |
| RB-033 | Seule la personne responsable arbitre une contradiction que les règles ne résolvent pas. | §8 | [D] |
| RB-034 | Un arbitrage vaut pour la demande concernée, sauf changement de règle par procédure explicite. | §3.6 | [P] |
| RB-035 | Une divergence entièrement expliquée par des portées ou périodes différentes n'est pas une contradiction, lorsque les règles le reconnaissent. | §5-É7 | [P] |
| RB-036 | Le livrable ne masque jamais une contradiction non résolue et ne choisit jamais silencieusement l'une des informations. | §3.1, §3.2 | [D] |

### 7.4 Calculs et données dérivées (RB-037 à RB-044)

| ID | Règle | Cahier | Statut |
|---|---|---|---|
| RB-037 | Un calcul n'est autorisé que s'il est explicitement défini. | §6.1 | [D] |
| RB-038 | Pour chaque résultat dérivé : données d'entrée, sources, formule ou méthode, unités et conventions, règles d'arrondi, résultat. | §6.1 | [D] |
| RB-039 | Si la méthode nécessaire n'est pas définie, l'Agent demande une clarification ou bloque l'élément. | §6.1 | [D] |
| RB-040 | Un calcul est reproductible par rejeu. | §5-É9 | [D] |
| RB-041 | Une donnée dérivée est identifiée comme dérivée. | §3.4 | [P] |
| RB-042 | La qualité d'une donnée dérivée ne dépasse pas celle de ses entrées. | §5-É5 | [P] |
| RB-043 | La conversion d'unités, de dates ou de formats n'est faite que selon des règles explicites. | §5-É6 | [D] |
| RB-044 | En cas d'échec d'une méthode définie, l'Agent n'invente pas de formule de remplacement. | §6.5 | [D] |

### 7.5 Contrôles, anomalies et corrections (RB-045 à RB-056)

| ID | Règle | Cahier | Statut |
|---|---|---|---|
| RB-045 | Tous les contrôles obligatoires doivent réussir avant que le livrable puisse être déclaré conforme. | §5-É9 | [D] |
| RB-046 | Les contrôles méthodologiques ne portent que sur la cohérence des éléments lorsqu'ils sont définis par des règles explicites. | §5-É9 | [D] |
| RB-047 | L'Agent ne modifie pas les choix méthodologiques pour rendre le document artificiellement cohérent. | §5-É9 | [D] |
| RB-048 | Les anomalies se distinguent en non-conformités avérées, incohérences établies et observations. | §5-É10 | [D] |
| RB-049 | Un défaut mécanique n'est corrigé automatiquement que si une règle l'autorise explicitement. | §5-É10 | [D] |
| RB-050 | Toute correction est tracée et les contrôles concernés sont rejoués. | §5-É10 | [D] |
| RB-051 | Si la correction exige une interprétation ou une décision non autorisée, l'Agent suspend l'opération concernée et sollicite la personne habilitée. | §5-É10 | [D] |
| RB-052 | Les anomalies non couvertes par les règles sont consignées comme observations ; elles ne justifient pas, à elles seules, une modification. | §5-É10 | [D] |
| RB-053 | Un contrôle obligatoire échoué sur une exigence obligatoire empêche la déclaration de conformité tant qu'il n'est pas résolu. | §5-É9 | [D] |
| RB-054 | Un contrôle non exécutable n'est pas un contrôle réussi. | §5-É9 | [P] |
| RB-055 | L'Agent ne peut ni sauter, ni affaiblir, ni reconfigurer un contrôle obligatoire. | §3.6, §5-É9 | [D] |
| RB-056 | Des réserves peuvent subsister sans empêcher la conformité si elles proviennent de contrôles non obligatoires ou d'observations ; elles sont obligatoirement mentionnées dans le rapport de conformité. | §5-É11 | [P] |

### 7.6 Confidentialité, droits et données sensibles (RB-057 à RB-066)

| ID | Règle | Cahier | Statut |
|---|---|---|---|
| RB-057 | L'accès aux sources, l'utilisation de leur contenu, l'intégration dans un livrable et la diffusion du résultat sont contrôlés séparément. | §6.4 | [D] |
| RB-058 | Si les droits applicables sont incertains, l'Agent suspend l'opération concernée jusqu'à clarification. | §6.4 | [D] |
| RB-059 | Les explications de refus restent générales lorsqu'un détail supplémentaire risquerait de révéler l'existence, l'identité ou le contenu d'une source protégée. | §6.4 | [D] |
| RB-060 | Minimisation : l'Agent ne reprend que les données nécessaires, autorisées pour l'usage prévu et permises pour les destinataires concernés. | §6.3 | [D] |
| RB-061 | Les données non permises sont masquées ou exclues selon les règles applicables. | §6.3 | [D] |
| RB-062 | L'accès largement partagé aux actions ordinaires ne supprime ni les restrictions de confidentialité, ni les autorisations propres aux sources, ni les limites de diffusion. | §8 | [D] |
| RB-063 | Le rapport de traçabilité est lui-même soumis aux règles de confidentialité et de diffusion. | §6.4 | [P] |
| RB-064 | Chaque profil ne voit que ce que ses droits lui permettent, y compris l'état d'avancement. | §7 | [D] |
| RB-065 | Les motifs de blocage communicables varient selon le profil et les droits de l'interlocuteur. | §7 | [D] |
| RB-066 | La combinaison d'informations individuellement autorisées ne doit pas révéler ce qui est protégé. | §6.4 | [P] |

### 7.7 Versions, historique et immutabilité (RB-067 à RB-076)

| ID | Règle | Cahier | Statut |
|---|---|---|---|
| RB-067 | Les livrables existants sont immuables. | §6.8 | [D] |
| RB-068 | Chaque production reste liée aux sources, règles et modèles utilisés au moment de sa création. | §6.8 | [D] |
| RB-069 | Une modification des règles ne modifie pas automatiquement les productions antérieures. | §6.8 | [D] |
| RB-070 | Toute révision demandée donne lieu à une nouvelle version, avec analyse des impacts, contrôles applicables et conservation de l'historique. | §6.8 | [D] |
| RB-071 | Une version déjà approuvée n'est jamais écrasée silencieusement. | §6.8 | [D] |
| RB-072 | Une révision est explicitement déclenchée ; elle n'est jamais automatique. | §6.6 | [D] |
| RB-073 | Les statuts de conformité, d'approbation et de diffusion sont propres à chaque version. | §5-É11 | [P] |
| RB-074 | Une version remplacée reste consultable. | §6.8 | [P] |
| RB-075 | Une version provisoire n'est jamais présentée comme une version finale. | §6.11 | [D] |
| RB-076 | La numérotation des versions est séquentielle, sans trou et sans réutilisation. | §6.8 | [P] |

### 7.8 Blocage, suspension, reprise et annulation (RB-077 à RB-088)

| ID | Règle | Cahier | Statut |
|---|---|---|---|
| RB-077 | Un blocage est local à l'élément ou à l'opération concernés, sauf dépendance ; les opérations indépendantes se poursuivent. | §5-É2, §5-É7 | [D] |
| RB-078 | Tout blocage porte un motif communicable enregistré. | §5-É2 | [D] |
| RB-079 | Un blocage n'est levé que par la résolution de sa cause (information obtenue, décision, autorisation, clarification, règle). | §5-É7 | [P] |
| RB-080 | L'Agent ne contourne pas un blocage et n'invente pas de règle de remplacement. | §6.5 | [D] |
| RB-081 | Une demande suspendue conserve son état de travail dans les limites des règles de conservation. | §6.9 | [D] |
| RB-082 | À la reprise, l'Agent vérifie la validité de ce qui a pu changer, conserve ce qui est valide et rejoue ce qui est affecté. | §6.9 | [D] |
| RB-083 | Une demande suspendue n'est pas un livrable finalisé. | §6.9 | [D] |
| RB-084 | Une interruption à l'initiative de l'utilisateur entraîne une suspension. | §6.11 | [D] |
| RB-085 | L'annulation définitive est distincte de la suspension et irréversible. | §6.11 | [P] |
| RB-086 | À l'interruption ou à l'annulation, les résultats validés sont distingués des résultats provisoires. | §6.11 | [D] |
| RB-087 | Au MVP, aucune péremption automatique d'une suspension ; une durée maximale ne s'applique que si la personne responsable l'a fixée dans les règles de conservation. | §6.9 | [P] |
| RB-088 | Lorsqu'une durée de conservation fixée est expirée, les éléments non conservables sont supprimés ou anonymisés selon les règles ; la demande ne peut plus reprendre. | §6.9 | [P] |

### 7.9 Priorisation, livrables multiples et indépendance (RB-089 à RB-096)

| ID | Règle | Cahier | Statut |
|---|---|---|---|
| RB-089 | Les priorités s'établissent selon des critères explicites : échéances, urgence validée, importance autorisée, dépendances, ressources disponibles. | §6.7 | [D] |
| RB-090 | L'ordre d'arrivée ne sert de critère de départage que s'il est défini par une règle. | §6.7 | [P] |
| RB-091 | Si les règles ne permettent pas d'établir une priorité, l'Agent prépare les éléments d'arbitrage et sollicite la personne responsable. | §6.7 | [D] |
| RB-092 | Les demandes sont traitées indépendamment. | §6.10 | [D] |
| RB-093 | Aucune répercussion automatique ne s'opère entre productions ; elle exige un signalement explicite ou une révision demandée. | §6.10 | [D] |
| RB-094 | Pour des livrables multiples, l'Agent coordonne les dépendances, vérifie la cohérence entre documents et évalue les conséquences des changements. | §6.6 | [D] |
| RB-095 | L'Agent ne modifie jamais automatiquement un livrable déjà produit. | §6.6 | [D] |
| RB-096 | Une urgence non validée n'altère pas la priorité. | §6.7 | [D] |

### 7.10 Gouvernance, décisions et exceptions (RB-097 à RB-108)

| ID | Règle | Cahier | Statut |
|---|---|---|---|
| RB-097 | Une seule personne responsable est habilitée. | §8 | [D] |
| RB-098 | Elle seule arbitre les décisions sensibles, résout les conflits que les règles ne résolvent pas, autorise les exceptions, approuve les changements de règles et prend les décisions de livraison qui lui sont réservées. | §8 | [D] |
| RB-099 | Les utilisateurs ordinaires soumettent des demandes, fournissent des informations et suivent l'avancement, sous réserve de leurs droits. | §8 | [D] |
| RB-100 | « Personne habilitée » désigne la personne responsable, sauf règle explicite contraire. | §3.2, §8 | [P] |
| RB-101 | Une exception est explicite, ponctuelle et tracée. | §8 | [P] |
| RB-102 | Une correction d'utilisateur est ponctuelle. | §3.6 | [D] |
| RB-103 | Les préférences suivent la même procédure que les règles. | §3.6 | [D] |
| RB-104 | Un changement de règle approuvé a une date d'effet explicite et n'est pas rétroactif. | §6.8 | [P] |
| RB-105 | Un changement de règle ne s'applique pas aux demandes en cours sans décision explicite. | §6.8 | [P] |
| RB-106 | Toute décision humaine est tracée avec l'identité du décideur. | §3.4 | [P] |
| RB-107 | L'Agent n'attribue jamais à la place d'un humain un statut d'approbation, de diffusion ou d'arbitrage. | §5-É11 | [D] |
| RB-108 | Si la personne responsable est indisponible, aucune décision réservée n'est prise par un autre ; les éléments concernés restent en attente (aucune suppléance au MVP). | §8 | [P] |

### 7.11 Statuts de conformité, d'approbation et de diffusion (RB-109 à RB-116)

| ID | Règle | Cahier | Statut |
|---|---|---|---|
| RB-109 | Conformité aux contrôles, approbation humaine et autorisation de diffuser sont trois statuts distincts. | §5-É11 | [D] |
| RB-110 | Aucun de ces statuts n'est déduit automatiquement des deux autres. | §5-É11 | [D] |
| RB-111 | Les états fonctionnels ne se confondent ni avec les étapes internes de production ni avec les décisions d'approbation ou de diffusion. | §10 | [D] |
| RB-112 | La conformité exige la réussite de tous les contrôles obligatoires. | §5-É9 | [D] |
| RB-113 | L'approbation ne peut porter que sur une version **finalisée**, donc conforme. Une version non conforme ne peut pas être approuvée. | §5-É11 | [P] |
| RB-114 | L'autorisation de diffusion ne peut porter que sur une version finalisée (donc conforme) dont l'approbation est « Approuvée » ou « Non requise ». La diffusion d'une version non finalisée ou non conforme est impossible au MVP. | §5-É11 | [P] |
| RB-115 | L'autorisation de diffusion est propre à une version, à des destinataires et à un périmètre. | §6.4 | [P] |
| RB-116 | Une nouvelle version démarre avec des statuts remis à zéro. | §6.8 | [P] |

*Remarque sur RB-113 et RB-114 : exiger un prérequis (une version conforme avant approbation) n'est pas « déduire » un statut d'un autre. Le prérequis conditionne la possibilité de la décision humaine, il ne la remplace jamais.*

#### Compléments v0.2 : approbation, diffusion et conformité (RB-123 à RB-128)

| ID | Règle | Cahier | Statut |
|---|---|---|---|
| RB-123 | L'approbation et la diffusion ne modifient jamais le statut de conformité : seule l'exécution des contrôles le modifie. | §5-É11 | [P] |
| RB-124 | Une version non conforme n'a pas d'autre issue que la correction, le complément de production ou la révision ; elle ne peut être ni approuvée ni diffusée au MVP. | §5-É9, §5-É11 | [P] |
| RB-125 | L'approbation, comme le refus, est définitive pour sa version. | §6.8 | [P] |
| RB-126 | Une version dont l'approbation est refusée ou en attente ne peut pas être diffusée. | §5-É11 | [P] |
| RB-127 | Une exception ne transforme pas un contrôle échoué en contrôle réussi ; la conformité s'apprécie par rapport aux règles telles qu'exceptées, et l'exception est mentionnée en réserve. | §8, §5-É9 | [P] |
| RB-128 | Au MVP, la diffusion consiste à rendre le livrable accessible dans le produit ; l'Agent ne transmet aucun livrable hors du produit. | §5-É11 | [P] |

### 7.12 Communication et interaction (RB-117 à RB-122)

| ID | Règle | Cahier | Statut |
|---|---|---|---|
| RB-117 | L'Agent n'annonce jamais la réussite d'une opération avant que les contrôles ou validations requis aient abouti. | §7 | [D] |
| RB-118 | L'Agent réduit autant que possible la charge de clarification. | §7 | [D] |
| RB-119 | Les questions sont ciblées, nécessaires et hiérarchisées. | §7 | [D] |
| RB-120 | Les motifs de blocage sont formulés en termes compréhensibles par un utilisateur non technique. | §7 | [P] |
| RB-121 | Au MVP, les échanges et livrables sont rédigés en français, sauf indication contraire du modèle. | §1 | [P] |
| RB-122 | L'Agent ne présente jamais une incertitude comme une certitude dans sa communication. | §5-É5 | [P] |

---

## 8. États fonctionnels et transitions

### 8.1 Principe : plusieurs axes indépendants

Le cahier exige que les états fonctionnels ne soient **ni confondus avec les étapes internes de production, ni avec les décisions d'approbation ou de diffusion** (§10). La spécification retient donc **six axes d'états**, indépendants, portant sur des objets différents.

| Axe | Objet qualifié | États | Cahier |
|---|---|---|---|
| **R** — État de la demande | La demande | ST-R-01 à ST-R-10 | §10 |
| **C** — Conformité | Une version de livrable | ST-C-01 à ST-C-04 | §5-É11, §10 |
| **A** — Approbation | Une version de livrable | ST-A-01 à ST-A-05 | §5-É11, §10 |
| **D** — Diffusion | Une version de livrable | ST-D-01 à ST-D-03 | §5-É11, §10 |
| **V** — Version | Une version de livrable | ST-V-01 à ST-V-04 | §6.8, §6.11 |
| **E** — Élément | Un élément du livrable | ST-E-01 à ST-E-07 | §5-É4, §5-É7 |

Les **étapes internes** (mobilisation, cartographie, évaluation de la qualité, transformation, rédaction) sont des activités, pas des états : elles ne se présentent pas à l'utilisateur comme des états de la demande.

### 8.2 Axe R — État de la demande

| ID | État | Définition | Cahier | Statut |
|---|---|---|---|---|
| ST-R-01 | **Reçue** | La demande est enregistrée, la compréhension est en cours. | §10 | [D] |
| ST-R-02 | **En clarification** | L'Agent attend une réponse sur une ambiguïté significative. | §10 | [D] |
| ST-R-03 | **En vérification de faisabilité** | L'Agent vérifie les préalables avant production. | §10 | [D] |
| ST-R-04 | **En production** | L'Agent mobilise, cartographie, évalue, transforme, rédige. Des éléments peuvent être bloqués individuellement (axe E). | §10 | [D] |
| ST-R-05 | **En contrôle qualité** | La production est en cours de contrôle. | §10 | [D] |
| ST-R-06 | **Bloquée** | Aucune opération ne peut progresser tant qu'une cause de blocage n'est pas levée. | §10 | [D] |
| ST-R-07 | **En attente d'une décision humaine** | L'avancement dépend d'une décision de la personne responsable (ou d'une réponse requise). | §10 | [D] |
| ST-R-08 | **Suspendue** | Interrompue avec conservation de l'état de travail ; non finalisée. | §10, §6.9 | [D] |
| ST-R-09 | **Finalisée** | Une version du livrable a été finalisée, conforme, accompagnée de ses rapports. N'implique ni approbation ni autorisation de diffuser. | §7 (« finalisées ») | [P] |
| ST-R-10 | **Annulée définitivement** | Arrêt irréversible d'une demande **non finalisée**, sur action explicite et confirmée de son auteur ou de la personne responsable. | §10 | [P] |

**Origine de l'attente.** Pour revenir au bon état après une attente ou un blocage (TR-R-14, TR-R-23, TR-R-24, TR-R-26), l'Agent conserve l'état d'où la demande est entrée en attente ou en blocage. [P]

**Blocage partiel.** Une demande est **Bloquée** (ST-R-06) lorsque plus aucune opération ne peut avancer ; si seuls certains éléments sont bloqués, la demande reste **En production** et l'indicateur « avec éléments bloqués » est affiché. [P]

#### Transitions de l'axe R

| ID | De | Vers | Condition | Acteur | Statut |
|---|---|---|---|---|---|
| TR-R-01 | — | Reçue | Soumission d'une demande par un utilisateur autorisé | Utilisateur | [D] |
| TR-R-02 | Reçue | En clarification | Ambiguïté significative non déterminable | Agent | [D] |
| TR-R-03 | Reçue | En vérification de faisabilité | Paramètres suffisants | Agent | [D] |
| TR-R-04 | En clarification | En vérification de faisabilité | Réponses suffisantes | Agent | [D] |
| TR-R-05 | En vérification de faisabilité | En production | Faisable au moins en partie | Agent | [D] |
| TR-R-06 | En vérification de faisabilité | Bloquée | Aucune partie réalisable | Agent | [D] |
| TR-R-07 | En vérification de faisabilité | En attente d'une décision humaine | Décision non couverte ou droits incertains | Agent | [D] |
| TR-R-08 | En vérification de faisabilité | En clarification | Nouvelle ambiguïté révélée | Agent | [P] |
| TR-R-09 | En production | En contrôle qualité | Tous les éléments requis sont produits | Agent | [D] |
| TR-R-10 | En production | Bloquée | Plus aucune opération ne peut avancer | Agent | [D] |
| TR-R-11 | En production | En attente d'une décision humaine | Seule une décision humaine fait avancer | Agent | [D] |
| TR-R-12 | En production | En clarification | Seule une réponse de l'utilisateur fait avancer | Agent | [P] |
| TR-R-13 | Bloquée | En production | Cause levée | Agent | [D] |
| TR-R-14 | En attente d'une décision humaine | En production | Décision enregistrée, lorsque la demande était entrée en attente depuis En production | Personne responsable puis Agent | [D] |
| TR-R-15 | En clarification | En production | Réponse suffisante (si la faisabilité est déjà acquise) | Agent | [P] |
| TR-R-16 | En contrôle qualité | En production | Échec nécessitant un complément de production | Agent | [D] |
| TR-R-17 | En contrôle qualité | En attente d'une décision humaine | Correction exigeant une décision | Agent | [D] |
| TR-R-18 | En contrôle qualité | Finalisée | Tous les contrôles obligatoires réussis ; rapports produits | Agent | [D] |
| TR-R-19 | Tout état non final, sauf Suspendue | Suspendue | Interruption à l'initiative de l'utilisateur ou suspension ordonnée | Utilisateur ou personne responsable | [D] |
| TR-R-20 | Suspendue | État réévalué (En production, En clarification, En contrôle qualité, Bloquée ou En attente d'une décision humaine) | Reprise ; revalidation effectuée | Utilisateur puis Agent | [D] |
| TR-R-21 | Tout état non final (de Reçue à Suspendue) | Annulée définitivement | Action explicite **et** confirmation explicite ; impossible sur une demande Finalisée | Auteur de la demande ou personne responsable | [P] |
| TR-R-22 | Finalisée | (inchangée) | Une révision crée une **nouvelle demande liée** à l'état Reçue ; la demande finalisée reste Finalisée | Utilisateur | [P] |
| TR-R-23 | En attente d'une décision humaine | En vérification de faisabilité | Décision enregistrée, lorsque l'attente est née pendant la vérification de faisabilité | Personne responsable puis Agent | [P] |
| TR-R-24 | En attente d'une décision humaine | En contrôle qualité | Décision enregistrée, lorsque l'attente est née pendant le contrôle qualité | Personne responsable puis Agent | [P] |
| TR-R-25 | En attente d'une décision humaine | Bloquée | La décision ne lève pas la cause du blocage et plus aucune opération ne peut avancer | Agent | [P] |
| TR-R-26 | Bloquée | En vérification de faisabilité | Cause levée, lorsque le blocage est né pendant la vérification de faisabilité | Agent | [P] |
| TR-R-27 | Bloquée | En attente d'une décision humaine | La levée de la cause exige une décision | Agent | [P] |

**Transitions interdites** : Finalisée → tout autre état (dont Annulée définitivement) ; Annulée définitivement → tout autre état ; En production → Finalisée sans passer par En contrôle qualité ; Suspendue → Finalisée directement ; toute transition vers Finalisée sans version conforme.

### 8.3 Axe C — Conformité aux contrôles (par version)

| ID | État | Définition | Statut |
|---|---|---|---|
| ST-C-01 | **Non évalué** | Les contrôles n'ont pas été lancés (par exemple parce que des éléments obligatoires sont encore bloqués). | [P] |
| ST-C-02 | **En contrôle** | Les contrôles sont en cours. | [D] |
| ST-C-03 | **Non conforme** | Au moins un contrôle obligatoire a échoué ou n'est pas exécutable. | [P] |
| ST-C-04 | **Conforme aux contrôles** | Tous les contrôles obligatoires ont réussi. Des réserves non bloquantes peuvent subsister. | [D] |

| ID | De | Vers | Condition | Statut |
|---|---|---|---|---|
| TR-C-01 | Non évalué | En contrôle | Lancement des contrôles | [P] |
| TR-C-02 | En contrôle | Conforme | Tous les contrôles obligatoires réussis | [D] |
| TR-C-03 | En contrôle | Non conforme | Au moins un contrôle obligatoire échoué ou non exécutable | [P] |
| TR-C-04 | Non conforme | En contrôle | Après correction autorisée ou complément de production, contrôles rejoués | [D] |
| TR-C-05 | Conforme (version non encore finalisée) | En contrôle | La version est modifiée avant sa finalisation ; les contrôles sont rejoués | [P] |

**Seule l'exécution des contrôles modifie l'état de conformité** (IV-11). Une version finalisée ne change plus d'état de conformité (immutabilité) ; toute modification passe par une nouvelle version.

### 8.4 Axe A — Approbation (par version)

| ID | État | Définition | Statut |
|---|---|---|---|
| ST-A-01 | **Non soumise** | Aucune approbation n'a été demandée. C'est l'état de toute version non finalisée. | [P] |
| ST-A-02 | **Non requise** | Les règles du type de livrable n'exigent pas d'approbation (constat de règle, et non approbation). | [P] |
| ST-A-03 | **En attente d'approbation** | L'approbation est requise et sollicitée. | [D] |
| ST-A-04 | **Approuvée** | L'approbateur habilité a approuvé cette version. Définitif pour la version. | [D] |
| ST-A-05 | **Refusée** | L'approbateur a refusé, avec motif. Définitif pour la version. | [P] |

| ID | De | Vers | Condition | Statut |
|---|---|---|---|---|
| TR-A-01 | Non soumise | En attente d'approbation | Version **finalisée** (donc conforme), approbation exigée par les règles du type, soumission à l'approbateur (la personne responsable au MVP) | [P] |
| TR-A-02 | Non soumise | Non requise | À la finalisation, les règles du type n'exigent pas d'approbation | [P] |
| TR-A-03 | En attente d'approbation | Approuvée | Décision de l'approbateur habilité | [D] |
| TR-A-04 | En attente d'approbation | Refusée | Décision motivée | [P] |

Une version non finalisée ne peut quitter l'état Non soumise (RF-272). Un refus peut conduire à une révision, c'est-à-dire à une **nouvelle version** ; l'état Refusée n'évolue pas.

### 8.5 Axe D — Autorisation de diffusion (par version)

| ID | État | Définition | Statut |
|---|---|---|---|
| ST-D-01 | **Diffusion non autorisée** | État par défaut de toute version, y compris provisoire. | [P] |
| ST-D-02 | **Diffusion autorisée** | Autorisée pour des destinataires et un périmètre précisés. | [D] |
| ST-D-03 | **Autorisation révoquée** | L'autorisation a été retirée ; la révocation est tracée. | [P] |

| ID | De | Vers | Condition | Statut |
|---|---|---|---|---|
| TR-D-01 | Non autorisée | Autorisée | Décision de la personne responsable. Prérequis : version **finalisée**, approbation « Approuvée » ou « Non requise », droits de diffusion vérifiés pour chaque destinataire | [D] pour la décision, [P] pour les prérequis |
| TR-D-02 | Autorisée | Révoquée | Décision de la personne responsable | [P] |
| TR-D-03 | Révoquée | Autorisée | Nouvelle décision explicite, mêmes prérequis | [P] |
| TR-D-04 | Autorisée | Autorisée (périmètre modifié) | Nouvelle décision de la personne responsable modifiant destinataires, périmètre ou éléments exclus ; tracée | [P] |

### 8.6 Axe V — Version

| ID | État | Définition | Statut |
|---|---|---|---|
| ST-V-01 | **Provisoire** | Non finalisée, modifiable par l'Agent dans le cycle de production. Jamais présentée comme finale. Le reste pendant une suspension. | [D] |
| ST-V-02 | **Finalisée** | Immuable. | [D] |
| ST-V-03 | **Remplacée** | Une version ultérieure du même livrable a été finalisée ; reste immuable et consultable. | [P] |
| ST-V-04 | **Abandonnée** | Version provisoire d'une demande annulée définitivement ; conservée selon les règles de conservation, jamais présentée comme un livrable. | [P] |

| ID | De | Vers | Condition | Statut |
|---|---|---|---|---|
| TR-V-01 | Provisoire | Finalisée | Finalisation de la demande (TR-R-18) : tous les contrôles obligatoires réussis, rapports produits | [D] |
| TR-V-02 | Finalisée | Remplacée | Une version ultérieure du même livrable est finalisée | [P] |
| TR-V-03 | Provisoire | Abandonnée | Annulation définitive de la demande (TR-R-21) | [P] |

### 8.7 Axe E — Élément du livrable

| ID | État | Définition | Statut |
|---|---|---|---|
| ST-E-01 | **À produire** | Exigence identifiée, non encore traitée. | [P] |
| ST-E-02 | **Produit (provisoire)** | Contenu produit, non encore contrôlé. | [P] |
| ST-E-03 | **Bloqué** | Impossible à produire (voir MB). | [D] |
| ST-E-04 | **En attente de clarification ou de décision** | Dépend d'une réponse ou d'une décision. | [P] |
| ST-E-05 | **Contrôlé conforme** | Contrôles applicables réussis. | [P] |
| ST-E-06 | **Non conforme** | Au moins un contrôle obligatoire échoué. | [P] |
| ST-E-07 | **Non applicable** | Sans objet pour cette demande selon les règles. | [P] |

| ID | De | Vers | Condition | Statut |
|---|---|---|---|---|
| TR-E-01 | À produire | Produit (provisoire) | Conditions de production satisfaites ; élément produit | [P] |
| TR-E-02 | À produire | Bloqué | Cause de blocage (Annexe C) | [D] |
| TR-E-03 | À produire | En attente de clarification ou de décision | Ambiguïté ou décision requise | [P] |
| TR-E-04 | À produire | Non applicable | Une règle écarte l'exigence pour cette demande | [P] |
| TR-E-05 | Bloqué | À produire | Cause levée | [P] |
| TR-E-06 | En attente de clarification ou de décision | À produire | Réponse ou décision reçue | [P] |
| TR-E-07 | Produit (provisoire) | Contrôlé conforme | Contrôles applicables réussis | [P] |
| TR-E-08 | Produit (provisoire) | Non conforme | Contrôle obligatoire échoué | [P] |
| TR-E-09 | Non conforme | Produit (provisoire) | Correction autorisée ou complément de production ; contrôles à rejouer | [P] |
| TR-E-10 | Contrôlé conforme | Produit (provisoire) | L'élément ou ses entrées sont modifiés (correction, reprise) ; recontrôle nécessaire | [P] |
| TR-E-11 | Produit (provisoire) | Bloqué | Une cause de blocage apparaît après la production (par exemple une source invalidée à la reprise) | [P] |

### 8.8 Invariants d'états

| ID | Invariant | Cahier | Statut |
|---|---|---|---|
| IV-01 | À tout instant, une demande a exactement un état sur l'axe R ; chaque version a exactement un état sur chacun des axes C, A, D, V. | §10 | [P] |
| IV-02 | Les axes C, A et D sont indépendants : aucun statut n'est déduit d'un autre. Un prérequis (par exemple une version finalisée avant approbation) conditionne la possibilité d'une décision, il ne la remplace pas. | §5-É11 | [D] |
| IV-03 | Une version Finalisée est immuable. | §6.8 | [D] |
| IV-04 | Une demande Finalisée ou Annulée définitivement ne change plus d'état. | §6.8 | [P] |
| IV-05 | Une demande ne devient Finalisée que si elle dispose d'une version à l'état Conforme. | §5-É9 | [D] |
| IV-06 | Une demande Suspendue n'est jamais Finalisée. | §6.9 | [D] |
| IV-07 | Un élément Bloqué n'est jamais livré comme s'il était produit. | §3.1 | [D] |
| IV-08 | Les états fonctionnels ne se confondent pas avec les étapes internes de production. | §10 | [D] |
| IV-09 | Les statuts d'approbation et de diffusion ne sont attribués que par décision humaine (hors constat « Non requise »). | §5-É11, §8 | [D] |
| IV-10 | Aucun message de l'Agent ne présente un état non atteint. | §7 | [D] |
| IV-11 | L'approbation et la diffusion ne modifient jamais l'état de l'axe C ; seule l'exécution des contrôles le modifie. | §5-É11 | [P] |
| IV-12 | Une version non finalisée n'est ni approuvable ni diffusable (MVP). | §5-É11 | [P] |
| IV-13 | Une version n'est finalisée que si tous ses éléments obligatoires sont « Contrôlé conforme » ou « Non applicable ». | §5-É9 | [D] |
| IV-14 | Une version dont l'approbation est Refusée ou En attente ne peut pas passer à Diffusion autorisée. | §5-É11 | [P] |
| IV-15 | La finalisation n'attribue ni approbation ni autorisation de diffuser. | §5-É11 | [D] |

### 8.9 Vérification de la cohérence des axes avec le cahier

#### 8.9.1 Couverture de la liste d'états du cahier (§10)

| État listé au cahier (§10) | État de la spécification | Axe |
|---|---|---|
| Demande reçue | ST-R-01 | R |
| Demande en cours de clarification | ST-R-02 | R |
| Demande en vérification de faisabilité | ST-R-03 | R |
| Demande en production | ST-R-04 | R |
| Demande bloquée | ST-R-06 | R |
| Demande en attente d'une décision humaine | ST-R-07 | R |
| Demande suspendue | ST-R-08 | R |
| Production en contrôle qualité | ST-R-05 | R |
| Livrable conforme aux contrôles | ST-C-04 | C |
| Livrable en attente d'approbation | ST-A-03 | A |
| Livrable approuvé | ST-A-04 | A |
| Livrable autorisé à être diffusé | ST-D-02 | D |
| Demande annulée définitivement | ST-R-10 | R |

#### 8.9.2 Besoins du cahier au-delà de cette liste

| Besoin | Où il est couvert |
|---|---|
| Distinguer tâches terminées, suspendues, bloquées, en attente de décision et finalisées (§7) | ST-R-09 (Finalisée) et axe R |
| Blocage ciblé d'un élément, les opérations indépendantes se poursuivant (§5-É7) | Axe E (ST-E-03), TR-E-02 |
| Distinguer résultats validés et résultats provisoires (§6.11) | Axes V (ST-V-01, ST-V-02) et E |
| Ne pas présenter un travail inachevé comme livrable final (§6.11) | ST-V-01, ST-V-04, IV-06 |
| Immutabilité des livrables (§6.8) | ST-V-02, IV-03 |
| Conformité, approbation et diffusion distinctes (§5-É11) | Axes C, A, D ; IV-02, IV-11 |

#### 8.9.3 Dépendances entre axes (prérequis)

Ces prérequis conditionnent la possibilité d'une transition ; ils ne la déclenchent jamais (IV-02).

| Transition | Prérequis sur les autres axes |
|---|---|
| TR-R-18 (Finalisée) | Axe C : Conforme ; axe E : tous les éléments obligatoires Contrôlé conforme ou Non applicable |
| TR-V-01 (version Finalisée) | TR-R-18 accomplie |
| TR-A-01 (soumission à l'approbation) | Axe V : Finalisée |
| TR-D-01, TR-D-03 (diffusion autorisée) | Axe V : Finalisée ; axe A : Approuvée ou Non requise ; droits de diffusion vérifiés (AU-4) |
| TR-R-21 (annulation définitive) | Axe R : demande non Finalisée |
| TR-V-03 (Abandonnée) | TR-R-21 accomplie |

#### 8.9.4 Contrôle d'atteignabilité

- Chaque état non final de l'axe R a au moins une transition sortante ; les états finaux sont **Finalisée** et **Annulée définitivement**.
- Les états finaux des autres axes sont : Conforme (C, pour une version finalisée), Approuvée et Refusée (A), Remplacée et Abandonnée (V).
- Une révision ne rouvre jamais une demande Finalisée : elle crée une **demande liée** (TR-R-22) et une nouvelle version dont tous les statuts partent de zéro (RB-116).

---

## 9. Règles de blocage, de reprise, de révision et de finalisation

### 9.1 Blocage

**Principe.** Un blocage est **ciblé** : il porte sur l'élément ou l'opération concernés et sur ceux qui en dépendent, pas sur toute la demande, sauf si plus rien ne peut avancer (RB-077). Chaque blocage a un **motif communicable** (RB-078, Annexe C).

| Déclencheur | Motif (Annexe C) | Portée | Ce qui continue | Levée | Qui lève |
|---|---|---|---|---|---|
| Modèle ou règle absent | MB-01 | Production entière du type de livrable | Diagnostic, clarification | Fourniture du modèle ou de la règle | Personne responsable |
| Information obligatoire absente | MB-02 | Éléments dépendants | Éléments indépendants | Information obtenue ou source autorisée | Utilisateur, personne responsable (autorisation ponctuelle) |
| Contradiction irrésolue sur information indispensable | MB-03 | Éléments dépendants | Éléments indépendants | Arbitrage | Personne responsable |
| Information non vérifiée (QI-02, QI-03) lorsque QI-01 est requis | MB-04 | Éléments dépendants | Vérification auprès d'autres sources | Vérification aboutie ou décision | Agent (vérification), personne responsable |
| Information hors période pour l'usage prévu | MB-05 | Éléments dépendants | Éléments indépendants | Information valide ou décision | Utilisateur, personne responsable |
| Source non accessible | MB-06 | Éléments dépendants | Autres sources autorisées | Autorisation | Personne responsable |
| Contenu non utilisable | MB-07 | Éléments dépendants | Idem | Autorisation | Personne responsable |
| Intégration non autorisée | MB-08 | Éléments concernés | Idem | Autorisation | Personne responsable |
| Diffusion non autorisée ou incertaine | MB-09 | Diffusion | Production et contrôles | Clarification des droits | Personne responsable |
| Calcul sans méthode définie | MB-10 | Éléments calculés | Éléments non calculés | Méthode définie | Personne responsable |
| Décision non couverte | MB-11 | Opération concernée | Diagnostic, éléments indépendants | Décision | Personne responsable |
| Correspondance source/cible incertaine | MB-12 | Ligne concernée | Autres lignes | Clarification | Utilisateur, personne responsable |
| Droits incertains | MB-13 | Opération concernée | Opérations indépendantes | Clarification | Personne responsable |
| Paramètre indispensable manquant | MB-14 | Éléments dépendants | Opérations indépendantes | Réponse | Utilisateur |
| Dépendance bloquée | MB-15 | Éléments en aval | Éléments indépendants | Levée du blocage amont | Selon la cause |
| Contrôle obligatoire échoué | MB-16 | Finalisation | Corrections autorisées | Correction ou décision, contrôle rejoué | Agent ou personne responsable |
| Règle ou modèle devenu invalide à la reprise | MB-17 | Éléments affectés | Éléments toujours valides | Nouvelle règle, décision | Personne responsable |

**Règles complémentaires.**
- L'Agent ne contourne pas un blocage (RB-080).
- Pendant un blocage, il poursuit les diagnostics et vérifications autorisés (RF-026, RF-244).
- Le blocage est visible dans le suivi avec son motif communicable, adapté au profil (RB-065).

### 9.2 Suspension et reprise

| Ce qui est vérifié à la reprise | Action si changé |
|---|---|
| Versions de modèle et de règles figées | Conserver par défaut ; si invalidées par décision explicite, réexécuter les opérations affectées (MB-17) |
| Registre des sources et autorisations (permanentes et ponctuelles) | Vérifier la validité ; une autorisation ponctuelle expirée est à redemander |
| Sources interrogées | Vérifier leur disponibilité et la stabilité des informations utilisées |
| Statuts de qualité des informations | Réévaluer (périodes, validité temporelle) |
| Droits de l'utilisateur et des destinataires | Revérifier |
| Décisions humaines antérieures | Conserver ; vérifier qu'elles s'appliquent encore à l'objet |
| Résultats de contrôle | Rejouer ceux dont les entrées ont changé |
| Conservation | Vérifier que l'état de travail est encore conservable |

À l'issue, l'Agent présente à l'utilisateur ce qui est conservé, ce qui est réexécuté et pourquoi (RF-209).

### 9.3 Révision

1. **Déclenchement explicite** par un utilisateur autorisé (jamais automatique, RB-072).
2. **Analyse d'impact** : éléments, contrôles, livrables liés (RF-191).
3. **Création d'une nouvelle version**, la version précédente restant intacte (RB-067, RB-071).
4. **Choix des versions de modèle et de règles** : par défaut celles d'origine ; l'utilisation de versions plus récentes exige une décision explicite (QO-032).
5. **Rejeu des contrôles applicables** (RF-192).
6. **Statuts remis à zéro** pour la nouvelle version (RB-116).
7. **Historique** : motif, auteur, date, différences (RF-193, RF-194, RF-198).

### 9.4 Finalisation

Une version ne peut être finalisée que si **toutes** les conditions suivantes sont réunies :

| ID | Condition de finalisation | Réf. |
|---|---|---|
| FN-01 | Tous les contrôles obligatoires ont le résultat « réussi » (ou « non applicable » justifié). | RB-045, RF-141 |
| FN-02 | Aucun élément obligatoire n'est bloqué. | RB-028, RB-031 |
| FN-03 | Aucune contradiction bloquante n'est irrésolue. | CT-04 |
| FN-04 | Toutes les informations intégrées comme faits établis sont QI-01 ; toute autre est explicitement qualifiée. | RB-018, RF-069 |
| FN-05 | Les autorisations d'accès, d'utilisation et d'intégration sont vérifiées pour chaque source utilisée. | CT-05 |
| FN-06 | Les restrictions de confidentialité sont appliquées (minimisation, masquage, exclusion). | RB-060, CT-11 |
| FN-07 | Les références et traces exigées sont présentes. | CT-10 |
| FN-08 | Les rapports exigés par les règles du type sont produits et liés à la version. | RF-156, RF-167 |
| FN-09 | Les exceptions, décisions humaines et observations figurent dans le rapport de conformité. | RF-170 |
| FN-10 | Le message de remise distingue conformité, approbation et diffusion, sans en déduire aucun. | RF-161, RF-162, RF-237 |

La finalisation **rend la version immuable** (RF-166) mais **ne crée ni approbation, ni autorisation de diffusion** (RB-110).

### 9.5 Escalade vers la personne responsable

| ID | Cas d'escalade | Statut |
|---|---|---|
| ES-01 | Décision substantielle non couverte (RB-005) | [D] |
| ES-02 | Contradiction irrésolue (RB-033) | [D] |
| ES-03 | Correction exigeant une interprétation (RB-051) | [D] |
| ES-04 | Droits incertains persistants (RB-058) | [D] |
| ES-05 | Priorités non départageables (RB-091) | [D] |
| ES-06 | Boucle de correction non convergente (RF-153) | [P] |
| ES-07 | Exemple contredisant une règle (RF-256) | [P] |
| ES-08 | Source indisponible empêchant un élément obligatoire (RF-042) | [P] |
| ES-09 | Demande d'autorisation ponctuelle d'une source (RF-245) | [D] |
| ES-10 | Proposition d'évolution de règle d'un utilisateur (RF-266) | [P] |

### 9.6 Approbation et diffusion : possibilités, conditions et effets sur la conformité

**Principe.** Trois décisions de nature différente coexistent : la **conformité** est le résultat de contrôles exécutés par l'Agent ; l'**approbation** est un jugement humain sur une version finalisée ; la **diffusion** est une décision de livraison réservée à la personne responsable. Chacune est examinée séparément ci-dessous. **Aucune des deux décisions humaines ne modifie la conformité** (IV-11, RB-123). Ces règles sont des propositions [P] (PV-05).

#### 9.6.1 L'approbation est-elle possible ?

| État de la version | Approbation possible ? | Conditions | Effet sur la conformité |
|---|---|---|---|
| Provisoire, Non évaluée ou Non conforme | **Non**, au MVP comme en V2 | La version doit d'abord être corrigée, complétée ou révisée (RF-272, RB-124). | Aucun : reste Non évaluée ou Non conforme. |
| Provisoire, Conforme, pas encore finalisée | **Non** | Elle doit d'abord être finalisée (RF-272). | Aucun. |
| Finalisée, approbation exigée par les règles du type | **Oui** | Soumission par l'Agent ; approbateur : la personne responsable au MVP (RF-174) ; refus motivé ; décision définitive pour la version (RB-125). | Aucun : reste Conforme, que l'on approuve ou que l'on refuse. |
| Finalisée, approbation non exigée | Sans objet | Statut « Non requise » (TR-A-02). | Aucun. |
| Remplacée par une version ultérieure | **Non** | L'approbation vise la version courante. | Aucun. |

#### 9.6.2 La diffusion est-elle possible ?

| État de la version | Diffusion possible ? | Conditions | Effet sur la conformité |
|---|---|---|---|
| Provisoire ou Non conforme | **Non au MVP.** En V2, uniquement par diffusion exceptionnelle si elle est retenue (QO-036) | V2 : décision explicite de la personne responsable, marquage visible, réserve dans les rapports (RF-280). | Aucun : la version reste Non conforme et le marquage le dit. |
| Finalisée, approbation En attente | **Non** | Attendre la décision d'approbation (RF-276). | Aucun. |
| Finalisée, approbation Refusée | **Non** | Une nouvelle version est nécessaire (RB-126). | Aucun. |
| Finalisée, approbation Approuvée | **Oui** | Décision de la personne responsable (version, destinataires, périmètre, éléments exclus) ; droits de diffusion (AU-4) vérifiés pour chaque destinataire (RF-181) ; diffusion = accessibilité dans le produit (RF-278). | Aucun. |
| Finalisée, approbation Non requise | **Oui** | Mêmes conditions que ci-dessus. | Aucun. |
| Remplacée par une version ultérieure | **Non au MVP** | C'est la version courante qui est diffusée. | Aucun. |

#### 9.6.3 Ce que chaque décision modifie

| Décision ou événement | Axe modifié | Axes jamais modifiés |
|---|---|---|
| Exécution des contrôles | C (conformité) | A, D |
| Finalisation | V (Finalisée) ; A (Non soumise, ou Non requise par constat de règle) | C (déjà Conforme), D |
| Approbation ou refus | A | C, D |
| Autorisation, révocation ou modification de la diffusion | D | C, A |
| Révision | Crée une nouvelle version dont tous les statuts partent de zéro | Statuts des versions antérieures |

#### 9.6.4 Livrer malgré tout une version non conforme ?

Une version non conforme **ne devient pas conforme par décision humaine**. Elle n'a que trois issues : (1) correction ou complément, puis contrôles rejoués ; (2) révision, c'est-à-dire nouvelle version ; (3) en **V2**, exception accordée par la personne responsable sur la règle concernée (RF-281) : la conformité s'apprécie alors par rapport aux règles telles qu'exceptées et l'exception figure en réserve, sans transformer un contrôle échoué en contrôle réussi. [P]

---
## 10. Exigences transverses : confidentialité, traçabilité, conformité, contrôle qualité

Ces exigences s'appliquent à **tous** les cas d'usage. Elles complètent les exigences fonctionnelles (section 6) sans les répéter.

### 10.1 Confidentialité et droits d'accès (RT-001 à RT-016)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RT-001 | Chaque source, information, livrable et rapport doit porter une classification de confidentialité définie par les règles ou le registre. | §6.4 | [P] | MVP |
| RT-002 | L'Agent doit appliquer les droits d'accès de chaque utilisateur à chaque objet (demande, livrable, rapport, traçabilité, historique). | §8 | [D] | MVP |
| RT-003 | L'accès à la source, l'utilisation du contenu, l'intégration et la diffusion font l'objet de quatre vérifications distinctes. | §3.5 | [D] | MVP |
| RT-004 | Les vérifications sont faites aux moments adéquats : avant mobilisation (accès), avant exploitation (utilisation), avant insertion (intégration), avant diffusion (diffusion). | §3.5, §6.4 | [P] | MVP |
| RT-005 | Lorsque les droits sont incertains, l'Agent suspend l'opération concernée jusqu'à clarification. | §6.4 | [D] | MVP |
| RT-006 | Aucune information protégée ne doit être révélée par l'état d'avancement, les motifs de blocage, les questions de clarification ou les messages d'erreur. | §6.4, §7 | [D] | MVP |
| RT-007 | Les explications de refus restent générales lorsque le détail révélerait l'existence, l'identité ou le contenu d'une source protégée. | §6.4 | [D] | MVP |
| RT-008 | L'Agent ne confirme ni n'infirme l'existence d'une source à laquelle l'interlocuteur n'a pas accès. | §6.4 | [P] | MVP |
| RT-009 | Les droits sont évalués au moment de l'opération et revérifiés à la reprise d'une demande suspendue. | §6.9 | [D] | MVP |
| RT-010 | Un livrable agrégeant des informations de sensibilités différentes hérite de la restriction la plus contraignante parmi celles qu'il contient, sauf règle contraire. | §6.4 | [P] | MVP |
| RT-011 | Le rapport de traçabilité a sa propre classification et peut être plus restrictif que le livrable. | §6.4 | [P] | MVP |
| RT-012 | Les journaux d'historique sont soumis aux mêmes restrictions d'accès que les objets qu'ils décrivent. | §6.4 | [P] | MVP |
| RT-013 | Un destinataire n'accède qu'aux éléments autorisés pour lui. | §6.4 | [D] | MVP |
| RT-014 | Le partage large des actions ordinaires ne lève aucune restriction de confidentialité, de source ou de diffusion. | §8 | [D] | MVP |
| RT-015 | Les informations fournies par un utilisateur dans une demande sont confidentielles par défaut et ne sont pas réutilisées pour d'autres demandes sans autorisation. | §6.10 | [P] | MVP |
| RT-016 | Au MVP, une demande n'est accessible qu'à son auteur et à la personne responsable ; tout accès non expressément accordé est refusé. | §8 | [P] | MVP |

### 10.2 Données personnelles et sensibles (RT-017 à RT-026)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RT-017 | L'Agent doit appliquer un principe de minimisation : ne reprendre que les données nécessaires, autorisées pour l'usage prévu et permises pour les destinataires. | §6.3 | [D] | MVP |
| RT-018 | Les données non permises doivent être masquées ou exclues selon les règles applicables. | §6.3 | [D] | MVP |
| RT-019 | Les catégories de données personnelles et sensibles sont fournies par les règles du type de livrable ; sans règle de minimisation applicable, la donnée n'est pas reprise. | §6.3 | [P] | MVP |
| RT-020 | Le rapport de traçabilité doit référencer une information masquée sans en révéler le contenu aux lecteurs non autorisés. | §6.3, §6.4 | [P] | MVP |
| RT-021 | L'Agent ne doit pas déduire ou reconstituer des données masquées à partir d'autres éléments du livrable. | §6.3 | [P] | MVP |
| RT-022 | Si les règles de minimisation ne couvrent pas un cas, l'élément concerné est suspendu et traité comme une décision non couverte. | §3.2, §6.3 | [D] | MVP |
| RT-023 | Si un masquage ou une exclusion rend un élément obligatoire manquant ou incohérent, l'Agent bloque l'élément et sollicite une décision. | §6.3 | [P] | MVP |
| RT-024 | Les données personnelles des utilisateurs (auteur d'une demande, destinataires) suivent également le principe de minimisation. | §6.3 | [P] | MVP |
| RT-025 | Les journaux enregistrent l'usage de données sensibles sans en dupliquer inutilement le contenu. | §6.3 | [P] | MVP |
| RT-026 | La conservation des données personnelles est limitée par les règles de conservation. | §6.9 | [D] | MVP |

### 10.3 Traçabilité (RT-027 à RT-042)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RT-027 | Toute information significative d'un livrable doit être reliée à sa source, sa référence précise, son statut de validation et ses transformations. | §3.4 | [D] | MVP |
| RT-028 | Au MVP, sont significatifs tout contenu factuel, chiffre, référence, calcul et décision, ainsi que tout élément que le modèle qualifie de significatif. | §3.4 | [P] | MVP |
| RT-029 | Pour chaque calcul : données d'entrée, sources, méthode, unités, conventions, arrondi, résultat. | §3.4, §6.1 | [D] | MVP |
| RT-030 | Pour chaque transformation : opération, règle autorisante, état avant, état après. | §3.4 | [D] | MVP |
| RT-031 | Les versions du modèle, des règles, du registre des sources et du catalogue de contrôles utilisées sont enregistrées. | §6.8 | [D] | MVP |
| RT-032 | Chaque autorisation pertinente (permanente, ponctuelle, exception) est enregistrée. | §5-É11 | [D] | MVP |
| RT-033 | Chaque décision humaine est enregistrée avec son décideur. | §5-É11 | [P] | MVP |
| RT-034 | Chaque contrôle et chacun de ses résultats est enregistré, y compris lors des rejeux. | §5-É9 | [P] | MVP |
| RT-035 | Chaque changement d'état (demande, conformité, approbation, diffusion, version) est horodaté, avec son auteur (humain ou Agent) et son motif. | §10 | [P] | MVP |
| RT-036 | L'historique permet de reconstituer chronologiquement ce qui s'est passé pour une demande. | §5-É11 | [P] | MVP |
| RT-037 | La traçabilité est navigable du livrable vers les sources, et des sources vers les éléments qui les utilisent. | §3.4 | [P] | MVP |
| RT-038 | Les liens de traçabilité sont stables dans le temps. | §6.8 | [P] | MVP |
| RT-039 | La traçabilité n'est pas une simple bibliographie. | §5-É11 | [D] | MVP |
| RT-040 | La traçabilité mentionne aussi ce qui a été exclu ou masqué (existence de l'exclusion et motif général). | §6.3 | [P] | MVP |
| RT-041 | Les informations candidates non retenues sont consignées avec leur motif. | §5-É5 | [P] | MVP |
| RT-042 | La traçabilité est complète avant finalisation (contrôle CT-10). | §5-É9 | [D] | MVP |

### 10.4 Conformité (RT-043 à RT-052)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RT-043 | Le rapport de conformité doit être complet (contenu minimal en Annexe D). | §5-É11 | [D] | MVP |
| RT-044 | Les trois statuts (conformité, approbation, diffusion) sont séparés dans tous les affichages et rapports. | §5-É11 | [D] | MVP |
| RT-045 | Aucune déclaration de conformité n'est émise sans réussite de tous les contrôles obligatoires. | §5-É9 | [D] | MVP |
| RT-046 | La conformité s'apprécie par rapport aux règles et modèles figés pour la demande. | §6.8 | [D] | MVP |
| RT-047 | La conformité est rattachée à une version précise. | §6.8 | [P] | MVP |
| RT-048 | Les réserves sont formulées clairement et rattachées à des éléments. | §5-É11 | [D] | MVP |
| RT-049 | Les exceptions et décisions humaines sont mentionnées dans le rapport de conformité. | §5-É11 | [P] | MVP |
| RT-050 | Le rapport de conformité mentionne les limites du contrôle : ce qui n'est pas contrôlé parce qu'aucune règle ne le définit. | §5-É9, §5-É10 | [P] | MVP |
| RT-051 | La conformité atteste le respect des règles et des contrôles définis ; elle n'est pas une garantie de véracité au-delà des statuts de vérification des informations. | §5-É5 | [P] | MVP |
| RT-052 | Toute version modifiée par une correction est recontrôlée. | §5-É10 | [D] | MVP |

### 10.5 Contrôle qualité (RT-053 à RT-060)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RT-053 | Les contrôles obligatoires sont définis par les modèles et règles ; l'Agent ne peut en retirer. | §5-É9, §3.6 | [D] | MVP |
| RT-054 | Les contrôles respectent leurs dépendances : si un préalable échoue, les contrôles dépendants sont « non exécutables ». | §5-É9 | [P] | MVP |
| RT-055 | Chaque contrôle est reproductible : mêmes entrées, même résultat. | §5-É9 | [P] | MVP |
| RT-056 | Après correction ou reprise, les contrôles rejoués couvrent au minimum les éléments affectés et les contrôles transversaux. | §5-É10, §6.9 | [D] | MVP |
| RT-057 | Les résultats de toutes les exécutions de contrôle sont conservés, pas seulement la dernière. | §6.8 | [P] | MVP |
| RT-058 | Un contrôle ne modifie jamais le contenu qu'il contrôle : contrôler et corriger sont deux opérations distinctes. | §5-É10 | [P] | MVP |
| RT-059 | L'Agent ne peut marquer « réussi » un contrôle qu'il n'a pas exécuté. | §7 | [D] | MVP |
| RT-060 | Le catalogue de contrôles est versionné ; la version utilisée est enregistrée pour chaque production. | §6.8 | [P] | MVP |

### 10.6 Conservation, audit et historique (RT-061 à RT-068)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RT-061 | Au MVP, aucune suppression automatique : l'historique et les états suspendus sont conservés jusqu'à décision explicite de la personne responsable, qui peut fixer des règles de conservation (durée, contenu, sensibilité) par type de livrable. | §6.9 | [P] | MVP |
| RT-062 | L'historique de production est immuable : aucune entrée n'est modifiée ou supprimée par un utilisateur. | §6.8 | [P] | MVP |
| RT-063 | Rien n'est écrasé silencieusement. | §6.8 | [D] | MVP |
| RT-064 | La suppression en fin de conservation laisse une trace minimale (existence, date, motif général). | §6.9 | [P] | MVP |
| RT-065 | Un audit doit pouvoir reconstituer pourquoi un livrable est ce qu'il est : règles, sources, décisions, contrôles. | §5-É11 | [P] | MVP |
| RT-066 | Les demandes suspendues ou annulées suivent les règles de conservation. | §6.9, §6.11 | [D] | MVP |
| RT-067 | Les rapports peuvent être restitués dans les formats de sortie prévus. | §9 | [P] | V2 |
| RT-068 | Les défaillances de l'Agent en cours d'exécution (opération interrompue sans fin normale) sont consignées. | §7 | [P] | MVP |

### 10.7 Intégrité des contenus (RT-069 à RT-074)

| ID | Exigence | Cahier | Statut | Priorité |
|---|---|---|---|---|
| RT-069 | Aucun contenu n'est généré sans rattachement à une source, un modèle ou une règle. | §3.1 | [D] | MVP |
| RT-070 | La traçabilité distingue le contenu repris tel quel, reformulé, calculé, et issu d'un texte fixe du modèle. | §5-É6 | [P] | MVP |
| RT-071 | Les textes fixes d'un modèle sont tracés comme issus du modèle. | §4 | [P] | MVP |
| RT-072 | Les contrôles de fidélité d'une reformulation sont définis par les règles. | §5-É6 | [P] | MVP |
| RT-073 | Lorsqu'une règle exige une citation exacte, l'Agent restitue le texte à l'identique et l'identifie comme citation. | §5-É11 | [P] | MVP |
| RT-074 | L'Agent n'attribue jamais à une source une information qu'elle ne contient pas. | §3.1, §3.4 | [D] | MVP |

---
## 11. Critères d'acceptation (CA)

Chaque critère est **vérifiable** et formulé selon le schéma *Étant donné / Quand / Alors*. Il renvoie aux exigences qu'il permet de valider (RF, RB, RT). Ces critères couvrent les comportements critiques de chaque domaine ; la conception détaillée des tests en dérivera d'autres, chaque exigence restant vérifiable individuellement.

Tous les critères portant sur des exigences [P] ou [Q] sont **conditionnels à la validation** de ces exigences.

### 11.1 Réception et clarification (CA-001 à CA-010)

| ID | Liens | Critère |
|---|---|---|
| CA-001 | RF-001, RF-002 | **Étant donné** un utilisateur autorisé, **quand** il soumet une demande en langage naturel, **alors** la demande est enregistrée avec identifiant, auteur, date et texte d'origine inchangé, à l'état Reçue. |
| CA-002 | RF-003 | **Étant donné** une demande « rapport de suivi-évaluation en PDF », **quand** l'Agent l'analyse, **alors** le type de livrable et le format de fichier sont identifiés séparément. |
| CA-003 | RF-006, RF-012 | **Étant donné** un paramètre déterminable par le contexte autorisé et les règles, **quand** l'Agent analyse la demande, **alors** il ne pose aucune question à ce sujet. |
| CA-004 | RF-009, RB-064 | **Étant donné** un utilisateur non autorisé à soumettre ce type de demande, **quand** il soumet, **alors** l'Agent refuse avec un motif communicable et ne produit rien. |
| CA-005 | RF-011 | **Étant donné** une ambiguïté sans incidence significative sur la conformité ou la validité, **quand** l'Agent poursuit, **alors** il ne pose pas de question. |
| CA-006 | RF-011, RF-014, RF-016 | **Étant donné** une ambiguïté significative, **quand** l'Agent la détecte, **alors** il pose une question ciblée indiquant en quoi la réponse conditionne le livrable et la demande passe à En clarification. |
| CA-007 | RF-013, RF-015 | **Étant donné** plusieurs ambiguïtés, **quand** l'Agent sollicite l'utilisateur, **alors** les questions bloquantes passent en premier et aucun formulaire long n'est présenté. |
| CA-008 | RF-018, RB-004 | **Étant donné** un choix substantiel sans réponse de l'utilisateur, **quand** l'Agent poursuit, **alors** il ne choisit pas à sa place et l'élément dépendant reste en attente ou bloqué. |
| CA-009 | RF-007, RF-264 | **Étant donné** une instruction ponctuelle de l'utilisateur, **quand** l'Agent la traite, **alors** elle s'applique à cette demande et aucune règle n'est modifiée. |
| CA-010 | RF-008 | **Étant donné** une demande portant sur deux livrables, **quand** l'Agent l'analyse, **alors** il la détecte comme multiple, n'effectue aucun traitement coordonné et propose de la scinder en demandes distinctes et indépendantes. |

### 11.2 Faisabilité (CA-011 à CA-020)

| ID | Liens | Critère |
|---|---|---|
| CA-011 | RF-019, RF-029 | **Étant donné** un type de livrable sans modèle, **quand** l'Agent vérifie la faisabilité, **alors** il bloque, n'improvise aucune structure et sollicite la personne responsable. |
| CA-012 | RF-019 à RF-024 | **Étant donné** une demande comprise, **quand** l'Agent vérifie la faisabilité, **alors** le diagnostic couvre modèle, règles, informations, autorisations, exigences obligatoires, contradictions connues et conditions préalables. |
| CA-013 | RF-025 | **Étant donné** une condition indispensable non satisfaite, **quand** le diagnostic se termine, **alors** la partie concernée est bloquée avec un motif communicable. |
| CA-014 | RF-026, RF-244 | **Étant donné** un blocage, **quand** des opérations de diagnostic ou de vérification restent autorisées, **alors** l'Agent les poursuit. |
| CA-015 | RF-027 | **Étant donné** un diagnostic terminé, **quand** l'Agent le présente, **alors** il distingue réalisable, à clarifier et bloqué, avec les motifs. |
| CA-016 | RF-028, RB-068 | **Étant donné** une faisabilité acquise, **quand** la production démarre, **alors** les versions de modèle, de règles et de registre sont figées et enregistrées. |
| CA-017 | RF-021, RB-058, RT-005 | **Étant donné** des droits incertains sur une source, **quand** l'Agent doit l'exploiter, **alors** l'opération concernée est suspendue jusqu'à clarification. |
| CA-018 | RF-187, RF-258 | **Étant donné** une règle modifiée après la faisabilité, **quand** la demande se poursuit, **alors** elle reste liée aux versions figées. |
| CA-019 | RF-030 | **Étant donné** une demande de diagnostic seul, **quand** l'Agent l'exécute, **alors** il remet un diagnostic sans produire de livrable. |
| CA-020 | RF-025, RT-006 | **Étant donné** un blocage lié à une source protégée, **quand** l'Agent l'explique à un interlocuteur sans droit, **alors** le motif reste général. |

### 11.3 Mobilisation et sources (CA-021 à CA-030)

| ID | Liens | Critère |
|---|---|---|
| CA-021 | RF-031, RF-034 | **Étant donné** une source pertinente mais non autorisée, **quand** l'Agent mobilise des informations, **alors** il ne la consulte pas. |
| CA-022 | RF-032 | **Étant donné** une information qu'INIS peut fournir, **quand** l'Agent la recherche, **alors** INIS est interrogé en premier. |
| CA-023 | RF-033 | **Étant donné** une information obligatoire absente d'INIS, **quand** d'autres sources sont explicitement autorisées, **alors** l'Agent les consulte. |
| CA-024 | RF-035, RF-036, RF-247 | **Étant donné** une autorisation ponctuelle accordée, **quand** l'Agent utilise la source, **alors** elle est utilisable pour la demande concernée et le registre permanent reste inchangé. |
| CA-025 | RF-037 | **Étant donné** une source accessible contenant une information non utilisable, **quand** l'Agent l'évalue, **alors** il ne l'utilise pas. |
| CA-026 | RF-038, RT-003 | **Étant donné** une source accessible mais dont l'intégration est non autorisée, **quand** l'Agent produit, **alors** le contenu n'est pas intégré au livrable. |
| CA-027 | RF-039 | **Étant donné** une information mobilisée, **quand** on consulte son enregistrement, **alors** source, référence précise et date de consultation figurent. |
| CA-028 | RF-040 | **Étant donné** une information transformée, **quand** on consulte la trace, **alors** sa forme d'origine reste disponible. |
| CA-029 | RF-042 | **Étant donné** une source indisponible, **quand** l'Agent mobilise, **alors** il le signale, poursuit auprès des autres sources et ne conclut pas à l'absence de l'information. |
| CA-030 | RF-041, RF-044 | **Étant donné** l'absence de méthode de recherche définie, **quand** l'Agent doit chercher, **alors** il n'invente pas de méthode ; toute consultation, y compris infructueuse, est journalisée. |

### 11.4 Cartographie (CA-031 à CA-040)

| ID | Liens | Critère |
|---|---|---|
| CA-031 | RF-045 | **Étant donné** une demande en production, **quand** l'Agent n'a pas établi la cartographie, **alors** aucune rédaction ne commence. |
| CA-032 | RF-046 | **Étant donné** un modèle de N éléments exigés, **quand** la cartographie est établie, **alors** chacun a une ligne. |
| CA-033 | RF-047 à RF-054 | **Étant donné** une ligne de cartographie, **quand** on la consulte, **alors** elle contient exigence, information nécessaire, information disponible, source et référence, statut de validation, transformations, manques, contradictions, incertitudes et dépendances. |
| CA-034 | RF-055 | **Étant donné** une cartographie terminée, **quand** l'Agent la synthétise, **alors** il indique ce qui peut être produit, ce qui doit être clarifié et ce qui reste bloqué. |
| CA-035 | RF-056, RB-023 | **Étant donné** une correspondance source/cible incertaine, **quand** l'Agent établit la ligne, **alors** elle est À clarifier et non résolue arbitrairement. |
| CA-036 | RF-057 | **Étant donné** une information nouvelle, **quand** elle affecte la cartographie, **alors** celle-ci est mise à jour et les versions antérieures sont conservées. |
| CA-037 | RF-058, RT-007 | **Étant donné** un utilisateur sans droit sur une source, **quand** il consulte la cartographie, **alors** la source est mentionnée de façon générique. |
| CA-038 | RF-078 | **Étant donné** une lacune, **quand** l'Agent la consigne, **alors** les éléments qui en dépendent sont identifiés. |
| CA-039 | RF-053 | **Étant donné** une contradiction, **quand** la ligne est renseignée, **alors** la contradiction y est signalée. |
| CA-040 | RF-054, RB-077 | **Étant donné** un élément bloqué, **quand** l'Agent évalue les dépendances, **alors** seuls les éléments dépendants sont bloqués. |

### 11.5 Qualité des informations, lacunes et contradictions (CA-041 à CA-052)

| ID | Liens | Critère |
|---|---|---|
| CA-041 | RF-060 | **Étant donné** une information évaluée, **quand** on consulte son enregistrement, **alors** elle porte exactement un statut QI pour l'usage prévu. |
| CA-042 | RF-061 à RF-063 | **Étant donné** une information d'INIS dont la fiabilité n'est pas établie, **quand** l'Agent l'évalue, **alors** il tente de la vérifier et, tant que ce n'est pas abouti, ne la présente pas comme fait établi. |
| CA-043 | RF-064, RF-067 | **Étant donné** une information valide seulement pour une période passée, **quand** elle est visée pour décrire la situation actuelle, **alors** elle est Hors période ; elle reste utilisable pour une analyse historique. |
| CA-044 | RF-066, RF-068 | **Étant donné** deux informations dont l'une est plus récente, **quand** l'Agent choisit, **alors** la récence seule ne décide pas ; une information non autorisée pour l'usage est exclue du livrable. |
| CA-045 | RF-073 à RF-076 | **Étant donné** une information obligatoire manquante sans source alternative, **quand** l'Agent produit, **alors** les éléments dépendants sont bloqués et aucune valeur n'est inventée. |
| CA-046 | RF-074 | **Étant donné** une information manquante trouvée dans une source alternative autorisée, **quand** elle est QI-01, **alors** elle est intégrée avec sa provenance. |
| CA-047 | RF-077, RB-029 | **Étant donné** une information facultative manquante, **quand** l'Agent produit, **alors** il applique la règle du modèle et signale l'omission. |
| CA-048 | RF-081 à RF-083 | **Étant donné** deux sources divergentes, **quand** une règle de priorité s'applique, **alors** l'Agent l'applique en tenant compte du contexte, de la provenance, de la portée et de la période, et trace le résultat. |
| CA-049 | RF-084 à RF-086 | **Étant donné** une contradiction qu'aucune règle ne tranche, **quand** l'information est indispensable, **alors** les éléments dépendants sont bloqués et l'Agent ne choisit pas. |
| CA-050 | RF-087 | **Étant donné** une contradiction irrésolue, **quand** des éléments en sont indépendants, **alors** leur production se poursuit. |
| CA-051 | RF-088, RF-089 | **Étant donné** une contradiction irrésolue, **quand** la personne responsable arbitre, **alors** un dossier d'arbitrage lui a été remis et la décision est enregistrée, limitée à la demande. |
| CA-052 | RF-090, RB-035 | **Étant donné** une divergence expliquée par des portées différentes reconnues par les règles, **quand** l'Agent l'analyse, **alors** elle est documentée comme telle. |

### 11.6 Transformations et calculs (CA-053 à CA-062)

| ID | Liens | Critère |
|---|---|---|
| CA-053 | RF-092, RF-104 | **Étant donné** une transformation sans règle autorisante, **quand** l'Agent y est conduit, **alors** il la refuse et la traite comme décision non couverte. |
| CA-054 | RF-102, RT-030 | **Étant donné** une transformation appliquée, **quand** on consulte la trace, **alors** opération, règle, état avant et état après sont présents. |
| CA-055 | RF-096, RB-043 | **Étant donné** une conversion de format de date autorisée par une règle, **quand** l'Agent l'applique, **alors** elle est tracée ; sans règle, elle est refusée. |
| CA-056 | RF-101, RB-024 | **Étant donné** une hypothèse dans les sources, **quand** elle est intégrée, **alors** elle reste présentée comme hypothèse. |
| CA-057 | RF-103 | **Étant donné** un texte à reformuler fidèlement, **quand** l'Agent le reformule, **alors** modalité, incertitude, conditions et périmètre sont préservés. |
| CA-058 | RF-097 | **Étant donné** une correction grammaticale autorisée, **quand** elle est appliquée, **alors** elle est tracée et le sens est inchangé. |
| CA-059 | RF-105, RF-111 | **Étant donné** un élément nécessitant un calcul sans méthode définie, **quand** l'Agent y est conduit, **alors** il ne calcule pas et demande une clarification ou bloque l'élément. |
| CA-060 | RF-106 à RF-110 | **Étant donné** un calcul défini, **quand** il est exécuté, **alors** entrées, sources, méthode, unités et conventions, arrondi et résultat sont conservés. |
| CA-061 | RF-112, RF-135 | **Étant donné** un calcul tracé, **quand** il est rejoué, **alors** il donne le même résultat. |
| CA-062 | RF-113, RF-114 | **Étant donné** une entrée de statut QI-02, **quand** le résultat est produit, **alors** son statut ne dépasse pas QI-02 et il est identifié comme dérivé. |

### 11.7 Production (CA-063 à CA-070)

| ID | Liens | Critère |
|---|---|---|
| CA-063 | RF-115 | **Étant donné** des conditions de production non satisfaites, **quand** la demande avance, **alors** aucun livrable final n'est produit. |
| CA-064 | RF-117 | **Étant donné** une section obligatoire, **quand** une suppression est tentée sans autorisation explicite, **alors** elle est refusée. |
| CA-065 | RF-119, RF-120, RF-171 | **Étant donné** des éléments bloqués, **quand** l'Agent produit les autres, **alors** la version est marquée provisoire, les emplacements bloqués portent leur motif et aucun contenu n'est inventé. |
| CA-066 | RF-121, RF-122 | **Étant donné** un livrable produit, **quand** on consulte un élément significatif, **alors** il est lié à ses lignes de cartographie et porte ses références. |
| CA-067 | RF-123, RT-069 | **Étant donné** un contenu sans rattachement à une source, un modèle ou une règle, **quand** l'Agent assemble, **alors** ce contenu est absent du livrable. |
| CA-068 | RF-124 | **Étant donné** des données non permises pour les destinataires, **quand** l'Agent insère, **alors** elles sont masquées ou exclues. |
| CA-069 | RF-125, RF-126 | **Étant donné** un format non autorisé pour le type, **quand** il est demandé, **alors** l'Agent bloque ou propose les formats autorisés. |
| CA-070 | RF-118 | **Étant donné** une adaptation de présentation hors des limites prévues, **quand** elle est tentée, **alors** elle est refusée. |

### 11.8 Contrôle qualité et anomalies (CA-071 à CA-084)

| ID | Liens | Critère |
|---|---|---|
| CA-071 | RF-127, RF-141 | **Étant donné** un contrôle obligatoire échoué, **quand** l'Agent évalue la conformité, **alors** le livrable n'est pas déclaré conforme. |
| CA-072 | RF-129 à RF-138 | **Étant donné** un livrable produit, **quand** les contrôles s'exécutent, **alors** chaque contrôle du catalogue applicable (CT-01 à CT-11) est exécuté. |
| CA-073 | RF-139, RF-140 | **Étant donné** des règles méthodologiques explicites, **quand** une incohérence est détectée, **alors** elle est signalée et aucun choix méthodologique n'est modifié. |
| CA-074 | RF-142, RT-059 | **Étant donné** un contrôle, **quand** il est enregistré, **alors** résultat, éléments examinés, règle et date figurent, et aucun contrôle non exécuté n'est marqué réussi. |
| CA-075 | RB-054, RT-054 | **Étant donné** un contrôle dont une donnée préalable manque, **quand** il est évalué, **alors** son résultat est « non exécutable » et non « réussi ». |
| CA-076 | RF-141, RB-112 | **Étant donné** tous les contrôles obligatoires réussis, **quand** l'Agent conclut, **alors** la version peut être déclarée conforme. |
| CA-077 | RF-143, RF-144 | **Étant donné** une anomalie, **quand** l'Agent la traite, **alors** elle est classée et, si avérée, rattachée à une règle explicite. |
| CA-078 | RF-145 à RF-147 | **Étant donné** une règle autorisant la correction d'un défaut mécanique, **quand** le défaut est détecté, **alors** il est corrigé, tracé (avant, après, règle, date) et les contrôles concernés sont rejoués. |
| CA-079 | RF-145, RB-049 | **Étant donné** un défaut mécanique sans règle de correction, **quand** il est détecté, **alors** il n'est pas corrigé automatiquement. |
| CA-080 | RF-148 | **Étant donné** une correction exigeant une interprétation, **quand** l'Agent y est conduit, **alors** il suspend l'opération concernée et sollicite la personne habilitée. |
| CA-081 | RF-149, RF-150 | **Étant donné** une observation, **quand** elle est consignée, **alors** le livrable est inchangé. |
| CA-082 | RF-151 | **Étant donné** des observations, **quand** le rapport de conformité est produit, **alors** elles y figurent. |
| CA-083 | RF-153 | **Étant donné** des cycles de correction non convergents, **quand** la borne est atteinte, **alors** l'Agent escalade à la personne responsable. |
| CA-084 | RF-154 | **Étant donné** une correction, **quand** on consulte l'historique, **alors** les résultats de contrôle antérieurs sont conservés. |

### 11.9 Finalisation et remise (CA-085 à CA-094)

| ID | Liens | Critère |
|---|---|---|
| CA-085 | RF-155, RF-163 | **Étant donné** des contrôles obligatoires non tous réussis, **quand** l'utilisateur s'enquiert du résultat, **alors** l'Agent n'annonce ni finalisation ni conformité. |
| CA-086 | RF-156 à RF-159 | **Étant donné** des règles exigeant les trois éléments, **quand** la version est finalisée, **alors** livrable, rapport de conformité et rapport de traçabilité sont remis. |
| CA-087 | RF-160, RT-039 | **Étant donné** le rapport de traçabilité, **quand** on le lit, **alors** il présente la chaîne complète pour chaque élément significatif et non une simple bibliographie. |
| CA-088 | RF-161, RF-162 | **Étant donné** une version conforme et finalisée, **quand** l'Agent présente le statut, **alors** l'approbation et la diffusion sont présentées comme non accordées, non déduites. |
| CA-089 | RF-164, RF-172 | **Étant donné** une remise, **quand** elle est présentée, **alors** elle indique le statut, les réserves et les actions restantes. |
| CA-090 | RF-166, RB-067 | **Étant donné** une version finalisée, **quand** une modification est tentée, **alors** elle est refusée et une nouvelle version est nécessaire. |
| CA-091 | RF-167 | **Étant donné** les trois éléments remis, **quand** on les consulte, **alors** chacun renvoie à la même version précise et aux versions de modèle et de règles. |
| CA-092 | RF-168 | **Étant donné** un type de livrable n'exigeant pas le rapport de traçabilité, **quand** la remise est faite, **alors** le rapport de conformité le mentionne avec la règle concernée. |
| CA-093 | RF-169, RF-170 | **Étant donné** des informations qualifiées, des exceptions ou des décisions humaines, **quand** le rapport de conformité est produit, **alors** ils y sont mentionnés. |
| CA-094 | RF-165, RT-011 | **Étant donné** un destinataire de la remise sans droit sur certains éléments, **quand** la remise est faite, **alors** ces éléments en sont exclus. |

### 11.10 Approbation et diffusion (CA-095 à CA-104)

| ID | Liens | Critère |
|---|---|---|
| CA-095 | RF-173, RF-176 | **Étant donné** une approbation requise, **quand** elle est accordée, **alors** elle est rattachée à une version précise. |
| CA-096 | RF-177, RB-110 | **Étant donné** une approbation accordée, **quand** on consulte les statuts, **alors** conformité et diffusion sont inchangées. |
| CA-097 | RF-175 | **Étant donné** une demande d'approbation, **quand** l'Agent la présente, **alors** livrable, rapport de conformité, réserves, observations et décisions antérieures sont fournis. |
| CA-098 | RF-178 | **Étant donné** un refus d'approbation, **quand** il est enregistré, **alors** il porte un motif et une révision peut être demandée. |
| CA-099 | RB-113, RF-272 | **Étant donné** une version non finalisée ou non conforme, **quand** l'approbation est demandée, **alors** elle est impossible et l'Agent en explique la raison. |
| CA-100 | RF-179, RB-107 | **Étant donné** une version conforme, **quand** aucune décision humaine n'a été prise, **alors** la diffusion reste non autorisée. |
| CA-101 | RF-180 | **Étant donné** une autorisation de diffusion, **quand** on la consulte, **alors** version, destinataires et périmètre sont précisés. |
| CA-102 | RF-181, RF-184 | **Étant donné** un destinataire non autorisé, **quand** une transmission est demandée, **alors** elle n'a pas lieu. |
| CA-103 | RF-182, RB-058 | **Étant donné** des droits de diffusion incertains, **quand** la diffusion est envisagée, **alors** l'opération est suspendue jusqu'à clarification. |
| CA-104 | RF-183 | **Étant donné** une autorisation de diffusion révoquée, **quand** on consulte l'historique, **alors** la révocation est tracée. |

### 11.11 Versions et révision (CA-105 à CA-114)

| ID | Liens | Critère |
|---|---|---|
| CA-105 | RF-188, RB-067 | **Étant donné** une version finalisée, **quand** une révision est demandée, **alors** une nouvelle version est créée et la précédente est intacte. |
| CA-106 | RF-189, RB-071 | **Étant donné** une version approuvée, **quand** une révision est produite, **alors** la version approuvée n'est ni écrasée ni altérée. |
| CA-107 | RF-190, RB-072 | **Étant donné** une information source modifiée, **quand** aucune révision n'est demandée, **alors** aucune nouvelle version n'est créée. |
| CA-108 | RF-191 | **Étant donné** une demande de révision, **quand** l'Agent la prépare, **alors** il présente l'analyse d'impact. |
| CA-109 | RF-192 | **Étant donné** une nouvelle version, **quand** elle est produite, **alors** les contrôles applicables sont rejoués. |
| CA-110 | RF-196, RB-116 | **Étant donné** une nouvelle version, **quand** on consulte ses statuts, **alors** conformité, approbation et diffusion sont remis à zéro. |
| CA-111 | RF-187, RB-069 | **Étant donné** une règle modifiée, **quand** on consulte les livrables antérieurs, **alors** ils sont inchangés. |
| CA-112 | RF-185, RT-031 | **Étant donné** un livrable, **quand** on consulte sa traçabilité, **alors** les versions de sources, règles et modèles de sa création sont retrouvées. |
| CA-113 | RF-193, RF-198 | **Étant donné** une révision, **quand** on consulte l'historique, **alors** motif, auteur et date figurent. |
| CA-114 | RF-194, RF-197 | **Étant donné** deux versions, **quand** on les compare, **alors** les différences sont présentées et la version remplacée reste consultable. |

### 11.12 Suspension, reprise et annulation (CA-115 à CA-126)

| ID | Liens | Critère |
|---|---|---|
| CA-115 | RF-199 à RF-201 | **Étant donné** une demande en cours, **quand** l'utilisateur l'interrompt, **alors** les opérations s'arrêtent et la demande est Suspendue. |
| CA-116 | RF-202, RF-203 | **Étant donné** une suspension, **quand** on consulte l'état conservé, **alors** les résultats validés sont distingués des provisoires. |
| CA-117 | RF-204, RB-083 | **Étant donné** une demande Suspendue, **quand** un livrable provisoire existe, **alors** il est marqué non final. |
| CA-118 | RF-205 | **Étant donné** une demande Suspendue, **quand** les règles de conservation le permettent, **alors** l'état de travail est conservé. |
| CA-119 | RB-084, RF-200 | **Étant donné** une interruption à l'initiative de l'utilisateur, **quand** elle est enregistrée, **alors** elle vaut suspension et non annulation. |
| CA-120 | RF-212 | **Étant donné** une demande Suspendue, **quand** l'Agent décrit son statut, **alors** elle n'est jamais présentée comme finalisée. |
| CA-121 | RF-206 | **Étant donné** une reprise, **quand** elle est demandée, **alors** l'Agent vérifie sources, informations, règles et autorisations. |
| CA-122 | RF-207, RF-208 | **Étant donné** une reprise après changement d'une source, **quand** l'Agent poursuit, **alors** les éléments valides sont conservés et les éléments affectés réexécutés avec leurs contrôles. |
| CA-123 | RF-209 | **Étant donné** une reprise, **quand** elle est effectuée, **alors** l'utilisateur est informé de ce qui a changé et de ses conséquences. |
| CA-124 | RB-087, RB-088 | **Étant donné** une durée maximale de conservation fixée par la personne responsable et expirée, **quand** la reprise est demandée, **alors** elle est refusée avec un motif communicable ; sans durée fixée, la demande peut être reprise. |
| CA-125 | RF-210 | **Étant donné** une demande d'annulation définitive, **quand** l'utilisateur ne confirme pas explicitement, **alors** la demande est suspendue et non annulée. |
| CA-126 | RF-211 | **Étant donné** une annulation confirmée, **quand** une reprise est tentée, **alors** elle est impossible, les versions provisoires sont Abandonnées et le travail n'est pas présenté comme livrable. |

### 11.13 Livrables multiples et priorités (CA-127 à CA-134)

| ID | Liens | Critère |
|---|---|---|
| CA-127 | RF-213 | **Étant donné** deux livrables dépendants, **quand** l'un est bloqué, **alors** les éléments de l'autre qui en dépendent sont bloqués. |
| CA-128 | RF-214 | **Étant donné** une incohérence entre deux documents, **quand** l'Agent la détecte, **alors** elle est signalée. |
| CA-129 | RF-216, RB-095 | **Étant donné** un livrable déjà produit, **quand** une incohérence inter-documents est détectée, **alors** il n'est pas modifié automatiquement. |
| CA-130 | RF-223 | **Étant donné** un livrable bloqué, **quand** d'autres livrables n'en dépendent pas, **alors** ils avancent. |
| CA-131 | RF-219 | **Étant donné** deux demandes concurrentes, **quand** les critères explicites tranchent, **alors** l'ordre est appliqué et motivé. |
| CA-132 | RF-221, RB-096 | **Étant donné** une urgence non validée, **quand** les priorités sont établies, **alors** elle n'est pas prise en compte. |
| CA-133 | RF-220, RB-091 | **Étant donné** des règles insuffisantes pour départager, **quand** l'Agent ordonne, **alors** il prépare les éléments d'arbitrage et sollicite la personne responsable. |
| CA-134 | RF-217, RF-218 | **Étant donné** une information modifiée utilisée par une autre production, **quand** aucun signalement ni révision n'est demandé, **alors** cette production n'est pas révisée. |

### 11.14 Interaction et suivi (CA-135 à CA-144)

| ID | Liens | Critère |
|---|---|---|
| CA-135 | RF-226 à RF-231 | **Étant donné** une demande en cours, **quand** l'utilisateur demande l'état, **alors** l'Agent indique étapes terminées, étapes en cours, motifs communicables, éléments attendus et prochaine action. |
| CA-136 | RF-232 | **Étant donné** plusieurs éléments à des états différents, **quand** l'Agent les présente, **alors** terminé, suspendu, bloqué, en attente de décision et finalisé sont distingués. |
| CA-137 | RF-233, RT-006 | **Étant donné** une information protégée, **quand** l'état d'avancement est présenté, **alors** elle n'y est pas exposée. |
| CA-138 | RF-234, RB-065 | **Étant donné** deux interlocuteurs de droits différents, **quand** ils demandent le motif d'un même blocage, **alors** chacun reçoit un motif adapté à ses droits. |
| CA-139 | RF-235, RB-117 | **Étant donné** une opération non aboutie, **quand** l'Agent communique, **alors** il n'annonce aucune réussite. |
| CA-140 | RF-236, RB-111 | **Étant donné** un message d'état, **quand** on le lit, **alors** il emploie les états fonctionnels et non les étapes internes. |
| CA-141 | RF-237, RB-109 | **Étant donné** un livrable finalisé, **quand** son statut est présenté, **alors** conformité, approbation et diffusion apparaissent séparément. |
| CA-142 | RF-225 | **Étant donné** un utilisateur sans connaissance des modèles ni des règles, **quand** il formule sa demande, **alors** l'Agent la traite sans exiger cette connaissance. |
| CA-143 | RF-238 | **Étant donné** un utilisateur autorisé, **quand** il demande l'historique de sa demande, **alors** échanges et décisions lui sont restitués selon ses droits. |
| CA-144 | RB-120 | **Étant donné** un blocage, **quand** son motif est communiqué, **alors** il est formulé sans jargon technique. |

### 11.15 Gouvernance (CA-145 à CA-156)

| ID | Liens | Critère |
|---|---|---|
| CA-145 | RF-239, RB-005 | **Étant donné** une décision substantielle non couverte, **quand** l'Agent y est confronté, **alors** il suspend l'opération concernée et ne décide pas. |
| CA-146 | RF-240, RF-244 | **Étant donné** une décision requise, **quand** l'Agent sollicite la personne responsable, **alors** la demande contient question, contexte, options issues des règles, conséquences et urgence, et les opérations indépendantes continuent. |
| CA-147 | RF-241 à RF-243 | **Étant donné** une décision réservée, **quand** elle est prise par une personne autre que la personne responsable, **alors** elle n'est pas valable ; quand elle est valable, **alors** elle est tracée et sa portée est limitée à l'objet et à la demande. |
| CA-148 | RF-245 à RF-247 | **Étant donné** une autorisation ponctuelle, **quand** la personne responsable l'accorde, **alors** la source est utilisable pour la demande et le registre permanent reste inchangé. |
| CA-149 | RF-246, RF-248, RF-249 | **Étant donné** une autorisation ponctuelle, **quand** la demande se termine ou la durée expire, **alors** elle prend fin ; elle figure dans la traçabilité. |
| CA-150 | RF-250, RF-252 | **Étant donné** une modification du registre permanent, **quand** elle est tentée par un autre que la personne responsable, **alors** elle est refusée ; quand elle est faite par la personne responsable, **alors** le registre est versionné et les productions antérieures restent liées à l'ancien. |
| CA-151 | RF-251 | **Étant donné** une source du registre, **quand** on la consulte, **alors** ses autorisations aux quatre niveaux figurent. |
| CA-152 | RF-254, RF-258, RF-259 | **Étant donné** une modification de règle, de modèle ou de préférence, **quand** elle est tentée par un utilisateur ordinaire, **alors** elle est refusée ; faite par la personne responsable, **alors** elle est versionnée sans effet sur les productions antérieures ni sur les demandes en cours. |
| CA-153 | RF-255, RF-256 | **Étant donné** un exemple contredisant une règle, **quand** l'Agent produit, **alors** il applique la règle et signale l'incohérence comme observation. |
| CA-154 | RF-260 à RF-263 | **Étant donné** une exception, **quand** elle est demandée par un autre que la personne responsable, **alors** elle est refusée ; quand elle est accordée, **alors** elle est tracée, mentionnée en réserve et n'a modifié aucune règle. |
| CA-155 | RF-264, RF-265, RF-267 | **Étant donné** une correction ponctuelle d'un utilisateur, **quand** une demande ultérieure est traitée, **alors** elle n'est pas influencée par cette correction. |
| CA-156 | RF-266 | **Étant donné** une proposition d'évolution de règle, **quand** elle est faite, **alors** elle est consignée et transmise à la personne responsable, sans effet avant décision. |

### 11.16 Confidentialité et données sensibles (CA-157 à CA-168)

| ID | Liens | Critère |
|---|---|---|
| CA-157 | RT-002, RT-013 | **Étant donné** un utilisateur et un destinataire de droits différents, **quand** ils accèdent à un même livrable, **alors** chacun n'accède qu'à ce que ses droits permettent. |
| CA-158 | RT-003, RT-004 | **Étant donné** une source accessible mais dont l'utilisation est interdite, **quand** l'Agent traite, **alors** il ne l'utilise pas. |
| CA-159 | RT-005, RB-058 | **Étant donné** des droits incertains, **quand** l'opération est lancée, **alors** elle est suspendue. |
| CA-160 | RT-006, RT-007 | **Étant donné** le refus d'accès à une source protégée, **quand** l'Agent l'explique, **alors** l'explication ne révèle ni son existence, ni son identité, ni son contenu. |
| CA-161 | RT-008 | **Étant donné** une question sur une source inaccessible à l'interlocuteur, **quand** l'Agent répond, **alors** il ne confirme ni n'infirme son existence. |
| CA-162 | RT-009 | **Étant donné** une reprise, **quand** elle est effectuée, **alors** les droits sont revérifiés. |
| CA-163 | RT-010, RT-011 | **Étant donné** un livrable agrégeant des informations de sensibilités différentes, **quand** on consulte sa classification, **alors** elle est au moins aussi restrictive que la plus contraignante ; le rapport de traçabilité a sa propre classification. |
| CA-164 | RT-017, RT-018 | **Étant donné** des données non nécessaires ou non permises, **quand** l'Agent insère, **alors** elles ne sont pas reprises ou sont masquées. |
| CA-165 | RT-020, RT-021 | **Étant donné** une donnée masquée, **quand** un lecteur non autorisé consulte livrable et traçabilité, **alors** le contenu n'est pas reconstituable. |
| CA-166 | RT-022, RT-023 | **Étant donné** un cas non couvert par les règles de minimisation ou un masquage rendant un élément obligatoire incohérent, **quand** l'Agent y est conduit, **alors** il suspend ou bloque l'élément et sollicite une décision. |
| CA-167 | RT-014, RB-062 | **Étant donné** une action ordinaire largement ouverte, **quand** un utilisateur l'exécute, **alors** aucune restriction de source, de confidentialité ni de diffusion n'est levée. |
| CA-168 | RT-015, RT-026 | **Étant donné** une information fournie par un utilisateur, **quand** une autre demande est traitée, **alors** elle n'est pas réutilisée sans autorisation ; sa conservation respecte les règles. |

### 11.17 Traçabilité et historique (CA-169 à CA-176)

| ID | Liens | Critère |
|---|---|---|
| CA-169 | RT-027, RT-037 | **Étant donné** un élément significatif d'un livrable finalisé, **quand** on remonte sa chaîne, **alors** on retrouve source, référence, statut de validation et transformations. |
| CA-170 | RT-035, RT-036 | **Étant donné** une demande terminée, **quand** on consulte son historique, **alors** chaque changement d'état est horodaté avec son auteur et son motif et l'ensemble se reconstitue chronologiquement. |
| CA-171 | RT-062, RT-063, RF-271 | **Étant donné** une entrée d'historique, **quand** un utilisateur tente de la modifier ou de la supprimer, **alors** c'est refusé ; une correction s'ajoute comme entrée complémentaire. |
| CA-172 | RT-031, RT-034 | **Étant donné** un livrable, **quand** on consulte sa traçabilité, **alors** les versions de règles, de modèle, de registre et de contrôles et tous les résultats de contrôle (rejeux inclus) y figurent. |
| CA-173 | RF-268, RF-270 | **Étant donné** un lecteur sans droit sur une source, **quand** il consulte la traçabilité, **alors** il voit une mention générique à la place de la source. |
| CA-174 | RT-040, RT-041 | **Étant donné** des informations exclues, masquées ou candidates non retenues, **quand** on consulte la traçabilité, **alors** leur existence et leur motif général y figurent. |
| CA-175 | RT-064, RT-066 | **Étant donné** une suppression en fin de conservation, **quand** elle a lieu, **alors** une trace minimale (existence, date, motif général) subsiste. |
| CA-176 | RT-065 | **Étant donné** un livrable finalisé, **quand** une personne autorisée à consulter la traçabilité (l'auteur de la demande ou la personne responsable) l'examine, **alors** elle peut reconstituer pourquoi il est tel qu'il est (règles, sources, décisions, contrôles). |

### 11.18 Compléments : approbation, diffusion et règles MVP (CA-177 à CA-195)

| ID | Liens | Critère |
|---|---|---|
| CA-177 | RF-272, RB-113, RB-124 | **Étant donné** une version provisoire non conforme, **quand** l'approbation est demandée, **alors** elle est impossible et le statut de conformité reste Non conforme. |
| CA-178 | RF-273, RB-123 | **Étant donné** une version finalisée conforme, **quand** elle est approuvée ou refusée, **alors** son statut de conformité reste Conforme. |
| CA-179 | RF-274, RB-125 | **Étant donné** une version approuvée, **quand** on tente d'annuler l'approbation, **alors** c'est refusé ; sa remise en cause passe par une révision. |
| CA-180 | RF-275, RB-114 | **Étant donné** une version finalisée dont l'approbation requise est En attente, **quand** la diffusion est demandée, **alors** elle est impossible. |
| CA-181 | RF-275, RB-124 | **Étant donné** une version provisoire ou non conforme, **quand** la diffusion est demandée, **alors** elle est impossible au MVP. |
| CA-182 | RF-276, RB-126 | **Étant donné** une version dont l'approbation est Refusée, **quand** la diffusion est demandée, **alors** elle est impossible. |
| CA-183 | RF-277, RB-123 | **Étant donné** une autorisation de diffusion accordée, révoquée ou modifiée, **quand** on consulte les statuts, **alors** conformité et approbation sont inchangées. |
| CA-184 | RF-275 | **Étant donné** une version finalisée dont l'approbation est Non requise, **quand** la personne responsable autorise la diffusion et que les droits sont vérifiés, **alors** la diffusion est autorisée sans approbation. |
| CA-185 | RF-278, RB-128 | **Étant donné** une diffusion autorisée, **quand** des destinataires accèdent au livrable, **alors** seuls les destinataires désignés y accèdent dans le produit et l'Agent ne transmet rien hors du produit. |
| CA-186 | RF-279 | **Étant donné** une autorisation révoquée, **quand** un destinataire tente d'accéder au livrable, **alors** l'accès est refusé et l'Agent a mentionné que les copies déjà obtenues ne sont pas concernées. |
| CA-187 | RF-210 | **Étant donné** une demande d'annulation définitive, **quand** elle émane d'une personne autre que l'auteur ou la personne responsable, ou porte sur une demande Finalisée, **alors** elle est refusée ; **quand** l'auteur confirme explicitement sur une demande non finalisée, **alors** la demande est Annulée définitivement. |
| CA-188 | RF-211 | **Étant donné** l'annulation d'une demande de révision liée, **quand** elle est confirmée, **alors** la demande d'origine et ses versions finalisées restent inchangées. |
| CA-189 | RF-008, IN-04 | **Étant donné** une demande portant sur deux livrables, **quand** l'utilisateur confirme la scission, **alors** deux demandes indépendantes sont créées, chacune avec son propre cycle. |
| CA-190 | RF-017, RF-043, RB-026 | **Étant donné** une information fournie par l'utilisateur, **quand** l'Agent l'évalue, **alors** elle est QI-02 ; elle ne devient QI-01 que par règle du type ou décision explicite de la personne responsable pour la demande. |
| CA-191 | RF-195 | **Étant donné** une révision, **quand** elle démarre, **alors** les versions d'origine de modèle, de règles et de registre sont utilisées ; des versions plus récentes ne le sont que sur décision explicite et tracée de la personne responsable. |
| CA-192 | RB-108, RF-244 | **Étant donné** l'indisponibilité de la personne responsable, **quand** une décision réservée est requise, **alors** aucun autre acteur ne la prend, les éléments restent en attente et les opérations indépendantes continuent. |
| CA-193 | RB-087, RT-061 | **Étant donné** qu'aucune durée de conservation n'est fixée, **quand** une demande reste suspendue, **alors** elle n'est ni supprimée ni périmée automatiquement. |
| CA-194 | RF-281, RB-127 (V2) | **Étant donné** une exception accordée sur une règle contrôlée, **quand** les contrôles s'exécutent, **alors** ils s'appliquent aux règles telles qu'exceptées, l'exception figure en réserve et aucun contrôle échoué n'est converti en réussi. |
| CA-195 | RF-280 (V2, sous réserve de QO-036) | **Étant donné** une diffusion exceptionnelle d'une version non conforme décidée par la personne responsable, **quand** le document est rendu accessible, **alors** il porte un marquage visible, la décision et la réserve figurent dans les rapports et le statut de conformité reste Non conforme. |

---
## 12. Cas limites et scénarios d'erreur

Chaque cas indique le **comportement attendu** de l'Agent. Les cas dont la réponse dépend d'une question ouverte renvoient à celle-ci.

| ID | Situation | Comportement attendu | Liens | Statut |
|---|---|---|---|---|
| CL-001 | Un utilisateur non autorisé soumet une demande. | Refus avec motif communicable ; aucune production ; aucune information protégée révélée. | RF-009, RT-006 | [D] |
| CL-002 | L'utilisateur ne répond pas à une question de clarification portant sur un choix substantiel. | L'Agent ne choisit pas ; l'élément dépendant reste en attente ou bloqué ; les opérations indépendantes continuent. | RF-018 | [D] |
| CL-003 | Une réponse de l'utilisateur contredit une règle. | La règle prévaut ; l'Agent le signale ; seule la personne responsable peut accorder une exception. | RF-007, RB-006, RB-101 | [D] |
| CL-004 | Le type de livrable demandé n'a pas de modèle. | Blocage (MB-01) ; aucune structure improvisée ; sollicitation de la personne responsable. | RF-029 | [D] |
| CL-005 | Une condition indispensable est insatisfaite mais des diagnostics restent possibles. | La partie concernée est bloquée avec motif communicable ; le diagnostic se poursuit. | RF-025, RF-026 | [D] |
| CL-006 | Les droits d'accès à une source sont incertains dès la faisabilité. | L'opération concernée est suspendue jusqu'à clarification ; pas de consultation. | RB-058, RT-005 | [D] |
| CL-007 | Une source autorisée est indisponible. | Signalement ; poursuite auprès des autres sources ; pas de conclusion d'absence ; escalade si l'élément est obligatoire (ES-08). | RF-042 | [P] |
| CL-008 | Une information source peut correspondre à plusieurs champs cibles. | Ligne À clarifier ; aucune résolution arbitraire. | RF-056, RB-023 | [D] |
| CL-009 | INIS fournit une information sans indication de vérification. | Traitée comme candidate tant que les critères explicites de vérification ne sont pas satisfaits ; pas présentée comme fait établi. | RF-061, RF-063, QO-029 | [D] / [Q] |
| CL-010 | Une même information est utile pour une analyse historique et pour décrire la situation actuelle. | Statut évalué par usage : utilisable pour le premier, Hors période pour le second. | RF-064, RF-067 | [D] |
| CL-011 | L'Agent « pourrait raisonnablement estimer » une valeur manquante. | Interdit ; la lacune est consignée ; éléments dépendants bloqués si obligatoires. | RF-075, RB-001 | [D] |
| CL-012 | Une information plus récente contredit une plus ancienne mais plus fiable. | Application des règles de priorité ; la récence seule ne décide pas ; à défaut de règle, arbitrage. | RF-066, RF-082 | [D] |
| CL-013 | Un arbitrage a été rendu pour une demande ; un cas similaire survient plus tard. | L'arbitrage ne vaut pas règle générale ; l'Agent sollicite à nouveau, sauf changement de règle par procédure. | RF-243, RB-034 | [D] |
| CL-014 | L'utilisateur demande une transformation non couverte par une règle. | Refus ; traitée comme décision non couverte ; sollicitation de la personne habilitée. | RF-104 | [D] |
| CL-015 | Une source énonce une hypothèse comme une certitude, ou l'inverse. | L'Agent préserve le statut d'origine et le signale ; il ne transforme pas une hypothèse en fait. | RF-101, RB-024 | [D] |
| CL-016 | La méthode de calcul n'est pas définie. | Clarification ou blocage ; aucune formule de remplacement. | RF-111, RB-044 | [D] |
| CL-017 | Une donnée d'entrée d'un calcul est incertaine. | Le résultat dérivé reste au plus de même qualité et est identifié comme dérivé. | RF-113, RF-114 | [P] |
| CL-018 | Des éléments obligatoires sont bloqués alors que le reste est prêt. | Version provisoire marquée, emplacements bloqués avec motif ; jamais présentée comme finale. | RF-119, RF-120, RF-171 | [P] |
| CL-019 | Le format demandé n'est pas autorisé pour ce type de livrable. | Blocage ou proposition des formats autorisés ; pas de dégradation silencieuse. | RF-126 | [P] |
| CL-020 | Un contrôle ne peut pas être exécuté (données manquantes). | Résultat « non exécutable », jamais « réussi » ; conformité impossible tant que non résolu. | RB-054, RT-054 | [P] |
| CL-021 | Les objectifs et les indicateurs d'un protocole sont incohérents. | Contrôle CT-12 échoué (si la règle existe) ; l'incohérence est signalée ; l'Agent ne modifie aucun choix méthodologique ; décision humaine. | RF-139, RF-140, RF-152 | [D] |
| CL-022 | Les cycles de correction ne convergent pas. | Escalade à la personne responsable après la borne ; historique conservé. | RF-153, ES-06 | [P] |
| CL-023 | Une anomalie n'est couverte par aucune règle. | Consignée comme observation ; livrable inchangé. | RF-149, RF-150 | [D] |
| CL-024 | Le type de livrable n'exige pas de rapport de traçabilité. | Mention dans le rapport de conformité avec la règle correspondante. | RF-168 | [P] |
| CL-025 | L'utilisateur demande « c'est terminé ? » alors que des contrôles sont en cours. | L'Agent indique l'état exact (En contrôle qualité) sans annoncer de réussite. | RF-163, RF-235 | [D] |
| CL-026 | L'approbateur refuse la version. | Refus motivé enregistré ; révision possible ; la version refusée reste intacte. | RF-178 | [P] |
| CL-027 | On sollicite l'approbation d'une version non finalisée ou non conforme. | Impossible : l'Agent explique que la version doit d'abord être corrigée ou révisée ; aucune approbation implicite ; statut de conformité inchangé. | RF-272, RF-273, RB-113 | [P] |
| CL-028 | Les droits de diffusion sont incertains. | Opération concernée suspendue jusqu'à clarification. | RF-182, RT-005 | [D] |
| CL-029 | Une autorisation de diffusion est révoquée alors que le livrable a déjà été consulté ou obtenu. | Révocation tracée ; l'accessibilité cesse dans le produit ; les copies déjà obtenues ne sont pas concernées et l'Agent le mentionne. | RF-183, RF-279 | [P] |
| CL-030 | Une révision est demandée sur une version approuvée. | Nouvelle version ; l'approuvée reste intacte et consultable. | RF-189, RB-071 | [D] |
| CL-031 | Les règles ont changé depuis la version d'origine, et une révision est demandée. | Versions d'origine par défaut ; versions plus récentes seulement sur décision explicite et tracée de la personne responsable. | RF-195 | [P] |
| CL-032 | L'utilisateur interrompt la demande pendant un calcul ou un contrôle. | L'opération en cours est considérée comme non aboutie ; elle est rejouée à la reprise. | RF-201, RF-208 | [D] |
| CL-033 | Une source ou une règle change pendant la suspension. | À la reprise, revalidation ; éléments valides conservés ; éléments affectés réexécutés avec leurs contrôles. | RF-206 à RF-208 | [D] |
| CL-034 | La durée maximale de conservation fixée par la personne responsable expire avant la reprise. | Reprise impossible ; motif communicable ; nouvelle demande nécessaire. Sans durée fixée, aucune péremption. | RB-087, RB-088 | [P] |
| CL-035 | L'utilisateur demande l'annulation sans confirmer. | La demande est suspendue et non annulée. | RF-210 | [P] |
| CL-036 | Une annulation est demandée sur une demande déjà Finalisée. | Impossible (état final, IV-04) ; les versions finalisées, approuvées ou diffusées restent inchangées ; seule la demande de révision liée peut être annulée ; la révocation de diffusion est une décision distincte. | RF-210, IV-04 | [P] |
| CL-037 | Un livrable dépend d'un autre livrable bloqué. | Éléments dépendants bloqués ; éléments indépendants poursuivis. | RF-223 | [P] |
| CL-038 | Une incohérence entre livrables touche un livrable déjà produit. | Signalement ; aucune modification automatique ; révision explicite requise. | RF-216, RB-095 | [D] |
| CL-039 | Un utilisateur déclare une demande urgente sans validation. | L'urgence n'est pas prise en compte dans la priorité. | RF-221 | [D] |
| CL-040 | Les critères de priorité ne permettent pas de départager deux demandes. | Éléments d'arbitrage préparés ; personne responsable sollicitée. | RF-220 | [D] |
| CL-041 | Un utilisateur sans droit sur certaines sources demande l'état d'avancement. | État présenté avec motifs généraux ; aucune information protégée. | RF-234, RT-006 | [D] |
| CL-042 | La personne responsable est indisponible. | Les éléments concernés restent en attente ; les opérations indépendantes continuent ; aucune décision réservée par un tiers (pas de suppléance au MVP). | RB-108 | [P] |
| CL-043 | L'accès à une source est accordé sans droit d'intégration. | Le contenu peut être consulté et utilisé s'il est autorisé, mais n'est pas intégré au livrable. | RF-246, RT-003 | [D] |
| CL-044 | Une source est retirée du registre permanent pendant des demandes en cours. | Les demandes en cours restent liées au registre figé ; la validité des autorisations est revérifiée avant intégration et diffusion. | RF-028, RT-004 | [P] |
| CL-045 | Un exemple du modèle contredit une règle. | La règle est appliquée ; incohérence signalée comme observation à la personne responsable. | RF-256 | [D] / [P] |
| CL-046 | Une règle est modifiée pendant une demande en cours. | Aucun effet automatique sur la demande en cours. | RF-258, RB-105 | [D] |
| CL-047 | Une exception est demandée sur une restriction relevant de droits de tiers. | L'Agent signale que le droit pourrait ne pas relever de la personne responsable ; en cas de doute, les droits sont considérés incertains (suspension). | RB-058 | [Q] |
| CL-048 | L'utilisateur insiste pour que sa correction vaille pour toutes les demandes futures. | L'Agent explique que cela exige une décision de la personne responsable ; propose de transmettre la proposition. | RF-266 | [P] |
| CL-049 | Un lecteur sans droit sur une source consulte la traçabilité. | Mention générique à la place de la source. | RF-270 | [D] |
| CL-050 | Le masquage d'une donnée rend un élément obligatoire incohérent. | Blocage de l'élément et décision sollicitée. | RT-023 | [P] |
| CL-051 | Une donnée masquée peut être reconstituée par recoupement avec d'autres éléments. | Les éléments de recoupement sont également masqués ou exclus ; en cas de doute, suspension. | RT-021, RB-066 | [P] |
| CL-052 | Une demande identique à une demande en cours est soumise. | L'Agent signale un doublon possible et ne les fusionne pas sans confirmation ; les demandes restent indépendantes. | RB-092 | [P] |
| CL-053 | La demande fait référence à une pièce jointe absente ou illisible. | L'Agent le signale et la demande ; il ne suppose pas son contenu. | RF-043, RF-075 | [P] |
| CL-054 | La demande suppose une décision de fond (« choisis les meilleurs indicateurs »). | L'Agent ne décide pas ; décision non couverte ; sollicitation de la personne habilitée. | RB-003, RB-004 | [D] |
| CL-055 | Une information source est modifiée après la finalisation d'un livrable qui l'utilise. | Aucune modification automatique ; signalement éventuel ; révision seulement sur demande explicite. | RF-217, RF-218 | [D] |
| CL-056 | Deux demandes utilisent la même information et l'une la corrige. | Demandes indépendantes ; aucune propagation automatique. | RB-092, RB-093 | [D] |
| CL-057 | Une information fournie par l'utilisateur (QI-02 par défaut) contredit celle d'INIS. | Contradiction traitée par les règles de priorité ; aucune préférence implicite pour l'une ou l'autre. | RF-017, RF-081 | [P] |
| CL-058 | Le destinataire du livrable diffère du demandeur. | Les droits sont évalués pour chaque destinataire. | RF-181 | [D] |
| CL-059 | L'Agent est interrompu involontairement pendant une opération. | L'opération non aboutie n'est pas considérée comme réussie ; l'état est reconstitué depuis l'historique ; l'incident est consigné. | RT-068 | [P] |
| CL-060 | Deux règles applicables se contredisent. | L'Agent ne choisit pas ; décision non couverte ; sollicitation de la personne habilitée. | RB-003, RB-006 | [P] |
| CL-061 | Une diffusion est demandée pour une version provisoire ou non conforme. | Impossible au MVP ; l'Agent explique les prérequis (version finalisée, approbation obtenue ou non requise) ; statut de conformité inchangé. | RF-275, RB-124 | [P] |
| CL-062 | Une diffusion est demandée alors que l'approbation requise est en attente ou refusée. | Impossible ; l'Agent indique l'état d'approbation ; en cas de refus, une nouvelle version est nécessaire. | RF-276, RB-126 | [P] |
| CL-063 | Une erreur est découverte après l'approbation d'une version. | L'approbation n'est pas révoquée ; une révision crée une nouvelle version ; la personne responsable peut révoquer la diffusion de la version concernée. | RF-274, RF-279 | [P] |
| CL-064 | La demande porte sur deux livrables (par exemple un protocole et un tableau de suivi). | Au MVP : aucun traitement coordonné ; l'Agent propose de scinder en deux demandes indépendantes ; sans confirmation, rien n'est produit. | RF-008 | [P] |

---

## 13. MVP, évolutions ultérieures et points à arbitrer

### 13.1 Principe de découpage

Le MVP doit **démontrer que le contrôle fonctionne**, pas couvrir tous les types de livrables. Un produit étroit mais fiable vaut mieux qu'un produit large et incertain, parce que la valeur du produit tient à ses garanties (section 1.2). [P]

### 13.2 Périmètre du MVP proposé

| Capacité | Cas d'usage | Exigences principales | Remarque |
|---|---|---|---|
| Réception, clarification minimale, suivi | UC-001, UC-002, UC-023 | RF-001 à RF-018, RF-225 à RF-238 | Questions ciblées uniquement. |
| Faisabilité et versions figées | UC-003 | RF-019 à RF-029 | Diagnostic seul reporté (RF-030). |
| Mobilisation INIS + autres sources du registre | UC-004, UC-026 (minimal), UC-025 | RF-031 à RF-044, RF-245 à RF-252 | Le contrat avec INIS est une condition (QO-003). |
| Cartographie et qualité | UC-005, UC-006 | RF-045 à RF-072 | Cœur du produit. |
| Lacunes et contradictions | UC-007, UC-008, UC-024 | RF-073 à RF-090, RF-239 à RF-244 | Arbitrage par la personne responsable. |
| Transformations et calculs autorisés | UC-009, UC-010 | RF-091 à RF-114 | Limités aux transformations nécessaires au type pilote. |
| Production, contrôles, anomalies | UC-011, UC-012, UC-013 | RF-115 à RF-154 | Corrections mécaniques limitées à la liste autorisée. |
| Finalisation, trois éléments, trois statuts | UC-014, UC-015, UC-016 | RF-155 à RF-184, RF-272 à RF-279 | Cœur de la valeur de confiance ; approbation et diffusion selon 9.6. |
| Versions et révision | UC-017 | RF-185 à RF-198 | Différences détaillées reportées (RF-194). |
| Suspension, reprise, annulation | UC-018, UC-019, UC-020 | RF-199 à RF-212 | Annulation selon la règle MVP de 13.4 (QO-011). |
| Gouvernance minimale | UC-027 | RF-254 à RF-259, RF-265 | Modèles et règles du type pilote. |
| Traçabilité et historique | UC-030 | RF-268 à RF-271, RT-027 à RT-042, RT-061 à RT-068 | |
| Confidentialité et minimisation | UC-031 | RT-001 à RT-026 | Sur la base des règles du type pilote. |

**Cadrage proposé du MVP** [P] (à valider, QO-001, QO-002) :
- **Un seul type de livrable pilote**, avec un seul modèle et ses règles. Le cahier cite le protocole de recherche comme exemple de contrôles méthodologiques (§5-É9) : il pourrait servir de pilote, **sans que cela soit décidé**.
- **Un ou deux formats de sortie** parmi ceux envisagés au §9.
- **Une seule personne responsable**, sans suppléance dans un premier temps (QO-008 pour le risque).
- **Une demande, un livrable** : une demande portant sur plusieurs livrables est scindée, sur confirmation, en demandes indépendantes (RF-008). La coordination de livrables multiples, la priorisation entre demandes, les exceptions et les propositions de règles sont **hors MVP**.
- **Approbation et diffusion** : règles MVP définies en 13.4 et 9.6 (approbateur unique, version finalisée uniquement, diffusion limitée à l'accessibilité dans le produit).

### 13.3 Évolutions ultérieures

| Version | Contenu | Exigences |
|---|---|---|
| **V2** | Livrables multiples avec dépendances et cohérence inter-documents. | RF-213 à RF-215, RF-223 |
| **V2** | Priorisation de demandes concurrentes. | RF-219 à RF-222 |
| **V2** | Exceptions tracées. | RF-260 à RF-263 |
| **V2** | Propositions de règles par les utilisateurs et gestion des corrections ponctuelles. | RF-264, RF-266, RF-267 |
| **V2** | Diagnostic de faisabilité seul. | RF-030 |
| **V2** | Récapitulatif des différences entre versions. | RF-194 |
| **V2** | Signalement d'impact entre productions. | RF-224 |
| **V2** | Liste des sources autorisées par type de livrable. | RF-253 |
| **V2** | Profil d'auditeur dédié (PU-05) : lecture seule de la traçabilité et de l'historique de demandes dont l'auditeur n'est pas l'auteur ; export des rapports. | PU-05, RT-067 |
| **V2** | Diffusion exceptionnelle d'une version non finalisée ou non conforme, si elle est retenue (QO-036). | RF-280 |
| **V2** | Exceptions et appréciation de la conformité par rapport aux règles telles qu'exceptées. | RF-281, RB-127 |
| **V2** | Approbateurs autres que la personne responsable, désignés par les règles ; approbation avec réserves de l'approbateur. | RF-174 |
| **V2** | Transmission hors produit par l'Agent, si elle est retenue. | RF-278 |
| **V3** | Types de livrables supplémentaires, formats supplémentaires. | §9 |
| **V3** | Multi-organisations et cloisonnement (si besoin, QO-021). | — |
| **V3** | Suppléance de la personne responsable (si arbitrée). | QO-008 |

### 13.4 Règles MVP retenues pour lever les dépendances aux questions ouvertes

Le MVP ne peut pas comporter de fonctionnalité dont les règles essentielles restent ouvertes. Pour chaque fonctionnalité du MVP qui dépendait d'une question ouverte, le tableau ci-dessous retient une **règle MVP testable** ; la partie qui n'est pas tranchée est **reportée hors MVP**. Ces règles restent des **propositions [P]** jusqu'à validation (Annexe E) : une fois validées, la question correspondante est refermée pour le MVP, et seule sa partie reportée reste ouverte.

| QO | Fonctionnalité MVP concernée | Règle MVP retenue | Reporté hors MVP | Exigences et critères | PV |
|---|---|---|---|---|---|
| QO-008 | Décisions réservées à la personne responsable | **Aucune suppléance.** En son absence, aucune décision réservée n'est prise par un tiers ; les éléments concernés restent en attente, les opérations indépendantes continuent et les demandeurs sont informés que la décision est attendue. | Suppléance, délai maximal d'attente (V3). | RB-108, RF-239, RF-244 ; CA-192 | PV-32 |
| QO-009 | Approbation (UC-015) | **La personne responsable est seule approbatrice**, lorsque les règles du type exigent une approbation. L'approbation porte sur une version finalisée (donc conforme) ; une version non finalisée ou non conforme ne peut pas être approuvée. Approbation et refus sont définitifs pour la version et sans effet sur la conformité. | Autres approbateurs désignés par les règles ; approbation avec réserves de l'approbateur (V2). | RF-174, RF-272 à RF-274 ; RB-113, RB-123 à RB-125 ; CA-177 à CA-179 | PV-05, PV-28, PV-34 |
| QO-010 | Diffusion (UC-016) | **« Diffuser » = rendre le livrable accessible dans le produit** à des destinataires désignés et autorisés. Seule la personne responsable l'autorise, pour une version finalisée dont l'approbation est Approuvée ou Non requise. L'Agent ne transmet rien hors du produit. La révocation met fin à l'accessibilité dans le produit ; les copies déjà obtenues sont hors périmètre et l'Agent le mentionne. | Transmission hors produit par l'Agent ; diffusion exceptionnelle d'une version non finalisée ou non conforme (QO-036). | RF-179 à RF-184, RF-275 à RF-279 ; RB-114, RB-126, RB-128 ; CA-180 à CA-186 | PV-05, PV-27 |
| QO-011 | Annulation définitive (UC-020) | **Action explicite et confirmée** de l'auteur de la demande ou de la personne responsable ; irréversible ; réservée aux demandes non finalisées. Les versions provisoires deviennent « Abandonnées » ; les versions finalisées restent intactes ; le travail est conservé selon les règles de conservation sans être présenté comme un livrable. | Annulation par d'autres rôles ; effets sur plusieurs demandes liées. | RF-210, RF-211 ; RB-085 ; CA-125, CA-126, CA-187, CA-188 | PV-13, PV-33 |
| QO-012, QO-033 | Conservation et durée de suspension | **Aucune suppression ni péremption automatique.** La personne responsable peut fixer des durées par type de livrable ; si une durée est fixée, la reprise est refusée à son expiration ; toute suppression est tracée. | Durées par défaut, politique d'archivage (QO-028). | RT-061, RT-064 ; RB-087, RB-088 ; CA-124, CA-193 | PV-29 |
| QO-014 | Données personnelles et sensibles | **Sans règle de minimisation applicable, la donnée n'est pas reprise.** Les catégories sont fournies avec les règles du type pilote ; un masquage qui rend un élément obligatoire incohérent bloque l'élément. | Taxonomie générale des données sensibles. | RT-017 à RT-026 ; CA-164 à CA-166 | PV-35 |
| QO-018 | Traçabilité : « élément significatif » | **Tout contenu factuel, chiffre, référence, calcul ou décision**, ainsi que tout élément que le modèle qualifie de significatif. | Définitions plus fines par type. | RT-027, RT-028 ; CA-169 | PV-35 |
| QO-026 | Demandes et livrables multiples | **Une demande vise un livrable.** Une demande portant sur plusieurs livrables est scindée, sur confirmation, en demandes indépendantes. | Coordination de livrables multiples (V2). | RF-008, IN-04 ; CA-010, CA-189 | PV-31 |
| QO-031 | Informations fournies par l'utilisateur | **Source identifiée « fournie par l'utilisateur », statut initial QI-02.** QI-01 seulement par règle du type ou décision de la personne responsable pour la demande. | Règles d'acceptation par catégorie (contenu fourni avec les règles). | RF-017, RF-043 ; RB-026 ; CA-190 | PV-30 |
| QO-013, QO-027, QO-032 | Langue, visibilité, versions en révision | **Français** ; **une demande n'est accessible qu'à son auteur et à la personne responsable** ; **une révision utilise les versions d'origine** sauf décision explicite et tracée de la personne responsable. | Multilingue ; partage entre utilisateurs ; profil d'auditeur (V2). | RB-121 ; RT-016 ; RF-195 ; CA-191 | PV-35 |

### 13.5 Décisions de cadrage et contenus à fournir avant le démarrage du MVP

Ces points ne sont pas des trous de comportement : ce sont des **décisions de cadrage ou des contenus** (types de livrables, règles, registre, droits) que la spécification ne peut pas décider à la place de la personne responsable. **Le comportement du produit en leur absence est spécifié** ; ils bloquent donc le démarrage du pilote, pas la cohérence de la spécification.

| QO | Décision ou contenu attendu | Comportement du produit tant qu'il n'est pas fourni | Exigences |
|---|---|---|---|
| QO-001 | Type de livrable pilote, avec son modèle documentaire et ses règles (par exemple le protocole de recherche, **sans que cela soit décidé**). | Pas de modèle : blocage MB-01, aucune structure improvisée. | RF-019, RF-029 |
| QO-002 | Formats de sortie du MVP, pour le livrable et pour les rapports. | Format non autorisé : blocage ou proposition des formats autorisés. | RF-125, RF-126 |
| QO-003 | Contrat fonctionnel avec INIS : nature des informations fournies, provenance, statut de validation. | Information d'INIS traitée comme candidate tant que les critères de vérification ne sont pas satisfaits. | RF-061, RF-063 ; CL-009 |
| QO-004 | Contenu initial du registre permanent des sources. | Sans registre, aucune source n'est consultable, sauf autorisation ponctuelle. | RF-035, RF-245 |
| QO-005 | Règles de priorité en cas de contradiction (hiérarchie de sources, portée, période). | Sans règle, arbitrage systématique par la personne responsable. | RF-082, RF-084, RF-088 |
| QO-006 | Règles de validité temporelle par catégorie d'information. | Sans règle, une information de la catégorie ne peut pas être QI-01 pour décrire la situation actuelle. | RF-065, RF-067 |
| QO-007 | Définition des droits des utilisateurs, destinataires et sources. | Tout accès non expressément accordé est refusé. | RT-002, RT-016 |
| QO-015 | Liste des corrections mécaniques autorisées, par type de livrable. | Sans règle, aucune correction automatique. | RF-145 |
| QO-029 | Critères explicites de vérification d'une information. | Sans critère, aucune promotion automatique à QI-01. | RF-059 à RF-063, RB-018 |

### 13.6 Questions ouvertes reportables

Ces questions n'empêchent pas le MVP ; elles doivent être tranchées avant la version qui les concerne. Pour QO-013, QO-027, QO-032 et QO-033, la partie MVP est traitée en 13.4 ; seule la partie reportée reste ouverte ici.

| ID | Question | Exigences impactées | Réponse par défaut proposée |
|---|---|---|---|
| QO-013 | Quelle politique de langues pour les échanges et livrables (français seul, multilingue, traduction autorisée comme transformation) ? | RB-121, HY-006 | **MVP : français ; traduction non autorisée sans règle (13.4).** Multilingue : reporté. |
| QO-016 | Quelles catégories de calculs, unités, conventions et arrondis autoriser ? | RF-105 à RF-114 | Définis par type de livrable. |
| QO-017 | Quel niveau d'explication des blocages par profil et par sensibilité de source ? | RF-234, RB-065 | Motif général pour tout interlocuteur sans droit. |
| QO-019 | Quelles attentes de délai, de volumétrie et de disponibilité ? | — | À définir après pilote. |
| QO-020 | Qui signale l'impact d'une modification sur d'autres productions, et selon quelles règles (§6.10 « explicitement signalée ») ? | RF-218, RF-224 | Signalement humain ; signalement par l'Agent informatif, V2. |
| QO-021 | Le produit est-il mono-organisation ou multi-organisations (cloisonnement) ? | RT-002, RT-013 | Mono-organisation. |
| QO-022 | Faut-il modéliser les licences et conditions d'usage des sources ? | RF-038, RF-251 | Conditions d'usage portées par le registre. |
| QO-023 | Comment traiter les sources multilingues ? | RF-093, RF-098 | Hors périmètre sans règle. |
| QO-024 | Quelle norme de citation et de références dans les livrables ? | RF-121 | Définie par le modèle. |
| QO-025 | Comment les utilisateurs sont-ils notifiés (uniquement dans l'échange, ou aussi hors échange) ? | RF-226 à RF-231 | Dans l'échange uniquement. |
| QO-027 | Visibilité entre utilisateurs ordinaires des demandes d'autrui ? | RT-016, §2.4 | **MVP : une demande n'est accessible qu'à son auteur et à la personne responsable (13.4).** Partage : reporté. |
| QO-028 | Politique d'archivage et de suppression des demandes annulées ? | RT-066 | Selon QO-012. |
| QO-030 | Comment représenter et versionner les exemples documentaires des modèles ? | RF-255, RF-256 | Rattachés au modèle versionné. |
| QO-032 | En révision, utilise-t-on par défaut les versions de règles d'origine ou les plus récentes ? | RF-195, RB-105 | **MVP : versions d'origine, sauf décision explicite et tracée de la personne responsable (13.4).** |
| QO-033 | Quelle durée maximale d'une suspension avant péremption ? | RB-087 | **MVP : aucune péremption automatique, sauf durée fixée par la personne responsable (13.4).** |
| QO-034 | Quelle granularité de dépendances entre éléments pour le blocage ciblé ? | RF-054, RB-077 | Dépendances déclarées dans le modèle. |
| QO-035 | Un mode « diagnostic seul » est-il souhaité dès le MVP ? | RF-030 | V2. |
| QO-036 | Souhaite-t-on, en V2, la diffusion exceptionnelle d'une version non finalisée ou non conforme (partage de travail en cours), et sous quelles conditions ? | RF-280 | Non ; hors périmètre tant que non arbitré. |

---
## Annexe A — Matrice de couverture du cahier

Cette matrice montre où chaque partie du cahier est traitée dans la spécification. Aucune partie du cahier n'est laissée sans exigence.

### A.1 Sections du cahier

| Cahier | Objet | Exigences et sections de la spécification |
|---|---|---|
| §1 | Mission et vision | Section 1 ; GP-01 à GP-08 ; RB-012 |
| §2 (1) | Comprendre le livrable et les contraintes | UC-001, UC-002 ; RF-001 à RF-018 |
| §2 (2) | Identifier modèle, règles, ressources, autorisations | UC-003 ; RF-019 à RF-030 |
| §2 (3) | Mobiliser les informations | UC-004 ; RF-031 à RF-044 |
| §2 (4) | Correspondance exigences / informations | UC-005 ; RF-045 à RF-058 |
| §2 (5) | Détecter manques, contradictions, incertitudes, violations | UC-006 à UC-008 ; RF-059 à RF-090 |
| §2 (6) | Organiser selon la structure et les critères | UC-009, UC-011 ; RF-091 à RF-104, RF-115 à RF-126 |
| §2 (7) | Transformations autorisées uniquement | RF-092, RF-104, RF-105 à RF-114 |
| §2 (8) | Contrôles de conformité et de cohérence | UC-012 ; RF-127 à RF-142 |
| §2 (9) | Livrable, rapport de conformité, traçabilité | UC-014 ; RF-155 à RF-172 |
| §2 (10) | Statut et actions restantes | UC-023 ; RF-164, RF-172, RF-225 à RF-238 |
| §3.1 | Aucune invention | RB-001, RB-002 ; RF-073 à RF-076, RF-123 ; RT-069, RT-074 |
| §3.2 | Séparation information / décision | RB-003 à RB-005 ; RF-084, RF-104, RF-239 à RF-244 |
| §3.3 | Primauté des règles explicites | RB-006 ; RF-255, RF-256 |
| §3.4 | Traçabilité | RB-007, RB-008 ; RF-102, RF-122 ; RT-027 à RT-042 |
| §3.5 | Respect des autorisations | RB-009 ; RF-038 ; RT-003, RT-004 |
| §3.6 | Pas d'apprentissage normatif implicite | RB-010, RB-011 ; RF-254, RF-259, RF-264 à RF-267 |
| §4 | Modèle de fonctionnement hybride | OB-04 à OB-08 ; RF-007 ; RF-254 à RF-259 |
| §5-É1 | Réception et compréhension | RF-001 à RF-018 |
| §5-É2 | Vérification de la faisabilité | RF-019 à RF-030 ; MB-01 à MB-17 |
| §5-É3 | Mobilisation des informations | RF-031 à RF-044 ; RF-245 à RF-253 |
| §5-É4 | Cartographie | RF-045 à RF-058 ; LC-01 à LC-05 |
| §5-É5 | Qualité des informations | RF-059 à RF-072 ; QI-01 à QI-07 |
| §5-É6 | Organisation et transformation | RF-091 à RF-104 ; TF-01 à TF-09 |
| §5-É7 | Lacunes et contradictions | RF-073 à RF-090 |
| §5-É8 | Production | RF-115 à RF-126 |
| §5-É9 | Contrôle qualité | RF-127 à RF-142 ; CT-01 à CT-16 |
| §5-É10 | Traitement des anomalies | RF-143 à RF-154 ; AN-1 à AN-3 |
| §5-É11 | Finalisation et remise | RF-155 à RF-184, RF-272 à RF-281 ; RB-109 à RB-116, RB-123 à RB-128 ; 9.6 ; Annexe D |
| §6.1 | Calculs et données dérivées | RF-105 à RF-114 ; RB-037 à RB-044 |
| §6.2 | Informations anciennes | RF-064 à RF-067 ; RB-020, RB-021 |
| §6.3 | Données personnelles et sensibles | RT-017 à RT-026 ; RB-060, RB-061 |
| §6.4 | Confidentialité et droits d'accès | RT-001 à RT-016 ; RB-057 à RB-066 |
| §6.5 | Demandes dépassant les règles | RF-239, RF-244 ; RB-005, RB-080 |
| §6.6 | Livrables multiples | RF-213 à RF-216, RF-223 ; RB-094, RB-095 |
| §6.7 | Demandes concurrentes | RF-219 à RF-222 ; RB-089 à RB-091 |
| §6.8 | Versions et historique | RF-185 à RF-198 ; RB-067 à RB-076 |
| §6.9 | Demandes suspendues | RF-205 à RF-209, RF-212 ; RB-081 à RB-083 |
| §6.10 | Informations communes à plusieurs demandes | RF-217, RF-218, RF-224 ; RB-092, RB-093 |
| §6.11 | Annulation et abandon | RF-199 à RF-204, RF-210, RF-211 ; RB-084 à RB-086 |
| §7 | Interaction avec l'utilisateur | RF-225 à RF-238 ; RB-117 à RB-122 |
| §8 | Utilisateurs et responsabilités | Section 2 ; RB-097 à RB-108 ; RF-239 à RF-271 |
| §9 | Formats et types de livrables | RF-003, RF-125, RF-126 ; QO-001, QO-002 |
| §10 | États fonctionnels | Section 8 ; RB-109 à RB-111 ; RF-236, RF-237 |
| §11 | Contenu de la spécification | Voir A.2 |
| §12 | Limites de la mission | Sections 0.2 et 1.8 ; section 13 |

### A.2 Les douze éléments demandés par le cahier (§11)

| # | Élément demandé | Où |
|---|---|---|
| 1 | Vision et périmètre fonctionnel | Section 1 |
| 2 | Profils d'utilisateurs et responsabilités | Section 2 |
| 3 | Cas d'usage principaux | Section 4.1 et 4.3 |
| 4 | Parcours fonctionnels détaillés | Section 5 |
| 5 | Entrées, sorties, préconditions et postconditions | Fiches de la section 4.3 |
| 6 | Règles métier explicites | Section 7 |
| 7 | États fonctionnels et transitions | Section 8 |
| 8 | Règles de blocage, de reprise, de révision et de finalisation | Section 9 |
| 9 | Critères d'acceptation vérifiables | Section 11 |
| 10 | Cas limites et scénarios d'erreur | Section 12 |
| 11 | Exigences de confidentialité, de traçabilité, de conformité et de contrôle qualité | Section 10 |
| 12 | MVP, évolutions ultérieures et points à arbitrer | Section 13 |

---

## Annexe B — Catalogue des contrôles (CT)

Le catalogue donne le **socle minimal**. Les contrôles effectivement **obligatoires** pour un type de livrable sont fixés par son modèle et ses règles (RT-053). CT-01 à CT-12 reprennent la liste du cahier (§5-É9) ; CT-13 à CT-16 sont des propositions.

| ID | Contrôle | Vérifie | Échec | Origine |
|---|---|---|---|---|
| CT-01 | Sections et champs obligatoires | Présence de chaque élément obligatoire du modèle | AN-1 ; MB-16 | [D] |
| CT-02 | Modèle et version | Le bon modèle, dans la version figée de la demande | AN-1 ; MB-16 | [D] |
| CT-03 | Conformité des informations intégrées | Statut QI, usage prévu, période de validité de chaque information intégrée comme fait | AN-1 ; MB-16 | [D] |
| CT-04 | Contradictions bloquantes | Aucune contradiction bloquante non résolue | AN-1 ; MB-03 | [D] |
| CT-05 | Sources et autorisations | Validité des sources et des quatre niveaux d'autorisation | AN-1 ; MB-06 à MB-09 | [D] |
| CT-06 | Transformations éditoriales | Chaque transformation est autorisée par une règle et tracée | AN-1 | [D] |
| CT-07 | Reproductibilité des calculs | Le rejeu de chaque calcul donne le même résultat | AN-1 ; MB-10 | [D] |
| CT-08 | Cohérence interne | Absence de contradiction à l'intérieur du document | AN-2 | [D] |
| CT-09 | Cohérence entre éléments | Cohérence entre les éléments du livrable | AN-2 | [D] |
| CT-10 | Références et traces | Présence des références et des traces exigées | AN-1 | [D] |
| CT-11 | Confidentialité et diffusion | Respect des restrictions pour les destinataires visés | AN-1 ; MB-09 | [D] |
| CT-12 | Cohérence méthodologique | Cohérence objectifs, questions, méthodes, variables, indicateurs, outils de collecte, résultats attendus, calendrier, lorsque des règles explicites la définissent | AN-2 ; décision humaine | [D] |
| CT-13 | Absence de contenu non rattaché | Tout contenu se rattache à une source, un modèle ou une règle | AN-1 | [P] |
| CT-14 | Conformité éditoriale et de présentation | Règles éditoriales et de présentation du type | AN-1 | [P] |
| CT-15 | Minimisation des données | Données personnelles et sensibles minimisées selon les règles | AN-1 | [P] |
| CT-16 | Cohérence entre livrables | Cohérence entre livrables d'une même opération | AN-2 | [P] (V2) |

**Règle de lecture.** Un contrôle sans règle explicite qui le définit est « non applicable » ; il ne peut pas être inventé par l'Agent (RB-055, RB-046).

---

## Annexe C — Catalogue des motifs de blocage (MB)

Les messages ci-dessous sont des **exemples génériques** : ils ne révèlent aucune information protégée et sont adaptés aux droits de l'interlocuteur (RB-065, RT-006).

| ID | Motif | Message type communicable | Cas d'usage |
|---|---|---|---|
| MB-01 | Absence de modèle ou de règle applicable | « Je n'ai pas de modèle ou de règle validés pour ce type de document. Je ne peux pas en improviser la structure. » | UC-003 |
| MB-02 | Information obligatoire absente | « Une information obligatoire est manquante et n'a pu être trouvée dans les sources autorisées. » | UC-007 |
| MB-03 | Contradiction irrésolue sur information indispensable | « Deux informations se contredisent et les règles ne permettent pas de trancher. Une décision est nécessaire. » | UC-008 |
| MB-04 | Information non vérifiée | « Une information requise n'a pas pu être vérifiée et ne peut pas être présentée comme établie. » | UC-006 |
| MB-05 | Information hors période de validité | « L'information disponible ne couvre pas la période visée. » | UC-006 |
| MB-06 | Source non accessible | « Une source nécessaire n'est pas disponible pour cette demande. » (sans nommer la source) | UC-004 |
| MB-07 | Contenu non utilisable | « Une information disponible ne peut pas être utilisée pour cet usage. » | UC-004 |
| MB-08 | Intégration non autorisée | « Une information ne peut pas être intégrée dans ce document. » | UC-011 |
| MB-09 | Diffusion non autorisée ou incertaine | « La diffusion à ces destinataires n'est pas autorisée ou n'est pas clarifiée. » | UC-016 |
| MB-10 | Calcul sans méthode définie | « Aucune méthode de calcul validée n'est définie pour cet élément. » | UC-010 |
| MB-11 | Décision non couverte par les règles | « Cette étape exige une décision qui n'est pas couverte par les règles. Elle est soumise à la personne habilitée. » | UC-024 |
| MB-12 | Correspondance source/cible incertaine | « Je ne sais pas avec certitude où placer cette information. Une précision est nécessaire. » | UC-005 |
| MB-13 | Droits incertains | « Les droits applicables ne sont pas clairs ; je suspends cette opération. » | UC-003 |
| MB-14 | Paramètre indispensable manquant | « Il me manque un paramètre indispensable : [paramètre]. » | UC-002 |
| MB-15 | Dépendance bloquée | « Cet élément dépend d'un autre qui est bloqué. » | UC-005 |
| MB-16 | Contrôle obligatoire échoué | « Un contrôle obligatoire n'a pas réussi : le document ne peut pas être déclaré conforme. » | UC-012 |
| MB-17 | Règle ou modèle devenu invalide à la reprise | « Une règle ou un modèle utilisé a changé depuis la suspension ; certains éléments doivent être réexaminés. » | UC-019 |

---

## Annexe D — Contenu minimal des rapports et dossiers

### D.1 Livrable

- Contenu conforme au modèle (sections, champs, tableaux, annexes exigés).
- Citations et références nécessaires à sa compréhension et à sa vérification.
- Qualification explicite de toute information non QI-01 (si les règles permettent de l'intégrer).
- Mention « provisoire » si la version n'est pas finalisée.

### D.2 Rapport de conformité

| Rubrique | Contenu | Réf. |
|---|---|---|
| Identification | Demande, livrable, version, type, versions de modèle, de règles, de registre et de catalogue de contrôles | RT-031, RT-046 |
| Statuts | **Conformité**, **approbation** et **diffusion**, présentés séparément | RF-161, RT-044 |
| Résultats des contrôles | Pour chaque contrôle : résultat, éléments examinés, règle, date | RF-142 |
| Réserves | Réserves non bloquantes, rattachées à des éléments | RB-056, RT-048 |
| Observations | Anomalies potentielles consignées | RF-151 |
| Informations qualifiées | Informations non QI-01 intégrées et leur qualification | RF-169 |
| Décisions humaines et exceptions | Arbitrages, autorisations ponctuelles, exceptions | RF-170, RT-049 |
| Éléments non exigés | Rapports ou contrôles non exigés par les règles, avec la règle concernée | RF-168 |
| Limites du contrôle | Ce qui n'est pas contrôlé faute de règle | RT-050 |
| Conditions restantes | Conditions à satisfaire avant approbation ou diffusion | RF-158 |
| Actions possibles | Approbation, diffusion, révision | RF-172 |

### D.3 Rapport de traçabilité

| Rubrique | Contenu | Réf. |
|---|---|---|
| Élément significatif | Identifiant et emplacement dans le livrable | RF-122 |
| Sources | Source, référence précise, date de consultation, période de référence | RF-039 |
| Statut de validation | Statut QI, critères appliqués, vérifications | RF-070 |
| Transformations | Type (TF), règle autorisante, avant, après | RF-102 |
| Calculs | Entrées, sources, méthode, unités, conventions, arrondi, résultat | RF-106 à RF-110 |
| Règles appliquées | Règles et leurs versions | RT-031 |
| Autorisations | Niveaux d'autorisation pertinents, permanents ou ponctuels, exceptions | RT-032 |
| Décisions humaines | Décideur, date, objet, motif | RT-033 |
| Exclusions et masquages | Existence et motif général (sans contenu protégé) | RT-040 |
| Informations non retenues | Candidates rejetées et motif | RT-041 |
| Historique de production | États, contrôles, corrections, versions | RT-035, RT-036 |

Le rapport de traçabilité est lui-même soumis aux règles de confidentialité (RB-063).

### D.4 Dossier d'arbitrage ou de décision

- Objet de la décision (contradiction, point non couvert, exception, source, priorité).
- Contexte et éléments impactés.
- Informations ou options en présence, avec sources, portée, période.
- Règles examinées et raison pour laquelle elles ne tranchent pas.
- Conséquences de chaque option sur le livrable.
- Urgence et échéance.
- **L'Agent ne formule aucune recommandation qui sorte des règles ; il expose ce qu'elles permettent.** [P]

### D.5 Dossier d'approbation

Version concernée ; rapport de conformité ; réserves ; observations ; décisions et exceptions antérieures ; différences avec la version précédente (V2) ; actions possibles après décision.

### D.6 Message d'état

Étapes terminées ; étapes en cours ; motifs communicables des blocages ; éléments attendus (et de qui) ; prochaine action ; état de la demande ; statuts de conformité, d'approbation et de diffusion **séparés**.

---

## Annexe E — Registre des propositions à valider (PV)

Chaque proposition marquée [P] dans ce document est regroupée ici lorsque sa validation conditionne une partie importante de la spécification. Tant qu'une proposition n'est pas validée, elle n'engage pas le produit.

| ID | Proposition | Réf. | Si refusée | Décideur |
|---|---|---|---|---|
| PV-01 | « Personne habilitée » et « personne responsable » désignent la même personne. | IN-01, RB-100 | Définir un second rôle d'habilitation. | Personne responsable |
| PV-02 | Six axes d'états indépendants et un état « Finalisée » pour la demande. | Section 8 | Revoir la grille d'états. | Personne responsable |
| PV-03 | Statuts de conformité « Non évalué » et « Non conforme ». | ST-C-01, ST-C-03 | Simplifier à « conforme » / « non conforme ». | Personne responsable |
| PV-04 | Statut d'approbation « Non requise » selon les règles du type. | ST-A-02 | Approbation systématique. | Personne responsable |
| PV-05 | Approbation et diffusion sont deux décisions distinctes, sans effet sur la conformité. Au MVP, une version non finalisée ou non conforme ne peut être ni approuvée ni diffusée ; la diffusion exige en outre une approbation « Approuvée » ou « Non requise » (9.6). | RB-113, RB-114, RB-123, RB-124, RF-272 à RF-277 | Préciser séparément, pour l'approbation et pour la diffusion, la variante autorisée (9.6). | Personne responsable |
| PV-06 | Version provisoire pour les éléments produits quand d'autres sont bloqués. | RF-119, RF-120 | Aucune production tant qu'un élément obligatoire est bloqué. | Personne responsable |
| PV-07 | Statuts de lignes de cartographie LC-01 à LC-05. | 3.3.2 | Utiliser seulement produisible / à clarifier / bloqué. | Personne responsable |
| PV-08 | Contrôles obligatoires et informatifs ; résultat « non exécutable » distinct de « réussi ». | 3.3.6, RB-054 | Binaire réussi/échoué. | Personne responsable |
| PV-09 | Qualité d'une donnée dérivée limitée par celle de ses entrées. | RF-113 | Qualité propre au calcul. | Personne responsable |
| PV-10 | Qualification explicite dans le livrable des informations non QI-01 intégrées. | RF-069 | Exclusion totale des informations non QI-01. | Personne responsable |
| PV-11 | Dossier d'arbitrage structuré par l'Agent. | RF-088, RF-240 | Sollicitation libre. | Personne responsable |
| PV-12 | Borne du nombre de cycles de correction avec escalade. | RF-153 | Cycles non bornés. | Personne responsable |
| PV-13 | Annulation définitive : action explicite et confirmée de l'auteur ou de la personne responsable, irréversible, réservée aux demandes non finalisées. | RF-210, RF-211, RB-085 | Redéfinir les modalités (QO-011). | Personne responsable |
| PV-14 | Une révision crée une nouvelle demande liée. | TR-R-22 | Réouverture de la demande finalisée. | Personne responsable |
| PV-15 | Statuts remis à zéro à chaque nouvelle version. | RF-196, RB-116 | Héritage partiel des statuts. | Personne responsable |
| PV-16 | Autorisation ponctuelle : périmètre, niveaux, durée, expiration. | RF-246, RF-249 | Autorisation sans expiration. | Personne responsable |
| PV-17 | Propositions de règles par les utilisateurs. | RF-266 | Aucune proposition possible. | Personne responsable |
| PV-18 | Signalement informatif d'impact entre productions. | RF-224 | Aucun signalement par l'Agent. | Personne responsable |
| PV-19 | Classification d'un livrable héritée de la plus restrictive de ses informations. | RT-010 | Classification explicite à chaque livrable. | Personne responsable |
| PV-20 | Rapport de traçabilité éventuellement plus restrictif que le livrable. | RT-011 | Même classification. | Personne responsable |
| PV-21 | Journal des interrogations de sources, infructueuses comprises. | RF-044 | Seules les consultations fructueuses tracées. | Personne responsable |
| PV-22 | Mode « diagnostic seul ». | RF-030 | Faisabilité toujours suivie de production. | Personne responsable |
| PV-23 | Cadrage du MVP : un type pilote, formats limités. | 13.2 | Élargir le MVP. | Personne responsable |
| PV-24 | Indicateurs de réussite fonctionnelle. | 1.7 | Définir d'autres indicateurs. | Personne responsable |
| PV-25 | Profil « destinataire » comme acteur de droits (MVP) ; profil « auditeur » dédié reporté en V2, la consultation de traçabilité relevant au MVP d'un droit d'accès. | PU-03, PU-05, UC-030 | Retirer ces profils ou avancer l'auditeur au MVP. | Personne responsable |
| PV-26 | Informations fournies par un utilisateur confidentielles par défaut. | RT-015 | Réutilisables selon règle. | Personne responsable |
| PV-27 | Diffusion = accessibilité dans le produit ; l'Agent ne transmet rien hors du produit ; la révocation ne couvre pas les copies déjà obtenues. | RF-278, RF-279, RB-128 | Définir la transmission par l'Agent (QO-010). | Personne responsable |
| PV-28 | Au MVP, la personne responsable est seule approbatrice. | RF-174 | Désigner d'autres approbateurs (QO-009). | Personne responsable |
| PV-29 | Au MVP, aucune suppression ni péremption automatique tant que la personne responsable n'a pas fixé de durée. | RB-087, RT-061 | Fixer des durées par défaut (QO-012). | Personne responsable |
| PV-30 | Information fournie par l'utilisateur : statut initial QI-02. | RF-017, RF-043, RB-026 | Statut initial défini par règle (QO-031). | Personne responsable |
| PV-31 | Une demande vise un livrable ; scission sur confirmation. | RF-008, IN-04 | Avancer la coordination de livrables multiples au MVP. | Personne responsable |
| PV-32 | Aucune suppléance de la personne responsable au MVP. | RB-108, RP-05 | Définir une suppléance (QO-008). | Personne responsable |
| PV-33 | État de version « Abandonnée » pour les versions provisoires d'une demande annulée. | ST-V-04, RF-211 | Conserver ces versions comme « Provisoires ». | Personne responsable |
| PV-34 | Approbation et refus définitifs pour leur version, non révocables. | RF-274, RB-125 | Prévoir la révocation d'une approbation. | Personne responsable |
| PV-35 | Règles MVP par défaut : donnée personnelle non reprise sans règle ; définition d'« élément significatif » ; français ; demande visible de son auteur et de la personne responsable ; versions d'origine en révision. | RT-016, RT-019, RT-028, RB-121, RF-195 | Fixer d'autres valeurs par défaut (QO-013, QO-014, QO-018, QO-027, QO-032). | Personne responsable |

---

## Annexe F — Matrice cas d'usage × exigences

| UC | Exigences fonctionnelles | Règles métier | Exigences transverses | Critères d'acceptation | Priorité |
|---|---|---|---|---|---|
| UC-001 | RF-001 à RF-010 | RB-118, RB-119 | — | CA-001 à CA-004, CA-189 | MVP |
| UC-002 | RF-011 à RF-018 | RB-118, RB-119 | — | CA-005 à CA-010, CA-190 | MVP |
| UC-003 | RF-019 à RF-030 | RB-013, RB-057, RB-058, RB-077, RB-078 | — | CA-011 à CA-020 | MVP |
| UC-004 | RF-031 à RF-044 | RB-013 à RB-016 | RT-003, RT-004 | CA-021 à CA-030 | MVP |
| UC-005 | RF-045 à RF-058 | RB-023 à RB-025 | — | CA-031 à CA-040 | MVP |
| UC-006 | RF-059 à RF-072 | RB-016 à RB-022 | — | CA-041 à CA-044 | MVP |
| UC-007 | RF-073 à RF-080 | RB-001, RB-002, RB-027 à RB-029 | — | CA-045 à CA-047 | MVP |
| UC-008 | RF-081 à RF-090 | RB-030 à RB-036 | — | CA-048 à CA-052 | MVP |
| UC-009 | RF-091 à RF-104 | RB-023 à RB-025, RB-043 | RT-030 | CA-053 à CA-058 | MVP |
| UC-010 | RF-105 à RF-114 | RB-037 à RB-044 | RT-029 | CA-059 à CA-062 | MVP |
| UC-011 | RF-115 à RF-126 | RB-075 | — | CA-063 à CA-070 | MVP |
| UC-012 | RF-127 à RF-142 | RB-045 à RB-047, RB-053 à RB-055, RB-112 | RT-053 à RT-060 | CA-071 à CA-076 | MVP |
| UC-013 | RF-143 à RF-154 | RB-048 à RB-052, RB-056 | — | CA-077 à CA-084 | MVP |
| UC-014 | RF-155 à RF-172 | RB-109 à RB-112, RB-117 | RT-043 à RT-052 | CA-085 à CA-094 | MVP |
| UC-015 | RF-173 à RF-178, RF-272 à RF-274 | RB-109 à RB-113, RB-123 à RB-126 | — | CA-095 à CA-099, CA-177 à CA-179 | MVP |
| UC-016 | RF-179 à RF-184, RF-275 à RF-279 (RF-280 en V2) | RB-057, RB-058, RB-114, RB-115, RB-126, RB-128 | — | CA-100 à CA-104, CA-180 à CA-186 (CA-195 en V2) | MVP |
| UC-017 | RF-185 à RF-198 | RB-067 à RB-076 | — | CA-105 à CA-114, CA-191 | MVP |
| UC-018 | RF-199 à RF-205 | RB-081, RB-083, RB-084, RB-086 | — | CA-115 à CA-120 | MVP |
| UC-019 | RF-206 à RF-209 | RB-082, RB-087, RB-088 | RT-009 | CA-121 à CA-124, CA-193 | MVP |
| UC-020 | RF-210 à RF-212 | RB-085, RB-088 | — | CA-125, CA-126, CA-187, CA-188 | MVP |
| UC-021 | RF-213 à RF-218 | RB-094, RB-095 | — | CA-127 à CA-130 | V2 |
| UC-022 | RF-219 à RF-224 | RB-089 à RB-091, RB-096 | — | CA-131 à CA-134 | V2 |
| UC-023 | RF-225 à RF-238 | RB-064, RB-065, RB-117, RB-120, RB-122 | RT-006 | CA-135 à CA-144 | MVP |
| UC-024 | RF-239 à RF-244 | RB-003 à RB-005, RB-033, RB-097, RB-098, RB-106 à RB-108 | — | CA-145 à CA-147, CA-192 | MVP |
| UC-025 | RF-245 à RF-249 | RB-013, RB-014 | — | CA-148, CA-149 | MVP |
| UC-026 | RF-250 à RF-253 | — | — | CA-150, CA-151 | MVP (minimal) |
| UC-027 | RF-254 à RF-259 | RB-006, RB-010, RB-011, RB-103 à RB-105 | — | CA-152, CA-153 | MVP |
| UC-028 | RF-260 à RF-263, RF-281 | RB-101, RB-127 | — | CA-154, CA-194 | V2 |
| UC-029 | RF-264 à RF-267 | RB-010, RB-102 | — | CA-155, CA-156 | V2 |
| UC-030 | RF-268 à RF-271 | — | RT-027 à RT-042, RT-061 à RT-068 | CA-169 à CA-176 | MVP |
| UC-031 | — | RB-060, RB-061, RB-066 | RT-017 à RT-026 | CA-157 à CA-168 | MVP |

---

## Prochaines étapes suggérées

1. **Valider les règles MVP de 13.4**, en particulier PV-05 (approbation et diffusion), PV-13 (annulation) et PV-27 à PV-35. Elles referment, pour le MVP, les dépendances à QO-008 à QO-014, QO-018, QO-026 et QO-031 à QO-033.
2. **Fournir les décisions de cadrage et contenus de 13.5**, en commençant par QO-001 (type pilote), QO-003 (contrat avec INIS), QO-005 (règles de priorité entre sources) et QO-029 (critères de vérification).
3. **Valider ou rejeter les autres propositions** de l'Annexe E, en particulier PV-02 (axes d'états) et PV-25 (profils).
4. **Rédiger, pour le type pilote**, son modèle documentaire, ses règles éditoriales, son registre de sources et son catalogue de contrôles obligatoires. La spécification définit comment l'Agent se comporte face à ces éléments, pas leur contenu.
5. **Dériver le plan de tests d'acceptation** à partir des CA de la section 11.
6. **Seulement ensuite**, ouvrir la conception technique, sans qu'elle remette en cause les garanties GP-01 à GP-08.

## Historique du document

| Version | Date | Nature |
|---|---|---|
| 0.1 | 20 octobre 2026 | Première version structurée à partir du cahier de cadrage fonctionnel. Aucune architecture technique. |
| 0.2 | 20 octobre 2026 | Corrections après revue (voir ci-dessous). |

### Journal des modifications de la version 0.2

1. **États fonctionnels.** Le texte annonce désormais six axes, comme le tableau et PV-02. Transitions complétées : retour à l'état d'origine après une attente ou un blocage (TR-R-23 à TR-R-27), TR-C-05, TR-D-04, tableaux de transitions des axes V et E (TR-V-01 à TR-V-03, TR-E-01 à TR-E-11), état ST-V-04, invariants IV-11 à IV-15, nouvelle section 8.9 (couverture de la liste d'états du cahier, prérequis entre axes, atteignabilité).
2. **Profil d'auditeur.** PU-05 reste une évolution V2. Au MVP, la consultation de la traçabilité et de l'historique (UC-030) est un droit d'accès de l'auteur de la demande et de la personne responsable ; elle ne requiert aucun profil dédié (sections 2.1, 2.4, UC-030, CA-176).
3. **Règles MVP et questions ouvertes.** Règles MVP testables pour QO-008 à QO-014, QO-018, QO-026 et QO-031 à QO-033 (13.4) ; passage de plusieurs exigences de [Q] à [P] et de ARB à MVP (RF-008, RF-017, RF-043, RF-174, RF-184, RF-195, RF-210, RF-211, RB-026, RB-087, RB-108, RB-121, RT-016, RT-019, RT-028, RT-061) ; décisions de cadrage séparées des comportements (13.5) ; nouvelle question reportable QO-036.
4. **Approbation et diffusion.** Traitées séparément en 9.6, avec pour chacune : possible ou non selon l'état de la version, conditions, effet sur la conformité (aucun). RB-113 et RB-114 réécrites ; PV-05 reformulée ; RF-272 à RF-281, RB-123 à RB-128, CA-177 à CA-195 et CL-061 à CL-064 ajoutés.
