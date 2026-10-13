#!/usr/bin/env python3
"""Check a recent-media scan catalogue against the scan's own rules.

    python scan_check.py <catalogue-dir> --scope scope.yaml [--json] [--strict]

Run it after check_catalogue.py (water-tenure-analysis skill), which checks the general record
rules. This script checks what is specific to a media scan:

errors
- a record resting only on social media, AI-generated or derived sources is graded above
  `uncorroborated` (social media are clues, never findings on their own);
- a social-media source records a personal @handle without being marked as an institutional
  account (private persons are never identified);
- a record takes a figure from a source whose page text could not be read (reliability_notes say
  the page loads by script, or UNVERIFIED) without marking that figure UNVERIFIED in figures_source;
warnings
- a source dated outside the scan window (background source types listed in the scope are allowed);
- a record matches one of the scope's exclusion terms (for review against the scope ruling);
- a record is located above the scope's minimum administrative level (the scan is place-based).

Exit 0 = no errors (and, with --strict, no warnings); 1 otherwise; 2 = usage error.
Needs PyYAML for a YAML scope (a JSON scope works with the standard library).
"""
from __future__ import annotations

import csv
import json
import pathlib
import re
import sys

CLUE_TYPES = {"social-media", "ai-generated", "derived-summary"}
UNREAD = re.compile(r"loads? by script|javascript|js-loaded|not loaded|unverified|could not be read", re.I)
HANDLE = re.compile(r"(?<![\w.])@[A-Za-z0-9_.]{2,}")


def read(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def split(cell):
    return [x.strip() for x in (cell or "").split(";") if x.strip()]


def load_scope(path):
    text = pathlib.Path(path).read_text(encoding="utf-8")
    if str(path).lower().endswith(".json"):
        return json.loads(text)
    import yaml
    return yaml.safe_load(text) or {}


def check(d, scope):
    d = pathlib.Path(d)
    sources = {s["source_id"].strip(): s for s in read(d / "sources.csv")}
    arrs = read(d / "arrangements.csv")
    errors, warnings = [], []
    win = scope.get("window") or {}
    lo, hi = str(win.get("from", "")), str(win.get("to", ""))
    background = set(scope.get("background_source_types") or [])
    excl = [t for t in (scope.get("exclude_terms") or []) if t]
    excl_re = re.compile(r"\b(" + "|".join(re.escape(t) for t in excl) + r")\b", re.I) if excl else None
    min_levels = int(scope.get("min_admin_levels") or 0)

    for sid, s in sources.items():
        st = (s.get("source_type") or "").strip()
        date = (s.get("date") or "").strip()
        if lo and hi and date and st not in background:
            if date[:len(lo)] < lo[:len(date)] or date[:len(hi)] > hi[:len(date)]:
                warnings.append(f"sources.csv {sid}: dated {date}, outside the scan window {lo} to {hi}")
        if st == "social-media":
            who = f"{s.get('author_org', '')} {s.get('title', '')}"
            notes = f"{s.get('author_org', '')} {s.get('reliability_notes', '')}".lower()
            if HANDLE.search(who) and "institutional" not in notes:
                errors.append(f"sources.csv {sid}: a personal @handle is recorded; write 'private account' "
                              "or mark the account as institutional in reliability_notes")

    for a in arrs:
        aid = (a.get("arrangement_id") or "").strip()
        ids = split(a.get("source_ids"))
        types = {(sources.get(x) or {}).get("source_type", "").strip() for x in ids}
        conf = (a.get("confidence") or "").strip()
        if ids and types and types <= CLUE_TYPES and conf != "uncorroborated":
            errors.append(f"{aid}: rests only on {', '.join(sorted(types))} but is graded '{conf}'; "
                          "social media are clues: grade it 'uncorroborated' and seek other evidence")
        fs = a.get("figures_source") or ""
        for x in ids:
            src = sources.get(x) or {}
            if UNREAD.search(src.get("reliability_notes") or "") and re.search(rf"(?<![\w-]){re.escape(x)}(?![\w-])", fs):
                for part in fs.split("|"):
                    if x in part and "UNVERIFIED" not in part:
                        errors.append(f"{aid}: figure from {x}, whose page text was not read, is not marked "
                                      f"UNVERIFIED in figures_source: '{part.strip()}'")
        text = " ".join(a.get(c) or "" for c in ("arrangement", "local_name", "classification_basis", "conflicts"))
        if excl_re:
            m = excl_re.search(text)
            if m:
                warnings.append(f"{aid}: mentions '{m.group(1)}', an exclusion term of the scope; keep it only "
                                "if the record is about tenure at a place, not about the excluded topic")
        levels = [p for p in (a.get("location_admin") or "").split(">") if p.strip()]
        if min_levels and len(levels) < min_levels:
            warnings.append(f"{aid}: located at {len(levels)} administrative levels; the scan is place-based "
                            f"(scope asks for {min_levels})")
    return errors, warnings, len(sources), len(arrs)


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = {a for a in argv if a.startswith("--")}
    scope_path = None
    if "--scope" in argv:
        i = argv.index("--scope")
        scope_path = argv[i + 1] if i + 1 < len(argv) else None
        args = [a for a in args if a != scope_path]
    if len(args) != 1 or not scope_path or flags - {"--scope", "--json", "--strict"}:
        print(__doc__)
        return 2
    errors, warnings, ns, na = check(args[0], load_scope(scope_path))
    failed = bool(errors) or ("--strict" in flags and bool(warnings))
    if "--json" in flags:
        print(json.dumps({"sources": ns, "arrangements": na, "errors": errors, "warnings": warnings,
                          "passed": not failed}, indent=1, ensure_ascii=False))
    else:
        for e in errors:
            print("ERROR", e)
        for w in warnings:
            print("WARN ", w)
        print(f"{ns} sources, {na} arrangements, {len(errors)} errors, {len(warnings)} warnings")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
