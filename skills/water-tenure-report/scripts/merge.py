#!/usr/bin/env python3
"""Merge one or more water-tenure catalogues into a master set, grade every source, and write
per-tenure-type evidence packs for chapter drafters.

    python merge.py <config.yaml>

Inputs : the catalogues listed under `inputs:` in the config (each a folder with sources.csv
         and arrangements.csv that passes check_catalogue.py).
Outputs: <work>/data/master_sources.csv, master_arrangements.csv, sources.json
         <work>/packs/<tenure-type>.md

Records are never deleted or fused: where two catalogues describe the same place and mechanism,
both records stay and the chapters cite them together. Source and record ids from each input
are prefixed as configured so registers cannot collide.
"""
from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (TYPES, die, group_of, load_config, read_csv, secondary_of,  # noqa: E402
                    split, units_of, write_csv)
from citations import apa, grade, oscola  # noqa: E402

SHOW = ["local_name", "local_name_language", "classification_basis", "secondary_tenure_types",
        "water_source", "water_use", "users", "user_attributes", "holder_controller", "location_admin",
        "location_hydro", "coordinates", "upstream_downstream", "period_season", "arrangement",
        "access_rule", "allocation_rule", "payment", "labour_contribution", "decision_making",
        "enforcement_sanction", "recognition_reported", "perceived_security", "conflicts",
        "gedsi_notes", "locators", "figures_source", "quote_original", "quote_translation",
        "confidence", "contradictions", "legal_flag", "gaps_next_steps", "notes"]


def new_record_id(old: str, prefix: str) -> str:
    return prefix + re.sub(r"^[A-Za-z]+", "", old) if prefix else old


def main(cfg_path: str) -> int:
    cfg = load_config(cfg_path)
    work = cfg.work
    style = (cfg.get("report.citation_style", "oscola") or "oscola").lower()
    accessed = cfg.get("report.accessed", "")
    press = cfg.get("grades.press_media_markers")
    master_src, master_arr, idmap = [], [], {}

    inputs = cfg.get("inputs", []) or []
    if not inputs:
        die("config has no inputs")
    for inp in inputs:
        d = cfg.rel(inp["path"])
        if not d or not (d / "sources.csv").exists():
            die(f"input catalogue not found: {inp['path']}")
        origin, sp, rp = inp.get("origin", d.name), inp.get("prefix", ""), inp.get("record_prefix", "")
        for s in read_csv(d / "sources.csv"):
            sid = sp + s["source_id"].strip()
            if any(m["id"] == sid for m in master_src):
                die(f"source id collision after prefixing: {sid}; set a prefix for input {inp['path']}")
            idmap[(origin, s["source_id"].strip())] = sid
            full, short = (apa if style == "apa" else oscola)(s, accessed)
            master_src.append(dict(
                id=sid, origin=origin, orig_id=s["source_id"].strip(), type=s["source_type"].strip(),
                grade=grade(s["source_type"].strip(), s.get("author_org", ""), press),
                title=s.get("title", ""), author=s.get("author_org", ""), date=s.get("date", ""),
                url=s.get("path_or_url", ""), language=s.get("language", ""),
                verifiability=s.get("verifiability", ""), notes=s.get("reliability_notes", ""),
                ref=full, short=short))
        src_by_id = {m["id"]: m for m in master_src}

        def remap_ids(raw: str) -> list[str]:
            return [idmap.get((origin, t), "?" + t) for t in split(raw)]

        local_ids = sorted((k[1] for k in idmap if k[0] == origin), key=len, reverse=True)
        bare = (re.compile(r"(?<![A-Za-z0-9_-])(" + "|".join(re.escape(x) for x in local_ids) + r")(?![A-Za-z0-9_-])")
                if sp and local_ids else None)

        def remap_text(txt: str) -> str:
            # [[slug|pinpoint]] wikilinks (hyperresearch vault notes) -> {{ID}} pinpoint
            def rep(m: re.Match) -> str:
                sid = idmap.get((origin, m.group(1)))
                return f"{{{{{sid}}}}} {m.group(2) or ''}".strip() if sid else m.group(0)
            out = re.sub(r"\[\[([^\]|]+)(?:\|([^\]]*))?\]\]", rep, txt or "")
            # Inline citations such as "(K01 para 3)" follow their source when its id is prefixed.
            if bare:
                out = bare.sub(lambda m: idmap[(origin, m.group(1))], out)
            return out

        for r in read_csv(d / "arrangements.csv"):
            m = {k: remap_text(v) for k, v in r.items()}
            m["arrangement_id"] = new_record_id(r["arrangement_id"].strip(), rp)
            sids = remap_ids(r["source_ids"])
            m["source_ids"] = ";".join(sids)
            gs = sorted({src_by_id[s]["grade"] for s in sids if s in src_by_id})
            m["grades"] = ";".join(gs)
            m["best_grade"] = min((g for g in gs if g != "D"), default="D")
            m["e5_only"] = "yes" if gs and all(g in ("E5", "D") for g in gs) else "no"
            m["origin"] = origin
            m["group"] = group_of(cfg, r)
            m["units"] = ";".join(units_of(cfg, r))
            master_arr.append(m)

    unmapped = [(m["arrangement_id"], s) for m in master_arr for s in m["source_ids"].split(";") if s.startswith("?")]
    if unmapped:
        die(f"source ids in arrangements not found in their sources.csv: {unmapped[:5]}")
    ids = [m["arrangement_id"] for m in master_arr]
    dupes = [i for i, n in collections.Counter(ids).items() if n > 1]
    if dupes:
        die(f"arrangement id collision after prefixing: {dupes[:5]}; set record_prefix on an input")

    data = work / "data"
    front = ["arrangement_id", "origin", "group", "units", "best_grade", "grades", "e5_only"]
    rest = [k for k in master_arr[0] if k not in front]
    write_csv(data / "master_arrangements.csv", master_arr, front + rest)
    write_csv(data / "master_sources.csv", master_src)
    with open(data / "sources.json", "w", encoding="utf-8") as fh:
        json.dump({m["id"]: {k: m[k] for k in ("ref", "short", "grade", "type", "author", "title", "date", "origin")}
                   for m in master_src}, fh, ensure_ascii=False, indent=1)
    (data / "style.txt").write_text(style + "\n", encoding="utf-8")
    write_packs(work, master_arr, {m["id"]: m for m in master_src})

    c = collections.Counter(m["tenure_type"] for m in master_arr)
    g = collections.Counter(s["grade"] for s in master_src)
    print(f"merged {len(master_arr)} records and {len(master_src)} sources from {len(inputs)} catalogue(s)")
    print("records by type:", dict(c))
    print("sources by grade:", dict(g))
    print("records resting on E5/D only:", sum(m["e5_only"] == "yes" for m in master_arr))
    return 0


