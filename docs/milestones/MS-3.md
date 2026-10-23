# Jalon MS-3 — Sources et preuves

> Brief généré par `tools/gen_briefs.py` — ne pas modifier à la main. Pour tout détail : `python tools/spec.py show <ID>`.

## 1. Objectif

Port de sources, simulateur INIS, téléversement, ingestion, texte canonique, vérification des citations (algorithme A5), extraction LT-03, évaluation de la qualité (QI), autorisations ponctuelles minimales.

**À savoir.** `make test-llm-replay` doit écrire `docs/reports/eval-report.md` (suites EVL, mesures, seuils, verdict ; point PO-09 de la checklist). Pour CA-148/149, implémenter dès ce jalon le strict minimum de l'autorisation ponctuelle (ET-212 : création, périmètre, expiration) ; la boîte de décisions complète arrive en MS-4.

## 2. Périmètre

- Cas d'usage : UC-004, UC-006, UC-025
- Suites de tests visées : TST-03, TST-05 (partie qualité)
- Hors périmètre de ce jalon : Cartographie, calculs, rendu.

## 3. Exigences techniques à réaliser (26)

- **ET-091** ([T] · MVP) — Le port `SourcePort` et ses types sont définis comme en 15.1.  
  _Réalise : RF-031 à RF-044 · ADR-014_
- **ET-092** ([T] · MVP) — Un adaptateur INIS **simulé** reproduit des scénarios figés (manquant, contradictoire, ancien, indisponible).  
  _Réalise : RF-042, RF-074 · ADR-014_
- **ET-093** ([T] · MVP) — L'adaptateur INIS réel implémente le même port ; des tests de contrat le valident.  
  _Réalise : RF-032 · ADR-014_
- **ET-094** ([T] · MVP) — Les adaptateurs « téléversement utilisateur » et « corpus documentaire du registre » sont disponibles.  
  _Réalise : RF-043 · MOD-06_
- **ET-095** ([F] · MVP) — Toute entrée d'adaptateur est normalisée en `InformationCandidate`, puis en `information_items` de statut initial candidat.  
  _Réalise : RF-039, RB-016 · MOD-06_
- **ET-096** ([F] · MVP) — Les erreurs sont typées : `Unavailable` ne vaut jamais « absence » ; `NoResult` est distinct.  
  _Réalise : RF-042 · MOD-06_
- **ET-097** ([T] · MVP) — Délais d'attente, reprises avec attente croissante et coupe-circuit existent par source.  
  _Réalise : RF-042 · MOD-06_
- **ET-098** ([F] · MVP) — Chaque interrogation, y compris infructueuse, est enregistrée dans `source_queries`.  
  _Réalise : RF-044 · MOD-06_
- **ET-099** ([F] · MVP) — Le plan de recherche est généré de façon déterministe depuis le modèle et l'ordre du registre ; aucune méthode n'est inventée.  
  _Réalise : RF-041, RB-004 · MOD-06_
- **ET-100** ([F] · MVP) — L'ingestion hache (SHA-256), stocke dans l'objet verrouillé et produit le texte canonique avec table d'offsets.  
  _Réalise : RF-040 · MOD-06, MOD-22_
- **ET-101** ([T] · MVP) — Les analyseurs couvrent PDF numérique, Word, Excel, CSV, Markdown, texte et HTML ; un OCR optionnel [V] renvoie un indicateur de confiance.  
  _Réalise : HT-02 · MOD-22_
- **ET-102** ([T] · MVP) — La normalisation Unicode et la table d'offsets sont versionnées (`normalization_version`) et stables.  
  _Réalise : RT-073 · MOD-22_
- **ET-103** ([T] · MVP) — Le fenêtrage du texte (taille, chevauchement) est paramétré ; la recomposition des offsets est testée.  
  _Réalise : RF-039 · MOD-06_
- **ET-104** ([T] · MVP) — Antivirus, vérification de type par contenu et limites de taille s'appliquent à tout fichier ; les analyseurs sont isolés.  
  _Réalise : FS-01, FS-02 · MOD-22_
- **ET-105** ([T] · MVP) — Les appels sortants sont restreints par liste blanche ; les secrets de sources sont dans un coffre.  
  _Réalise : IG-04 · MOD-06_
