# Jalon MS-4 — Cartographie, lacunes, contradictions, décisions

> Brief généré par `tools/gen_briefs.py` — ne pas modifier à la main. Pour tout détail : `python tools/spec.py show <ID>`.

## 1. Objectif

Lignes de cartographie et leur statut, propagation des blocages, lacunes, contradictions et règles de priorité, dossiers d'arbitrage, boîte de décisions.

**À savoir.** La personne responsable est unique et sans suppléance (RB-108).

## 2. Périmètre

- Cas d'usage : UC-005, UC-007, UC-008, UC-024
- Suites de tests visées : TST-04, TST-05, TST-15 (arbitrage)
- Hors périmètre de ce jalon : Transformations, calculs, rendu, approbation, diffusion.

## 3. Exigences techniques à réaliser (19)

- **ET-117** ([F] · MVP) — `compute_line_status` est une fonction pure testée par tables de cas.  
  _Réalise : RF-055, LC-01 à LC-05 · MOD-08_
- **ET-118** ([F] · MVP) — La cartographie est versionnée ; les versions antérieures sont conservées.  
  _Réalise : RF-057 · MOD-08_
- **ET-119** ([T] · MVP) — La recherche de candidats est hybride (champ exact, plein texte, vecteurs).  
  _Réalise : EM-03 · MOD-08_
- **ET-120** ([F] · MVP) — Le code valide les sorties de LT-04 : types, unités, autorisations, période.  
  _Réalise : PT-01 · MOD-08_
- **ET-121** ([F] · MVP) — Le graphe de dépendances du modèle est vérifié acyclique à la validation du modèle.  
  _Réalise : RF-054 · MOD-02_
- **ET-122** ([F] · MVP) — L'algorithme A3 propage les blocages avec leur cause (`caused_by`) et les lève en cascade.  
  _Réalise : RB-077 · MOD-08_
- **ET-123** ([F] · MVP) — Les lacunes sont détectées depuis les lignes ; la relance de mobilisation sur les autres sources est automatique.  
  _Réalise : RF-073, RF-074 · MOD-09_
- **ET-124** ([F] · MVP) — Aucune valeur n'est insérée sans preuve ; un test d'invariant échoue si un atome n'est pas lié (CT-13).  
  _Réalise : RF-075, RF-123 · MOD-11_
- **ET-125** ([F] · MVP) — La détection de contradictions utilise des comparateurs typés (nombre, unité, date, catégorie, texte).  
  _Réalise : RF-081 · MOD-09_
- **ET-126** ([F] · MVP) — LT-06 propose des paires suspectes ; le code ne retient que celles dont les extraits sont vérifiés.  
  _Réalise : RF-081 · MOD-09_
- **ET-127** ([F] · MVP) — Les règles de priorité (CEL) sont évaluées dans l'ordre déclaré ; la première règle décisive tranche ; aucune règle = non résolu.  
  _Réalise : RF-082, RF-084 · MOD-09_
- **ET-128** ([F] · MVP) — Une divergence expliquée par une portée ou une période reconnue par les règles est documentée comme telle.  
  _Réalise : RF-090 · MOD-09_
- **ET-129** ([F] · MVP) — Le dossier d'arbitrage est assemblé par du code à partir de faits ; LT-11 est optionnelle et étiquetée.  
  _Réalise : RF-088, RF-240 · MOD-09, MOD-15_
- **ET-130** ([F] · MVP) — Un test garantit que la récence n'est jamais un critère implicite de priorité.  
  _Réalise : RF-066, RB-022 · MOD-09_
- **ET-201** ([F] · MVP) — La commande `RecordDecision` vérifie l'identité du décideur ; une décision réservée n'est valable que si elle émane de la personne responsable.  
  _Réalise : RF-241, RB-098 · MOD-15_
- **ET-202** ([F] · MVP) — La boîte de décisions liste les `DecisionRequested` non traitées, avec dossier, échéance et demande concernée.  
  _Réalise : RF-240 · MOD-15_
- **ET-203** ([F] · MVP) — Le dossier de décision est assemblé par du code ; LT-11 est facultative, étiquetée comme aide et vérifiée contre les faits.  
  _Réalise : RF-088, RF-240 · MOD-15_
- **ET-204** ([F] · MVP) — La portée d'une décision est limitée à son objet et à sa demande ; une décision ne modifie jamais un artefact de gouvernance.  
  _Réalise : RF-243 · MOD-15_
