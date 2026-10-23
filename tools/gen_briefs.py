#!/usr/bin/env python3
"""Génère docs/milestones/MS-n.md (briefs) et docs/prompts/PROMPT-MS-n.md à partir des spécifications.

À relancer après toute modification des spécifications : python tools/gen_briefs.py
Un brief contient UNIQUEMENT ce dont l'agent a besoin pour un jalon : exigences techniques (texte complet),
critères d'acceptation (texte complet), exigences fonctionnelles liées (une ligne chacune) et les commandes
pour lire le reste à la demande. Les V2 sont exclues des jalons MVP (elles relèvent de MS-9).
"""
from __future__ import annotations

import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import spec  # noqa: E402

ROOT = spec.ROOT
T = spec.load("T")
F = spec.load("F")


def cells_of(doc, ident):
    lns = doc.rows.get(ident)
    if not lns:
        return None
    ln = lns[0]
    hdr = doc.table_header(ln)
    row = spec.cells(doc.lines[ln])
    if hdr and len(hdr) == len(row):
        return dict(zip(hdr, row))
    return {"_raw": row}


def rng(a, b, prefix):
    return [f"{prefix}-{n:03d}" for n in range(a, b + 1)]


MS = {
    "MS-0": dict(
        title="Fondations",
        objective="Mettre en place le dépôt, l'intégration continue, les images, la base de données et ses migrations, la configuration, "
                  "le journal chaîné, le moteur d'états généré depuis la spécification fonctionnelle, l'outil de traçabilité spécification ↔ tests "
                  "et les règles de dépendance. Aucune fonction métier dans ce jalon.",
        ucs=[], et=[(1, 12), (13, 29), (35, 52), (353, 359), (372, 372)], ca=[], suites="TST-18 (invariants d'états)",
        read=[("F", "8", "États et transitions à générer (TR-xx, IV-xx)"), ("T", "5.1", "Modules"), ("T", "5.2", "Règles de dépendance"),
              ("T", "5.3", "Organisation du dépôt"), ("T", "6.3", "Types énumérés"), ("T", "6.5", "Tables d'états et contraintes"),
              ("T", "6.8", "Journal, appels LLM, étapes"), ("T", "6.9", "Déclencheurs d'immutabilité"), ("T", "7.2", "Format des transitions (YAML)"),
              ("T", "7.4", "Algorithme d'application d'une transition"), ("T", "19.2", "Traçabilité spécification ↔ tests"), ("T", "18.2", "Portes de qualité CI")],
        exit="TST-18 vert (test à états aléatoires sur IV-01 à IV-15) ; chaîne du journal testée, y compris tentatives de contournement ; "
             "`spec_trace` publie un tableau de bord ; intégration continue verte ; `make check` existe et passe.",
        notes="`make check`, `make spec-trace` et `make gen-transitions` n'existent pas encore : les créer dans ce jalon (ET-314, ET-353 à ET-356, ET-035). "
              "`make spec-trace` doit écrire un tableau de bord lisible par un non-développeur : `docs/reports/spec-trace.html` (ouvrable dans un navigateur) et `docs/reports/spec-trace.md`, "
              "avec : CA verts / rouges / ignorés / sans test, exigences sans test, tests orphelins, transitions non couvertes, et l'évolution par rapport au jalon précédent (le Product Owner s'en sert pour la checklist, point PO-01).",
        not_now="Tout cas d'usage métier ; tout appel à un LLM ; toute interface au-delà d'un squelette."),
    "MS-1": dict(
        title="Gouvernance",
        objective="Artefacts de gouvernance versionnés (lots de règles, modèles, registre, catalogue de contrôles), schémas, pipeline de validation, "
                  "épinglage par demande, console minimale de gouvernance.",
        ucs=["UC-026", "UC-027"], et=[(53, 68), (121, 121)], ca=[(150, 153)], suites="TST-15 (partie gouvernance)",
        read=[("T", "8", "Moteur de règles et gouvernance"), ("T", "6.4", "Tables de gouvernance et d'épinglage"), ("F", "UC-026", "Registre des sources"),
              ("F", "UC-027", "Modèles, règles, préférences"), ("T", "Annexe-C", "Exemple de lot de règles (illustratif)"), ("F", "7.10", "Règles de gouvernance (RB-097 à RB-108)")],
        exit="TST-15 (gouvernance) vert ; un lot de règles d'exemple approuvé de bout en bout ; épinglage et non-rétroactivité testés.",
        notes="Le contenu des règles métier est fourni par la personne responsable : utiliser l'Annexe C comme exemple, sans le considérer comme décision.",
        not_now="Appels LLM ; interface au-delà de la console minimale (SCR-15) et des utilisateurs/rôles (SCR-17)."),
    "MS-2": dict(
        title="Demande et faisabilité",
        objective="Passerelle LLM (enregistrements rejoués, journal d'appels), compréhension de la demande, clarification, faisabilité, messages d'état par gabarits. "
                  "Produire le « squelette de bout en bout » : une demande va de la saisie au diagnostic de faisabilité.",
        ucs=["UC-001", "UC-002", "UC-003", "UC-023"], et=[(231, 246), (247, 262), (293, 299)],
        ca=[(1, 20), (135, 140), (142, 144), (189, 190)], suites="TST-01, TST-02, TST-14 (partie suivi)",
        read=[("T", "10.1", "Orchestration"), ("T", "10.2", "É1 Compréhension"), ("T", "10.3", "É2 Faisabilité"), ("T", "11.1", "Passerelle LLM"),
              ("T", "11.2", "Rôles de modèles"), ("T", "11.4", "Catalogue des tâches LT"), ("T", "11.9", "Garde des messages"), ("T", "13.1", "Conventions d'API"),
              ("T", "Annexe-B", "Schémas LT-01, LT-02"), ("T", "Annexe-D", "Prompts PRM-01"), ("F", "UC-001", ""), ("F", "UC-002", ""), ("F", "UC-003", ""),
              ("F", "UC-023", ""), ("F", "Annexe-C", "Motifs de blocage MB-01 à MB-17")],
        exit="TST-01 et TST-02 verts ; suivi d'avancement avec statuts séparés ; squelette de bout en bout fonctionnel ; aucune annonce d'état non atteint (EVL-H partielle).",
        notes="CA-141 (statuts d'un livrable finalisé) est traité en MS-6. Les appels LLM de la CI utilisent des enregistrements rejoués, jamais un fournisseur réel.",
        not_now="Sources, extraction, cartographie, rendu de livrables."),
    "MS-3": dict(
        title="Sources et preuves",
        objective="Port de sources, simulateur INIS, téléversement, ingestion, texte canonique, vérification des citations (algorithme A5), extraction LT-03, "
                  "évaluation de la qualité (QI), autorisations ponctuelles minimales.",
        ucs=["UC-004", "UC-006", "UC-025"], et=[(91, 116)], ca=[(21, 30), (41, 44), (148, 149)], suites="TST-03, TST-05 (partie qualité)",
        read=[("T", "10.4", "É3 Mobilisation (dont A5)"), ("T", "10.6", "É5 Qualité (evaluate_quality)"), ("T", "15", "Intégrations et sources"),
              ("T", "9.1", "Modèle de décision d'autorisation"), ("T", "9.2", "Quatre points de contrôle"), ("T", "9.3", "Algorithme de décision"),
              ("T", "11.4", "Tâches LT-03, LT-05"), ("T", "Annexe-B", "Schémas LT-03"), ("T", "Annexe-D", "Prompt PRM-03"),
              ("F", "UC-004", ""), ("F", "UC-006", ""), ("F", "UC-025", ""), ("F", "3.3.1", "Statuts de qualité QI")],
        exit="TST-03 et TST-05 (qualité) verts ; EVL-A au seuil ; citations inventées retenues = 0 ; revalidation par empreinte de source testée.",
        notes="`make test-llm-replay` doit écrire `docs/reports/eval-report.md` (suites EVL, mesures, seuils, verdict ; point PO-09 de la checklist). Pour CA-148/149, implémenter dès ce jalon le strict minimum de l'autorisation ponctuelle (ET-212 : création, périmètre, expiration) ; la boîte de décisions complète arrive en MS-4.",
        not_now="Cartographie, calculs, rendu."),
    "MS-4": dict(
        title="Cartographie, lacunes, contradictions, décisions",
        objective="Lignes de cartographie et leur statut, propagation des blocages, lacunes, contradictions et règles de priorité, dossiers d'arbitrage, boîte de décisions.",
        ucs=["UC-005", "UC-007", "UC-008", "UC-024"], et=[(117, 130), (201, 204), (212, 212)], ca=[(31, 40), (45, 52), (145, 147), (192, 192)],
        suites="TST-04, TST-05, TST-15 (arbitrage)",
        read=[("T", "10.5", "É4 Cartographie (compute_line_status, A3)"), ("T", "10.8", "É7 Lacunes et contradictions (A4)"), ("T", "11.4", "Tâches LT-04, LT-06, LT-11"),
              ("F", "UC-005", ""), ("F", "UC-007", ""), ("F", "UC-008", ""), ("F", "UC-024", ""), ("F", "9.1", "Règles de blocage"), ("F", "Annexe-C", "Motifs MB")],
        exit="TST-04, TST-05 et TST-15 (arbitrage) verts ; EVL-B et EVL-C au seuil ; la récence n'est jamais un critère implicite.",
        notes="La personne responsable est unique et sans suppléance (RB-108).",
        not_now="Transformations, calculs, rendu, approbation, diffusion."),
    "MS-5": dict(
        title="Transformations, calculs, atomes, rendu",
        objective="Transformations autorisées, calcul décimal (CEL), reformulation fidèle (A6), atomes de contenu, minimisation des données, rendus Word/PDF/CSV/Markdown avec relecture.",
        ucs=["UC-009", "UC-010", "UC-011", "UC-031"], et=[(84, 90), (131, 162)], ca=[(53, 70), (157, 168)], suites="TST-06, TST-07, TST-16",
        read=[("T", "9.6", "Classification et héritage"), ("T", "9.7", "Minimisation et masquage"), ("T", "10.7", "É6 Transformation"), ("T", "10.9", "É8 Production"),
              ("T", "11.5", "Reformulation fidèle (A6)"), ("T", "12.1", "Chaîne de rendu"), ("T", "12.2", "Détails par format"), ("T", "12.3", "Relecture après rendu"),
              ("T", "8.8", "Évaluateur de formules (CEL)"), ("T", "8.9", "Corrections mécaniques"), ("T", "Annexe-B", "Schémas LT-07, LT-08"), ("T", "Annexe-D", "Prompts PRM-07, PRM-08"),
              ("F", "UC-009", ""), ("F", "UC-010", ""), ("F", "UC-011", ""), ("F", "UC-031", "")],
        exit="TST-06, TST-07 et TST-16 verts ; EVL-D au seuil ; chaque rendu relu sans écart ; aucun atome sans lien de preuve.",
        notes="Excel et PowerPoint sont en V2 (MS-9). Le contrôle visuel manuel de fidélité Word/PDF (ET-162) se fait avec le Product Owner.",
        not_now="Contrôles qualité, rapports, finalisation."),
    "MS-6": dict(
        title="Contrôles, finalisation, rapports, scellement",
        objective="Catalogue de contrôles, anomalies et corrections mécaniques, finalisation atomique, rapports de conformité et de traçabilité, export de provenance, scellement.",
        ucs=["UC-012", "UC-013", "UC-014", "UC-030"], et=[(163, 200)], ca=[(71, 94), (141, 141), (169, 176)], suites="TST-08, TST-09, TST-17",
        read=[("T", "10.10", "É9 Contrôles (catalogue CT)"), ("T", "10.11", "É10 Anomalies"), ("T", "10.12", "É11 Finalisation"), ("T", "12.4", "Rapport de conformité"),
              ("T", "12.5", "Rapport de traçabilité et PROV"), ("T", "12.6", "Scellement"), ("T", "11.4", "Tâche LT-09"), ("F", "Annexe-B", "Catalogue de contrôles"),
              ("F", "Annexe-D", "Contenu des rapports"), ("F", "9.4", "Conditions de finalisation FN-01 à FN-10"), ("F", "UC-012", ""), ("F", "UC-013", ""),
              ("F", "UC-014", ""), ("F", "UC-030", "")],
        exit="TST-08, TST-09 et TST-17 verts ; sceau vérifiable hors ligne ; chaîne et sceaux vérifiés ; aucune finalisation partielle.",
        notes="La finalisation est atomique (ET-195) : tout ou rien.",
        not_now="Approbation, diffusion, révision, suspension."),
    "MS-7": dict(
        title="Approbation, diffusion, versions, cycle de vie",
        objective="Approbation, diffusion, révocation, révision, suspension, reprise, annulation.",
        ucs=["UC-015", "UC-016", "UC-017", "UC-018", "UC-019", "UC-020"], et=[(205, 210), (213, 227), (229, 230)],
        ca=[(95, 104), (105, 113), (115, 126), (177, 188), (191, 191), (193, 193)], suites="TST-10, TST-11, TST-12",
        read=[("F", "9.6", "Approbation et diffusion : possibilités, conditions, effets"), ("T", "10.12", "É11 (approbation, diffusion)"), ("T", "10.13", "Suspension, reprise (A10), révision, annulation"),
              ("T", "7.4", "Application d'une transition"), ("F", "UC-015", ""), ("F", "UC-016", ""), ("F", "UC-017", ""), ("F", "UC-018", ""), ("F", "UC-019", ""), ("F", "UC-020", "")],
        exit="TST-10, TST-11 et TST-12 verts ; tests de reprise après crash ; l'approbation et la diffusion ne modifient jamais la conformité.",
        notes="ET-201 à ET-204 et ET-212 ont été réalisés en MS-4 ; ne pas les refaire.",
        not_now="Différences entre versions, exceptions, livrables multiples (V2)."),
    "MS-8": dict(
        title="Durcissement et pilote",
        objective="Sécurité, observabilité, évaluations nocturnes, performance, sauvegardes, accessibilité, tests de bout en bout, revue de sécurité.",
        ucs=[], et=[(267, 276), (305, 352), (373, 384)], ca=[], suites="TST-19, TST-20",
        read=[("T", "17", "Sécurité"), ("T", "18", "Exploitation"), ("T", "19", "Stratégie de test"), ("T", "20", "Performance"), ("T", "Annexe-H", "Vérifications avant gel"),
              ("T", "11.6", "Défense contre l'injection"), ("T", "11.8", "Évaluation des LLM")],
        exit="TST-19 et TST-20 verts ; liste de préparation au pilote signée ; mesures NF relevées ; aucune donnée réelle avant la fin de ce jalon.",
        notes="Les questions QT-04, QT-07 doivent être tranchées avant toute donnée réelle (PL-05).",
        not_now="Évolutions V2."),
    "MS-9": dict(
        title="Évolutions V2",
        objective="Livrables multiples, priorités, exceptions, propositions de règles, profil auditeur, différences entre versions, formats Excel et PowerPoint, mutation testing.",
        ucs=["UC-021", "UC-022", "UC-028", "UC-029"], et=[(67, 68), (148, 149), (197, 197), (211, 211), (228, 228), (263, 263), (289, 289), (360, 360)],
        ca=[(114, 114), (127, 134), (154, 156), (194, 195)], suites="TST-13 et suites V2", v2=True,
        read=[("T", "10.13", "Priorisation et livrables multiples (SC-01 à SC-05)"), ("F", "UC-021", ""), ("F", "UC-022", ""), ("F", "UC-028", ""), ("F", "UC-029", ""),
              ("F", "9.6.4", "Version non conforme et exceptions")],
        exit="TST-13 vert ; suites V2 vertes.",
        notes="Chaque élément V2 reste sous confirmation du Product Owner (QO-036 pour la diffusion exceptionnelle).",
        not_now="—"),
}


