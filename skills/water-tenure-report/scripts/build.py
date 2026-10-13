#!/usr/bin/env python3
"""Assemble the report: resolve citation tokens into footnotes, number figures, insert Part pages,
run mechanical checks, and build .docx files with pandoc.

    python build.py <config.yaml> [--annexes] [--check-only] [--strict]

Run merge.py first (it writes <work>/data/sources.json), then figures.py and, for --annexes,
annexes.py. Chapters are the ch<NN>-*.md files in `chapters_dir`, assembled in number order.

Citations. Inside a pandoc inline footnote ^[...], a source is cited only by token: {{S01}},
{{INT-V1-01}} or, for a private social-media account, {{NT01|anon}}, followed by a pinpoint.
- OSCOLA (report.citation_style: oscola): the first use of a source prints its full reference,
  later uses print the short form and "(n X)", X being the footnote of first use.
- APA (apa): every use prints the author-date short form, and a reference list is appended.
Tokens may name a source in the merged register or a `reserved_sources` key in the config.

Outputs in <work>/out/: main.md, <output_name>.docx, build-report.json, sources-cited.json, and
with --annexes: annexes.md, <output_name>-annexes.docx.

Exit 1 when a token does not resolve, a token sits outside a footnote, or a figure file is
missing; with --strict, also on warnings (vocabulary hits, em dashes, footnotes resting only on
social media outside a Clues section, unknown record ids). --check-only skips pandoc.
"""
from __future__ import annotations

import collections
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from citations import anonymise  # noqa: E402
from common import TOKEN, die, load_config, read_csv  # noqa: E402

SKILL_DIR = Path(__file__).resolve().parents[1]
RECORD_REF = re.compile(r"\(((?:[A-Z]{1,2}\d{2,4}[a-z]?)(?:\s*[,;]\s*[A-Z]{1,2}\d{2,4}[a-z]?)*)\)")
FIG = re.compile(r"!\[(.*?)\]\((figures/[^)\s]+)\)(\{[^}]*\})?")
NON_EVIDENCE = {"E5", "D"}


def find_pandoc(cfg) -> str | None:
    for cand in (os.environ.get("PANDOC"), cfg.get("docx.pandoc"), shutil.which("pandoc"),
                 r"C:\Program Files\Pandoc\pandoc.exe", "/usr/local/bin/pandoc", "/opt/homebrew/bin/pandoc"):
        if cand and Path(cand).exists():
            return str(cand)
    return None


def footnote_spans(text: str):
    """Yield (start, end) of each ^[...] inline footnote; end is the index of the closing bracket."""
    i = 0
    while True:
        s = text.find("^[", i)
        if s < 0:
            return
        depth, j = 0, s + 1
        while j < len(text):
            if text[j] == "[":
                depth += 1
            elif text[j] == "]":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        yield s, j
        i = j + 1


def chapter_files(chdir: Path) -> list[tuple[int, Path]]:
    out = []
    for f in chdir.glob("ch*.md"):
        m = re.match(r"ch(\d+)", f.name)
        if m:
            out.append((int(m.group(1)), f))
    return sorted(out)


def assemble(cfg, chdir: Path) -> str:
    parts = {int(p["first_chapter"]): p for p in (cfg.get("parts") or [])}
    blocks = []
    for num, f in chapter_files(chdir):
        if num in parts:
            p = parts[num]
            intro = (p.get("intro") or "").strip()
            blocks.append(f"# {p['title']} {{.unnumbered .part}}\n\n{intro}\n")
        blocks.append(f.read_text(encoding="utf-8").strip() + "\n")
    return "\n\n".join(blocks)


def number_figures(doc: str) -> tuple[str, list[tuple[str, str, str]]]:
    state = {"label": "P", "k": 0}
    lines, figs = [], []
    for line in doc.split("\n"):
        m = re.match(r"# Chapter (\d+)\.", line)
        a = re.match(r"# Annex ([A-Z])\.", line)
        if m:
            state.update(label=m.group(1), k=0)
        elif a:
            state.update(label=a.group(1), k=0)
        elif re.match(r"# Executive Summary", line):
            state.update(label="ES", k=0)
        fm = FIG.match(line.strip())
        if fm:
            state["k"] += 1
            label = f"Figure {state['label']}.{state['k']}"
            figs.append((label, fm.group(1), fm.group(2)))
            attrs = fm.group(3) or "{width=100%}"
            line = f"![{label}. {fm.group(1)}]({fm.group(2)}){attrs}"
        lines.append(line)
    return "\n".join(lines), figs


