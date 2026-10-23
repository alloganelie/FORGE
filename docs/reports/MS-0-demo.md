# Guide de démonstration — MS-0 Fondations

**Pour qui :** Product Owner, sans lecture de code.  
**Durée :** 30 à 45 minutes.  
**But :** vérifier les preuves observables de MS-0 et remplir la fiche de revue (`docs/CHECKLIST-PO.md`) sans juger le code.

Ce guide ne remplace pas le rapport : il donne les commandes exactes et le résultat attendu à chaque étape. Si un résultat diffère, notez l'étape et le message exact ; ne validez pas par défaut.

---

## 0. Préparer une copie propre (5 min)

1. Ouvrez un terminal dans le dossier du projet.
2. Vérifiez que vous êtes sur le dernier commit :

```powershell
git status
git log --oneline -1
```

Attendu : aucune modification en attente (ou seulement des fichiers non suivis que vous savez être à vous) et un commit MS-0.

3. Vérifiez les prérequis :
   - **Docker Desktop** démarré (icône verte). Sans lui, les tests PostgreSQL ne peuvent pas tourner.
   - **Python 3.13** : commande `py -3.13 --version`.
   - **make** : commande `make --version`. S'il manque sous Windows, installez-le une fois avec `winget install ezwinports.make`, ou utilisez le repli indiqué plus bas.
   - **uv** : installé par la procédure du dépôt ; `make check` s'en charge.

> Repli si `make` n'est pas disponible : `py -3.13 tools/check.py check` produit exactement les mêmes contrôles.

---

## 1. Lancer la chaîne complète (5 à 8 min)

```bash
make check
```

**Attendu (fin de sortie) :**

```text
82 passed in ...
MS-0 : 0/0 CA exigibles verts, 0 sans test, 195 hors perimetre, 54/54 transitions couvertes, 82 tests, 0 orphelins.
Tableaux de bord ecrits : docs/reports/spec-trace.html, spec-trace.md, spec-trace.json
```

Les étapes intermédiaires doivent toutes être vertes : format, `mypy`, règles de dépendance, génération, tests, traçabilité. La première exécution télécharge les dépendances et l'image PostgreSQL ; elle peut prendre quelques minutes.

**Si une étape échoue :** copiez la dernière ligne d'erreur et l'étape concernée dans votre fiche. Ne relancez pas en boucle : le rapport doit expliquer l'écart.

---

## 2. Ouvrir le tableau de bord « spécification ↔ tests » (5 min) — PO-01

