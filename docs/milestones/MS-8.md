# Jalon MS-8 — Durcissement et pilote

> Brief généré par `tools/gen_briefs.py` — ne pas modifier à la main. Pour tout détail : `python tools/spec.py show <ID>`.

## 1. Objectif

Sécurité, observabilité, évaluations nocturnes, performance, sauvegardes, accessibilité, tests de bout en bout, revue de sécurité.

**À savoir.** Les questions QT-04, QT-07 doivent être tranchées avant toute donnée réelle (PL-05).

## 2. Périmètre

- Cas d'usage : — (jalon transversal)
- Suites de tests visées : TST-19, TST-20
- Hors périmètre de ce jalon : Évolutions V2.

## 3. Exigences techniques à réaliser (70)

- **ET-267** ([T] · MVP) — Un `EmbeddingPort` isole le modèle d'embeddings ; les vecteurs portent la version du modèle ; un changement impose un recalcul tracé.  
  _Réalise : EM-01, EM-02 · MOD-21_
- **ET-268** ([T] · MVP) — Les tâches LT-01 à LT-11 sont implémentées avec les schémas de l'Annexe B.  
  _Réalise : 11.4 · MOD-21_
- **ET-269** ([T] · MVP) — L'orchestration de A6 utilise un juge différent du générateur.  
  _Réalise : 11.5 · MOD-21_
- **ET-270** ([T] · MVP) — Les suites d'évaluation EVL-A à EVL-H existent avec des jeux de données figés et versionnés.  
  _Réalise : 11.8 · ADR-017_
- **ET-271** ([T] · MVP) — Les évaluations tournent en intégration continue sur enregistrements rejoués.  
  _Réalise : EL-01 · ADR-017_
- **ET-272** ([T] · MVP) — Les évaluations tournent chaque nuit en appels réels ; une dérive déclenche une alerte.  
  _Réalise : EL-01 · ADR-017_
- **ET-273** ([T] · MVP) — Les seuils d'évaluation sont des conditions de mise en production.  
  _Réalise : EL-03 · ADR-017_
- **ET-274** ([T] · MVP) — La version de modèle du fournisseur est épinglée ; toute nouvelle version exige la réussite des évaluations avant adoption.  
  _Réalise : PT-11 · MOD-21_
- **ET-275** ([F] · MVP) — La garde des messages (MG-01 à MG-03) est couverte par EVL-H.  
  _Réalise : IV-10 · MOD-18_
- **ET-276** ([F] · MVP) — Les sorties contenant des identifiants de sources non autorisées sont rejetées et couvertes par EVL-G.  
  _Réalise : RT-007, RT-008 · MOD-21_
- **ET-305** ([T] · MVP) — L'interface respecte WCAG 2.2 AA ; un contrôle d'accessibilité automatisé tourne en intégration continue.  
  _Réalise : UI-08 · CMP-01_
- **ET-306** ([T] · MVP) — Les textes sont externalisés ; le français est la langue par défaut.  
  _Réalise : RB-121 · CMP-01_
- **ET-307** ([T] · MVP) — Des tests de bout en bout couvrent les parcours PA-01 à PA-06 de la spécification fonctionnelle.  
  _Réalise : PA-01 à PA-06 · ADR-017_
- **ET-308** ([T] · MVP) — Des budgets de taille de page et un chargement progressif tiennent compte des connexions lentes.  
  _Réalise : UI-09 · CMP-01_
- **ET-309** ([T] · MVP) — Les journaux sont en JSON structuré avec identifiants de corrélation (`request_id`, `step`, `trace_id`).  
  _Réalise : PT-15 · ADR-015_
- **ET-310** ([T] · MVP) — Les traces OpenTelemetry couvrent API, job et appel LLM.  
  _Réalise : PT-15 · ADR-015_
- **ET-311** ([T] · MVP) — Les métriques incluent durée des étapes, profondeur des files, taux d'échec, coût LLM, taux de rejet A5 et A6.  
  _Réalise : RT-068 · ADR-015_
- **ET-312** ([T] · MVP) — Des alertes existent pour : échec de chaîne ou de sceau, file bloquée, coupe-circuit ouvert, budget dépassé, taux de rejet anormal.  
  _Réalise : RT-065, RT-068 · ADR-015_
- **ET-313** ([T] · MVP) — Des tableaux de bord d'exploitation sont fournis.  
  _Réalise : — · ADR-015_
