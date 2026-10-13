#!/usr/bin/env python3
"""Merge the partial catalogues written by the stage C group agents into one catalogue.

    python merge_partials.py <partials-dir> --out <catalogue-dir> [--force]

<partials-dir> holds arrangements-<GROUP>.csv and sources-<GROUP>.csv pairs (for example
research/runs/<tag>/temp/catalogue/). The script writes <catalogue-dir>/arrangements.csv and
sources.csv with the template column order of the water-tenure-analysis skill:

- sources are de-duplicated by source_id (the vault note id); when two groups registered the same id
  with different field values, the first is kept and every difference is reported for a person to
  settle;
- arrangement ids must be unique across groups; a collision stops the merge;
- columns a group added that are not in the template are dropped and reported.

It then tells you to run check_catalogue.py and build_matrix.py on the result. It refuses to
overwrite an existing catalogue unless --force is given. Standard library only.
"""
from __future__ import annotations

import csv
import pathlib
import sys

ANALYSIS = pathlib.Path(__file__).resolve().parents[2] / "water-tenure-analysis" / "assets"
FALLBACK_SRC = ["source_id", "source_type", "title", "author_org", "date", "path_or_url", "locator_scheme",
                "derived_from", "language", "respondent_code", "collected_by", "anonymised", "verifiability",
                "reliability_notes"]


def header(name: str, fallback: list[str] | None = None) -> list[str]:
    p = ANALYSIS / name
    if p.exists():
        with open(p, encoding="utf-8-sig", newline="") as f:
            return next(csv.reader(f))
    if fallback:
        return fallback
    raise SystemExit(f"template {p} not found; install the water-tenure-analysis skill beside this one")


def read(path: pathlib.Path) -> list[dict[str, str]]:
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write(path: pathlib.Path, rows: list[dict], cols: list[str]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def merge(partials: pathlib.Path) -> tuple[list[dict], list[dict], list[str], list[str]]:
    a_cols, s_cols = header("arrangements.template.csv"), header("sources.template.csv", FALLBACK_SRC)
    groups = sorted(p.stem.split("-", 1)[1] for p in partials.glob("arrangements-*.csv"))
    if not groups:
        raise SystemExit(f"no arrangements-<GROUP>.csv files in {partials}")
    sources: dict[str, dict] = {}
    arrs: list[dict] = []
    seen: dict[str, str] = {}
    notes, errors = [], []
    for g in groups:
        sp = partials / f"sources-{g}.csv"
        if not sp.exists():
            errors.append(f"group {g}: sources-{g}.csv is missing")
            continue
        for s in read(sp):
            sid = (s.get("source_id") or "").strip()
            extra = set(s) - set(s_cols)
            if extra:
                notes.append(f"group {g}: sources columns dropped: {sorted(extra)}")
            if sid in sources:
                diff = [c for c in s_cols if (s.get(c) or "").strip() != (sources[sid].get(c) or "").strip()]
                if diff:
                    notes.append(f"source {sid}: groups disagree on {diff}; kept the first registration")
                continue
            sources[sid] = s
        for a in read(partials / f"arrangements-{g}.csv"):
            aid = (a.get("arrangement_id") or "").strip()
            if aid in seen:
                errors.append(f"arrangement id {aid} used by groups {seen[aid]} and {g}")
            seen[aid] = g
            extra = set(a) - set(a_cols)
            if extra:
                notes.append(f"group {g}: arrangements columns dropped: {sorted(extra)}")
            arrs.append(a)
    return arrs, list(sources.values()), sorted(set(notes)), errors


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    out = None
    if "--out" in argv:
        i = argv.index("--out")
        out = argv[i + 1] if i + 1 < len(argv) else None
        args = [a for a in args if a != out]
    if len(args) != 1 or not out:
        print(__doc__)
        return 2
    out_dir = pathlib.Path(out)
    if (out_dir / "arrangements.csv").exists() and "--force" not in argv:
        print(f"ERROR {out_dir / 'arrangements.csv'} exists; use --force to overwrite", file=sys.stderr)
        return 1
    arrs, srcs, notes, errors = merge(pathlib.Path(args[0]))
    for n in notes:
        print("NOTE ", n)
    for e in errors:
        print("ERROR", e)
    if errors:
        return 1
    out_dir.mkdir(parents=True, exist_ok=True)
    write(out_dir / "arrangements.csv", arrs, header("arrangements.template.csv"))
    write(out_dir / "sources.csv", srcs, header("sources.template.csv", FALLBACK_SRC))
    print(f"wrote {out_dir}: {len(arrs)} arrangements, {len(srcs)} sources. Next: check_catalogue.py and "
          "build_matrix.py from the water-tenure-analysis skill.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