- **ET-212** ([F] · MVP) — Les autorisations ponctuelles sont créées par la personne responsable avec source, demande, niveaux et durée.  
  _Réalise : RF-245, RF-246 · MOD-15_

## 4. Critères d'acceptation à rendre verts (22)

Écrire d'abord un test par critère, étiqueté de son identifiant (`@pytest.mark.ca("CA-xxx")`).

- **CA-031** (RF-045) — **Étant donné** une demande en production, **quand** l'Agent n'a pas établi la cartographie, **alors** aucune rédaction ne commence.
- **CA-032** (RF-046) — **Étant donné** un modèle de N éléments exigés, **quand** la cartographie est établie, **alors** chacun a une ligne.
- **CA-033** (RF-047 à RF-054) — **Étant donné** une ligne de cartographie, **quand** on la consulte, **alors** elle contient exigence, information nécessaire, information disponible, source et référence, statut de validation, transformations, manques, contradictions, incertitudes et dépendances.
- **CA-034** (RF-055) — **Étant donné** une cartographie terminée, **quand** l'Agent la synthétise, **alors** il indique ce qui peut être produit, ce qui doit être clarifié et ce qui reste bloqué.
- **CA-035** (RF-056, RB-023) — **Étant donné** une correspondance source/cible incertaine, **quand** l'Agent établit la ligne, **alors** elle est À clarifier et non résolue arbitrairement.
- **CA-036** (RF-057) — **Étant donné** une information nouvelle, **quand** elle affecte la cartographie, **alors** celle-ci est mise à jour et les versions antérieures sont conservées.
- **CA-037** (RF-058, RT-007) — **Étant donné** un utilisateur sans droit sur une source, **quand** il consulte la cartographie, **alors** la source est mentionnée de façon générique.
- **CA-038** (RF-078) — **Étant donné** une lacune, **quand** l'Agent la consigne, **alors** les éléments qui en dépendent sont identifiés.
- **CA-039** (RF-053) — **Étant donné** une contradiction, **quand** la ligne est renseignée, **alors** la contradiction y est signalée.
- **CA-040** (RF-054, RB-077) — **Étant donné** un élément bloqué, **quand** l'Agent évalue les dépendances, **alors** seuls les éléments dépendants sont bloqués.
- **CA-045** (RF-073 à RF-076) — **Étant donné** une information obligatoire manquante sans source alternative, **quand** l'Agent produit, **alors** les éléments dépendants sont bloqués et aucune valeur n'est inventée.
- **CA-046** (RF-074) — **Étant donné** une information manquante trouvée dans une source alternative autorisée, **quand** elle est QI-01, **alors** elle est intégrée avec sa provenance.
- **CA-047** (RF-077, RB-029) — **Étant donné** une information facultative manquante, **quand** l'Agent produit, **alors** il applique la règle du modèle et signale l'omission.
- **CA-048** (RF-081 à RF-083) — **Étant donné** deux sources divergentes, **quand** une règle de priorité s'applique, **alors** l'Agent l'applique en tenant compte du contexte, de la provenance, de la portée et de la période, et trace le résultat.
- **CA-049** (RF-084 à RF-086) — **Étant donné** une contradiction qu'aucune règle ne tranche, **quand** l'information est indispensable, **alors** les éléments dépendants sont bloqués et l'Agent ne choisit pas.
- **CA-050** (RF-087) — **Étant donné** une contradiction irrésolue, **quand** des éléments en sont indépendants, **alors** leur production se poursuit.
- **CA-051** (RF-088, RF-089) — **Étant donné** une contradiction irrésolue, **quand** la personne responsable arbitre, **alors** un dossier d'arbitrage lui a été remis et la décision est enregistrée, limitée à la demande.
- **CA-052** (RF-090, RB-035) — **Étant donné** une divergence expliquée par des portées différentes reconnues par les règles, **quand** l'Agent l'analyse, **alors** elle est documentée comme telle.
- **CA-145** (RF-239, RB-005) — **Étant donné** une décision substantielle non couverte, **quand** l'Agent y est confronté, **alors** il suspend l'opération concernée et ne décide pas.
- **CA-146** (RF-240, RF-244) — **Étant donné** une décision requise, **quand** l'Agent sollicite la personne responsable, **alors** la demande contient question, contexte, options issues des règles, conséquences et urgence, et les opérations indépendantes continuent.
- **CA-147** (RF-241 à RF-243) — **Étant donné** une décision réservée, **quand** elle est prise par une personne autre que la personne responsable, **alors** elle n'est pas valable ; quand elle est valable, **alors** elle est tracée et sa portée est limitée à l'objet et à la demande.
- **CA-192** (RB-108, RF-244) — **Étant donné** l'indisponibilité de la personne responsable, **quand** une décision réservée est requise, **alors** aucun autre acteur ne la prend, les éléments restent en attente et les opérations indépendantes continuent.

