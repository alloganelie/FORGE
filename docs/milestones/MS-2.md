# Jalon MS-2 — Demande et faisabilité

> Brief généré par `tools/gen_briefs.py` — ne pas modifier à la main. Pour tout détail : `python tools/spec.py show <ID>`.

## 1. Objectif

Passerelle LLM (enregistrements rejoués, journal d'appels), compréhension de la demande, clarification, faisabilité, messages d'état par gabarits. Produire le « squelette de bout en bout » : une demande va de la saisie au diagnostic de faisabilité.

**À savoir.** CA-141 (statuts d'un livrable finalisé) est traité en MS-6. Les appels LLM de la CI utilisent des enregistrements rejoués, jamais un fournisseur réel.

## 2. Périmètre

- Cas d'usage : UC-001, UC-002, UC-003, UC-023
- Suites de tests visées : TST-01, TST-02, TST-14 (partie suivi)
- Hors périmètre de ce jalon : Sources, extraction, cartographie, rendu de livrables.

## 3. Exigences techniques à réaliser (39)

- **ET-231** ([F] · MVP) — Le routeur LT-10 ne produit que des commandes d'une liste blanche, validées par schéma, autorisées et exécutées par le code.  
  _Réalise : RF-225 · ADR-019_
- **ET-232** ([F] · MVP) — Les modèles de langage n'ont accès à aucune fonction d'écriture.  
  _Réalise : PT-01 · MOD-21_
- **ET-233** ([F] · MVP) — Les gabarits de messages d'état sont versionnés, en français ; leurs variables sont remplies depuis la base.  
  _Réalise : RF-163, RF-235 · MOD-18_
- **ET-234** ([F] · MVP) — Le suivi rend étapes terminées, étapes en cours, motifs communicables, éléments attendus et prochaine action.  
  _Réalise : RF-226 à RF-231 · MOD-18_
- **ET-235** ([F] · MVP) — Les statuts de conformité, d'approbation et de diffusion sont présentés séparément dans tous les messages.  
  _Réalise : RF-237 · MOD-18_
- **ET-236** ([F] · MVP) — Le filtre de sortie MG-01 à MG-03 s'applique à tout texte libre produit par un modèle.  
  _Réalise : RF-163, IV-10 · MOD-18_
- **ET-237** ([F] · MVP) — Les questions de clarification sont limitées par lot, hiérarchisées (bloquantes d'abord) et accompagnées de leur raison.  
  _Réalise : RF-013 à RF-015 · MOD-03_
- **ET-238** ([T] · MVP) — Un doublon possible de demande est signalé sans fusion automatique.  
  _Réalise : CL-052 · MOD-03_
- **ET-239** ([F] · MVP) — La commande `SplitRequest` crée des demandes indépendantes uniquement sur confirmation.  
  _Réalise : RF-008 · MOD-03_
- **ET-240** ([T] · MVP) — Le fil de conversation est persistant et immuable (ajout seul).  
  _Réalise : RT-063 · MOD-18_
- **ET-241** ([F] · MVP) — Le contexte conversationnel est limité à la demande ; aucune mémoire transversale ne modifie le comportement.  
  _Réalise : RF-265, RB-010 · MOD-18_
- **ET-242** ([T] · MVP) — L'Agent ne formule aucun engagement sur un état futur ni sur une date.  
  _Réalise : RF-163 · MOD-18_
- **ET-243** ([F] · MVP) — Les messages d'erreur utilisent les gabarits des motifs MB.  
  _Réalise : RB-120 · MOD-18_
- **ET-244** ([T] · MVP) — Le français est la langue par défaut ; les textes sont externalisés pour une future internationalisation.  
  _Réalise : RB-121 · MOD-18_
- **ET-245** ([F] · MVP) — L'historique des échanges est consultable selon les droits.  
  _Réalise : RF-238 · MOD-18_
- **ET-246** ([T] · MVP) — Une tentative d'injection détectée dans un message utilisateur est consignée comme observation.  
  _Réalise : IP-06 · MOD-18_
- **ET-247** ([T] · MVP) — `run_task` est l'unique point d'appel d'un fournisseur de LLM.  
  _Réalise : LG-01 · ADR-009_
- **ET-248** ([T] · MVP) — Deux adaptateurs existent : Anthropic natif et compatible OpenAI/OpenRouter.  
  _Réalise : PT-13 · ADR-009_
- **ET-249** ([T] · MVP) — Les tâches demandent des rôles ; la correspondance rôle → modèle est configurée ; un changement est enregistré et soumis aux évaluations.  
  _Réalise : 11.2 · MOD-21_
- **ET-250** ([T] · MVP) — Les sorties structurées sont demandées par schéma et **revalidées** par Pydantic.  
  _Réalise : LG-03 · MOD-21_
- **ET-251** ([T] · MVP) — Les schémas sont plats, à champs obligatoires, sans récursivité ; un test statique vérifie le respect des limites du fournisseur.  
  _Réalise : LG-06 · MOD-21_
- **ET-252** ([F] · MVP) — Refus, troncature et sortie invalide sont des échecs typés ; jamais traités comme succès.  
  _Réalise : LG-04, PT-17 · MOD-21_
- **ET-253** ([T] · MVP) — La fonction de citations du fournisseur n'est pas utilisée.  
  _Réalise : LG-07 · MOD-21_
- **ET-254** ([T] · MVP) — Les valeurs d'énumération sont comparées sans tenir compte de la casse.  
  _Réalise : LG-05 · MOD-21_
- **ET-255** ([T] · MVP) — La température et les paramètres sont fixés par tâche et enregistrés.  
  _Réalise : LG-08 · MOD-21_
- **ET-256** ([F] · MVP) — Chaque appel est enregistré dans `llm_calls` ; les charges utiles sont conservées dans le stockage objet, avec la classification de la demande.  
  _Réalise : LG-09, RT-034 · MOD-21_
- **ET-257** ([F] · MVP) — L'autorisation AU-2 et la minimisation s'appliquent avant chaque appel.  
  _Réalise : PT-10, RT-017 · MOD-21_
- **ET-258** ([T] · MVP) — Les prompts sont des fichiers versionnés avec empreinte enregistrée ; chaque appel référence sa version.  
  _Réalise : 11.10 · MOD-21_
- **ET-259** ([T] · MVP) — Les données sont délimitées dans le prompt ; la consigne anti-injection figure dans chaque message système.  
  _Réalise : IP-01, IP-02 · MOD-21_
- **ET-260** ([F] · MVP) — Aucun outil ni accès n'est exposé aux modèles.  
  _Réalise : LG-02, IP-03 · MOD-21_
- **ET-261** ([T] · MVP) — Le préfixe statique des prompts est mis en cache ; le taux de réussite du cache est mesuré.  
  _Réalise : BU-02 · MOD-21_
- **ET-262** ([T] · MVP) — Un budget de jetons et d'appels existe par tâche et par demande ; le dépassement est un échec typé.  
  _Réalise : BU-01 · MOD-21_
- **ET-293** ([T] · MVP) — L'interface est en Next.js (App Router) avec TypeScript strict.  
  _Réalise : ADR-012 · CMP-01_
- **ET-294** ([F] · MVP) — Aucune règle métier n'existe côté interface ; une revue systématique le vérifie.  
  _Réalise : UI-01 · CMP-01_
- **ET-295** ([F] · MVP) — Le composant `StatusStrip` présente séparément R, C, A, D et V ; il n'existe aucun indicateur global.  
  _Réalise : RF-237, RB-109 · CMP-01_
- **ET-296** ([F] · MVP) — Un badge de version provisoire est visible en permanence.  
  _Réalise : RF-171 · CMP-01_
- **ET-297** ([F] · MVP) — L'annulation définitive utilise une confirmation en deux étapes.  
  _Réalise : RF-210 · CMP-01_
- **ET-298** ([F] · MVP) — Les motifs communicables sont affichés tels que reçus de l'API.  
  _Réalise : RB-065 · CMP-01_
- **ET-299** ([T] · MVP) — Un conflit 412 recharge la ressource et conserve la saisie de l'utilisateur.  
  _Réalise : UI-07 · CMP-01_

## 4. Critères d'acceptation à rendre verts (31)

Écrire d'abord un test par critère, étiqueté de son identifiant (`@pytest.mark.ca("CA-xxx")`).

- **CA-001** (RF-001, RF-002) — **Étant donné** un utilisateur autorisé, **quand** il soumet une demande en langage naturel, **alors** la demande est enregistrée avec identifiant, auteur, date et texte d'origine inchangé, à l'état Reçue.
- **CA-002** (RF-003) — **Étant donné** une demande « rapport de suivi-évaluation en PDF », **quand** l'Agent l'analyse, **alors** le type de livrable et le format de fichier sont identifiés séparément.
- **CA-003** (RF-006, RF-012) — **Étant donné** un paramètre déterminable par le contexte autorisé et les règles, **quand** l'Agent analyse la demande, **alors** il ne pose aucune question à ce sujet.
- **CA-004** (RF-009, RB-064) — **Étant donné** un utilisateur non autorisé à soumettre ce type de demande, **quand** il soumet, **alors** l'Agent refuse avec un motif communicable et ne produit rien.
- **CA-005** (RF-011) — **Étant donné** une ambiguïté sans incidence significative sur la conformité ou la validité, **quand** l'Agent poursuit, **alors** il ne pose pas de question.
- **CA-006** (RF-011, RF-014, RF-016) — **Étant donné** une ambiguïté significative, **quand** l'Agent la détecte, **alors** il pose une question ciblée indiquant en quoi la réponse conditionne le livrable et la demande passe à En clarification.
- **CA-007** (RF-013, RF-015) — **Étant donné** plusieurs ambiguïtés, **quand** l'Agent sollicite l'utilisateur, **alors** les questions bloquantes passent en premier et aucun formulaire long n'est présenté.
- **CA-008** (RF-018, RB-004) — **Étant donné** un choix substantiel sans réponse de l'utilisateur, **quand** l'Agent poursuit, **alors** il ne choisit pas à sa place et l'élément dépendant reste en attente ou bloqué.
- **CA-009** (RF-007, RF-264) — **Étant donné** une instruction ponctuelle de l'utilisateur, **quand** l'Agent la traite, **alors** elle s'applique à cette demande et aucune règle n'est modifiée.
- **CA-010** (RF-008) — **Étant donné** une demande portant sur deux livrables, **quand** l'Agent l'analyse, **alors** il la détecte comme multiple, n'effectue aucun traitement coordonné et propose de la scinder en demandes distinctes et indépendantes.
- **CA-011** (RF-019, RF-029) — **Étant donné** un type de livrable sans modèle, **quand** l'Agent vérifie la faisabilité, **alors** il bloque, n'improvise aucune structure et sollicite la personne responsable.
- **CA-012** (RF-019 à RF-024) — **Étant donné** une demande comprise, **quand** l'Agent vérifie la faisabilité, **alors** le diagnostic couvre modèle, règles, informations, autorisations, exigences obligatoires, contradictions connues et conditions préalables.
- **CA-013** (RF-025) — **Étant donné** une condition indispensable non satisfaite, **quand** le diagnostic se termine, **alors** la partie concernée est bloquée avec un motif communicable.
- **CA-014** (RF-026, RF-244) — **Étant donné** un blocage, **quand** des opérations de diagnostic ou de vérification restent autorisées, **alors** l'Agent les poursuit.
- **CA-015** (RF-027) — **Étant donné** un diagnostic terminé, **quand** l'Agent le présente, **alors** il distingue réalisable, à clarifier et bloqué, avec les motifs.
- **CA-016** (RF-028, RB-068) — **Étant donné** une faisabilité acquise, **quand** la production démarre, **alors** les versions de modèle, de règles et de registre sont figées et enregistrées.
- **CA-017** (RF-021, RB-058, RT-005) — **Étant donné** des droits incertains sur une source, **quand** l'Agent doit l'exploiter, **alors** l'opération concernée est suspendue jusqu'à clarification.
- **CA-018** (RF-187, RF-258) — **Étant donné** une règle modifiée après la faisabilité, **quand** la demande se poursuit, **alors** elle reste liée aux versions figées.
- **CA-019** (RF-030) — **Étant donné** une demande de diagnostic seul, **quand** l'Agent l'exécute, **alors** il remet un diagnostic sans produire de livrable.
- **CA-020** (RF-025, RT-006) — **Étant donné** un blocage lié à une source protégée, **quand** l'Agent l'explique à un interlocuteur sans droit, **alors** le motif reste général.
- **CA-135** (RF-226 à RF-231) — **Étant donné** une demande en cours, **quand** l'utilisateur demande l'état, **alors** l'Agent indique étapes terminées, étapes en cours, motifs communicables, éléments attendus et prochaine action.
- **CA-136** (RF-232) — **Étant donné** plusieurs éléments à des états différents, **quand** l'Agent les présente, **alors** terminé, suspendu, bloqué, en attente de décision et finalisé sont distingués.
- **CA-137** (RF-233, RT-006) — **Étant donné** une information protégée, **quand** l'état d'avancement est présenté, **alors** elle n'y est pas exposée.
- **CA-138** (RF-234, RB-065) — **Étant donné** deux interlocuteurs de droits différents, **quand** ils demandent le motif d'un même blocage, **alors** chacun reçoit un motif adapté à ses droits.
- **CA-139** (RF-235, RB-117) — **Étant donné** une opération non aboutie, **quand** l'Agent communique, **alors** il n'annonce aucune réussite.
- **CA-140** (RF-236, RB-111) — **Étant donné** un message d'état, **quand** on le lit, **alors** il emploie les états fonctionnels et non les étapes internes.
- **CA-142** (RF-225) — **Étant donné** un utilisateur sans connaissance des modèles ni des règles, **quand** il formule sa demande, **alors** l'Agent la traite sans exiger cette connaissance.
- **CA-143** (RF-238) — **Étant donné** un utilisateur autorisé, **quand** il demande l'historique de sa demande, **alors** échanges et décisions lui sont restitués selon ses droits.
- **CA-144** (RB-120) — **Étant donné** un blocage, **quand** son motif est communiqué, **alors** il est formulé sans jargon technique.
- **CA-189** (RF-008, IN-04) — **Étant donné** une demande portant sur deux livrables, **quand** l'utilisateur confirme la scission, **alors** deux demandes indépendantes sont créées, chacune avec son propre cycle.
- **CA-190** (RF-017, RF-043, RB-026) — **Étant donné** une information fournie par l'utilisateur, **quand** l'Agent l'évalue, **alors** elle est QI-02 ; elle ne devient QI-01 que par règle du type ou décision explicite de la personne responsable pour la demande.

## 5. Exigences fonctionnelles liées (68) — une ligne chacune

Résumés seulement. Pour le texte complet et le contexte : `python tools/spec.py show RF-xxx`.

- IV-10 — Aucun message de l'Agent ne présente un état non atteint.
- RB-004 — L'Agent ne doit pas inventer une méthode de recherche, choisir arbitrairement un indicateur, modifier une définition ni résoudre librement une contradiction.
- RB-010 — **Pas d'apprentissage normatif implicite.** Une correction ponctuelle ne devient pas automatiquement une règle générale.
- RB-026 — Une information fournie par l'utilisateur est traitée comme une source identifiée, soumise aux mêmes évaluations ; son statut initial est QI-02 (RF-017).
- RB-058 — Si les droits applicables sont incertains, l'Agent suspend l'opération concernée jusqu'à clarification.
- RB-064 — Chaque profil ne voit que ce que ses droits lui permettent, y compris l'état d'avancement.
- RB-065 — Les motifs de blocage communicables varient selon le profil et les droits de l'interlocuteur.
- RB-068 — Chaque production reste liée aux sources, règles et modèles utilisés au moment de sa création.
- RB-109 — Conformité aux contrôles, approbation humaine et autorisation de diffuser sont trois statuts distincts.
- RB-111 — Les états fonctionnels ne se confondent ni avec les étapes internes de production ni avec les décisions d'approbation ou de diffusion.
- RB-117 — L'Agent n'annonce jamais la réussite d'une opération avant que les contrôles ou validations requis aient abouti.
- RB-120 — Les motifs de blocage sont formulés en termes compréhensibles par un utilisateur non technique.
- RB-121 — Au MVP, les échanges et livrables sont rédigés en français, sauf indication contraire du modèle.
- RF-001 — L'Agent doit accepter toute demande de livrable formulée en langage naturel par un utilisateur autorisé.
- RF-002 — L'Agent doit enregistrer chaque demande dès sa réception avec un identifiant stable, l'auteur, la date et l'heure, et le texte d'origine inchangé.
- RF-003 — L'Agent doit identifier le type de livrable demandé et le distinguer de son format de fichier.
- RF-006 — L'Agent doit déterminer les paramètres à partir du contexte autorisé et des règles applicables avant de les demander à l'utilisateur.
- RF-007 — L'Agent doit distinguer les instructions propres à la demande des règles permanentes, et ne jamais traiter une instruction ponctuelle comme une modification de règle.
- RF-008 — L'Agent doit détecter une demande portant sur plusieurs livrables. Au MVP, il n'effectue pas de traitement coordonné : il informe l'utilisateur et propose, sur confirm...
- RF-009 — L'Agent doit vérifier que l'utilisateur est autorisé à soumettre ce type de demande avant tout traitement de fond.
- RF-011 — L'Agent ne doit poser une question que lorsqu'une ambiguïté restante a une incidence significative sur la conformité ou la validité du livrable.
- RF-012 — L'Agent ne doit pas poser une question dont la réponse peut être déterminée par le contexte autorisé et les règles.
- RF-013 — L'Agent doit poser des questions ciblées plutôt que présenter systématiquement de longs formulaires.
- RF-014 — L'Agent doit indiquer, pour chaque question, en quoi la réponse conditionne le livrable.
- RF-015 — L'Agent doit hiérarchiser les questions : les bloquantes d'abord ; les non bloquantes sont regroupées ou différées.
- RF-016 — La demande doit passer à l'état En clarification dès qu'une question est posée ; l'Agent peut poursuivre les opérations indépendantes de la réponse.
- RF-017 — Une réponse de l'utilisateur doit être enregistrée comme information fournie par l'utilisateur, source identifiée de statut initial QI-02 (candidate), et jamais comme ...
- RF-018 — Si l'utilisateur ne répond pas ou si sa réponse reste ambiguë, l'Agent ne doit pas faire à sa place un choix substantiel ; l'élément dépendant reste en attente ou bloqué.
- RF-019 — Avant toute production, l'Agent doit vérifier l'existence d'un modèle documentaire et de règles applicables au type de livrable.
- RF-020 — L'Agent doit vérifier la disponibilité des informations nécessaires.
- RF-021 — L'Agent doit vérifier les autorisations d'accès et d'utilisation.
- RF-022 — L'Agent doit identifier les exigences obligatoires du livrable.
- RF-023 — L'Agent doit recenser les contradictions déjà identifiées.
- RF-024 — L'Agent doit vérifier les conditions préalables à la production.
- RF-025 — Si une condition indispensable n'est pas satisfaite, l'Agent doit bloquer la partie concernée et expliquer le motif communicable.
- RF-026 — L'Agent peut exécuter les opérations de diagnostic ou de vérification qui restent autorisées malgré un blocage.
- RF-027 — L'Agent doit produire un diagnostic de faisabilité structuré distinguant ce qui est réalisable, ce qui doit être clarifié et ce qui est bloqué, avec les motifs.
- RF-028 — L'Agent doit déterminer les versions applicables du modèle, des règles et du registre des sources, et les figer pour la demande.
- RF-029 — Lorsqu'aucun modèle n'existe pour le type demandé, l'Agent ne doit pas improviser de structure ; il bloque et sollicite la personne responsable.
- RF-030 — L'Agent doit pouvoir réaliser, à la demande de l'utilisateur, un diagnostic de faisabilité sans produire le livrable.
- RF-043 — Les informations fournies directement par l'utilisateur ou par pièces jointes doivent être traitées comme des informations à source identifiée (« fournie par l'utilisa...
- RF-163 — L'Agent ne doit jamais annoncer qu'un livrable est final, conforme, approuvé ou diffusable avant que les contrôles ou validations correspondants aient effectivement ab...
- RF-171 — Un livrable provisoire doit être explicitement marqué comme non finalisé, quel que soit son format.
- RF-187 — Une modification des règles ne doit pas modifier automatiquement les productions antérieures.
- RF-210 — L'annulation définitive doit être distincte de la suspension. Au MVP, elle exige une action explicite et une confirmation explicite, peut être demandée par l'auteur de...
- RF-225 — L'utilisateur doit pouvoir formuler sa demande en langage naturel sans connaître la structure interne (modèles, règles, étapes).
- RF-226 — L'utilisateur autorisé doit pouvoir obtenir à tout moment l'état de sa demande.
- RF-227 — L'Agent doit indiquer les étapes terminées.
- RF-228 — L'Agent doit indiquer les étapes en cours.
- RF-229 — L'Agent doit indiquer les motifs communicables des blocages.
- RF-230 — L'Agent doit indiquer les éléments attendus (de l'utilisateur, de la personne responsable ou d'un tiers).
- RF-231 — L'Agent doit indiquer la prochaine action.
- RF-232 — L'Agent doit distinguer les tâches terminées, suspendues, bloquées, en attente de décision et finalisées.
- RF-233 — L'Agent doit permettre de suivre l'avancement sans exposer d'informations protégées.
- RF-234 — L'Agent doit expliquer les blocages selon les droits d'accès de l'interlocuteur.
- RF-235 — L'Agent ne doit jamais annoncer la réussite d'une opération avant que les contrôles ou validations requis aient effectivement abouti (voir aussi RF-163).
- RF-236 — Les messages d'état doivent utiliser le vocabulaire des états fonctionnels (section 8) sans le confondre avec les étapes internes de production.
- RF-237 — Les statuts de conformité, d'approbation et de diffusion doivent toujours être présentés séparément.
- RF-238 — L'utilisateur doit pouvoir consulter, selon ses droits, l'historique des échanges et des décisions de sa demande.
- RF-244 — Pendant l'attente d'une décision, l'Agent poursuit les tâches de diagnostic, de vérification ou indépendantes qui restent autorisées.
- RF-258 — Une modification de règle ou de modèle n'affecte automatiquement ni les productions antérieures ni les demandes en cours.
- RF-264 — Une correction ponctuelle apportée par un utilisateur ne doit jamais devenir automatiquement une règle générale.
- RF-265 — Aucune règle, préférence ou modèle ne doit être modifié implicitement à partir de l'historique des interactions.
- RT-005 — Lorsque les droits sont incertains, l'Agent suspend l'opération concernée jusqu'à clarification.
- RT-006 — Aucune information protégée ne doit être révélée par l'état d'avancement, les motifs de blocage, les questions de clarification ou les messages d'erreur.
- RT-017 — L'Agent doit appliquer un principe de minimisation : ne reprendre que les données nécessaires, autorisées pour l'usage prévu et permises pour les destinataires.
- RT-034 — Chaque contrôle et chacun de ses résultats est enregistré, y compris lors des rejeux.
- RT-063 — Rien n'est écrasé silencieusement.

## 6. À lire à la demande (ne rien lire d'autre au départ)

| Quoi | Commande | Pourquoi |
|---|---|---|
| Spéc. technique 10.1 | `python tools/spec.py section T 10.1` | Orchestration |
| Spéc. technique 10.2 | `python tools/spec.py section T 10.2` | É1 Compréhension |
| Spéc. technique 10.3 | `python tools/spec.py section T 10.3` | É2 Faisabilité |
| Spéc. technique 11.1 | `python tools/spec.py section T 11.1` | Passerelle LLM |
| Spéc. technique 11.2 | `python tools/spec.py section T 11.2` | Rôles de modèles |
| Spéc. technique 11.4 | `python tools/spec.py section T 11.4` | Catalogue des tâches LT |
| Spéc. technique 11.9 | `python tools/spec.py section T 11.9` | Garde des messages |
| Spéc. technique 13.1 | `python tools/spec.py section T 13.1` | Conventions d'API |
| Spéc. technique Annexe-B | `python tools/spec.py section T Annexe-B` | Schémas LT-01, LT-02 |
| Spéc. technique Annexe-D | `python tools/spec.py section T Annexe-D` | Prompts PRM-01 |
| Spéc. fonctionnelle UC-001 | `python tools/spec.py section F UC-001` | Fiche du cas d’usage |
| Spéc. fonctionnelle UC-002 | `python tools/spec.py section F UC-002` | Fiche du cas d’usage |
| Spéc. fonctionnelle UC-003 | `python tools/spec.py section F UC-003` | Fiche du cas d’usage |
| Spéc. fonctionnelle UC-023 | `python tools/spec.py section F UC-023` | Fiche du cas d’usage |
| Spéc. fonctionnelle Annexe-C | `python tools/spec.py section F Annexe-C` | Motifs de blocage MB-01 à MB-17 |

## 7. Critères de sortie du jalon

TST-01 et TST-02 verts ; suivi d'avancement avec statuts séparés ; squelette de bout en bout fonctionnel ; aucune annonce d'état non atteint (EVL-H partielle).

## 8. Rappels (extraits d'AGENTS.md)

- Tests d'acceptation d'abord ; `make check` doit passer ; ne jamais affaiblir un test, une contrainte ou un déclencheur.
- Ambiguïté de spécification → question dans `docs/reports/QUESTIONS.md`, jamais d'invention.
- À la fin d'une tranche : mettre à jour `docs/reports/PROGRESS.md`.