def write_packs(work: Path, recs: list[dict], src: dict[str, dict]) -> None:
    for key, label in TYPES:
        prim = [m for m in recs if m["tenure_type"] == key]
        sec = [m for m in recs if key in secondary_of(m)]
        if not prim and not sec:
            continue
        body = prim or sec
        used: dict[str, dict] = {}
        lines = [f"# Evidence pack: {label} ({len(prim)} primary records, {len(sec)} secondary)\n",
                 "Each record: a header line, then its fields. Source tokens such as {{S01}} resolve in the "
                 "source list at the end. Cite only by token; never type a reference.\n"]
        if not prim:
            lines.append("No record carries this type as primary; the records below carry it as a SECONDARY type.\n")
        for m in body:
            lines.append(f"\n## {m['arrangement_id']} | {m['local_name']} | group {m['group']} | origin {m['origin']} | "
                         f"sources {m['source_ids']} | grades {m['grades']} | best {m['best_grade']} | E5-only {m['e5_only']}\n")
            for k in SHOW:
                v = (m.get(k) or "").strip()
                if v:
                    lines.append(f"- **{k}**: {v}")
            for s in m["source_ids"].split(";"):
                if s in src:
                    used[s] = src[s]
        if prim and sec:
            lines.append(f"\n# Records where {key} is a SECONDARY type ({len(sec)})\n")
            for m in sec:
                lines.append(f"- {m['arrangement_id']} ({m['tenure_type']}) {m['local_name']}: "
                             f"{m['location_admin'][:120]}; sources {m['source_ids']}")
        lines.append("\n# Sources used in this pack\n")
        for s, v in used.items():
            lines.append(f"- **{s}** [{v['grade']}, {v['type']}] {v['ref']}")
        (work / "packs" / f"{key}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
