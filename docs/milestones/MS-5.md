# Jalon MS-5 — Transformations, calculs, atomes, rendu

> Brief généré par `tools/gen_briefs.py` — ne pas modifier à la main. Pour tout détail : `python tools/spec.py show <ID>`.

## 1. Objectif

Transformations autorisées, calcul décimal (CEL), reformulation fidèle (A6), atomes de contenu, minimisation des données, rendus Word/PDF/CSV/Markdown avec relecture.

**À savoir.** Excel et PowerPoint sont en V2 (MS-9). Le contrôle visuel manuel de fidélité Word/PDF (ET-162) se fait avec le Product Owner.

## 2. Périmètre

- Cas d'usage : UC-009, UC-010, UC-011, UC-031
- Suites de tests visées : TST-06, TST-07, TST-16
- Hors périmètre de ce jalon : Contrôles qualité, rapports, finalisation.
- 2 exigence(s) V2 comprises dans les plages sont **reportées à MS-9** (non listées ci-dessous).

## 3. Exigences techniques à réaliser (37)

- **ET-084** ([F] · MVP) — Le pipeline de minimisation (9.7) s'applique avant création d'atome et avant tout appel LLM ; l'action par défaut est l'exclusion.  
  _Réalise : RT-017 à RT-019 · MOD-20_
- **ET-085** ([T] · MVP) — La pseudonymisation réversible remplace les valeurs par des jetons locaux avant envoi à un LLM ; la table de correspondance est chiffrée et ne quitte pas le périmètre.  
  _Réalise : RT-017 · MOD-20_
- **ET-086** ([F] · MVP) — Un contrôle de sortie LLM vérifie que seuls des jetons connus apparaissent et qu'aucune valeur sensible n'est produite.  
  _Réalise : RT-021 · MOD-21_
- **ET-087** ([F] · MVP) — Les quasi-identifiants sont déclarés dans le lot ; leurs combinaisons sont masquées ensemble ; en cas de doute, suspension.  
  _Réalise : RT-021, CL-051 · MOD-20_
- **ET-088** ([F] · MVP) — Chaque masquage ou exclusion est enregistré sans contenu (`masking_records`).  
  _Réalise : RT-020, RT-040 · MOD-20_
- **ET-089** ([F] · MVP) — Les journaux applicatifs et LLM ne contiennent aucune valeur sensible ; un filtre de journalisation l'impose.  
  _Réalise : RT-025 · MOD-23_
- **ET-090** ([F] · MVP) — Au MVP, une demande n'est visible que de son auteur et de la personne responsable ; tout autre accès est refusé.  
  _Réalise : RT-016 · MOD-20_
- **ET-131** ([F] · MVP) — Les fonctions TF-01 à TF-09 sont enregistrées ; une transformation ne s'exécute que si le lot la déclare pour l'élément.  
  _Réalise : RF-092, RF-104 · MOD-10_
- **ET-132** ([F] · MVP) — Chaque transformation écrit une ligne (opération, règle autorisante, entrée, sortie).  
  _Réalise : RF-102 · MOD-10_
- **ET-133** ([F] · MVP) — L'algorithme A6 (reformulation) est implémenté : vérifications déterministes puis contrôle de fidélité LT-08.  
  _Réalise : RF-103 · MOD-10, ADR-006_
- **ET-134** ([T] · MVP) — Des extracteurs de nombres, dates, entités, négations, modalités et quantificateurs existent pour le français et l'anglais, testés sur un corpus annoté.  
  _Réalise : RF-103 · MOD-10_
- **ET-135** ([F] · MVP) — En cas d'échec de la reformulation, repli sur la citation brute si la règle l'autorise, sinon blocage de l'élément.  
  _Réalise : RF-103, RB-001 · MOD-10_
- **ET-136** ([T] · MVP) — Le moteur de calcul CEL applique les limites d'exécution (profondeur, taille, durée).  
  _Réalise : FM-05 · MOD-10_
- **ET-137** ([F] · MVP) — `derived_values` conserve entrées, sources, formule (texte et empreinte), unités, arrondi, contexte et résultat.  
  _Réalise : RF-106 à RF-110 · MOD-10_
- **ET-138** ([F] · MVP) — Le rejeu d'un calcul compare valeur **et** représentation ; un écart est un échec de CT-07.  
  _Réalise : RF-112 · MOD-10, MOD-12_