## 5. Exigences fonctionnelles liées (49) — une ligne chacune

Résumés seulement. Pour le texte complet et le contexte : `python tools/spec.py show RF-xxx`.

- RB-005 — Lorsqu'une décision non autorisée est nécessaire, l'Agent suspend l'opération concernée et sollicite la personne habilitée.
- RB-022 — L'information la plus récente n'est pas systématiquement prioritaire.
- RB-023 — Une correspondance incertaine entre une information source et un champ cible est signalée, non résolue arbitrairement.
- RB-029 — Une lacune facultative est traitée selon la règle prévue au modèle.
- RB-035 — Une divergence entièrement expliquée par des portées ou périodes différentes n'est pas une contradiction, lorsque les règles le reconnaissent.
- RB-077 — Un blocage est local à l'élément ou à l'opération concernés, sauf dépendance ; les opérations indépendantes se poursuivent.
- RB-098 — Elle seule arbitre les décisions sensibles, résout les conflits que les règles ne résolvent pas, autorise les exceptions, approuve les changements de règles et prend l...
- RB-108 — Si la personne responsable est indisponible, aucune décision réservée n'est prise par un autre ; les éléments concernés restent en attente (aucune suppléance au MVP).
- RF-045 — Avant toute rédaction, l'Agent doit établir une correspondance structurée entre les exigences du livrable et les informations disponibles.
- RF-046 — La cartographie doit couvrir chaque section, champ, tableau ou élément significatif exigé.
- RF-047 — Pour chaque ligne, l'Agent doit préciser l'exigence à satisfaire.
- RF-048 — Pour chaque ligne, l'Agent doit préciser l'information nécessaire.
- RF-049 — Pour chaque ligne, l'Agent doit préciser l'information effectivement disponible.
- RF-050 — Pour chaque ligne, l'Agent doit préciser la source et la référence correspondantes.
- RF-051 — Pour chaque ligne, l'Agent doit préciser le statut de validation.
- RF-052 — Pour chaque ligne, l'Agent doit préciser les transformations éventuellement nécessaires.
- RF-053 — Pour chaque ligne, l'Agent doit préciser les informations manquantes, les contradictions et les incertitudes.
- RF-054 — Pour chaque ligne, l'Agent doit préciser les dépendances susceptibles de bloquer l'élément.
- RF-055 — À l'issue de la cartographie, l'Agent doit déterminer et présenter ce qui peut être produit, ce qui doit être clarifié et ce qui reste bloqué.
- RF-056 — Une correspondance incertaine entre une information source et un champ cible doit être signalée et non résolue arbitrairement.
- RF-057 — La cartographie doit être mise à jour à chaque changement qui l'affecte (nouvelle information, résolution, décision) et conserver ses versions successives.
- RF-058 — La cartographie doit être consultable, selon les droits, par l'utilisateur et par la personne responsable, et faire partie des éléments de traçabilité.
- RF-066 — L'Agent ne doit pas privilégier systématiquement l'information la plus récente.
- RF-073 — L'Agent doit détecter et consigner toute information manquante pour une exigence du livrable.
- RF-074 — Pour toute information manquante, l'Agent doit rechercher une source alternative lorsque cette recherche est autorisée.
- RF-075 — L'Agent ne doit pas combler une lacune par une déduction, une estimation, une valeur par défaut ou un contenu plausible qui ne provient pas d'une source ou d'une règle.
- RF-076 — Si une information obligatoire demeure indisponible, les éléments qui en dépendent restent bloqués.
- RF-077 — Si l'information manquante est facultative, l'Agent applique la règle du modèle (omission signalée ou mention d'indisponibilité).
- RF-078 — L'Agent doit identifier les éléments dépendant de l'information manquante.
- RF-081 — L'Agent doit détecter les contradictions entre informations destinées au même élément.
- RF-082 — L'Agent doit appliquer les règles de priorité explicites pour résoudre une contradiction.
- RF-083 — L'Agent doit tenir compte du contexte, de la provenance, de la portée et de la période de référence des informations.
- RF-084 — L'Agent ne doit pas résoudre librement une contradiction non couverte par les règles.
- RF-085 — Si la contradiction demeure irrésolue, l'Agent doit identifier les éléments qui en dépendent.
- RF-086 — Si l'information est indispensable, les éléments dépendants restent bloqués jusqu'à résolution.
- RF-087 — Les opérations indépendantes de la contradiction peuvent se poursuivre si les règles le permettent.
- RF-088 — L'Agent doit préparer pour la personne responsable un dossier d'arbitrage : informations en conflit, sources, contexte, portée, période, règles examinées, éléments imp...
- RF-089 — La résolution par la personne responsable doit être enregistrée comme décision tracée, avec date, motif et périmètre (la demande concernée uniquement).
- RF-090 — Lorsqu'une divergence s'explique par une différence de portée ou de période reconnue par les règles, l'Agent doit la documenter comme telle plutôt que la traiter comme...
- RF-123 — L'Agent ne doit inclure aucun contenu qui ne se rattache ni à une information source, ni à un modèle, ni à une règle.
- RF-239 — Lorsqu'une décision substantielle non couverte par les règles est nécessaire, l'Agent doit suspendre l'opération concernée et solliciter la personne habilitée.
- RF-240 — L'Agent doit formuler la demande de décision de façon autonome et exploitable : question, contexte, options issues des règles, conséquences sur le livrable, urgence.
- RF-241 — Une décision réservée n'est valable que si elle est prise par la personne responsable ; l'Agent doit en vérifier l'identité.
- RF-242 — Chaque décision doit être enregistrée : décideur, date, objet, périmètre, motif, éléments impactés.
- RF-243 — La portée d'une décision est limitée à son objet et à sa demande, sauf passage par la procédure de changement de règle.
- RF-244 — Pendant l'attente d'une décision, l'Agent poursuit les tâches de diagnostic, de vérification ou indépendantes qui restent autorisées.
- RF-245 — La personne responsable peut autoriser ponctuellement une source absente du registre permanent.
- RF-246 — Une autorisation ponctuelle doit préciser la source, la demande concernée, les niveaux accordés (accès, utilisation, intégration, diffusion) et la durée.
- RT-007 — Les explications de refus restent générales lorsque le détail révélerait l'existence, l'identité ou le contenu d'une source protégée.

## 6. À lire à la demande (ne rien lire d'autre au départ)

| Quoi | Commande | Pourquoi |
|---|---|---|
| Spéc. technique 10.5 | `python tools/spec.py section T 10.5` | É4 Cartographie (compute_line_status, A3) |
| Spéc. technique 10.8 | `python tools/spec.py section T 10.8` | É7 Lacunes et contradictions (A4) |
| Spéc. technique 11.4 | `python tools/spec.py section T 11.4` | Tâches LT-04, LT-06, LT-11 |
| Spéc. fonctionnelle UC-005 | `python tools/spec.py section F UC-005` | Fiche du cas d’usage |
| Spéc. fonctionnelle UC-007 | `python tools/spec.py section F UC-007` | Fiche du cas d’usage |
| Spéc. fonctionnelle UC-008 | `python tools/spec.py section F UC-008` | Fiche du cas d’usage |
| Spéc. fonctionnelle UC-024 | `python tools/spec.py section F UC-024` | Fiche du cas d’usage |
| Spéc. fonctionnelle 9.1 | `python tools/spec.py section F 9.1` | Règles de blocage |
| Spéc. fonctionnelle Annexe-C | `python tools/spec.py section F Annexe-C` | Motifs MB |

## 7. Critères de sortie du jalon

TST-04, TST-05 et TST-15 (arbitrage) verts ; EVL-B et EVL-C au seuil ; la récence n'est jamais un critère implicite.

## 8. Rappels (extraits d'AGENTS.md)

- Tests d'acceptation d'abord ; `make check` doit passer ; ne jamais affaiblir un test, une contrainte ou un déclencheur.
- Ambiguïté de spécification → question dans `docs/reports/QUESTIONS.md`, jamais d'invention.
- À la fin d'une tranche : mettre à jour `docs/reports/PROGRESS.md`.