def fmt_id(prefix, n):
    return f"{prefix}-{n:03d}" if prefix in ("RF", "RB", "RT") else f"{prefix}-{n:02d}"


def expand_ids(text):
    ids = []
    for m in re.finditer(r"\b(RF|RB|RT|IV)-(\d{1,3})\s+à\s+\1-(\d{1,3})\b", text):
        a, b = int(m.group(2)), int(m.group(3))
        if 0 < b - a <= 40:
            ids += [fmt_id(m.group(1), n) for n in range(a, b + 1)]
    for m in re.finditer(r"\b(RF|RB|RT|IV)-(\d{1,3})\b", text):
        ids.append(fmt_id(m.group(1), int(m.group(2))))
    return ids


def trunc(s, n=170):
    s = re.sub(r"\s+", " ", s)
    return s if len(s) <= n else s[: n - 3] + "..."


def build(msid, d):
    v2 = d.get("v2", False)
    et_ids = []
    for a, b in d["et"]:
        et_ids += rng(a, b, "ET")
    skipped_v2 = 0
    et_lines, fids = [], []
    for ident in et_ids:
        c = cells_of(T, ident)
        if not c:
            continue
        prio = c.get("Prio", "")
        if not v2 and prio == "V2":
            skipped_v2 += 1
            continue
        et_lines.append(f"- **{ident}** ({c.get('Statut','')} · {prio}) — {c.get('Exigence','')}  \n  _Réalise : {c.get('Réalise','')} · {c.get('Module / ADR','')}_")
        fids += expand_ids(c.get("Réalise", ""))
    ca_ids = []
    for item in d["ca"]:
        a, b = item
        ca_ids += [f"CA-{n:03d}" for n in range(a, b + 1)]
    ca_lines = []
    for ident in ca_ids:
        c = cells_of(F, ident)
        if not c:
            continue
        ca_lines.append(f"- **{ident}** ({c.get('Liens','')}) — {c.get('Critère','')}")
        fids += expand_ids(c.get("Liens", ""))
    seen, fsum = set(), []
    for fid in fids:
        if fid in seen:
            continue
        seen.add(fid)
        c = cells_of(F, fid)
        if c:
            txt = c.get("Exigence") or c.get("Règle") or c.get("Invariant") or ""
            fsum.append(f"- {fid} — {trunc(txt)}")
    fsum.sort()

    L = [f"# Jalon {msid} — {d['title']}",
         "",
         "> Brief généré par `tools/gen_briefs.py` — ne pas modifier à la main. Pour tout détail : `python tools/spec.py show <ID>`.",
         "",
         "## 1. Objectif", "", d["objective"], ""]
    if d["notes"]:
        L += ["**À savoir.** " + d["notes"], ""]
    L += ["## 2. Périmètre", "",
          f"- Cas d'usage : {', '.join(d['ucs']) if d['ucs'] else '— (jalon transversal)'}",
          f"- Suites de tests visées : {d['suites']}",
          f"- Hors périmètre de ce jalon : {d['not_now']}"]
    if skipped_v2:
        L.append(f"- {skipped_v2} exigence(s) V2 comprises dans les plages sont **reportées à MS-9** (non listées ci-dessous).")
    L += ["", f"## 3. Exigences techniques à réaliser ({len(et_lines)})", ""] + et_lines + [""]
    if ca_lines:
        L += [f"## 4. Critères d'acceptation à rendre verts ({len(ca_lines)})", "",
              "Écrire d'abord un test par critère, étiqueté de son identifiant (`@pytest.mark.ca(\"CA-xxx\")`).", ""] + ca_lines + [""]
    else:
        L += ["## 4. Critères d'acceptation", "", "Pas de CA propres à ce jalon : voir les critères de sortie ci-dessous.", ""]
    L += [f"## 5. Exigences fonctionnelles liées ({len(fsum)}) — une ligne chacune", "",
          "Résumés seulement. Pour le texte complet et le contexte : `python tools/spec.py show RF-xxx`.", ""] + fsum + [""]
    L += ["## 6. À lire à la demande (ne rien lire d'autre au départ)", "", "| Quoi | Commande | Pourquoi |", "|---|---|---|"]
    for doc, key, why in d["read"]:
        L.append(f"| {'Spéc. technique' if doc == 'T' else 'Spéc. fonctionnelle'} {key} | `python tools/spec.py section {doc} {key}` | {why or 'Fiche du cas d’usage'} |")
    L += ["", "## 7. Critères de sortie du jalon", "", d["exit"], "",
          "## 8. Rappels (extraits d'AGENTS.md)", "",
          "- Tests d'acceptation d'abord ; `make check` doit passer ; ne jamais affaiblir un test, une contrainte ou un déclencheur.",
          "- Ambiguïté de spécification → question dans `docs/reports/QUESTIONS.md`, jamais d'invention.",
          "- À la fin d'une tranche : mettre à jour `docs/reports/PROGRESS.md`.", ""]
    return "\n".join(L)


