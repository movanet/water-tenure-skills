#!/usr/bin/env python3
"""Export a checked catalogue as privacy-filtered map records (GeoJSON).

    python export_storymap.py <catalogue-dir> --out records.geojson
        [--include-uncorroborated] [--include-unclassified]
        [--sensitive-precision 2] [--precision 4]

Produces a GeoJSON FeatureCollection of Point features, one per arrangement
that has source-stated coordinates, for review before anything is published to
a map (for example the storymap engine in movanet/water-tenure-storymap, whose
own importer maps these records onto its vocabulary). Nothing is sent anywhere.

Data-protection rules applied here, and why:
- Only records with coordinates stated by a source are mapped; no coordinate is
  estimated, and area-level records are counted, not placed.
- No personal names, respondent codes or verbatim quotes are exported: the
  description is the arrangement text with bracketed and parenthetical
  citations removed, and the source line gives counts and types only.
- Sensitive tenure types (informal, impossible, unrecognised, assumed), sacred
  or ritual sites (use code H2 or words such as sacred/keramat), any record
  whose notes, conflicts or text mention an allegation, and any record citing a
  consent-restricted or non-anonymised source are marked
  sensitivity=aggregate_only and their coordinates are rounded (default 2
  decimals, roughly 1 km) BEFORE export, so exact points never leave the team.
- Records graded uncorroborated (allegations, hearsay) and unclassified records
  are left out unless explicitly included; records resting only on social media
  or AI-generated sources are always left out.

Standard library only. Exit 0 on success, 2 on usage error.
"""
import csv
import json
import pathlib
import re
import sys

SENSITIVE_TYPES = {"informal", "impossible", "unrecognised", "assumed"}
ALLEGATION = re.compile(r"brib|suap|mafia|extort|pungli|threat|ancam|intimidat|allege|dugaan", re.I)
SACRED = re.compile(r"sacred|keramat|holy|shrine|makam|grave|ritual site|sesaji", re.I)
CITATION = re.compile(r"\s*[\[(][^\])]*(\bl\.\s?\d|\bp\.\s?\d|\bpp?\s\d|slide|row|para|\d{2}:\d{2}|json|S\d{2,3}\b|INT-|FGD-)[^\])]*[\])]")
CODES = re.compile(r"\b(INT|FGD|KII|WS)-[A-Z0-9-]+\b")
SEASON = re.compile(r"\bMT ?([123])\b|\b(dry|wet|rainy) season\b", re.I)
LABELS = {
    "traditional-formal-right": "traditional formal right", "modern-permit": "modern permit",
    "regulatory-licence": "regulatory licence", "agency-control": "agency control",
    "water-supply-contract": "water supply contract", "commonhold": "commonhold",
    "investment-contract": "investment contract", "de-minimis": "de minimis right",
    "exempt-declared-commercial": "declared or exempt commercial use",
    "reserve-minimum-flow": "reserve or minimum flow", "customary": "customary tenure",
    "religious-law": "religious-law tenure", "informal": "informal tenure",
    "assumed": "assumed water right", "impossible": "impossible tenure",
    "unrecognised": "unrecognised tenure", "unclassified": "unclassified",
}