- **ET-314** ([T] · MVP) — L'intégration continue exécute : formatage, types, tests unitaires, de propriétés, d'intégration, migrations, traçabilité de la spécification, analyses de sécurité, construction d'image.  
  _Réalise : ADR-017 · ADR-017_
- **ET-315** ([T] · MVP) — Le déploiement vers la préproduction est automatique ; la promotion en production est manuelle.  
  _Réalise : — · ADR-016_
- **ET-316** ([T] · MVP) — Les secrets sont conservés dans un coffre et rotés ; ils n'apparaissent jamais dans les journaux.  
  _Réalise : RT-025 · ADR-016_
- **ET-317** ([T] · MVP) — L'infrastructure de préproduction et de production est décrite en code.  
  _Réalise : — · ADR-016_
- **ET-318** ([T] · MVP) — PostgreSQL géré avec restauration à un instant donné et sauvegardes chiffrées.  
  _Réalise : RT-061 · ADR-016_
- **ET-319** ([T] · MVP) — Des objectifs de reprise (RPO et RTO) sont documentés et testés.  
  _Réalise : NF-10 · ADR-016_
- **ET-320** ([T] · MVP) — Un test de restauration trimestriel vérifie ensuite la chaîne du journal et les sceaux.  
  _Réalise : RT-065 · ADR-016_
- **ET-321** ([T] · MVP) — Le stockage objet a versionnement et verrouillage activés.  
  _Réalise : ADR-010 · ADR-016_
- **ET-322** ([T] · MVP) — Un service de gestion de clés porte les clés de signature et de chiffrement.  
  _Réalise : SL-01 · ADR-022_
- **ET-323** ([T] · MVP) — Des procédures d'exploitation couvrent : échec de chaîne, file bloquée, fournisseur LLM indisponible, source indisponible, restauration.  
  _Réalise : — · ADR-016_
- **ET-324** ([T] · MVP) — La gestion des incidents définit gravités, journal et revue après incident.  
  _Réalise : — · ADR-016_
- **ET-325** ([T] · MVP) — Les dépendances sont mises à jour selon une cadence définie, avec un délai de carence avant adoption des versions très récentes.  
  _Réalise : TH-14 · ADR-016_
- **ET-326** ([T] · MVP) — Un environnement de démonstration avec données fictives est disponible.  
  _Réalise : — · ADR-016_
- **ET-327** ([T] · MVP) — Le modèle de menaces TH-01 à TH-20 (17.1) est tenu à jour à chaque évolution d'architecture.  
  _Réalise : — · 17_
- **ET-328** ([T] · MVP) — Tout trafic est chiffré en transit (TLS ≥ 1.2).  
  _Réalise : RT-006 · 17_
- **ET-329** ([T] · MVP) — Base, objets et sauvegardes sont chiffrés au repos.  
  _Réalise : RT-001 · 17_
- **ET-330** ([T] · MVP) — Les secrets sont en coffre, rotés, absents des journaux et du dépôt.  
  _Réalise : RT-025 · 17_
- **ET-331** ([T] · MVP) — Les entrées sont validées strictement (types, tailles, formats).  
  _Réalise : — · 17_
- **ET-332** ([T] · MVP) — L'accès à la base utilise exclusivement des requêtes paramétrées.  
  _Réalise : — · 17_
- **ET-333** ([T] · MVP) — Les en-têtes de sécurité (CSP, HSTS, etc.) et un CORS restrictif sont appliqués.  
  _Réalise : — · 17_
- **ET-334** ([T] · MVP) — La protection contre la falsification de requêtes est active selon le mode de session.  
  _Réalise : — · 17_
- **ET-335** ([T] · MVP) — Les sessions ont une durée limitée et sont révocables.  
  _Réalise : RT-002 · 17_
- **ET-336** ([T] · MVP) — Les rôles de base de données et d'infrastructure suivent le principe du moindre privilège.  
  _Réalise : RT-002 · 17_
- **ET-337** ([T] · MVP) — Les analyseurs de documents et le convertisseur n'ont aucun accès réseau.  
  _Réalise : FS-02 · 17_
- **ET-338** ([T] · MVP) — Les appels sortants sont restreints par liste blanche (protection SSRF).  
  _Réalise : IG-04 · 17_
- **ET-339** ([T] · MVP) — Les fichiers sont analysés par antivirus ; les fichiers suspects sont mis en quarantaine.  
  _Réalise : FS-01 · 17_
