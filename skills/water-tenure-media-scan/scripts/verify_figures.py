#!/usr/bin/env python3
"""Check that every figure a catalogue attributes to a source appears in that source's text.

    python verify_figures.py <catalogue-dir> --cache DIR [--fetch] [--json OUT] [--report-only]

For each record, `figures_source` says which source states each number, for example
`25 ha; 12 days: K01 para 4 | Rp 150,000 per tank: K02 para 4 (UNVERIFIED)`. The script reads the
text of each cited source from DIR/<source_id>.txt and looks for every number of two or more
digits, after removing thousands and decimal separators on both sides (so 150,000, 150.000 and
Rp150.000 all match). It reports, per figure: found, NOT FOUND, no text for the source, or not
checked (single-digit numbers cannot be matched reliably; read the source).

With --fetch, web sources (http/https) without a cached file are downloaded once and their visible
text is saved to DIR; this needs network access and the user's agreement. Pages whose body loads by
script return little text: open them in a browser, save the article text to DIR/<id>.txt by hand,
and keep the figure marked UNVERIFIED until it is found.

"found" only means the digits occur in the source text; a person still reads the sentence around
them before treating the figure as verified. Figures already marked UNVERIFIED are reported
separately so that a figure found later can have its mark removed.

Exit 1 when a figure is NOT FOUND (unless --report-only); 0 otherwise. Standard library only.
"""
from __future__ import annotations

import csv
import html
import json
import pathlib
import re
import sys
import urllib.request

NUM = re.compile(r"\d[\d.,]*\d|\d")


def read(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def digits(s: str) -> str:
    return re.sub(r"(?<=\d)[.,](?=\d)", "", s)


def parse_figures_source(fs: str, known: set[str]) -> list[tuple[str, list[str], bool]]:
    """Return (figure text, [source ids], marked_unverified) entries from a figures_source cell."""
    entries: list[list] = []
    for block in (fs or "").split("|"):
        pending = []
        for chunk in block.split(";"):
            chunk = chunk.strip()
            if not chunk:
                continue
            ids = [x for x in re.findall(r"[A-Za-z][A-Za-z0-9_-]*", chunk) if x in known]
            if ":" in chunk:
                fig, src = chunk.rsplit(":", 1)
                fig = "; ".join(pending + [fig.strip()])
                pending = []
                sids = [x for x in re.findall(r"[A-Za-z][A-Za-z0-9_-]*", src) if x in known]
                entries.append([fig, sids, "UNVERIFIED" in chunk.upper()])
            elif entries and ids and chunk.split()[0].strip("()") in known:
                entries[-1][1] += ids
                entries[-1][2] = entries[-1][2] or "UNVERIFIED" in chunk.upper()
            else:
                pending.append(chunk)
    return [(f, s, u) for f, s, u in entries]


def page_text(raw: str) -> str:
    t = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", " ", raw)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return re.sub(r"\s+", " ", t)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (verify_figures.py)"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return page_text(r.read().decode("utf-8", "ignore"))


def main(argv: list[str]) -> int:
    args, opts = [], {}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--cache", "--json"):
            if i + 1 >= len(argv):
                print(__doc__)
                return 2
            opts[a] = argv[i + 1]
            i += 2
            continue
        if a in ("--fetch", "--report-only"):
            opts[a] = True
        elif a.startswith("--"):
            print(__doc__)
            return 2
        else:
            args.append(a)
        i += 1
    if len(args) != 1 or "--cache" not in opts:
        print(__doc__)
        return 2
    d, cache = pathlib.Path(args[0]), pathlib.Path(opts["--cache"])
    cache.mkdir(parents=True, exist_ok=True)
    sources = {s["source_id"].strip(): s for s in read(d / "sources.csv")}
    texts: dict[str, str | None] = {}

    def text_of(sid: str) -> str | None:
        if sid in texts:
            return texts[sid]
        f = cache / f"{sid}.txt"
        if f.exists():
            texts[sid] = f.read_text(encoding="utf-8", errors="ignore")
        elif opts.get("--fetch") and (sources[sid].get("path_or_url") or "").startswith(("http://", "https://")):
            try:
                t = fetch(sources[sid]["path_or_url"])
                f.write_text(t, encoding="utf-8")
                texts[sid] = t
            except Exception as exc:  # network errors are reported, not raised
                print(f"fetch failed for {sid}: {str(exc)[:120]}")
                texts[sid] = None
        else:
            texts[sid] = None
        return texts[sid]

    results = []
    for a in read(d / "arrangements.csv"):
        for fig, sids, unverified in parse_figures_source(a.get("figures_source"), set(sources)):
            for n in NUM.findall(fig):
                dn = digits(n)
                if len(dn) < 2:
                    results.append(dict(record=a["arrangement_id"], figure=n, sources=sids, status="not checked (single digit)",
                                        marked_unverified=unverified))
                    continue
                avail = [s for s in sids if text_of(s)]
                if not avail:
                    status = "no text"
                else:
                    status = "found" if any(dn in digits(text_of(s)) for s in avail) else "NOT FOUND"
                results.append(dict(record=a["arrangement_id"], figure=n, sources=sids, status=status,
                                    marked_unverified=unverified))
    counts: dict[str, int] = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    checked = sum(v for k, v in counts.items() if k in ("found", "NOT FOUND"))
    print(f"{counts.get('found', 0)} of {checked} checkable figures found in their source text; "
          f"{counts.get('no text', 0)} without source text; {counts.get('not checked (single digit)', 0)} single-digit")
    for r in results:
        if r["status"] != "found":
            print(f"  {r['status']:<28} {r['record']} {r['figure']} ({', '.join(r['sources']) or 'no source id'})")
        elif r["marked_unverified"]:
            print(f"  found, still marked UNVERIFIED {r['record']} {r['figure']}: read the sentence, then update the record")
    if "--json" in opts:
        pathlib.Path(opts["--json"]).write_text(json.dumps({"counts": counts, "results": results}, indent=1,
                                                           ensure_ascii=False), encoding="utf-8")
    return 1 if counts.get("NOT FOUND") and not opts.get("--report-only") else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