PROMPT = """Tu es l'agent de codage du projet « Agent de production contrôlée de livrables ».

## 1. Lecture (économie de contexte)
Lis, dans cet ordre et RIEN d'autre au départ :
1. `AGENTS.md`
2. `docs/reports/PROGRESS.md`
3. `docs/milestones/{ms}.md`
Les spécifications complètes sont volumineuses et NE DOIVENT JAMAIS être ouvertes en entier. Pour toute précision, utilise
`python tools/spec.py show <ID>` | `section F|T <clé>` | `search <texte>` | `refs <ID>`. Sans accès à un terminal, utilise
`docs/spec/INDEX.md` pour ouvrir uniquement les lignes utiles des fichiers de `docs/spec/_sources/`.

## 2. Mission
Réaliser le jalon **{ms} — {title}**. {objective}

## 3. Méthode
- Procède par petites tranches (≤ ~400 lignes modifiées), chacune terminée par `make check` vert{ms0note}.
- Pour chaque critère CA du brief : écris d'abord le test, constate qu'il échoue, puis implémente.
- Cite les identifiants (RF, RB, RT, CA, ET, ADR) dans commits et tests.
- Respecte les fichiers protégés et les principes de `AGENTS.md`. N'ajoute aucune dépendance sans ADR dans `docs/adr/`.

## 4. Autonomie
Travaille sans t'arrêter jusqu'à ce que : (a) `make check` soit vert ET tous les CA du brief soient verts ; ou (b) tu butes sur une question que seul le
Product Owner peut trancher : écris-la dans `docs/reports/QUESTIONS.md` (avec ton hypothèse par défaut), passe à une tranche indépendante, et ne bloque pas ;
ou (c) le même test échoue après 3 tentatives différentes : arrête cette tranche, écris ton analyse dans `docs/reports/QUESTIONS.md` et passe à la suivante.
Après chaque tranche, mets à jour `docs/reports/PROGRESS.md` (fait, à faire, décisions, prochaine commande).
Si ton contexte approche 70 % : mets `PROGRESS.md` à jour et poursuis dans une session neuve en relisant seulement AGENTS.md, PROGRESS.md et le brief.

## 5. Fin de jalon
Rédige `docs/reports/{ms}-rapport.md` (gabarit : AGENTS.md, section « Rapport de fin de tâche »).
Rédige aussi `docs/reports/{ms}-demo.md` : un **guide de démonstration pas à pas pour un Product Owner non technique** — prérequis, commandes ou clics exacts, et pour chaque étape le résultat attendu ; couvre les points de `docs/CHECKLIST-PO.md` applicables à ce jalon (démonstration du parcours ET tentatives de violation avec le message de refus attendu).
Ne commence PAS le jalon suivant.
Critères de sortie : {exit}
"""

