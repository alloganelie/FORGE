#!/usr/bin/env python3
"""Lecteur par tranches des spécifications (fonctionnelle F et technique T).

Objectif : permettre à un agent de lire UNIQUEMENT ce dont il a besoin, sans ouvrir
les fichiers maîtres (volumineux). Aucune dépendance externe (Python >= 3.9).

Commandes :
  show ID [ID ...]        Affiche la ligne (ou la fiche) d'un ou plusieurs identifiants.
                          Plages : ET-091..ET-106   (même préfixe, numérique)
  section DOC CLE         Affiche une section. DOC = F ou T. CLE = 7.4 | 16.C | Annexe-C | UC-005 | ADR-005
  search TEXTE            Recherche plein texte (insensible à la casse) dans F et T.
  refs ID                 Liste les endroits qui mentionnent un identifiant.
  toc DOC                 Table des matières (sections de niveau 2 et 3) avec lignes.
  milestone MS-n          Affiche le brief d'un jalon (docs/milestones/MS-n.md).
  index                   Régénère docs/spec/INDEX.md et docs/spec/ids.json.

Options : --max N   nombre maximal de lignes affichées pour un bloc (défaut 120)
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "spec" / "_sources"
DOCS = {
    "F": SRC / "specification-fonctionnelle-agent-livrables.md",
    "T": SRC / "specification-technique-agent-livrables.md",
}
LABEL = {"F": "fonctionnelle", "T": "technique"}

ID_RE = r"[A-Z]{2,4}(?:-[A-Z])?-(?:\d{1,3}|[A-H])"
ROW_RE = re.compile(r"^\|\s*(?:\*\*)?(" + ID_RE + r")\b")
HEAD_RE = re.compile(r"^(#{1,6})\s+(.*)$")
HEAD_ID_RE = re.compile(r"^(" + ID_RE + r")\b")
SECNUM_RE = re.compile(r"^(\d+(?:\.(?:\d+|[A-Z]))*)\.?\s")
ANNEX_RE = re.compile(r"^Annexe\s+([A-Z])\b")


class Doc:
    def __init__(self, key: str, path: pathlib.Path):
        self.key = key
        self.path = path
        self.lines = path.read_text(encoding="utf-8").split("\n")
        self.headings = []   # (lineno0, level, text, secnum|None, idref|None)
        self.rows = {}       # id -> [lineno0]
        self._scan()

    def _scan(self):
        in_fence = False
        for i, line in enumerate(self.lines):
            if line.startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            m = HEAD_RE.match(line)
            if m:
                level, text = len(m.group(1)), m.group(2).strip()
                sec = None
                sm = SECNUM_RE.match(text)
                if sm:
                    sec = sm.group(1)
                am = ANNEX_RE.match(text)
                if am:
                    sec = "Annexe-" + am.group(1)
                im = HEAD_ID_RE.match(text)
                self.headings.append((i, level, text, sec, im.group(1) if im else None))
                continue
            r = ROW_RE.match(line)
            if r:
                self.rows.setdefault(r.group(1), []).append(i)

    # --- utilitaires ---
    def block_end(self, idx_heading: int) -> int:
        start, level = self.headings[idx_heading][0], self.headings[idx_heading][1]
        for j in range(idx_heading + 1, len(self.headings)):
            if self.headings[j][1] <= level:
                return self.headings[j][0]
        return len(self.lines)

    def context_heading(self, lineno0: int) -> str:
        best = ""
        for (i, level, text, _s, _id) in self.headings:
            if i <= lineno0:
                best = text
            else:
                break
        return best

    def table_header(self, lineno0: int):
        top = lineno0
        while top - 1 >= 0 and self.lines[top - 1].startswith("|"):
            top -= 1
        if top + 1 < len(self.lines) and re.match(r"^\|[\s\-|:]+\|$", self.lines[top + 1]):
            return cells(self.lines[top])
        return None


def cells(line: str):
    return [c.strip() for c in line.strip().strip("|").split("|")]


_DOCS_CACHE = {}


def load(key: str) -> Doc:
    if key not in _DOCS_CACHE:
        _DOCS_CACHE[key] = Doc(key, DOCS[key])
    return _DOCS_CACHE[key]


def all_docs():
    return [load(k) for k in ("F", "T")]


# ---------- show ----------
def expand(arg: str):
    m = re.match(r"^(" + ID_RE + r")\.\.(" + ID_RE + r")$", arg)
    if not m:
        return [arg]
    a, b = m.group(1), m.group(2)
    pa, na = a.rsplit("-", 1)
    pb, nb = b.rsplit("-", 1)
    if pa != pb or not (na.isdigit() and nb.isdigit()):
        return [a, b]
    width = len(na)
    return [f"{pa}-{n:0{width}d}" for n in range(int(na), int(nb) + 1)]


def show_one(ident: str, maxlines: int) -> bool:
    found = False
    for d in all_docs():
        for ln in d.rows.get(ident, []):
            found = True
            hdr = d.table_header(ln)
            print(f"--- [{d.key}] {ident}  (spéc. {LABEL[d.key]}, ligne {ln + 1}, section « {d.context_heading(ln)} »)")
            row = cells(d.lines[ln])
            if hdr and len(hdr) == len(row):
                for h, v in zip(hdr, row):
                    print(f"  {h} : {v}")
            else:
                print("  " + d.lines[ln])
        for idx, (i, level, text, _s, idref) in enumerate(d.headings):
            if idref == ident:
                found = True
                end = d.block_end(idx)
                print(f"--- [{d.key}] fiche {ident}  (spéc. {LABEL[d.key]}, lignes {i + 1}–{end})")
                block = d.lines[i:end]
                for line in block[:maxlines]:
                    print(line)
                if len(block) > maxlines:
                    print(f"... ({len(block) - maxlines} lignes de plus ; relancer avec --max {len(block)})")
    return found


def cmd_show(args, maxlines):
    if not args:
        sys.exit("usage: spec.py show ID [ID ...]")
    missing = []
    for a in args:
        for ident in expand(a):
            if not show_one(ident, maxlines):
                missing.append(ident)
    if missing:
        print("\nIntrouvables :", ", ".join(missing))


# ---------- section ----------
def cmd_section(args, maxlines):
    if len(args) != 2 or args[0] not in DOCS:
        sys.exit("usage: spec.py section F|T CLE   (ex. section T 10.4 | section F UC-005 | section T Annexe-C)")
    d, key = load(args[0]), args[1]
    for idx, (i, level, text, sec, idref) in enumerate(d.headings):
        if sec == key or idref == key:
            end = d.block_end(idx)
            print(f"[{d.key}] {text}  (lignes {i + 1}–{end})\n")
            block = d.lines[i:end]
            for line in block[:maxlines]:
                print(line)
            if len(block) > maxlines:
                print(f"\n... ({len(block) - maxlines} lignes de plus ; relancer avec --max {len(block)})")
            return
    sys.exit(f"Section introuvable : {key}. Voir « spec.py toc {args[0]} ».")


# ---------- search ----------
def cmd_search(args, maxlines):
    if not args:
        sys.exit("usage: spec.py search TEXTE")
    needle = " ".join(args).lower()
    n = 0
    for d in all_docs():
        for i, line in enumerate(d.lines):
            if needle in line.lower():
                snippet = line.strip()
                if len(snippet) > 200:
                    snippet = snippet[:197] + "..."
                print(f"[{d.key}:{i + 1}] {snippet}")
                n += 1
                if n >= 40:
                    print("... (40 premiers résultats ; affiner la recherche)")
                    return
    if n == 0:
        print("Aucun résultat.")


# ---------- refs ----------
def cmd_refs(args, maxlines):
    if len(args) != 1:
        sys.exit("usage: spec.py refs ID")
    ident = args[0]
    pat = re.compile(r"(?<![A-Z0-9-])" + re.escape(ident) + r"(?![0-9])")
    n = 0
    for d in all_docs():
        for i, line in enumerate(d.lines):
            if ROW_RE.match(line) and ROW_RE.match(line).group(1) == ident:
                continue
            if pat.search(line):
                snippet = line.strip()
                if len(snippet) > 180:
                    snippet = snippet[:177] + "..."
                print(f"[{d.key}:{i + 1}] {snippet}")
                n += 1
                if n >= 40:
                    print("... (40 premières mentions)")
                    return
    if n == 0:
        print("Aucune mention (les plages « A à B » ne sont pas dépliées).")


# ---------- toc ----------
def cmd_toc(args, maxlines):
    if len(args) != 1 or args[0] not in DOCS:
        sys.exit("usage: spec.py toc F|T")
    d = load(args[0])
    for idx, (i, level, text, sec, idref) in enumerate(d.headings):
        if level in (2, 3):
            end = d.block_end(idx)
            kb = sum(len(x) + 1 for x in d.lines[i:end]) / 1024
            indent = "  " * (level - 2)
            print(f"{indent}{text}  [L{i + 1}–{end}, {kb:.0f} Ko]")


# ---------- milestone ----------
def cmd_milestone(args, maxlines):
    if len(args) != 1:
        sys.exit("usage: spec.py milestone MS-n")
    p = ROOT / "docs" / "milestones" / f"{args[0]}.md"
    if not p.exists():
        sys.exit(f"Brief introuvable : {p}")
    print(p.read_text(encoding="utf-8"))


# ---------- index ----------
def family_ranges(d: Doc):
    fam = {}
    for ident, lns in d.rows.items():
        prefix, _, num = ident.rpartition("-")
        fam.setdefault(prefix, []).append((ident, lns[0]))
    out = []
    for prefix, items in sorted(fam.items()):
        items.sort(key=lambda t: t[1])
        first, last = items[0], items[-1]
        out.append((prefix, first[0], last[0], len(items), first[1] + 1, last[1] + 1))
    return out


def cmd_index(args, maxlines):
    ids = {}
    md = ["# Index des spécifications (généré — ne pas modifier à la main)",
          "",
          "Régénérer : `python tools/spec.py index`. Les numéros de ligne renvoient aux fichiers maîtres de `docs/spec/_sources/`.",
          "**Ne pas ouvrir les fichiers maîtres en entier** : utiliser `python tools/spec.py show|section|search|refs`.",
          ""]
    for d in all_docs():
        total_kb = sum(len(x) + 1 for x in d.lines) / 1024
        md += [f"## Spécification {LABEL[d.key]} ({d.key}) — {len(d.lines)} lignes, {total_kb:.0f} Ko", ""]
        md += ["### Sections", "", "| Section | Lignes | Taille |", "|---|---|---|"]
        for idx, (i, level, text, sec, idref) in enumerate(d.headings):
            if level == 2:
                end = d.block_end(idx)
                kb = sum(len(x) + 1 for x in d.lines[i:end]) / 1024
                md.append(f"| {text} | {i + 1}–{end} | {kb:.0f} Ko |")
        md += ["", "### Familles d'identifiants", "", "| Préfixe | De | À | Nombre | Lignes |", "|---|---|---|---|---|"]
        for prefix, a, b, n, la, lb in family_ranges(d):
            md.append(f"| {prefix} | {a} | {b} | {n} | {la}–{lb} |")
        md.append("")
        for ident, lns in d.rows.items():
            ln = lns[0]
            ids.setdefault(ident, []).append({"doc": d.key, "line": ln + 1, "section": d.context_heading(ln),
                                              "text": cells(d.lines[ln])[1] if len(cells(d.lines[ln])) > 1 else ""})
        for (i, level, text, sec, idref) in d.headings:
            if idref:
                ids.setdefault(idref, []).append({"doc": d.key, "line": i + 1, "section": text, "text": text})
    out = ROOT / "docs" / "spec"
    (out / "INDEX.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (out / "ids.json").write_text(json.dumps(ids, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"INDEX.md et ids.json écrits ({len(ids)} identifiants).")


COMMANDS = {"show": cmd_show, "section": cmd_section, "search": cmd_search, "refs": cmd_refs,
            "toc": cmd_toc, "milestone": cmd_milestone, "index": cmd_index}


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    maxlines = 120
    argv = list(argv)
    if "--max" in argv:
        i = argv.index("--max")
        maxlines = int(argv[i + 1])
        del argv[i:i + 2]
    if not argv or argv[0] not in COMMANDS:
        print(__doc__)
        return 1
    COMMANDS[argv[0]](argv[1:], maxlines)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except BrokenPipeError:  # sortie coupée par `head` : sans importance
        sys.exit(0)