- **ET-340** ([T] · MVP) — Les secrets présents dans les documents (clés, mots de passe) sont détectés et masqués avant tout appel LLM.  
  _Réalise : RT-017 · 17_
- **ET-341** ([F] · MVP) — Les actions sensibles (décisions, rôles, gouvernance, restauration) sont journalisées pour audit.  
  _Réalise : RT-033 · 17_
- **ET-342** ([T] · MVP) — L'approbation d'un artefact de gouvernance exige une confirmation en deux étapes et déclenche une alerte, la séparation des tâches ne pouvant reposer sur une seconde personne.  
  _Réalise : RB-097, RB-098 · MOD-02_
- **ET-343** ([F] · MVP) — Les identifiants sont non devinables (UUID) ; l'API ne permet pas l'énumération.  
  _Réalise : RT-008 · 17_
- **ET-344** ([F] · MVP) — Les réponses sont identiques pour « n'existe pas » et « non autorisé » (pas d'oracle d'existence).  
  _Réalise : RT-008 · MOD-20_
- **ET-345** ([T] · MVP) — La détection d'abus (débit, volumes inhabituels) alerte l'exploitation.  
  _Réalise : — · 17_
- **ET-346** ([T] · MVP) — Les dépendances sont analysées en continu (vulnérabilités, licences) et les images conteneurs sont scannées.  
  _Réalise : — · 17_
- **ET-347** ([T] · MVP) — Une liste de composants (SBOM) est produite à chaque build ; les dépendances sont épinglées par empreinte.  
  _Réalise : — · 17_
- **ET-348** ([T] · MVP) — Une revue de sécurité précède le pilote ; un test d'intrusion précède toute utilisation avec des données réelles sensibles.  
  _Réalise : — · 17_
- **ET-349** ([V] · MVP) — Un registre de traitements, les accords avec les sous-traitants, les durées de conservation et les procédures d'exercice des droits sont tenus selon le cadre juridique applicable.  
  _Réalise : RT-017 à RT-026 · 17_
- **ET-350** ([V] · MVP) — La région d'hébergement et celle du traitement LLM sont choisies pour la résidence des données (QT-04).  
  _Réalise : — · 17_
- **ET-351** ([T] · MVP) — Les sauvegardes sont chiffrées avec des clés distinctes de celles des données.  
  _Réalise : — · 17_
- **ET-352** ([T] · MVP) — Un plan de réponse aux incidents de sécurité est rédigé et exercé.  
  _Réalise : — · 17_
- **ET-373** ([V] · MVP) — Les cibles NF-01 à NF-12 (20.1) sont documentées et revues après le pilote.  
  _Réalise : QO-019 · 20_
- **ET-374** ([V] · MVP) — La latence de lecture de l'API vise un p95 inférieur à 500 ms hors flux.  
  _Réalise : NF-01 · 20_
- **ET-375** ([V] · MVP) — L'accusé de réception d'une demande est renvoyé en moins de 2 secondes.  
  _Réalise : NF-02 · 20_
- **ET-376** ([V] · MVP) — La durée de production d'un livrable type est mesurée et exprimée en minutes ; aucun engagement avant mesure.  
  _Réalise : NF-03 · 20_
- **ET-377** ([V] · MVP) — Un budget de jetons par demande type est défini et surveillé.  
  _Réalise : BU-01 · 20_
- **ET-378** ([V] · MVP) — Le nombre de demandes simultanées et la concurrence des jobs sont dimensionnés selon HT-01.  
  _Réalise : NF-04 · 20_
- **ET-379** ([V] · MVP) — La taille de la base et sa croissance sont estimées et suivies.  
  _Réalise : NF-05 · 20_
- **ET-380** ([V] · MVP) — Le stockage objet est dimensionné pour documents, versions et rapports.  
  _Réalise : NF-06 · 20_
- **ET-381** ([V] · MVP) — La disponibilité cible et les fenêtres de maintenance sont définies.  
  _Réalise : NF-09 · 20_
- **ET-382** ([V] · MVP) — Les objectifs RPO et RTO sont définis.  
  _Réalise : NF-10 · 20_
- **ET-383** ([V] · MVP) — Un coût mensuel cible est défini ; une alerte signale tout dépassement.  
  _Réalise : NF-11 · 20_
- **ET-384** ([V] · MVP) — Les mesures réelles du pilote remplacent les hypothèses.  
  _Réalise : NF-12 · 20_

## 4. Critères d'acceptation

Pas de CA propres à ce jalon : voir les critères de sortie ci-dessous.