REPRISE = """Reprends le travail sur le projet « Agent de production contrôlée de livrables ».
1. Lis `AGENTS.md`, puis `docs/reports/PROGRESS.md` (il indique le jalon courant et la prochaine tranche), puis le brief du jalon courant dans `docs/milestones/`.
2. Ne lis rien d'autre ; utilise `python tools/spec.py` pour toute précision.
3. Continue à la prochaine tranche indiquée, selon la méthode et les règles d'autonomie du prompt du jalon (`docs/prompts/`).
4. Mets `PROGRESS.md` à jour après chaque tranche.
"""

REVUE = """Tu es un relecteur indépendant. Tu ne modifies PAS le code. Tu produis un rapport.
1. Lis `AGENTS.md` et le brief du jalon à relire (`docs/milestones/MS-n.md`) — rien d'autre au départ.
2. Exécute `make check` et `make test-acceptance`. Note les résultats exacts.
3. Pour chaque CA du brief : vérifie qu'il existe un test étiqueté, qu'il passe, et qu'il teste réellement le comportement décrit (pas un test vide ou trop permissif).
4. Cherche activement les violations : état modifié hors du moteur ; contenu de livrable sans preuve ; logique métier dans l'API ou l'interface ; appel LLM hors `run_task` ;
   test, contrainte ou déclencheur affaibli ; donnée réelle dans le dépôt ; raison interne exposée à l'utilisateur ; trois statuts (conformité, approbation, diffusion) déduits l'un de l'autre.
5. Rédige `docs/reports/MS-n-revue.md` : verdict (conforme / réserves / non conforme), liste précise des écarts avec fichier:ligne, et exigences non couvertes.
Utilise `python tools/spec.py show <ID>` pour lire les exigences ; ne lis pas les spécifications en entier.
"""