1. Ouvrez `docs/reports/spec-trace.html` (double-clic ; il s'ouvre dans le navigateur).
2. Vérifiez les cartes du haut :
   - **Critères exigibles verts : 0 / 0** — normal : MS-0 ne comporte aucun critère d'acceptation métier.
   - **Critères exigibles rouges : 0**, **sans test : 0**, **ignorés : 0**.
   - **Critères hors périmètre : 195** — les CA appartiennent aux jalons métier suivants ; ils ne sont pas exigés maintenant.
   - **Transitions couvertes : 54 / 54**.
   - **Tests orphelins : 0**, **identifiants inconnus : 0**.
3. Dans le tableau « Critères d'acceptation (tous) », les 195 CA sont gris « hors périmètre » ; aucun n'est rouge, ignoré ou « sans test » dans le périmètre.
4. Dans « Transitions », chaque ligne est verte avec au moins un test.
5. Dans « Exigences RF / RB / RT sans test », le compteur est élevé (environ 482) : ce sont les exigences des jalons métier futurs. La porte correspondante (ET-355) est publiée et deviendra bloquante au jalon final (question Q-003). Ce n'est **pas** un échec MS-0.

**Bon :** aucun critère exigible rouge, aucun orphelin, 54/54 transitions.  
**Mauvais :** un critère exigible rouge ou « sans test », un identifiant inconnu, une transition non couverte.

Le même contenu est disponible en Markdown dans `docs/reports/spec-trace.md` et en JSON dans `docs/reports/spec-trace.json`.

---

## 3. Vérifier TST-18 (5 min) — PO-02

```bash
make tst18
```

**Attendu :** 3 tests verts, dont un test à états aléatoires qui génère 250 séquences de commandes et vérifie les quinze invariants IV-01 à IV-15 après chaque pas.

Le test PostgreSQL associé est inclus dans `make check` (fichier `backend/tests/integration/test_tst18_db.py`) : il rejoue le parcours nominal et vérifie que l'état, la projection `state_changes` et le journal restent dans la même transaction.

**À regarder :** le nom des tests cite les invariants. Aucun test n'est ignoré (`skip`).

---

## 4. Vérifier le journal chaîné et les refus (5 min) — preuve de robustesse

```bash
make demo-ledger
```

**Attendu :**

```text
1. Ajout de trois evenements dans le journal
   - evenement 1 : request_seq=1
   - evenement 2 : request_seq=2
   - evenement 3 : request_seq=3
2. Verification de la chaine
   - 3 evenements, resultat : OK
3. Tentative de modification d'un evenement
   - refusee : Table ledger_events en ajout seul : UPDATE interdit
4. Tentative de suppression d'un evenement
   - refusee : Table ledger_events en ajout seul : DELETE interdit
5. Tentative de changement d'etat hors moteur de transitions
   - refuse : Etat de demande modifie hors moteur de transitions
6. Fin : transaction annulee, aucune donnee de demonstration conservee.
```

**Ce que cela prouve :** le journal est en ajout seul, une écriture d'état directe est refusée même par un administrateur de la base, et la démonstration ne laisse aucune donnée.

Pour vérifier une base existante (par exemple après un essai) :

```bash
make verify-chain
```

Attendu sur une base vide : « Aucun espace de travail : rien à vérifier. » Sur une base contenant des événements : un compteur par espace et « OK » ; toute altération produit « ECHEC » et un code de sortie non nul.

---

## 5. Vérifier que les transitions viennent de la spécification (3 min)

1. Ouvrez `rulepacks/state_machines/request.yaml`. Vous y trouvez les 26 transitions de l'axe R, leurs états, acteurs, gardes, conditions et effets.
2. Ouvrez `rulepacks/state_machines/element.yaml` : 11 transitions de l'axe E.
3. Le fichier est généré depuis la spécification fonctionnelle 8.2 à 8.7 et la spécification technique 7.2 ; son en-tête contient les empreintes des sources.
4. `make check` exécute `gen_transitions.py --check` : si quelqu'un modifie le YAML sans régénérer, le build échoue.

**À ne pas faire :** modifier un YAML à la main. Le fichier est protégé et régénéré.

---

## 6. Vérifier les frontières des 23 modules (3 min)

```bash
py -3.13 tools/check_imports.py
```

**Attendu :** `DR-01 a DR-07 : aucune violation`.

Cette commande vérifie que le domaine pur n'importe pas d'infrastructure, qu'un module ne contourne pas la façade d'un autre, que seul `lifecycle` écrit un état, que seul `ledger` touche le journal, que seul `documents_io` lit des fichiers, etc.

---

## 7. Vérifier l'image non root (5 min)

```bash
docker build -f ops/Dockerfile -t agent-livrables:local .
docker run --rm --entrypoint id agent-livrables:local -u
```

**Attendu :** `10001` (pas `0`, qui serait root).

Pour voir l'API répondre :

```bash
docker run -d --name demo-api -p 18000:8000 \
  -e AGENT_DATABASE_URL="postgresql+psycopg://agent:agent@host.docker.internal:55432/agent" \
  agent-livrables:local
```

Puis ouvrez `http://127.0.0.1:18000/healthz` ou :

```powershell
(Invoke-WebRequest -UseBasicParsing http://127.0.0.1:18000/healthz).Content
```

**Attendu :** un JSON avec `"status":"ok"`, la version, le rôle et l'environnement.

Arrêtez et supprimez le conteneur :

```bash
docker rm -f demo-api
```

La SBOM est produite par la CI (`anchore/sbom-action`) ; localement, `ops/sbom.sh` la produit si `syft` est installé. Sans `syft`, ne considérez pas l'étape SBOM comme vérifiée localement : elle l'est dans la CI.

---

## 8. Lire la CI (2 min)

Ouvrez `.github/workflows/ci.yml`. Vous y voyez :

1. un service PostgreSQL réel (image pgvector/pgvector:pg17) ;
2. `uv sync --locked` puis `make check` ;
3. la publication du tableau de bord ;
4. la construction de l'image, la vérification de l'UID 10001 et la SBOM.

**Limite actuelle :** le dépôt n'a pas encore de remote GitHub ; la CI n'a donc pas encore tourné sur GitHub. L'exécution locale de `make check` est la même chaîne. C'est l'écart E-01 du rapport.

---

## 9. Remplir la fiche de revue (5 min)

| Vérification | MS-0 | Où / quoi regarder | Résultat attendu | Votre verdict |
|---|---|---|---|---|
| PO-01 Tableau de bord | ✔ | `docs/reports/spec-trace.html` | 0 CA exigible rouge/sans test ; 54/54 transitions ; 0 orphelin | |
| PO-02 CA du jalon verts | ✔ | `docs/milestones/MS-0.md` section 4 | Aucun CA propre à MS-0 ; les 195 CA sont hors périmètre | |
| PO-03 Parcours du jalon | — | — | Pas de parcours métier en MS-0 | |
| PO-04 Violation refusée | — (bonus démontré) | `make demo-ledger` | UPDATE/DELETE/état direct refusés | |
| PO-05 Trois statuts séparés | — | — | À partir de MS-6 | |
| PO-06 Messages de blocage | — | — | À partir de MS-2 | |
| PO-07 Aucun contenu sans source | — | — | À partir de MS-5 | |
| PO-08 Journaux sans données sensibles | — | — | À partir de MS-5 ; la démo n'utilise que des identifiants techniques | |
| PO-09 Évaluations LLM | — | — | Aucun LLM en MS-0 | |
| PO-10 Rapport traité | ✔ | `docs/reports/MS-0-rapport.md` et `QUESTIONS.md` | Écarts E-01 à E-09 listés ; Q-002 et Q-003 tranchées | |

**Verdict attendu si tout est bon :** « Validé ».  
**Si un point est rouge :** utilisez le texte de refus fourni dans `docs/CHECKLIST-PO.md` et citez l'étape exacte de ce guide.

---

## 10. Ce que vous ne verrez pas encore (et pourquoi)

- Aucun écran métier, aucune demande, aucun livrable : MS-0 ne contient **aucune fonction métier**.
- Aucun appel à un modèle de langage : la passerelle LLM arrive à un jalon ultérieur.
- Aucun envoi de courriel, aucune diffusion.
- Aucun déploiement cloud : l'image et la CI sont prêtes, mais la plateforme gérée n'est pas encore choisie (ET-011, écart E-02).

Ne demandez pas de commencer MS-1 avant d'avoir validé ce jalon.

---

## 11. En cas de problème

| Symptôme | Cause probable | Action |
|---|---|---|
| `make: command not found` | GNU make absent | `winget install ezwinports.make`, puis rouvrir le terminal ; ou `py -3.13 tools/check.py check` |
| `PostgreSQL indisponible` | Docker Desktop arrêté | Démarrer Docker Desktop, puis `make db-up` |
| `port 55432 already allocated` | Un autre PostgreSQL local écoute | Arrêter l'autre service ou modifier le port dans `ops/compose.yaml` (et la configuration) |
| `uv.lock absent` | Copie incomplète | Récupérer le dépôt complet ; ne pas régénérer le verrou sans ADR |
| Le tableau de bord n'existe pas | `make check` interrompu avant la traçabilité | Relancer `make check` et lire l'étape en échec |
| Un test PostgreSQL échoue | Base de test dans un état inattendu | `make db-down` puis `make db-up` et relancer ; ne jamais modifier un test pour le faire passer |

---

## 12. Nettoyage (facultatif)

```bash
make db-down
```

Cette commande supprime le conteneur PostgreSQL local et ses données de démonstration. Elle n'affecte ni le dépôt ni les rapports.

---

## Résumé des commandes

```bash
make check          # chaîne complète (obligatoire)
make tst18          # TST-18 uniquement
make demo-ledger    # journal, refus UPDATE/DELETE/état
make verify-chain   # vérifie une base existante
make test-acceptance
make spec-trace     # régénère le tableau de bord
make db-up / db-down
```