- **ET-106** ([F] · MVP) — Les autorisations ponctuelles sont stockées avec périmètre et durée, expirent automatiquement et ne modifient jamais le registre.  
  _Réalise : RF-245 à RF-249 · MOD-15_
- **ET-107** ([F] · MVP) — L'algorithme A5 (`verify_quote`) est une fonction pure avec un jeu de tests exhaustif (Unicode, espaces, ligatures, guillemets, ambiguïtés).  
  _Réalise : RT-073, RT-074 · MOD-07_
- **ET-108** ([F] · MVP) — La valeur d'une preuve est toujours la tranche du texte canonique, jamais la copie du modèle.  
  _Réalise : RT-073 · MOD-07_
- **ET-109** ([T] · MVP) — Un job d'intégrité recalcule l'empreinte de chaque extrait et la compare à celle du texte canonique.  
  _Réalise : RT-065 · MOD-07_
- **ET-110** ([F] · MVP) — `evaluate_quality` est une fonction pure, testée sur 100 % de ses branches (10.6).  
  _Réalise : RF-059 à RF-064 · MOD-07_
- **ET-111** ([F] · MVP) — Le statut de qualité est évalué par couple (information, usage, période).  
  _Réalise : RB-017, RF-064 · MOD-07_
- **ET-112** ([F] · MVP) — Un changement de règle, de période, d'usage ou de source déclenche la réévaluation.  
  _Réalise : RF-071 · MOD-07_
- **ET-113** ([F] · MVP) — `qi_basis` enregistre critères appliqués, résultats, sources de vérification et version de règle.  
  _Réalise : RF-070 · MOD-07_
- **ET-114** ([F] · MVP) — Un job de vérification croisée interroge d'autres sources autorisées pour les informations candidates ou incertaines.  
  _Réalise : RF-062 · MOD-07_
- **ET-115** ([F] · MVP) — Les sorties de LT-05 ne servent que de preuves aux critères du lot ; elles ne décident jamais d'un statut.  
  _Réalise : PT-01 · MOD-07_
- **ET-116** ([F] · MVP) — Sans critère de vérification défini, aucune promotion automatique vers QI-01 n'est possible.  
  _Réalise : QO-029, RB-019 · MOD-07_

## 4. Critères d'acceptation à rendre verts (16)

Écrire d'abord un test par critère, étiqueté de son identifiant (`@pytest.mark.ca("CA-xxx")`).

- **CA-021** (RF-031, RF-034) — **Étant donné** une source pertinente mais non autorisée, **quand** l'Agent mobilise des informations, **alors** il ne la consulte pas.
- **CA-022** (RF-032) — **Étant donné** une information qu'INIS peut fournir, **quand** l'Agent la recherche, **alors** INIS est interrogé en premier.
- **CA-023** (RF-033) — **Étant donné** une information obligatoire absente d'INIS, **quand** d'autres sources sont explicitement autorisées, **alors** l'Agent les consulte.
- **CA-024** (RF-035, RF-036, RF-247) — **Étant donné** une autorisation ponctuelle accordée, **quand** l'Agent utilise la source, **alors** elle est utilisable pour la demande concernée et le registre permanent reste inchangé.
- **CA-025** (RF-037) — **Étant donné** une source accessible contenant une information non utilisable, **quand** l'Agent l'évalue, **alors** il ne l'utilise pas.
- **CA-026** (RF-038, RT-003) — **Étant donné** une source accessible mais dont l'intégration est non autorisée, **quand** l'Agent produit, **alors** le contenu n'est pas intégré au livrable.
- **CA-027** (RF-039) — **Étant donné** une information mobilisée, **quand** on consulte son enregistrement, **alors** source, référence précise et date de consultation figurent.
- **CA-028** (RF-040) — **Étant donné** une information transformée, **quand** on consulte la trace, **alors** sa forme d'origine reste disponible.
- **CA-029** (RF-042) — **Étant donné** une source indisponible, **quand** l'Agent mobilise, **alors** il le signale, poursuit auprès des autres sources et ne conclut pas à l'absence de l'information.
- **CA-030** (RF-041, RF-044) — **Étant donné** l'absence de méthode de recherche définie, **quand** l'Agent doit chercher, **alors** il n'invente pas de méthode ; toute consultation, y compris infructueuse, est journalisée.
- **CA-041** (RF-060) — **Étant donné** une information évaluée, **quand** on consulte son enregistrement, **alors** elle porte exactement un statut QI pour l'usage prévu.
- **CA-042** (RF-061 à RF-063) — **Étant donné** une information d'INIS dont la fiabilité n'est pas établie, **quand** l'Agent l'évalue, **alors** il tente de la vérifier et, tant que ce n'est pas abouti, ne la présente pas comme fait établi.
- **CA-043** (RF-064, RF-067) — **Étant donné** une information valide seulement pour une période passée, **quand** elle est visée pour décrire la situation actuelle, **alors** elle est Hors période ; elle reste utilisable pour une analyse historique.
- **CA-044** (RF-066, RF-068) — **Étant donné** deux informations dont l'une est plus récente, **quand** l'Agent choisit, **alors** la récence seule ne décide pas ; une information non autorisée pour l'usage est exclue du livrable.
- **CA-148** (RF-245 à RF-247) — **Étant donné** une autorisation ponctuelle, **quand** la personne responsable l'accorde, **alors** la source est utilisable pour la demande et le registre permanent reste inchangé.
- **CA-149** (RF-246, RF-248, RF-249) — **Étant donné** une autorisation ponctuelle, **quand** la demande se termine ou la durée expire, **alors** elle prend fin ; elle figure dans la traçabilité.

