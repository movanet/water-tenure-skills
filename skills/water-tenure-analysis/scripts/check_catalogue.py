#!/usr/bin/env python3
"""Check a water-tenure catalogue before it goes to a human reviewer.

    python check_catalogue.py <catalogue-dir> [--json] [--strict]

The directory must hold sources.csv and arrangements.csv (columns: see
references/record-schema.md). Exit 0 = no errors; exit 1 = errors found (or,
with --strict, warnings found); exit 2 = usage error. Warnings do not fail the
run by default but must be read. --json prints a machine-readable result.

What it enforces, and why:
- every arrangement cites at least one registered source WITH a locator,
  because a citation a human cannot open at the right place is not a citation;
- every source has a path or URL, for the same reason;
- vocabularies (tenure type, source type, confidence, FAO use codes) are
  closed, so the catalogue can be cross-tabulated without hand-cleaning;
- legal_flag holds questions for a lawyer, not conclusions; a flag without a
  question mark, or one that asserts legality, is an error;
- "triangulated" needs >=3 independent origins and >=2 primary source types;
  "corroborated" needs >=2 independent origins. A source's origin is its
  derived_from value when set (a deck and a summary drawn from the same
  fieldwork share one origin), otherwise its own id. Derived and AI-generated
  sources never count as a type;
- AI-generated sources may never be the only support for a record.

Standard library only (Python 3.9+).
"""
import csv
import json
import pathlib
import re
import sys

TENURE_TYPES = {
    "traditional-formal-right", "modern-permit", "regulatory-licence",
    "de-minimis", "exempt-declared-commercial", "agency-control",
    "water-supply-contract", "commonhold", "investment-contract",
    "reserve-minimum-flow", "customary", "religious-law", "informal",
    "assumed", "impossible", "unrecognised", "unclassified",
}
SOURCE_TYPES = {
    "interview", "group-interview", "fgd", "workshop", "observation",
    "photo-video", "map-drone", "community-mapping", "admin-record",
    "permit-register", "statistics", "archive", "news", "ngo-report",
    "academic", "grey-report", "project-deliverable", "derived-summary",
    "social-media", "ai-generated",
}
USE_CODES = {"A1", "A2", "A3", "B1", "B2", "B3", "B4", "B5", "B6", "C", "D1", "D2",
             "E1", "E2", "F", "G1", "G2", "H1", "H2", "I"}
USER_ATTRIBUTES = {
    "women", "men", "persons-with-disabilities", "elderly", "youth", "landless",
    "tenant-or-lessee", "sharecropper", "labourer", "non-resident-landowner",
    "migrant-or-outsider", "tail-end", "head-end", "upland-not-served", "smallholder",
    "large-landholder", "indigenous-or-customary-community", "public-entity",
    "private-company", "collective-unregistered", "collective-registered",
}
# Types that restate other sources rather than observe anything themselves.
NON_PRIMARY = {"derived-summary", "ai-generated"}
# A figure worth tracing: a number with a unit, currency or percent, not a slide or season label.
FIGURE = re.compile(
    r"(rp|idr|usd|us\$|\$|eur)\s?\d|\d[\d.,]*\s?(%|percent|persen|ha\b|hektar|hectare|juta|jt\b|ribu|rb\b|"
    r"kg\b|kwintal|kuintal|quintal|ton\b|tonnes?\b|l/s|lps|liter|litre|m3|m³|km\b|mw\b|bau\b|bahu\b|"
    r"bata\b|tumbak|hours|jam\b|days|hari\b|households|kk\b|people|orang\b|pumps?\b|pompa\b)",
    re.I,
)
# Water bought or delivered has no hydrological location of its own.
PURCHASED = re.compile(r"galon|gallon|refill|isi ulang|tanker|tangki|vendor|purchased|dibeli|bottled", re.I)
CONFIDENCE = {"triangulated", "corroborated", "single-source", "uncorroborated", "contested"}
COORD = re.compile(r"^\s*-?\d{1,2}(\.\d+)?\s*,\s*-?\d{1,3}(\.\d+)?\s*$")

SRC_REQUIRED = ["source_id", "source_type", "title", "date", "path_or_url", "locator_scheme"]
ARR_REQUIRED = [
    "arrangement_id", "tenure_type", "classification_basis", "water_source",
    "water_use", "users", "location_admin", "arrangement", "source_ids",
    "locators", "confidence",
]
# A legal flag asserting a conclusion rather than asking a question.
LEGAL_CONCLUSION = re.compile(
    r"\b(is|are|was|were)\s+(il)?legal\b|\bviolat(es|ed)\b|\bmelanggar\b|"
    r"\b(sah|tidak sah)\b|\bunlawful\b|\bin breach of\b",
    re.I,
)
ATTRIBUTION = re.compile(r"report|said|says|state|describ|according|menurut|call|label|\[|\(", re.I)