class Resolver:
    def __init__(self, cfg, sources: dict):
        self.style = (cfg.get("report.citation_style", "oscola") or "oscola").lower()
        self.src = sources
        self.reserved = cfg.get("reserved_sources") or {}
        self.first: dict[str, int] = {}
        self.used: set[str] = set()
        self.unresolved: list[tuple[str, int]] = []
        self.grade_uses: collections.Counter = collections.Counter()
        self.apa_refs: dict[str, str] = {}

    def forms(self, key: str, anon: bool) -> tuple[str, str] | None:
        if key in self.reserved:
            r = self.reserved[key]
            full = r.get("apa" if self.style == "apa" else "oscola") or r.get("oscola") or key
            return full, r.get("short") or full
        if key in self.src:
            s = self.src[key]
            full, short = s["ref"], s["short"]
            if anon:
                full = anonymise(full)
                short = "Post by a private account"
            self.grade_uses[s["grade"]] += 1
            return full, short
        return None

    def footnote(self, body: str, n: int) -> str:
        def rep(m: re.Match) -> str:
            key, anon = m.group(1), bool(m.group(2))
            f = self.forms(key, anon)
            if f is None:
                self.unresolved.append((key, n))
                return f"[UNRESOLVED SOURCE {key}]"
            full, short = f
            self.used.add(key)
            if self.style == "apa":
                self.apa_refs[key] = full
                return short
            if key not in self.first:
                self.first[key] = n
                return full
            return f"{short} (n {self.first[key]})"
        body = TOKEN.sub(rep, body).strip()
        if body and not body.endswith((".", "?", "!")):
            body += "."
        return body

    def resolve(self, doc: str) -> tuple[str, int]:
        out, last, n = [], 0, 0
        for s, e in footnote_spans(doc):
            n += 1
            out.append(doc[last:s] + "^[" + self.footnote(doc[s + 2:e], n) + "]")
            last = e + 1
        out.append(doc[last:])
        return "".join(out), n


def e5_only_footnotes(doc: str, sources: dict, reserved: dict) -> list[str]:
    """Footnotes whose source tokens are all E5 or D, outside a section headed 'Clues'."""
    heads = [(m.start(), m.group(2)) for m in re.finditer(r"(?m)^(#{1,4})\s+(.*)$", doc)]
    found = []
    for s, e in footnote_spans(doc):
        keys = [m.group(1) for m in TOKEN.finditer(doc[s:e]) if m.group(1) not in reserved]
        grades = [sources[k]["grade"] for k in keys if k in sources]
        if not grades or any(g not in NON_EVIDENCE for g in grades):
            continue
        head = next((h for pos, h in reversed(heads) if pos < s), "")
        if "clue" in head.lower():
            continue
        found.append(f"{head[:60]}: {', '.join(keys)}")
    return found


def checks(cfg, doc_tokens: str, doc_final: str, work: Path, sources: dict) -> dict:
    rep: dict = {}
    body = doc_final
    for s, e in reversed(list(footnote_spans(body))):
        body = body[:s] + body[e + 1:]
    outside = [m.group(1) for m in TOKEN.finditer(body)]
    rep["tokens_outside_footnotes"] = sorted(set(outside))
    vocab = {}
    for w in cfg.get("vocab_check") or []:
        c = len(re.findall(r"\b" + re.escape(w) + r"\b", body, re.I))
        if c:
            vocab[w] = c
    rep["vocab_hits"] = vocab
    rep["em_dashes"] = body.count("\u2014")
    rep["figures_missing"] = sorted({p for p in re.findall(r"\]\((figures/[^)\s]+)\)", doc_final)
                                     if not (work / p).exists()})
    rep["e5_only_footnotes"] = e5_only_footnotes(doc_tokens, sources, cfg.get("reserved_sources") or {})
    known = set()
    master = work / "data" / "master_arrangements.csv"
    if master.exists():
        known = {r["arrangement_id"] for r in read_csv(master)}
    cited = {x.strip() for m in RECORD_REF.finditer(body) for x in re.split(r"[,;]", m.group(1))}
    rep["record_ids_cited"] = len(cited & known)
    rep["record_ids_unknown"] = sorted(cited - known) if known else []
    rep["words_main_text"] = len(body.split())
    return rep


def yaml_str(s: str) -> str:
    return json.dumps(str(s), ensure_ascii=False)


def metadata(cfg, subtitle: str | None = None) -> str:
    r = cfg.get("report") or {}
    lines = ["---", f"title: {yaml_str(r.get('title', 'Water tenure report'))}"]
    sub = subtitle or r.get("subtitle")
    if sub:
        lines.append(f"subtitle: {yaml_str(sub)}")
    authors = r.get("authors") or []
    if authors:
        lines.append("author:")
        lines += [f"- {yaml_str(a)}" for a in authors]
    for k in ("date", "lang"):
        if r.get(k):
            lines.append(f"{k}: {yaml_str(r[k])}")
    lines += ["toc-title: Contents", "---", ""]
    head = "\n".join(lines) + "\n"
    if r.get("notice"):
        head += f"> **{r['notice']}**\n\n"
    return head


def reference_doc(cfg, work: Path) -> Path | None:
    for cand in (cfg.rel(cfg.get("docx.reference_doc")), work / "reference.docx",
                 SKILL_DIR / "assets" / "reference.docx"):
        if cand and cand.exists():
            return cand
    return None