def check_keys():
    bad = []
    for msid, d in MS.items():
        for doc, key, _why in d["read"]:
            dd = spec.load(doc)
            if not any(sec == key or idref == key for (_i, _l, _t, sec, idref) in dd.headings):
                bad.append((msid, doc, key))
    if bad:
        print("ATTENTION — clés de section introuvables :", bad)
    return not bad


def main():
    check_keys()
    (ROOT / "docs" / "milestones").mkdir(parents=True, exist_ok=True)
    (ROOT / "docs" / "prompts").mkdir(parents=True, exist_ok=True)
    sizes = []
    for msid, d in MS.items():
        text = build(msid, d)
        (ROOT / "docs" / "milestones" / f"{msid}.md").write_text(text + "\n", encoding="utf-8")
        ms0note = " (ce jalon crée `make check` : le faire en premier)" if msid == "MS-0" else ""
        p = PROMPT.format(ms=msid, title=d["title"], objective=d["objective"], exit=d["exit"], ms0note=ms0note)
        (ROOT / "docs" / "prompts" / f"PROMPT-{msid}.md").write_text(p, encoding="utf-8")
        sizes.append((msid, len(text)))
    (ROOT / "docs" / "prompts" / "PROMPT-REPRISE.md").write_text(REPRISE, encoding="utf-8")
    (ROOT / "docs" / "prompts" / "PROMPT-REVUE.md").write_text(REVUE, encoding="utf-8")
    for msid, n in sizes:
        print(f"{msid}: {n/1024:.1f} Ko")


if __name__ == "__main__":
    main()