- **ET-139** ([F] · MVP) — Un résultat dérivé hérite du statut de qualité le plus faible de ses entrées.  
  _Réalise : RF-113 · MOD-10_
- **ET-140** ([F] · MVP) — Les atomes de calcul et la traçabilité marquent le résultat comme dérivé.  
  _Réalise : RF-114 · MOD-11_
- **ET-141** ([F] · MVP) — Aucune conversion de date ou d'unité n'est faite sans règle explicite.  
  _Réalise : RF-096, RB-043 · MOD-10_
- **ET-142** ([F] · MVP) — En cas d'échec d'une méthode définie, aucune formule de remplacement n'est utilisée.  
  _Réalise : RB-044 · MOD-10_
- **ET-143** ([F] · MVP) — La contrainte `atom_is_bound` est imposée par la base ; l'autorisation AU-3 est vérifiée avant chaque création d'atome.  
  _Réalise : RF-123, RF-124 · MOD-11_
- **ET-144** ([F] · MVP) — Un atome issu d'une information de statut autre que QI-01 porte une qualification explicite.  
  _Réalise : RF-069 · MOD-11_
- **ET-145** ([T] · MVP) — Un modèle de document neutre (blocs typés référençant des atomes) et un `RendererPort` existent.  
  _Réalise : RN-01 à RN-03 · ADR-011_
- **ET-146** ([T] · MVP) — Le rendu Word utilise le gabarit du type ; il embarque des signets de provenance.  
  _Réalise : RF-122, RF-125 · MOD-22_
- **ET-147** ([T] · MVP) — Le PDF est obtenu par conversion du Word dans un conteneur isolé sans réseau (15.7).  
  _Réalise : RF-125 · ADR-011_
- **ET-150** ([T] · MVP) — Le rendu CSV protège contre l'injection de formules.  
  _Réalise : RF-125 · MOD-22_
- **ET-151** ([T] · MVP) — Le rendu Markdown utilise des notes de bas de page pour la provenance.  
  _Réalise : RF-125 · MOD-22_
- **ET-152** ([F] · MVP) — Toute version provisoire porte le marquage « PROVISOIRE » dans le fichier et l'interface.  
  _Réalise : RF-171, RB-075 · MOD-11_
- **ET-153** ([F] · MVP) — Après rendu, le fichier est relu : tous les atomes présents, aucun texte en trop ; sinon le rendu est rejeté.  
  _Réalise : CT-01, CT-13 · MOD-22_
- **ET-154** ([T] · MVP) — Les propriétés de documents sont fixées pour la reproductibilité ; les empreintes de chaque fichier sont enregistrées.  
  _Réalise : RT-065 · MOD-22_
- **ET-155** ([T] · MVP) — Le jeu de polices est figé et embarqué dans l'image du convertisseur.  
  _Réalise : — · MOD-22_
- **ET-156** ([F] · MVP) — Les limites de présentation du modèle sont appliquées ; une adaptation hors limites est refusée.  
  _Réalise : RF-118 · MOD-11_
- **ET-157** ([F] · MVP) — Le format demandé est comparé aux formats autorisés du type ; sinon blocage ou proposition.  
  _Réalise : RF-126 · MOD-11_
- **ET-158** ([T] · MVP) — La vue de diffusion dérivée (12.7) est produite avec son empreinte propre et sans statut de version.  
  _Réalise : RF-180 · MOD-14_
- **ET-159** ([F] · MVP) — Les fichiers sont adressés par leur empreinte ; les objets des versions finalisées sont verrouillés.  
  _Réalise : RF-166 · ADR-010_
- **ET-160** ([T] · MVP) — Les liens de téléchargement sont signés et valables au plus quelques minutes.  
  _Réalise : RT-013 · ADR-010_
- **ET-161** ([T] · MVP) — Un paquet de modèle versionné regroupe structure, gabarits et limites de présentation.  
  _Réalise : RF-091 · MOD-02_
- **ET-162** ([T] · MVP) — Une liste de contrôle visuel manuel (Word et PDF) est exécutée au pilote pour valider la fidélité de présentation.  
  _Réalise : — · ADR-011_

## 4. Critères d'acceptation à rendre verts (30)