## 5. Exigences fonctionnelles liées (39) — une ligne chacune

Résumés seulement. Pour le texte complet et le contexte : `python tools/spec.py show RF-xxx`.

- RB-004 — L'Agent ne doit pas inventer une méthode de recherche, choisir arbitrairement un indicateur, modifier une définition ni résoudre librement une contradiction.
- RB-016 — INIS est une source prioritaire, sans être l'unique source ; une information issue d'INIS n'est pas automatiquement fiable.
- RB-017 — À un instant donné, une information a un seul statut de qualité (QI) pour un usage prévu et une période de référence donnés.
- RB-019 — Pour toute information candidate ou incertaine, l'Agent tente de la vérifier auprès de sources autorisées ; tant que la vérification n'aboutit pas, elle n'est pas prés...
- RF-031 — L'Agent doit rechercher les informations nécessaires uniquement dans les sources autorisées.
- RF-032 — L'Agent doit interroger INIS en priorité pour les informations qu'INIS peut fournir.
- RF-033 — Lorsqu'une information obligatoire est absente d'INIS, l'Agent peut consulter d'autres sources explicitement autorisées.
- RF-034 — L'Agent ne doit jamais consulter une source non autorisée, même si elle paraît pertinente.
- RF-035 — Les sources autorisées sont celles du registre permanent ou celles autorisées ponctuellement par la personne responsable.
- RF-036 — Une autorisation ponctuelle ne doit pas modifier le registre permanent.
- RF-037 — L'autorisation de consulter une source ne vaut ni validité ni droit d'utilisation de toutes les informations qu'elle contient ; l'Agent doit évaluer chaque information.
- RF-038 — L'Agent doit distinguer, pour chaque source, les niveaux d'autorisation d'accès, d'utilisation, d'intégration et de diffusion.
- RF-039 — L'Agent doit enregistrer, pour chaque information mobilisée : source, référence précise, date de consultation et, lorsqu'ils sont disponibles, période de référence et ...
- RF-040 — L'Agent doit conserver les informations mobilisées dans leur forme d'origine, distincte des versions transformées.
- RF-041 — L'Agent ne doit pas inventer de méthode de recherche ; il applique les méthodes et critères définis par les règles.
- RF-042 — Lorsqu'une source est indisponible, l'Agent doit le signaler, poursuivre auprès des autres sources autorisées et ne pas conclure à l'absence de l'information.
- RF-043 — Les informations fournies directement par l'utilisateur ou par pièces jointes doivent être traitées comme des informations à source identifiée (« fournie par l'utilisa...
- RF-044 — L'Agent doit tenir un journal des interrogations de sources (source, objet, résultat, date), y compris les consultations infructueuses.
- RF-059 — L'Agent doit évaluer chaque information selon des critères explicites définis par les règles.
- RF-060 — L'Agent doit classer chaque information dans l'un des statuts QI-01 à QI-07.
- RF-061 — L'Agent ne doit pas considérer une information issue d'INIS comme automatiquement fiable.
- RF-062 — Lorsque la fiabilité ou la pertinence d'une information est incertaine, l'Agent doit chercher à la vérifier auprès de sources autorisées.
- RF-063 — Tant que la vérification n'a pas abouti, l'Agent ne doit pas présenter l'information comme un fait établi.
- RF-064 — L'Agent doit évaluer le statut de qualité en fonction de l'usage prévu et de la période de référence.
- RF-066 — L'Agent ne doit pas privilégier systématiquement l'information la plus récente.
- RF-067 — Une information ancienne peut être retenue pour une analyse historique ; elle ne doit pas être utilisée pour décrire la situation actuelle.
- RF-068 — L'Agent doit exclure du livrable les informations interdites ou non autorisées pour l'usage prévu.
- RF-070 — L'Agent doit enregistrer, pour chaque évaluation, les critères appliqués, le résultat, les sources de vérification et la date.
- RF-071 — L'Agent doit réévaluer le statut d'une information lorsque la source, la règle, la période ou l'usage prévu change.
- RF-074 — Pour toute information manquante, l'Agent doit rechercher une source alternative lorsque cette recherche est autorisée.
- RF-245 — La personne responsable peut autoriser ponctuellement une source absente du registre permanent.
- RF-246 — Une autorisation ponctuelle doit préciser la source, la demande concernée, les niveaux accordés (accès, utilisation, intégration, diffusion) et la durée.
- RF-247 — Une autorisation ponctuelle ne modifie pas le registre permanent.
- RF-248 — Une autorisation ponctuelle doit figurer dans le rapport de traçabilité des productions concernées.
- RF-249 — Une autorisation ponctuelle prend fin avec la demande ou à la durée fixée, et n'est pas reconduite automatiquement pour d'autres demandes.
- RT-003 — L'accès à la source, l'utilisation du contenu, l'intégration et la diffusion font l'objet de quatre vérifications distinctes.
- RT-065 — Un audit doit pouvoir reconstituer pourquoi un livrable est ce qu'il est : règles, sources, décisions, contrôles.
- RT-073 — Lorsqu'une règle exige une citation exacte, l'Agent restitue le texte à l'identique et l'identifie comme citation.
- RT-074 — L'Agent n'attribue jamais à une source une information qu'elle ne contient pas.