def read(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def split(cell):
    return [x.strip() for x in (cell or "").split(";") if x.strip()]


def check(d):
    """Return (errors, warnings, n_sources, n_arrangements) for a catalogue directory."""
    d = pathlib.Path(d)
    errors, warnings = [], []
    for name in ("sources.csv", "arrangements.csv"):
        if not (d / name).exists():
            return [f"missing {d / name}"], [], 0, 0
    sources = read(d / "sources.csv")
    arrs = read(d / "arrangements.csv")

    by_id = {}
    for i, s in enumerate(sources, 2):
        sid = (s.get("source_id") or "").strip()
        for c in SRC_REQUIRED:
            if not (s.get(c) or "").strip():
                errors.append(f"sources.csv:{i} {sid or '?'}: empty {c}")
        if sid in by_id:
            errors.append(f"sources.csv:{i}: duplicate source_id {sid}")
        st = (s.get("source_type") or "").strip()
        if st and st not in SOURCE_TYPES:
            errors.append(f"sources.csv:{i} {sid}: source_type '{st}' not in vocabulary")
        by_id[sid] = s

    seen = set()
    for i, a in enumerate(arrs, 2):
        aid = (a.get("arrangement_id") or "").strip() or f"row{i}"
        where = f"arrangements.csv:{i} {aid}"
        for c in ARR_REQUIRED:
            if not (a.get(c) or "").strip():
                errors.append(f"{where}: empty {c}")
        if aid in seen:
            errors.append(f"{where}: duplicate arrangement_id")
        seen.add(aid)

        tt = (a.get("tenure_type") or "").strip()
        if tt and tt not in TENURE_TYPES:
            errors.append(f"{where}: tenure_type '{tt}' not in vocabulary")
        for st in split(a.get("secondary_tenure_types")):
            if st not in TENURE_TYPES:
                errors.append(f"{where}: secondary tenure type '{st}' not in vocabulary")
        conf = (a.get("confidence") or "").strip()
        if conf and conf not in CONFIDENCE:
            errors.append(f"{where}: confidence '{conf}' not in vocabulary")
        bad_codes = [c for c in split(a.get("water_use")) if c not in USE_CODES]
        if bad_codes:
            errors.append(f"{where}: water_use codes not in the FAO list: {', '.join(bad_codes)}")
        bad_attr = [u for u in split(a.get("user_attributes")) if u not in USER_ATTRIBUTES]
        if bad_attr:
            warnings.append(f"{where}: user_attributes outside the vocabulary: {', '.join(bad_attr)}")
        coords = (a.get("coordinates") or "").strip()
        if coords and not COORD.match(coords):
            warnings.append(f"{where}: coordinates '{coords}' are not 'lat,lon' in decimal degrees")

        ids, locs = split(a.get("source_ids")), split(a.get("locators"))
        if ids and len(locs) != len(ids):
            errors.append(f"{where}: {len(ids)} source_ids but {len(locs)} locators (pair them one-to-one)")
        missing = [x for x in ids if x not in by_id]
        if missing:
            errors.append(f"{where}: source_ids not in sources.csv: {', '.join(missing)}")
        for loc in locs:
            if loc.lower() in {"n/a", "na", "-", "?", "tbd"}:
                errors.append(f"{where}: placeholder locator '{loc}'")

        types = {by_id[x].get("source_type", "").strip() for x in ids if x in by_id}
        if ids and types and types <= {"ai-generated"}:
            errors.append(f"{where}: supported only by AI-generated sources")
        origins = {(by_id[x].get("derived_from") or "").strip() or x for x in ids if x in by_id}
        primary_types = types - NON_PRIMARY
        if conf == "triangulated" and (len(origins) < 3 or len(primary_types) < 2):
            errors.append(
                f"{where}: 'triangulated' needs >=3 independent origins and >=2 primary source types "
                f"(has {len(origins)} origins, {len(primary_types)} types); sources sharing derived_from count once")
        if conf == "corroborated" and len(origins) < 2:
            errors.append(f"{where}: 'corroborated' needs >=2 independent origins (has {len(origins)})")
        if conf == "triangulated" and not (a.get("notes") or "").strip():
            warnings.append(f"{where}: 'triangulated' without a note on why the legs are independent")

        flag = (a.get("legal_flag") or "").strip()
        if flag:
            if "?" not in flag:
                errors.append(f"{where}: legal_flag must be phrased as a question for legal assessment")
            if LEGAL_CONCLUSION.search(flag):
                errors.append(f"{where}: legal_flag states a legal conclusion; ask, do not decide")
        for col in ("arrangement", "classification_basis", "recognition_reported", "perceived_security"):
            text = a.get(col) or ""
            if LEGAL_CONCLUSION.search(text) and not ATTRIBUTION.search(text):
                warnings.append(f"{where}: {col} reads like a legal finding; attribute it to its source or move it to legal_flag")

        if types & {"interview", "group-interview", "fgd"} and not (a.get("quote_original") or "").strip():
            warnings.append(f"{where}: interview-based record without a verbatim quote")
        if not (a.get("location_hydro") or "").strip() and not PURCHASED.search(a.get("water_source") or ""):
            warnings.append(f"{where}: no hydrological location (scheme/canal/gate/river reach/aquifer)")
        figure_text = " ".join(a.get(c) or "" for c in ("arrangement", "payment", "allocation_rule", "gedsi_notes"))
        if FIGURE.search(figure_text) and not (a.get("figures_source") or "").strip():
            warnings.append(f"{where}: quantities found; record which source states each in figures_source")

    return errors, warnings, len(sources), len(arrs)


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = {a for a in argv if a.startswith("--")}
    unknown = flags - {"--json", "--strict"}
    if len(args) != 1 or unknown:
        print(__doc__)
        return 2
    errors, warnings, ns, na = check(args[0])
    failed = bool(errors) or ("--strict" in flags and bool(warnings))
    if "--json" in flags:
        print(json.dumps({"sources": ns, "arrangements": na, "errors": errors,
                          "warnings": warnings, "passed": not failed}, indent=1, ensure_ascii=False))
    else:
        for e in errors:
            print("ERROR", e)
        for w in warnings:
            print("WARN ", w)
        print(f"{ns} sources, {na} arrangements, {len(errors)} errors, {len(warnings)} warnings")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