Écrire d'abord un test par critère, étiqueté de son identifiant (`@pytest.mark.ca("CA-xxx")`).

- **CA-053** (RF-092, RF-104) — **Étant donné** une transformation sans règle autorisante, **quand** l'Agent y est conduit, **alors** il la refuse et la traite comme décision non couverte.
- **CA-054** (RF-102, RT-030) — **Étant donné** une transformation appliquée, **quand** on consulte la trace, **alors** opération, règle, état avant et état après sont présents.
- **CA-055** (RF-096, RB-043) — **Étant donné** une conversion de format de date autorisée par une règle, **quand** l'Agent l'applique, **alors** elle est tracée ; sans règle, elle est refusée.
- **CA-056** (RF-101, RB-024) — **Étant donné** une hypothèse dans les sources, **quand** elle est intégrée, **alors** elle reste présentée comme hypothèse.
- **CA-057** (RF-103) — **Étant donné** un texte à reformuler fidèlement, **quand** l'Agent le reformule, **alors** modalité, incertitude, conditions et périmètre sont préservés.
- **CA-058** (RF-097) — **Étant donné** une correction grammaticale autorisée, **quand** elle est appliquée, **alors** elle est tracée et le sens est inchangé.
- **CA-059** (RF-105, RF-111) — **Étant donné** un élément nécessitant un calcul sans méthode définie, **quand** l'Agent y est conduit, **alors** il ne calcule pas et demande une clarification ou bloque l'élément.
- **CA-060** (RF-106 à RF-110) — **Étant donné** un calcul défini, **quand** il est exécuté, **alors** entrées, sources, méthode, unités et conventions, arrondi et résultat sont conservés.
- **CA-061** (RF-112, RF-135) — **Étant donné** un calcul tracé, **quand** il est rejoué, **alors** il donne le même résultat.
- **CA-062** (RF-113, RF-114) — **Étant donné** une entrée de statut QI-02, **quand** le résultat est produit, **alors** son statut ne dépasse pas QI-02 et il est identifié comme dérivé.
- **CA-063** (RF-115) — **Étant donné** des conditions de production non satisfaites, **quand** la demande avance, **alors** aucun livrable final n'est produit.
- **CA-064** (RF-117) — **Étant donné** une section obligatoire, **quand** une suppression est tentée sans autorisation explicite, **alors** elle est refusée.
- **CA-065** (RF-119, RF-120, RF-171) — **Étant donné** des éléments bloqués, **quand** l'Agent produit les autres, **alors** la version est marquée provisoire, les emplacements bloqués portent leur motif et aucun contenu n'est inventé.
- **CA-066** (RF-121, RF-122) — **Étant donné** un livrable produit, **quand** on consulte un élément significatif, **alors** il est lié à ses lignes de cartographie et porte ses références.
- **CA-067** (RF-123, RT-069) — **Étant donné** un contenu sans rattachement à une source, un modèle ou une règle, **quand** l'Agent assemble, **alors** ce contenu est absent du livrable.
- **CA-068** (RF-124) — **Étant donné** des données non permises pour les destinataires, **quand** l'Agent insère, **alors** elles sont masquées ou exclues.
- **CA-069** (RF-125, RF-126) — **Étant donné** un format non autorisé pour le type, **quand** il est demandé, **alors** l'Agent bloque ou propose les formats autorisés.
- **CA-070** (RF-118) — **Étant donné** une adaptation de présentation hors des limites prévues, **quand** elle est tentée, **alors** elle est refusée.
- **CA-157** (RT-002, RT-013) — **Étant donné** un utilisateur et un destinataire de droits différents, **quand** ils accèdent à un même livrable, **alors** chacun n'accède qu'à ce que ses droits permettent.
- **CA-158** (RT-003, RT-004) — **Étant donné** une source accessible mais dont l'utilisation est interdite, **quand** l'Agent traite, **alors** il ne l'utilise pas.
- **CA-159** (RT-005, RB-058) — **Étant donné** des droits incertains, **quand** l'opération est lancée, **alors** elle est suspendue.
- **CA-160** (RT-006, RT-007) — **Étant donné** le refus d'accès à une source protégée, **quand** l'Agent l'explique, **alors** l'explication ne révèle ni son existence, ni son identité, ni son contenu.
- **CA-161** (RT-008) — **Étant donné** une question sur une source inaccessible à l'interlocuteur, **quand** l'Agent répond, **alors** il ne confirme ni n'infirme son existence.
- **CA-162** (RT-009) — **Étant donné** une reprise, **quand** elle est effectuée, **alors** les droits sont revérifiés.
- **CA-163** (RT-010, RT-011) — **Étant donné** un livrable agrégeant des informations de sensibilités différentes, **quand** on consulte sa classification, **alors** elle est au moins aussi restrictive que la plus contraignante ; le rapport de traçabilité a sa propre classification.
- **CA-164** (RT-017, RT-018) — **Étant donné** des données non nécessaires ou non permises, **quand** l'Agent insère, **alors** elles ne sont pas reprises ou sont masquées.
- **CA-165** (RT-020, RT-021) — **Étant donné** une donnée masquée, **quand** un lecteur non autorisé consulte livrable et traçabilité, **alors** le contenu n'est pas reconstituable.
- **CA-166** (RT-022, RT-023) — **Étant donné** un cas non couvert par les règles de minimisation ou un masquage rendant un élément obligatoire incohérent, **quand** l'Agent y est conduit, **alors** il suspend ou bloque l'élément et sollicite une décision.
- **CA-167** (RT-014, RB-062) — **Étant donné** une action ordinaire largement ouverte, **quand** un utilisateur l'exécute, **alors** aucune restriction de source, de confidentialité ni de diffusion n'est levée.
- **CA-168** (RT-015, RT-026) — **Étant donné** une information fournie par un utilisateur, **quand** une autre demande est traitée, **alors** elle n'est pas réutilisée sans autorisation ; sa conservation respecte les règles.