## 6. À lire à la demande (ne rien lire d'autre au départ)

| Quoi | Commande | Pourquoi |
|---|---|---|
| Spéc. technique 10.4 | `python tools/spec.py section T 10.4` | É3 Mobilisation (dont A5) |
| Spéc. technique 10.6 | `python tools/spec.py section T 10.6` | É5 Qualité (evaluate_quality) |
| Spéc. technique 15 | `python tools/spec.py section T 15` | Intégrations et sources |
| Spéc. technique 9.1 | `python tools/spec.py section T 9.1` | Modèle de décision d'autorisation |
| Spéc. technique 9.2 | `python tools/spec.py section T 9.2` | Quatre points de contrôle |
| Spéc. technique 9.3 | `python tools/spec.py section T 9.3` | Algorithme de décision |
| Spéc. technique 11.4 | `python tools/spec.py section T 11.4` | Tâches LT-03, LT-05 |
| Spéc. technique Annexe-B | `python tools/spec.py section T Annexe-B` | Schémas LT-03 |
| Spéc. technique Annexe-D | `python tools/spec.py section T Annexe-D` | Prompt PRM-03 |
| Spéc. fonctionnelle UC-004 | `python tools/spec.py section F UC-004` | Fiche du cas d’usage |
| Spéc. fonctionnelle UC-006 | `python tools/spec.py section F UC-006` | Fiche du cas d’usage |
| Spéc. fonctionnelle UC-025 | `python tools/spec.py section F UC-025` | Fiche du cas d’usage |
| Spéc. fonctionnelle 3.3.1 | `python tools/spec.py section F 3.3.1` | Statuts de qualité QI |

## 7. Critères de sortie du jalon

TST-03 et TST-05 (qualité) verts ; EVL-A au seuil ; citations inventées retenues = 0 ; revalidation par empreinte de source testée.

## 8. Rappels (extraits d'AGENTS.md)

- Tests d'acceptation d'abord ; `make check` doit passer ; ne jamais affaiblir un test, une contrainte ou un déclencheur.
- Ambiguïté de spécification → question dans `docs/reports/QUESTIONS.md`, jamais d'invention.
- À la fin d'une tranche : mettre à jour `docs/reports/PROGRESS.md`.

