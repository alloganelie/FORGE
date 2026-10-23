# Guide de démonstration — MS-2 Demande et faisabilité

**Pour qui :** Product Owner, sans lecture de code.  
**Durée :** 30 à 45 minutes.  
**But :** vérifier le parcours demande → clarification → faisabilité → statut, ainsi que les refus et les statuts séparés.

MS-2 couvre PO-01, PO-02, PO-03, PO-04 et PO-10.

---

## 0. Prérequis (5 min)

- Docker Desktop démarré ; Python 3.13 ; `make`.
- Repli si `make` manque : `py -3.13 tools/check.py check`.

```powershell
git status
git log --oneline -1
```

---

## 1. Chaîne complète (5 à 8 min)

```bash
make check
```

**Attendu (fin de sortie) :**

```text
160 passed in ...
MS-2 : 35/35 CA exigibles verts, 0 sans test, 160 hors perimetre, 54/54 transitions couvertes, 160 tests, 0 orphelins.
```

Les 35 CA incluent les 31 CA de MS-2 et les 4 CA de MS-1, qui restent verts.

---

## 2. Tests d'acceptation (5 min) — PO-02

```bash
make test-acceptance
```

**Attendu :** **40 tests verts** (4 MS-0, 5 MS-1, 31 MS-2).

Pour cibler les refus et la protection des données :

```powershell
.\.venv\Scripts\python.exe -m pytest -q backend/tests/acceptance/test_request_flow_ca.py -k "ca004 or ca020 or ca137"
```

**Attendu :** 3 tests verts. Ils vérifient le refus d'un acteur non autorisé, le motif général pour un interlocuteur sans droit et l'absence d'information protégée dans le suivi.

---

## 3. Parcours de bout en bout (5 min) — PO-03

```bash
make demo-requests
```

**Attendu :**

```text
1. Demande recue : <uuid>
   - etat : clarifying, type : note, format : pdf
2. Questions : 1
   - Quel est le perimetre geographique ? (Le perimetre conditionne les donnees du livrable.)
3. Reponse enregistree : etat feasibility
4. Diagnostic : realizable, dimensions : 7
5. Versions epinglees : 4
6. Statut : En production
   - etapes terminees : reception, comprehension, faisabilite
   - prochaine action : Poursuivre le traitement.
   - axes separes : {'C': 'non evaluee', 'A': 'non soumise', 'D': 'non autorisee', 'V': 'provisoire'}
7. Fin : transaction annulee, aucune donnee conservee.
```

Cette démonstration prouve :

- la demande est enregistrée avec son texte d'origine ;
- le type et le format sont identifiés séparément ;
- une question ciblée est posée avec sa raison ;
- la réponse devient une information fournie par l'utilisateur (QI-02) ;
- le diagnostic couvre les sept dimensions ;
- les versions sont épinglées ;
- les statuts R, C, A, D et V sont présentés séparément ;
- aucune donnée n'est conservée après la démonstration.

Toutes les réponses LLM sont **rejouées** : aucun fournisseur externe n'est appelé.

---

## 4. Vérifier les refus et les motifs (5 min) — PO-04

1. **Acteur non autorisé** : le test CA-004 utilise un auditeur ; la demande est refusée avec un motif communicable et aucune ligne n'est créée.
2. **Droits incertains** : CA-017 vérifie que l'opération est suspendue et la demande passe en attente de décision.
3. **Source protégée** : CA-020 et CA-137 vérifient que le motif public ne cite pas la source ; la personne responsable voit le détail.
4. **Message d'état** : CA-139 vérifie qu'aucune réussite n'est annoncée avant les contrôles ; CA-140 vérifie l'usage des états fonctionnels.

Pour rejouer uniquement ces scénarios :

```powershell
.\.venv\Scripts\python.exe -m pytest -q backend/tests/acceptance/test_request_flow_ca.py -k "ca013 or ca017 or ca020 or ca139 or ca140"
```

**Attendu :** 5 tests verts.

---

## 5. Suivi et statuts séparés (3 min)

- Ouvrir `backend/src/agent/conversation/core/templates.py` : les gabarits français sont versionnés (`v1`).
- Ouvrir `frontend/components/StatusStrip.tsx` : les axes R, C, A, D et V sont rendus séparément ; le badge « Version provisoire » est visible.
- Ouvrir `frontend/app/layout.tsx` : l'en-tête affiche **FORGE** (Q-001).
- Le test `test_ca136_items_distinguish_states` vérifie que terminé, suspendu, bloqué, en attente de décision et finalisé sont distingués.

L'interface Next.js est un squelette : `make check` vérifie ses fichiers et son typage strict statique, mais n'exécute pas `npm install`. Pour la lancer :

```bash
cd frontend
npm install
npm run dev
```

---

## 6. Tableau de bord (3 min) — PO-01

Ouvrir `docs/reports/spec-trace.html`.

**Attendu :**

- jalon MS-2 ;
- **35 / 35** CA exigibles verts ;
- 0 CA rouge, 0 sans test, 0 ignoré ;
- 160 CA hors périmètre (jalons suivants) ;
- 54/54 transitions, 0 test orphelin, 0 identifiant inconnu.

---

## 7. Fiche de revue

| Vérification | MS-2 | Où / quoi regarder | Résultat attendu | Votre verdict |
|---|---|---|---|---|
| PO-01 Tableau de bord | ✔ | `docs/reports/spec-trace.html` | 35/35 CA, 0 rouge, 0 sans test | |
| PO-02 CA du jalon verts | ✔ | `make test-acceptance` | 40 tests verts | |
| PO-03 Parcours du jalon | ✔ | `make demo-requests` | Demande → clarification → faisabilité → statut | |
| PO-04 Violation refusée | ✔ | Tests CA-004/013/017/020/137 | Refus ou motif général, aucune donnée exposée | |
| PO-05 à PO-09 | — | — | Non applicables à MS-2 (PO-08/09 complets plus tard) | |
| PO-10 Rapport traité | ✔ | `docs/reports/MS-2-rapport.md` | Écarts E-20 à E-25 et ET partiels listés | |

**Verdict attendu si tout est bon :** « Validé ».

---

## 8. Ce que vous ne verrez pas encore

- Aucun fournisseur LLM réel : uniquement des enregistrements rejoués, conformément à la décision PO.
- Pas de routeur de commandes LT-10 exécuté, ni de détection de doublons (ET-231, ET-238 partiels).
- Pas de budgets, cache de prompt ou minimisation AU-2 complets (ET-257, ET-261, ET-262 partiels).
- Interface Next.js non branchée à l'API et non construite par `make check`.
- Pas de livrable produit : MS-2 s'arrête au diagnostic de faisabilité.

---

## 9. Nettoyage

```bash
make db-down
```

---

## Résumé des commandes

```bash
make check
make test-acceptance
make demo-requests
make demo-governance
make db-up / db-down
```
