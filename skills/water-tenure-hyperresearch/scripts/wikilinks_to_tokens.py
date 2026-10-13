#!/usr/bin/env python3
"""Convert a hyperresearch report's [[note-id|pinpoint]] citations into report-skill footnotes.

    python wikilinks_to_tokens.py <report.md> <catalogue-dir> --out <chapter.md> [--prefix P]

Inside a hyperresearch run, statements cite vault notes as wikilinks, `[[note-id|p.34]]`. In a water
tenure run the catalogue registers each vault note as a source whose source_id IS the note id, so a
wikilink names a registered source. This script rewrites every run of adjacent wikilinks into one
pandoc footnote with citation tokens: `... figure [[abc|p.3]] [[def|l.12]].` becomes
`... figure^[{{abc}} p 3; {{def}} l 12.]`. The `water-tenure-report` skill's build.py then turns the
tokens into OSCOLA or APA references (put the output in a chapters folder as, for example,
`ch01-catalogue-report.md`, and list the catalogue as an input in the report config).

--prefix P matches the report config's `prefix` for this catalogue, so tokens name the merged ids.
Wikilinks whose note id is not in sources.csv are left as [[...]] and reported; register those
sources, or remove the statements. Standard library only. Exit 1 when any wikilink is unregistered.
"""
from __future__ import annotations

import csv
import pathlib
import re
import sys

LINK = r"\[\[([^\]|]+?)(?:\|([^\]]*))?\]\]"
RUN = re.compile(rf"[ \t]*{LINK}(?:[ \t,;]*{LINK})*")
ONE = re.compile(LINK)


def pinpoint(p: str | None) -> str:
    """'p.34' -> '34' (OSCOLA page), 'l.212' -> 'l 212', 'slide 3' stays."""
    p = (p or "").strip()
    if not p:
        return ""
    m = re.match(r"^pp?\.?\s*(\d[\d\-,\s]*)$", p, re.I)
    if m:
        return m.group(1).strip()
    return re.sub(r"^([A-Za-z]+)\.\s*", r"\1 ", p)


def convert(text: str, known: set[str], prefix: str = "") -> tuple[str, list[str], int]:
    unknown: list[str] = []
    count = 0

    def rep(m: re.Match) -> str:
        nonlocal count
        parts, keep = [], []
        for lm in ONE.finditer(m.group(0)):
            nid, pin = lm.group(1).strip(), lm.group(2)
            if nid in known:
                parts.append(f"{{{{{prefix}{nid}}}}} {pinpoint(pin)}".strip())
            else:
                unknown.append(nid)
                keep.append(lm.group(0))
        if not parts:
            return m.group(0)
        count += 1
        note = "^[" + "; ".join(parts) + ".]"
        return note + ((" " + " ".join(keep)) if keep else "")

    return RUN.sub(rep, text), sorted(set(unknown)), count


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    opts = {}
    for k in ("--out", "--prefix"):
        if k in argv:
            i = argv.index(k)
            if i + 1 >= len(argv):
                print(__doc__)
                return 2
            opts[k] = argv[i + 1]
            args = [a for a in args if a != argv[i + 1]]
    if len(args) != 2 or "--out" not in opts:
        print(__doc__)
        return 2
    report, cat = pathlib.Path(args[0]), pathlib.Path(args[1])
    with open(cat / "sources.csv", encoding="utf-8-sig", newline="") as f:
        known = {r["source_id"].strip() for r in csv.DictReader(f)}
    text, unknown, n = convert(report.read_text(encoding="utf-8"), known, opts.get("--prefix", ""))
    out = pathlib.Path(opts["--out"])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {out}: {n} footnotes from wikilinks; {len(unknown)} unregistered note ids")
    for u in unknown:
        print("  UNREGISTERED", u)
    return 1 if unknown else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
