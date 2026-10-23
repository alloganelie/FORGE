# Jalon MS-0 — Fondations

> Brief généré par `tools/gen_briefs.py` — ne pas modifier à la main. Pour tout détail : `python tools/spec.py show <ID>`.

## 1. Objectif

Mettre en place le dépôt, l'intégration continue, les images, la base de données et ses migrations, la configuration, le journal chaîné, le moteur d'états généré depuis la spécification fonctionnelle, l'outil de traçabilité spécification ↔ tests et les règles de dépendance. Aucune fonction métier dans ce jalon.

**À savoir.** `make check`, `make spec-trace` et `make gen-transitions` n'existent pas encore : les créer dans ce jalon (ET-314, ET-353 à ET-356, ET-035). `make spec-trace` doit écrire un tableau de bord lisible par un non-développeur : `docs/reports/spec-trace.html` (ouvrable dans un navigateur) et `docs/reports/spec-trace.md`, avec : CA verts / rouges / ignorés / sans test, exigences sans test, tests orphelins, transitions non couvertes, et l'évolution par rapport au jalon précédent (le Product Owner s'en sert pour la checklist, point PO-01).

## 2. Périmètre

- Cas d'usage : — (jalon transversal)
- Suites de tests visées : TST-18 (invariants d'états)
- Hors périmètre de ce jalon : Tout cas d'usage métier ; tout appel à un LLM ; toute interface au-delà d'un squelette.

## 3. Exigences techniques à réaliser (55)

- **ET-001** ([T] · MVP) — Le backend est écrit en Python (≥ 3.13) avec typage strict ; l'analyse de types (mypy ou pyright en mode strict) est bloquante en intégration continue.  
  _Réalise : PT-18 · ADR-002_
- **ET-002** ([T] · MVP) — L'API est construite avec FastAPI et Pydantic v2 ; le contrat OpenAPI est généré et versionné dans le dépôt.  
  _Réalise : AP-01 · ADR-002, MOD-23_
- **ET-003** ([T] · MVP) — L'accès aux données utilise SQLAlchemy 2 (typé), Alembic pour les migrations et psycopg 3 comme pilote.  
  _Réalise : DC-01 à DC-08 · ADR-002_
- **ET-004** ([T] · MVP) — Les dépendances sont gérées par un seul outil avec fichier de verrouillage ; les versions sont épinglées ; chaque mise à jour passe la chaîne d'intégration complète.  
  _Réalise : — · ADR-002, ADR-017_
- **ET-005** ([T] · MVP) — Les règles de dépendance DR-01 à DR-07 sont vérifiées par un outil de contrôle d'imports en intégration continue ; une violation fait échouer le build.  
  _Réalise : PT-13 · ADR-001_
- **ET-006** ([T] · MVP) — Le code est organisé en 23 modules (5.1) à façades explicites ; aucun module n'accède aux tables d'un autre.  
  _Réalise : PT-12 · ADR-001_
- **ET-007** ([T] · MVP) — Une seule image applicative est déployée en deux rôles (API et travailleur), choisis par configuration.  
  _Réalise : PT-12 · ADR-001_
- **ET-008** ([T] · MVP) — La configuration provient de variables d'environnement validées au démarrage (schéma Pydantic) ; aucune valeur secrète n'est dans le dépôt ; une configuration invalide empêche le démarrage.  
  _Réalise : — · MOD-23_
- **ET-009** ([T] · MVP) — Les images Docker sont construites en plusieurs étapes, s'exécutent sans privilèges administrateur et produisent une liste de composants (SBOM).  
  _Réalise : ET-347 · ADR-016_
- **ET-010** ([T] · MVP) — Quatre environnements existent : local (orchestrateur de conteneurs), intégration continue, préproduction, production ; leurs configurations sont séparées.  
  _Réalise : — · ADR-016_
- **ET-011** ([T] · MVP) — Le déploiement s'effectue sur une plateforme de conteneurs gérée, dans la région retenue (QT-04) ; les migrations de base sont appliquées avant la mise en service de la nouvelle version.  
  _Réalise : — · ADR-016_
- **ET-012** ([T] · MVP) — Le retour arrière est possible : images versionnées, migrations en « étendre puis contracter » (jamais de suppression de colonne dans la même version que l'arrêt de son usage).  
  _Réalise : — · ADR-016_
- **ET-013** ([T] · MVP) — PostgreSQL (≥ 17) est l'unique système d'enregistrement ; les extensions pgvector, pgcrypto et pg_trgm sont installées ; la version est figée par environnement.  
  _Réalise : RT-062 · ADR-003_
- **ET-014** ([T] · MVP) — Les identifiants sont des UUIDv7 générés par l'application.  
  _Réalise : DC-01 · MOD-23_
- **ET-015** ([T] · MVP) — Toutes les tables métier portent `workspace_id`.  
  _Réalise : HT-04 · ADR-021_
- **ET-016** ([T] · MVP) — L'horloge est injectée par un port ; le domaine ne lit jamais l'heure système.  
  _Réalise : DC-03 · MOD-23_
- **ET-017** ([T] · MVP) — Les types énumérés de la base sont **générés** depuis la spécification fonctionnelle (ST, QI, LC, AN, RC, DH, AU) ; un test compare leur contenu aux identifiants de la spécification.  
  _Réalise : DC-05 · MOD-04_
- **ET-018** ([F] · MVP) — Les invariants inter-axes (IV-05, IV-12, IV-14, RB-114) sont portés par des contraintes `CHECK` de la base (6.5).  
  _Réalise : IV-05, IV-12, IV-14, RB-114 · ADR-005_
- **ET-019** ([F] · MVP) — Aucun `DELETE` métier n'est autorisé ; la seule suppression est la procédure de purge, qui écrit un événement minimal.  
  _Réalise : RT-064, DC-04 · MOD-23_
- **ET-020** ([T] · MVP) — Les migrations sont versionnées, relues, et testées sur une copie de données (avant/après).  
  _Réalise : ET-362 · ADR-003_
- **ET-021** ([F] · MVP) — La table `ledger_events` est en ajout seul : une mise à jour ou une suppression lève une exception (déclencheur).  
  _Réalise : RT-062, RT-063 · ADR-004, MOD-19_
- **ET-022** ([F] · MVP) — Chaque événement contient le hachage du précédent de sa demande ; le hachage est calculé par l'application sur une sérialisation canonique (RFC 8785) ; un déclencheur vérifie la continuité (`request_seq`, `prev_hash`).  
  _Réalise : RT-035, RT-036, RT-062 · ADR-004_
- **ET-023** ([F] · MVP) — Toute écriture métier et son événement de journal sont validés dans **la même transaction** par une fonction unique (`ledger.append`).  
  _Réalise : RT-035 · ADR-004_
- **ET-024** ([F] · MVP) — La projection `state_changes` est alimentée dans la même transaction ; elle contient transition, acteur, raison interne et raison communicable.  
  _Réalise : RT-035 · MOD-04_
- **ET-025** ([F] · MVP) — Une tâche périodique recalcule la chaîne du journal et signale tout écart (alerte de sécurité).  
  _Réalise : RT-065 · ADR-004_
- **ET-026** ([T] · MVP) — Le numéro `request_seq` est attribué sans trou, sous verrou de ligne de la demande.  
  _Réalise : RT-036 · ADR-004_
- **ET-027** ([F] · MVP) — Les tables `control_results` et `documents` sont immuables (déclencheur).  
  _Réalise : RT-057, RF-040 · MOD-12, MOD-06_
- **ET-028** ([F] · MVP) — Les versions finalisées et leurs atomes sont protégés par déclencheurs : seuls les axes A, D et le passage Finalisée → Remplacée sont modifiables.  
  _Réalise : RB-067, RF-166 · MOD-11_
- **ET-029** ([F] · MVP) — La sécurité au niveau des lignes est **activée et forcée** sur toutes les tables liées à une demande ; le rôle applicatif n'est pas propriétaire des tables.  
  _Réalise : RT-002, RT-013 · ADR-008_
- **ET-035** ([F] · MVP) — Les transitions sont définies en YAML, **générées** depuis la section 8 de la spécification fonctionnelle par un outil, puis versionnées ; aucune transition n'existe seulement dans le code.  
  _Réalise : TR-R-01 à TR-E-11 · ADR-005_
- **ET-036** ([F] · MVP) — Un moteur unique applique les transitions ; aucune écriture de colonne d'état hors moteur (règle DR-03, déclencheur de base).  
  _Réalise : IV-01, IV-02 · MOD-04_
- **ET-037** ([F] · MVP) — L'application d'une transition suit l'algorithme transactionnel de 7.4 (verrou, version, existence, acteur, politique, gardes, effets, journal, jobs).  
  _Réalise : PT-07 · MOD-04_
- **ET-038** ([T] · MVP) — Les écritures concurrentes sont arbitrées par `row_version` ; un conflit est signalé par une erreur 412.  
  _Réalise : CC-04 · MOD-04_
- **ET-039** ([T] · MVP) — Chaque garde du registre (7.3) est une fonction pure, testée seule.  
  _Réalise : 7.3 · MOD-04_
- **ET-040** ([F] · MVP) — Les prérequis inter-axes (8.9.3 fonctionnel) sont implémentés **à la fois** comme gardes et comme contraintes de base.  
  _Réalise : IV-02, IV-12, IV-14 · MOD-04_
- **ET-041** ([F] · MVP) — Les colonnes `waiting_origin` et `suspended_from` conservent l'état d'origine ; la fonction `resume_target()` est pure.  
  _Réalise : TR-R-13, 14, 20, 23 à 27 · MOD-04_
- **ET-042** ([T] · MVP) — Les effets déclaratifs (`set`, `clear`, `emit`, `job`) sont exécutés dans la transaction (motif « boîte d'envoi »).  
  _Réalise : PT-07 · MOD-04_
- **ET-043** ([F] · MVP) — Un test à états aléatoires (Hypothesis) vérifie IV-01 à IV-15 après chaque pas ; il s'exécute à chaque intégration continue.  
  _Réalise : IV-01 à IV-15 · ADR-017_
- **ET-044** ([T] · MVP) — Un outil vérifie que **chaque transition** TR-xx est exercée par au moins un test ; tout écart fait échouer le build.  
  _Réalise : ST, TR · ADR-017_
- **ET-045** ([T] · MVP) — Les commandes sont idempotentes par `Idempotency-Key` ; les résultats sont conservés au moins 24 heures.  
  _Réalise : PT-08 · MOD-23_
- **ET-046** ([T] · MVP) — Les étapes du pipeline sont enregistrées dans `step_runs` avec clé `(request_id, step, input_hash)`.  
  _Réalise : CC-02, PT-08 · MOD-04_
- **ET-047** ([T] · MVP) — Un verrou consultatif par demande garantit qu'une seule étape est active.  
  _Réalise : CC-01 · MOD-04_
- **ET-048** ([T] · MVP) — Une étape interrompue est relancée après expiration de son bail ; ses effets partiels sont transactionnels ou idempotents.  
  _Réalise : CC-03, RF-199 · MOD-04_
- **ET-049** ([F] · MVP) — Une entrée modifiée marque `invalidated` les `step_runs` dépendants et replanifie le strict nécessaire.  
  _Réalise : RF-207, RF-208 · MOD-04_
- **ET-050** ([T] · MVP) — Les enchaînements de jobs sont décrits par des règles de planification déclaratives (événement → job).  
  _Réalise : 10.1 · MOD-23_
- **ET-051** ([T] · MVP) — La file de jobs en base fournit reprise, priorités, files séparées (courte, LLM, rendu) et concurrence bornée par file.  
  _Réalise : PT-08 · ADR-005_
- **ET-052** ([F] · MVP) — Une suspension envoie un signal d'arrêt coopératif ; les jobs non terminés dans le délai sont invalidés.  
  _Réalise : RF-201, CL-032 · MOD-04_
- **ET-353** ([T] · MVP) — Un outil de traçabilité lit les identifiants fonctionnels et techniques et calcule la couverture.  
  _Réalise : PT-14 · ADR-017_
- **ET-354** ([T] · MVP) — Chaque CA a au moins un test d'acceptation étiqueté de son identifiant ; sinon le build échoue.  
  _Réalise : CA-001 à CA-195 · ADR-017_
- **ET-355** ([T] · MVP) — Chaque RF, RB et RT est référencé par au moins un test ou une justification de non-testabilité.  
  _Réalise : PT-14 · ADR-017_
- **ET-356** ([T] · MVP) — Un test portant sur un identifiant inexistant fait échouer le build.  
  _Réalise : PT-14 · ADR-017_
- **ET-357** ([T] · MVP) — La pyramide de tests comprend : unitaires (domaine pur), propriétés, intégration, acceptation, de bout en bout.  
  _Réalise : ADR-017 · ADR-017_
- **ET-358** ([T] · MVP) — Les tests d'invariants utilisent une base PostgreSQL réelle ; la base n'est jamais simulée pour les invariants.  
  _Réalise : ET-018, ET-021 · ADR-017_
- **ET-359** ([T] · MVP) — Des tests de propriétés couvrent états, autorisations, calculs, A5 et classification.  
  _Réalise : ET-043, ET-077, ET-107 · ADR-017_
- **ET-372** ([T] · MVP) — Un tableau de bord « spécification ↔ tests » est généré à chaque build pour le Product Owner.  
  _Réalise : PT-14 · ADR-017_

## 4. Critères d'acceptation

Pas de CA propres à ce jalon : voir les critères de sortie ci-dessous.

## 5. Exigences fonctionnelles liées (32) — une ligne chacune

Résumés seulement. Pour le texte complet et le contexte : `python tools/spec.py show RF-xxx`.

- IV-01 — À tout instant, une demande a exactement un état sur l'axe R ; chaque version a exactement un état sur chacun des axes C, A, D, V.
- IV-02 — Les axes C, A et D sont indépendants : aucun statut n'est déduit d'un autre. Un prérequis (par exemple une version finalisée avant approbation) conditionne la possibil...
- IV-03 — Une version Finalisée est immuable.
- IV-04 — Une demande Finalisée ou Annulée définitivement ne change plus d'état.
- IV-05 — Une demande ne devient Finalisée que si elle dispose d'une version à l'état Conforme.
- IV-06 — Une demande Suspendue n'est jamais Finalisée.
- IV-07 — Un élément Bloqué n'est jamais livré comme s'il était produit.
- IV-08 — Les états fonctionnels ne se confondent pas avec les étapes internes de production.
- IV-09 — Les statuts d'approbation et de diffusion ne sont attribués que par décision humaine (hors constat « Non requise »).
- IV-10 — Aucun message de l'Agent ne présente un état non atteint.
- IV-11 — L'approbation et la diffusion ne modifient jamais l'état de l'axe C ; seule l'exécution des contrôles le modifie.
- IV-12 — Une version non finalisée n'est ni approuvable ni diffusable (MVP).
- IV-13 — Une version n'est finalisée que si tous ses éléments obligatoires sont « Contrôlé conforme » ou « Non applicable ».
- IV-14 — Une version dont l'approbation est Refusée ou En attente ne peut pas passer à Diffusion autorisée.
- IV-15 — La finalisation n'attribue ni approbation ni autorisation de diffuser.
- RB-067 — Les livrables existants sont immuables.
- RB-114 — L'autorisation de diffusion ne peut porter que sur une version finalisée (donc conforme) dont l'approbation est « Approuvée » ou « Non requise ». La diffusion d'une ve...
- RF-040 — L'Agent doit conserver les informations mobilisées dans leur forme d'origine, distincte des versions transformées.
- RF-166 — Une version finalisée devient immuable.
- RF-199 — L'Agent doit pouvoir suspendre une demande à l'initiative de l'utilisateur.
- RF-201 — À la suspension, l'Agent doit arrêter les opérations.
- RF-207 — À la reprise, l'Agent doit conserver les éléments toujours valides.
- RF-208 — À la reprise, l'Agent doit réexécuter les opérations affectées et les contrôles nécessaires.
- RT-002 — L'Agent doit appliquer les droits d'accès de chaque utilisateur à chaque objet (demande, livrable, rapport, traçabilité, historique).
- RT-013 — Un destinataire n'accède qu'aux éléments autorisés pour lui.
- RT-035 — Chaque changement d'état (demande, conformité, approbation, diffusion, version) est horodaté, avec son auteur (humain ou Agent) et son motif.
- RT-036 — L'historique permet de reconstituer chronologiquement ce qui s'est passé pour une demande.
- RT-057 — Les résultats de toutes les exécutions de contrôle sont conservés, pas seulement la dernière.
- RT-062 — L'historique de production est immuable : aucune entrée n'est modifiée ou supprimée par un utilisateur.
- RT-063 — Rien n'est écrasé silencieusement.
- RT-064 — La suppression en fin de conservation laisse une trace minimale (existence, date, motif général).
- RT-065 — Un audit doit pouvoir reconstituer pourquoi un livrable est ce qu'il est : règles, sources, décisions, contrôles.

## 6. À lire à la demande (ne rien lire d'autre au départ)

| Quoi | Commande | Pourquoi |
|---|---|---|
| Spéc. fonctionnelle 8 | `python tools/spec.py section F 8` | États et transitions à générer (TR-xx, IV-xx) |
| Spéc. technique 5.1 | `python tools/spec.py section T 5.1` | Modules |
| Spéc. technique 5.2 | `python tools/spec.py section T 5.2` | Règles de dépendance |
| Spéc. technique 5.3 | `python tools/spec.py section T 5.3` | Organisation du dépôt |
| Spéc. technique 6.3 | `python tools/spec.py section T 6.3` | Types énumérés |
| Spéc. technique 6.5 | `python tools/spec.py section T 6.5` | Tables d'états et contraintes |
| Spéc. technique 6.8 | `python tools/spec.py section T 6.8` | Journal, appels LLM, étapes |
| Spéc. technique 6.9 | `python tools/spec.py section T 6.9` | Déclencheurs d'immutabilité |
| Spéc. technique 7.2 | `python tools/spec.py section T 7.2` | Format des transitions (YAML) |
| Spéc. technique 7.4 | `python tools/spec.py section T 7.4` | Algorithme d'application d'une transition |
| Spéc. technique 19.2 | `python tools/spec.py section T 19.2` | Traçabilité spécification ↔ tests |
| Spéc. technique 18.2 | `python tools/spec.py section T 18.2` | Portes de qualité CI |

## 7. Critères de sortie du jalon

TST-18 vert (test à états aléatoires sur IV-01 à IV-15) ; chaîne du journal testée, y compris tentatives de contournement ; `spec_trace` publie un tableau de bord ; intégration continue verte ; `make check` existe et passe.

## 8. Rappels (extraits d'AGENTS.md)

- Tests d'acceptation d'abord ; `make check` doit passer ; ne jamais affaiblir un test, une contrainte ou un déclencheur.
- Ambiguïté de spécification → question dans `docs/reports/QUESTIONS.md`, jamais d'invention.
- À la fin d'une tranche : mettre à jour `docs/reports/PROGRESS.md`.