def pandoc(pandoc_bin: str, src: Path, dst: Path, work: Path, ref: Path | None) -> tuple[int, str]:
    cmd = [pandoc_bin, str(src), "-o", str(dst), "--toc", "--toc-depth=2", f"--resource-path={work}"]
    if ref:
        cmd.append(f"--reference-doc={ref}")
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, (r.stderr or "")[-1500:]


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    flags = {a for a in argv if a.startswith("--")}
    if len(args) != 1 or flags - {"--annexes", "--check-only", "--strict"}:
        print(__doc__)
        return 2
    cfg = load_config(args[0])
    work = cfg.work
    out = work / "out"
    sj = work / "data" / "sources.json"
    if not sj.exists():
        die("no sources.json; run merge.py first")
    sources = json.loads(sj.read_text(encoding="utf-8"))
    chdir = cfg.rel(cfg.get("chapters_dir", "chapters"))
    if not chdir or not chdir.is_dir() or not chapter_files(chdir):
        die(f"no ch<NN>-*.md chapter files in {chdir}")

    doc = assemble(cfg, chdir)
    doc, figs = number_figures(doc)
    res = Resolver(cfg, sources)
    final, n_notes = res.resolve(doc)
    rep = checks(cfg, doc, final, work, sources)

    if figs:
        lof = "# List of Figures {.unnumbered}\n\n" + "\n".join(f"- {lab}. {cap}" for lab, cap, _ in figs) + "\n\n"
        i = final.find(" {.unnumbered .part}")
        i = final.rfind("\n# ", 0, i) + 1 if i > 0 else final.find("# Chapter 1.")
        final = (final[:i] + lof + final[i:]) if i > 0 else lof + final
    if res.style == "apa" and res.apa_refs:
        final += "\n\n# References {.unnumbered}\n\n" + "\n\n".join(sorted(res.apa_refs.values(), key=str.lower)) + "\n"
    # Tokens left in the running text are errors; print them visibly rather than as template syntax.
    final_body = TOKEN.sub(lambda m: f"[{m.group(1)}]", final)
    name = cfg.get("report.output_name", "water-tenure-report")
    (out / "main.md").write_text(metadata(cfg) + final_body, encoding="utf-8")

    report = {"style": res.style, "footnotes": n_notes, "unresolved": res.unresolved,
              "sources_cited": len(res.used), "grade_uses": dict(res.grade_uses), "figures": len(figs), **rep}
    errors = bool(res.unresolved or rep["tokens_outside_footnotes"] or rep["figures_missing"])
    warnings = bool(rep["vocab_hits"] or rep["em_dashes"] or rep["e5_only_footnotes"] or rep["record_ids_unknown"])

    docx_written = []
    if "--annexes" in flags:
        parts = []
        summ_path = cfg.rel(cfg.get("ai_use.citecheck_summary")) or (work / "data" / "citecheck-summary.md")
        summary = summ_path.read_text(encoding="utf-8") if summ_path.exists() else "(Cite-check results not yet recorded.)"
        for L in [x.upper() for x in (cfg.get("annexes") or list("ABCDEFGHIJK"))]:
            f = work / "annexes" / f"annex-{L.lower()}.md"
            if not f.exists():
                die(f"missing {f}; run annexes.py first")
            t = f.read_text(encoding="utf-8").replace("{{CITECHECK-SUMMARY}}", summary)
            parts.append(number_figures(t)[0])
        sub = (cfg.get("report.subtitle_annexes") or "Annexes")
        (out / "annexes.md").write_text(metadata(cfg, sub) + "\n\n".join(parts), encoding="utf-8")

    if "--check-only" not in flags and not errors:
        pb = find_pandoc(cfg)
        if not pb:
            die("pandoc not found: install it (https://pandoc.org/installing.html) or set PANDOC; "
                "main.md was written, so the text can still be read")
        ref = reference_doc(cfg, work)
        report["reference_doc"] = ref.name if ref else "pandoc default"
        code, err = pandoc(pb, out / "main.md", out / f"{name}.docx", work, ref)
        report["pandoc_main"] = {"exit": code, "stderr": err}
        if code == 0:
            docx_written.append(f"{name}.docx")
        if "--annexes" in flags:
            code2, err2 = pandoc(pb, out / "annexes.md", out / f"{name}-annexes.docx", work, ref)
            report["pandoc_annexes"] = {"exit": code2, "stderr": err2}
            if code2 == 0:
                docx_written.append(f"{name}-annexes.docx")
        errors = errors or code != 0 or ("--annexes" in flags and code2 != 0)
    report["docx"] = docx_written

    with open(out / "build-report.json", "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=1, ensure_ascii=False)
    with open(out / "sources-cited.json", "w", encoding="utf-8") as fh:
        json.dump(sorted(res.used), fh, indent=0)
    print(json.dumps({k: report[k] for k in ("footnotes", "sources_cited", "figures", "unresolved",
                                              "tokens_outside_footnotes", "figures_missing", "vocab_hits",
                                              "em_dashes", "e5_only_footnotes", "record_ids_unknown",
                                              "words_main_text", "docx")}, indent=1, ensure_ascii=False))
    if errors:
        return 1
    return 1 if ("--strict" in flags and warnings) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