def read(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def split(cell):
    return [x.strip() for x in (cell or "").split(";") if x.strip()]


def parse_coords(text):
    m = re.match(r"^\s*(-?\d{1,2}(?:\.\d+)?)\s*,\s*(-?\d{1,3}(?:\.\d+)?)\s*$", text or "")
    if not m:
        return None
    lat, lon = float(m.group(1)), float(m.group(2))
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None
    return lat, lon


def clean(text):
    text = CITATION.sub("", text or "")
    text = CODES.sub("[respondent]", text)
    return re.sub(r"\s{2,}", " ", text).strip()


def village_of(location_admin):
    parts = [p.strip() for p in (location_admin or "").split(">") if p.strip()]
    if len(parts) >= 4:
        return re.sub(r"\s*\(unverified\)", "", parts[3])
    return parts[-1] if parts else "unknown"


def seasons_of(period):
    out = []
    for m in SEASON.finditer(period or ""):
        out.append(f"MT{m.group(1)}" if m.group(1) else f"{m.group(2).lower()} season")
    return sorted(set(out))


def export(d, include_uncorroborated=False, include_unclassified=False,
           precision=4, sensitive_precision=2):
    d = pathlib.Path(d)
    sources = {s["source_id"].strip(): s for s in read(d / "sources.csv")}
    feats, skipped = [], {"no_coordinates": [], "uncorroborated": [], "unclassified": [],
                          "clue_or_ai_only": []}
    for a in read(d / "arrangements.csv"):
        aid = a["arrangement_id"].strip()
        tt = a["tenure_type"].strip()
        conf = a["confidence"].strip()
        types = [sources[s]["source_type"].strip() for s in split(a["source_ids"]) if s in sources]
        if types and all(t in ("social-media", "ai-generated", "derived-summary") for t in types):
            skipped["clue_or_ai_only"].append(aid)
            continue
        if conf == "uncorroborated" and not include_uncorroborated:
            skipped["uncorroborated"].append(aid)
            continue
        if tt == "unclassified" and not include_unclassified:
            skipped["unclassified"].append(aid)
            continue
        ll = parse_coords(a.get("coordinates"))
        if not ll:
            skipped["no_coordinates"].append(aid)
            continue
        text = " ".join(a.get(c) or "" for c in ("notes", "conflicts", "arrangement", "local_name", "water_source"))
        restricted = any((sources[s].get("verifiability") or "").strip() == "restricted"
                         or (sources[s].get("anonymised") or "").strip() == "no"
                         for s in split(a["source_ids"]) if s in sources)
        sensitive = (tt in SENSITIVE_TYPES or "H2" in split(a["water_use"]) or restricted
                     or bool(ALLEGATION.search(text)) or bool(SACRED.search(text)))
        nd = sensitive_precision if sensitive else precision
        lat, lon = round(ll[0], nd), round(ll[1], nd)
        uses = split(a["water_use"])
        type_counts = {}
        for t in types:
            type_counts[t] = type_counts.get(t, 0) + 1
        local = (a.get("local_name") or "").split(";")[0].strip()
        title = f"{local + ': ' if local else ''}{LABELS.get(tt, tt)}, {village_of(a['location_admin'])}"
        feats.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": {
                "title": title,
                "catalogue_id": aid,
                "tenure_type": tt,
                "secondary_tenure_types": split(a.get("secondary_tenure_types")),
                "use_codes": uses,
                "use_type": uses[0] if uses else "I",
                "village": village_of(a["location_admin"]),
                "location_hydro": clean(a.get("location_hydro")),
                "season_relevance": seasons_of(a.get("period_season")),
                "description": clean(a["arrangement"]),
                "perceived_security_text": clean(a.get("perceived_security")),
                "confidence": conf,
                "source": "Catalogue record {}; {} source(s): {}".format(
                    aid, len(types), ", ".join(f"{n} {t}" for t, n in sorted(type_counts.items()))),
                "sensitivity": "aggregate_only" if sensitive else "public",
                "coordinate_precision_decimals": nd,
            },
        })
    return {"type": "FeatureCollection", "features": feats}, skipped


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
        if a in ("--include-uncorroborated", "--include-unclassified"):
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
    fc, skipped = export(args[0], "--include-uncorroborated" in opts, "--include-unclassified" in opts,
                         int(opts.get("--precision", 4)), int(opts.get("--sensitive-precision", 2)))
    out = pathlib.Path(opts["--out"])
    out.write_text(json.dumps(fc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    n_sens = sum(1 for f in fc["features"] if f["properties"]["sensitivity"] == "aggregate_only")
    print(json.dumps({"written": str(out), "features": len(fc["features"]), "aggregate_only": n_sens,
                      "skipped": {k: v for k, v in skipped.items() if v}}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
