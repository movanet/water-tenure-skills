#!/usr/bin/env python3
"""Write a publication copy of a checked catalogue, ready for a public map.

    python publication_copy.py <catalogue-dir> --out <publication-dir>
        [--include-uncorroborated] [--sensitive-precision 2] [--precision 4]

The copy keeps the catalogue format (sources.csv, arrangements.csv) so the storymap importer
(tools/import_catalogue.py in movanet/water-tenure-storymap) can read it, and applies the
data-protection rules before anything leaves the team:

- adds a `sensitivity` column: `aggregate_only` for sensitive tenure types (informal, impossible,
  unrecognised, assumed), sacred or ritual sites (use code H2, or words such as sacred or keramat),
  records whose text mentions an allegation (bribery, extortion, threats), uncorroborated records, and
  records citing a consent-restricted (verifiability `restricted`) or non-anonymised source; `public`
  otherwise. The importer applies the last rule too, and an explicit column overrides its own logic,
  so this copy is never less strict than the importer. The importer honours the
  column, and the storymap API jitters aggregate_only points on public reads;
- rounds the coordinates of aggregate_only records to --sensitive-precision decimals (default 2,
  about 1 km) and of the others to --precision (default 4, about 10 m), so exact sensitive points
  never leave the team even before the API's own jitter;
- drops records resting only on social media, AI-generated or derived sources, and uncorroborated
  records unless --include-uncorroborated;
- clears verbatim quotes and translations, gedsi_notes, perceived_security, notes, respondent codes,
  and the paths of sources a reader cannot open (replaced by "on file with the research team");
- replaces interview and focus-group codes in the remaining text with "[respondent]".

Standard library only. Prints a summary; exit 0 on success, 2 on usage error.
"""
from __future__ import annotations

import csv
import json
import pathlib
import re
import sys

SENSITIVE_TYPES = {"informal", "impossible", "unrecognised", "assumed"}
ALLEGATION = re.compile(r"brib|suap|mafia|extort|pungli|threat|ancam|intimidat|allege|dugaan", re.I)
SACRED = re.compile(r"sacred|keramat|holy|shrine|makam|grave|ritual site|sesaji", re.I)
CODES = re.compile(r"\b(INT|FGD|KII|WS)-[A-Z0-9-]+\b")
CLUE_ONLY = {"social-media", "ai-generated", "derived-summary"}
CLOSED = {"restricted", "team", "drive-only", "lost"}
CLEAR_ARR = ("quote_original", "quote_translation", "gedsi_notes", "perceived_security", "notes")
COORD = re.compile(r"^\s*(-?\d{1,2}(?:\.\d+)?)\s*,\s*(-?\d{1,3}(?:\.\d+)?)\s*$")


def read(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return list(r), list(r.fieldnames or [])


def write(path, rows, cols):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def split(cell):
    return [x.strip() for x in (cell or "").split(";") if x.strip()]


def sensitivity(a: dict, srcs: list[dict]) -> str:
    text = " ".join(a.get(c) or "" for c in ("arrangement", "conflicts", "notes", "local_name", "water_source"))
    if ((a.get("tenure_type") or "").strip() in SENSITIVE_TYPES or "H2" in split(a.get("water_use"))
            or ALLEGATION.search(text) or SACRED.search(text)
            or (a.get("confidence") or "").strip() == "uncorroborated"
            or any((s.get("verifiability") or "").strip() == "restricted" or (s.get("anonymised") or "").strip() == "no"
                   for s in srcs)):
        return "aggregate_only"
    return "public"


def make_copy(d, include_uncorroborated=False, precision=4, sensitive_precision=2):
    d = pathlib.Path(d)
    sources, s_cols = read(d / "sources.csv")
    arrs, a_cols = read(d / "arrangements.csv")
    by_id = {s["source_id"].strip(): s for s in sources}
    out, dropped = [], {"clue_or_ai_only": [], "uncorroborated": []}
    for a in arrs:
        aid = a["arrangement_id"].strip()
        srcs = [by_id[x] for x in split(a.get("source_ids")) if x in by_id]
        if srcs and all((s.get("source_type") or "").strip() in CLUE_ONLY for s in srcs):
            dropped["clue_or_ai_only"].append(aid)
            continue
        if (a.get("confidence") or "").strip() == "uncorroborated" and not include_uncorroborated:
            dropped["uncorroborated"].append(aid)
            continue
        b = dict(a)
        b["sensitivity"] = sensitivity(a, srcs)
        m = COORD.match(a.get("coordinates") or "")
        if m:
            nd = sensitive_precision if b["sensitivity"] == "aggregate_only" else precision
            b["coordinates"] = f"{round(float(m.group(1)), nd)},{round(float(m.group(2)), nd)}"
        for c in CLEAR_ARR:
            if c in b:
                b[c] = ""
        for c in b:
            if c not in ("source_ids", "locators", "arrangement_id") and isinstance(b[c], str):
                b[c] = CODES.sub("[respondent]", b[c])
        out.append(b)
    pub_sources = []
    for s in sources:
        t = dict(s)
        t["respondent_code"] = ""
        if (t.get("verifiability") or "").strip() in CLOSED or not (t.get("path_or_url") or "").lower().startswith("http"):
            t["path_or_url"] = "on file with the research team"
        pub_sources.append(t)
    cols = a_cols + (["sensitivity"] if "sensitivity" not in a_cols else [])
    return out, cols, pub_sources, s_cols, dropped


def main(argv):
    args, opts = [], {}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--out", "--precision", "--sensitive-precision"):
            if i + 1 >= len(argv):
                print(__doc__)
                return 2
            opts[a] = argv[i + 1]
            i += 2
            continue
        if a == "--include-uncorroborated":
            opts[a] = True
        elif a.startswith("--"):
            print(__doc__)
            return 2
        else:
            args.append(a)
        i += 1
    if len(args) != 1 or "--out" not in opts:
        print(__doc__)
        return 2
    arrs, a_cols, srcs, s_cols, dropped = make_copy(args[0], "--include-uncorroborated" in opts,
                                                     int(opts.get("--precision", 4)),
                                                     int(opts.get("--sensitive-precision", 2)))
    out = pathlib.Path(opts["--out"])
    out.mkdir(parents=True, exist_ok=True)
    write(out / "arrangements.csv", arrs, a_cols)
    write(out / "sources.csv", srcs, s_cols)
    print(json.dumps({"written": str(out), "records": len(arrs),
                      "aggregate_only": sum(1 for a in arrs if a["sensitivity"] == "aggregate_only"),
                      "with_coordinates": sum(1 for a in arrs if (a.get("coordinates") or "").strip()),
                      "dropped": {k: v for k, v in dropped.items() if v}}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