## 5. Exigences fonctionnelles liées (68) — une ligne chacune

Résumés seulement. Pour le texte complet et le contexte : `python tools/spec.py show RF-xxx`.

- RB-001 — **Aucune invention.** L'Agent ne fabrique ni fait, ni chiffre, ni référence, ni résultat, ni décision, ni justification pour combler une lacune.
- RB-024 — Une hypothèse n'est jamais transformée en fait établi.
- RB-043 — La conversion d'unités, de dates ou de formats n'est faite que selon des règles explicites.
- RB-044 — En cas d'échec d'une méthode définie, l'Agent n'invente pas de formule de remplacement.
- RB-058 — Si les droits applicables sont incertains, l'Agent suspend l'opération concernée jusqu'à clarification.
- RB-062 — L'accès largement partagé aux actions ordinaires ne supprime ni les restrictions de confidentialité, ni les autorisations propres aux sources, ni les limites de diffus...
- RB-075 — Une version provisoire n'est jamais présentée comme une version finale.
- RF-069 — Lorsque les règles permettent d'intégrer une information non QI-01, l'Agent doit la qualifier explicitement dans le livrable.
- RF-091 — L'Agent doit organiser les informations disponibles selon le modèle documentaire et les règles applicables.
- RF-092 — L'Agent ne doit appliquer que les transformations éditoriales, structurelles et calculatoires autorisées.
- RF-096 — L'Agent peut convertir des formats de dates, d'unités ou de fichiers selon des règles explicites (TF-04).
- RF-097 — L'Agent peut corriger des erreurs grammaticales ou typographiques lorsque cela est autorisé (TF-05).
- RF-101 — L'Agent ne doit pas modifier le sens des informations, inventer des relations entre données ni transformer une hypothèse en fait établi.
- RF-102 — L'Agent doit tracer chaque transformation : opération, règle autorisante, entrée, sortie.
- RF-103 — Une reformulation fidèle doit préserver le sens, la portée et les nuances (modalité, incertitude, conditions, périmètre).
- RF-104 — Une transformation non couverte par une règle explicite doit être refusée et traitée comme une décision non autorisée.
- RF-105 — L'Agent ne doit effectuer aucun calcul ni aucune transformation numérique sans méthode explicitement définie.
- RF-106 — Pour chaque résultat dérivé, l'Agent doit conserver les données d'entrée et leurs sources.
- RF-107 — Pour chaque résultat dérivé, l'Agent doit conserver la formule ou la méthode.
- RF-108 — Pour chaque résultat dérivé, l'Agent doit conserver les unités et conventions applicables.
- RF-109 — Pour chaque résultat dérivé, l'Agent doit conserver les règles d'arrondi éventuelles.
- RF-110 — Pour chaque résultat dérivé, l'Agent doit conserver le résultat.
- RF-111 — Si la méthode nécessaire n'est pas définie, l'Agent doit demander une clarification ou bloquer l'élément concerné.
- RF-112 — Un calcul doit être reproductible : mêmes entrées et même méthode donnent le même résultat.
- RF-113 — Un résultat dérivé ne doit pas avoir un statut de qualité supérieur au plus faible de ses entrées.
- RF-114 — Un résultat dérivé doit être identifié comme tel dans le livrable et dans la traçabilité, et ne jamais être présenté comme une donnée source.
- RF-115 — L'Agent ne doit produire le livrable que lorsque les conditions nécessaires sont satisfaites.
- RF-117 — Les sections, champs et éléments obligatoires ne doivent être ni supprimés ni modifiés sans autorisation explicite.
- RF-118 — Les adaptations de présentation ne sont permises que dans les limites prévues.
- RF-119 — L'Agent peut produire les éléments non bloqués avant la résolution des blocages, sous forme **provisoire** clairement marquée, jamais présentée comme livrable final.
- RF-120 — Les éléments bloqués doivent apparaître comme tels dans une version provisoire (emplacement identifié et motif), sans contenu inventé.
- RF-121 — Le livrable doit inclure les citations et références nécessaires à sa compréhension et à sa vérification.
- RF-122 — Chaque élément significatif du livrable doit être relié à ses lignes de cartographie et à ses sources.
- RF-123 — L'Agent ne doit inclure aucun contenu qui ne se rattache ni à une information source, ni à un modèle, ni à une règle.
- RF-124 — L'Agent doit appliquer les règles de minimisation, de masquage et d'exclusion lors de l'insertion des informations.
- RF-125 — L'Agent doit produire le livrable dans le format demandé parmi les formats prévus (Word, PDF, Excel, PowerPoint, CSV, Markdown), dans la mesure où le type de livrable ...
- RF-126 — Si le format demandé n'est pas autorisé pour le type de livrable, l'Agent doit bloquer ou proposer les formats autorisés, sans dégrader silencieusement le contenu.
- RF-135 — L'Agent doit contrôler la reproductibilité des calculs autorisés (CT-07).
- RF-166 — Une version finalisée devient immuable.
- RF-171 — Un livrable provisoire doit être explicitement marqué comme non finalisé, quel que soit son format.
- RF-180 — L'autorisation de diffusion doit préciser la version, les destinataires ou catégories de destinataires, le périmètre et les éléments exclus.
- RT-002 — L'Agent doit appliquer les droits d'accès de chaque utilisateur à chaque objet (demande, livrable, rapport, traçabilité, historique).
- RT-003 — L'accès à la source, l'utilisation du contenu, l'intégration et la diffusion font l'objet de quatre vérifications distinctes.
- RT-004 — Les vérifications sont faites aux moments adéquats : avant mobilisation (accès), avant exploitation (utilisation), avant insertion (intégration), avant diffusion (diff...
- RT-005 — Lorsque les droits sont incertains, l'Agent suspend l'opération concernée jusqu'à clarification.
- RT-006 — Aucune information protégée ne doit être révélée par l'état d'avancement, les motifs de blocage, les questions de clarification ou les messages d'erreur.
- RT-007 — Les explications de refus restent générales lorsque le détail révélerait l'existence, l'identité ou le contenu d'une source protégée.
- RT-008 — L'Agent ne confirme ni n'infirme l'existence d'une source à laquelle l'interlocuteur n'a pas accès.
- RT-009 — Les droits sont évalués au moment de l'opération et revérifiés à la reprise d'une demande suspendue.
- RT-010 — Un livrable agrégeant des informations de sensibilités différentes hérite de la restriction la plus contraignante parmi celles qu'il contient, sauf règle contraire.
- RT-011 — Le rapport de traçabilité a sa propre classification et peut être plus restrictif que le livrable.
- RT-013 — Un destinataire n'accède qu'aux éléments autorisés pour lui.
- RT-014 — Le partage large des actions ordinaires ne lève aucune restriction de confidentialité, de source ou de diffusion.
- RT-015 — Les informations fournies par un utilisateur dans une demande sont confidentielles par défaut et ne sont pas réutilisées pour d'autres demandes sans autorisation.
- RT-016 — Au MVP, une demande n'est accessible qu'à son auteur et à la personne responsable ; tout accès non expressément accordé est refusé.
- RT-017 — L'Agent doit appliquer un principe de minimisation : ne reprendre que les données nécessaires, autorisées pour l'usage prévu et permises pour les destinataires.
- RT-018 — Les données non permises doivent être masquées ou exclues selon les règles applicables.
- RT-019 — Les catégories de données personnelles et sensibles sont fournies par les règles du type de livrable ; sans règle de minimisation applicable, la donnée n'est pas reprise.
- RT-020 — Le rapport de traçabilité doit référencer une information masquée sans en révéler le contenu aux lecteurs non autorisés.
- RT-021 — L'Agent ne doit pas déduire ou reconstituer des données masquées à partir d'autres éléments du livrable.
- RT-022 — Si les règles de minimisation ne couvrent pas un cas, l'élément concerné est suspendu et traité comme une décision non couverte.
- RT-023 — Si un masquage ou une exclusion rend un élément obligatoire manquant ou incohérent, l'Agent bloque l'élément et sollicite une décision.
- RT-025 — Les journaux enregistrent l'usage de données sensibles sans en dupliquer inutilement le contenu.
- RT-026 — La conservation des données personnelles est limitée par les règles de conservation.
- RT-030 — Pour chaque transformation : opération, règle autorisante, état avant, état après.
- RT-040 — La traçabilité mentionne aussi ce qui a été exclu ou masqué (existence de l'exclusion et motif général).
- RT-065 — Un audit doit pouvoir reconstituer pourquoi un livrable est ce qu'il est : règles, sources, décisions, contrôles.
- RT-069 — Aucun contenu n'est généré sans rattachement à une source, un modèle ou une règle.

## 6. À lire à la demande (ne rien lire d'autre au départ)

| Quoi | Commande | Pourquoi |
|---|---|---|
| Spéc. technique 9.6 | `python tools/spec.py section T 9.6` | Classification et héritage |
| Spéc. technique 9.7 | `python tools/spec.py section T 9.7` | Minimisation et masquage |
| Spéc. technique 10.7 | `python tools/spec.py section T 10.7` | É6 Transformation |
| Spéc. technique 10.9 | `python tools/spec.py section T 10.9` | É8 Production |
| Spéc. technique 11.5 | `python tools/spec.py section T 11.5` | Reformulation fidèle (A6) |
| Spéc. technique 12.1 | `python tools/spec.py section T 12.1` | Chaîne de rendu |
| Spéc. technique 12.2 | `python tools/spec.py section T 12.2` | Détails par format |
| Spéc. technique 12.3 | `python tools/spec.py section T 12.3` | Relecture après rendu |
| Spéc. technique 8.8 | `python tools/spec.py section T 8.8` | Évaluateur de formules (CEL) |
| Spéc. technique 8.9 | `python tools/spec.py section T 8.9` | Corrections mécaniques |
| Spéc. technique Annexe-B | `python tools/spec.py section T Annexe-B` | Schémas LT-07, LT-08 |
| Spéc. technique Annexe-D | `python tools/spec.py section T Annexe-D` | Prompts PRM-07, PRM-08 |
| Spéc. fonctionnelle UC-009 | `python tools/spec.py section F UC-009` | Fiche du cas d’usage |
| Spéc. fonctionnelle UC-010 | `python tools/spec.py section F UC-010` | Fiche du cas d’usage |
| Spéc. fonctionnelle UC-011 | `python tools/spec.py section F UC-011` | Fiche du cas d’usage |
| Spéc. fonctionnelle UC-031 | `python tools/spec.py section F UC-031` | Fiche du cas d’usage |

## 7. Critères de sortie du jalon

TST-06, TST-07 et TST-16 verts ; EVL-D au seuil ; chaque rendu relu sans écart ; aucun atome sans lien de preuve.

## 8. Rappels (extraits d'AGENTS.md)

- Tests d'acceptation d'abord ; `make check` doit passer ; ne jamais affaiblir un test, une contrainte ou un déclencheur.
- Ambiguïté de spécification → question dans `docs/reports/QUESTIONS.md`, jamais d'invention.
- À la fin d'une tranche : mettre à jour `docs/reports/PROGRESS.md`.