## 5. Exigences fonctionnelles liées (23) — une ligne chacune

Résumés seulement. Pour le texte complet et le contexte : `python tools/spec.py show RF-xxx`.

- IV-10 — Aucun message de l'Agent ne présente un état non atteint.
- RB-097 — Une seule personne responsable est habilitée.
- RB-098 — Elle seule arbitre les décisions sensibles, résout les conflits que les règles ne résolvent pas, autorise les exceptions, approuve les changements de règles et prend l...
- RB-121 — Au MVP, les échanges et livrables sont rédigés en français, sauf indication contraire du modèle.
- RT-001 — Chaque source, information, livrable et rapport doit porter une classification de confidentialité définie par les règles ou le registre.
- RT-002 — L'Agent doit appliquer les droits d'accès de chaque utilisateur à chaque objet (demande, livrable, rapport, traçabilité, historique).
- RT-006 — Aucune information protégée ne doit être révélée par l'état d'avancement, les motifs de blocage, les questions de clarification ou les messages d'erreur.
- RT-007 — Les explications de refus restent générales lorsque le détail révélerait l'existence, l'identité ou le contenu d'une source protégée.
- RT-008 — L'Agent ne confirme ni n'infirme l'existence d'une source à laquelle l'interlocuteur n'a pas accès.
- RT-017 — L'Agent doit appliquer un principe de minimisation : ne reprendre que les données nécessaires, autorisées pour l'usage prévu et permises pour les destinataires.
- RT-018 — Les données non permises doivent être masquées ou exclues selon les règles applicables.
- RT-019 — Les catégories de données personnelles et sensibles sont fournies par les règles du type de livrable ; sans règle de minimisation applicable, la donnée n'est pas reprise.
- RT-020 — Le rapport de traçabilité doit référencer une information masquée sans en révéler le contenu aux lecteurs non autorisés.
- RT-021 — L'Agent ne doit pas déduire ou reconstituer des données masquées à partir d'autres éléments du livrable.
- RT-022 — Si les règles de minimisation ne couvrent pas un cas, l'élément concerné est suspendu et traité comme une décision non couverte.
- RT-023 — Si un masquage ou une exclusion rend un élément obligatoire manquant ou incohérent, l'Agent bloque l'élément et sollicite une décision.
- RT-024 — Les données personnelles des utilisateurs (auteur d'une demande, destinataires) suivent également le principe de minimisation.
- RT-025 — Les journaux enregistrent l'usage de données sensibles sans en dupliquer inutilement le contenu.
- RT-026 — La conservation des données personnelles est limitée par les règles de conservation.
- RT-033 — Chaque décision humaine est enregistrée avec son décideur.
- RT-061 — Au MVP, aucune suppression automatique : l'historique et les états suspendus sont conservés jusqu'à décision explicite de la personne responsable, qui peut fixer des r...
- RT-065 — Un audit doit pouvoir reconstituer pourquoi un livrable est ce qu'il est : règles, sources, décisions, contrôles.
- RT-068 — Les défaillances de l'Agent en cours d'exécution (opération interrompue sans fin normale) sont consignées.

## 6. À lire à la demande (ne rien lire d'autre au départ)

| Quoi | Commande | Pourquoi |
|---|---|---|
| Spéc. technique 17 | `python tools/spec.py section T 17` | Sécurité |
| Spéc. technique 18 | `python tools/spec.py section T 18` | Exploitation |
| Spéc. technique 19 | `python tools/spec.py section T 19` | Stratégie de test |
| Spéc. technique 20 | `python tools/spec.py section T 20` | Performance |
| Spéc. technique Annexe-H | `python tools/spec.py section T Annexe-H` | Vérifications avant gel |
| Spéc. technique 11.6 | `python tools/spec.py section T 11.6` | Défense contre l'injection |
| Spéc. technique 11.8 | `python tools/spec.py section T 11.8` | Évaluation des LLM |

## 7. Critères de sortie du jalon

TST-19 et TST-20 verts ; liste de préparation au pilote signée ; mesures NF relevées ; aucune donnée réelle avant la fin de ce jalon.

## 8. Rappels (extraits d'AGENTS.md)

- Tests d'acceptation d'abord ; `make check` doit passer ; ne jamais affaiblir un test, une contrainte ou un déclencheur.
- Ambiguïté de spécification → question dans `docs/reports/QUESTIONS.md`, jamais d'invention.
- À la fin d'une tranche : mettre à jour `docs/reports/PROGRESS.md`.

