#!/usr/bin/env python3
"""Generate the annex volume from the merged catalogue.

    python annexes.py <config.yaml>

Run merge.py first. Writes <work>/annexes/annex-<letter>.md for the letters listed under
`annexes:` in the config (default A-K):

  A Catalogue by tenure type        G Seasonal fieldwork calendar
  B Points gazetteer                H AI use and provenance (from config ai_use and sessions.json)
  C Coverage by map unit and type   I Social-media clue register (E5 sources)
  D Legal-referral questions        J Unclassified records
  E Source register with grades     K Fieldwork questions by place
  F Contested classifications

Annex text is generated from the records, so it carries the records' own wording and source
tokens; build.py resolves the tokens into references.
"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (GRADE_LABEL, GRADES, SEASONS, TYPE_LABEL, TYPES, coords_of, load_config,  # noqa: E402
                    md_cell, read_csv, season_of, secondary_of)

FIELDS = [("tenure_type", "Tenure type"), ("secondary_tenure_types", "Secondary types"), ("water_use", "Water use"),
          ("users", "Users"), ("holder_controller", "Holder or controller"), ("location_admin", "Administrative location"),
          ("location_hydro", "Hydrological location"), ("upstream_downstream", "Position"), ("period_season", "Period"),
          ("arrangement", "Arrangement"), ("access_rule", "Access rule"), ("allocation_rule", "Allocation rule"),
          ("payment", "Payment"), ("labour_contribution", "Labour"), ("decision_making", "Decision-making"),
          ("enforcement_sanction", "Enforcement"), ("recognition_reported", "Recognition (reported)"),
          ("perceived_security", "Perceived security"), ("conflicts", "Conflicts"), ("gedsi_notes", "GEDSI"),
          ("quote_original", "Quote"), ("quote_translation", "Translation"), ("source_ids", "Sources"),
          ("locators", "Locators"), ("grades", "Evidence grades"), ("confidence", "Confidence"),
          ("contradictions", "Contradictions"), ("legal_flag", "Legal question"), ("gaps_next_steps", "Gaps and next steps")]
SENSITIVE = {"informal", "impossible", "unrecognised", "assumed"}


class Annexes:
    def __init__(self, cfg):
        self.cfg = cfg
        self.A = read_csv(cfg.work / "data" / "master_arrangements.csv")
        self.S = {r["id"]: r for r in read_csv(cfg.work / "data" / "master_sources.csv")}
        self.units = [u["name"] for u in cfg.units]

    def a(self) -> str:
        out = ["# Annex A. Catalogue by Tenure Type\n",
               "Every record of the merged catalogue, grouped by primary tenure type in the order of the FAO typology. "
               "Bracketed source ids resolve to Annex E.\n"]
        for key, name in TYPES:
            recs = [r for r in self.A if r["tenure_type"] == key]
            if not recs:
                continue
            out.append(f"## A.{key} {name} ({len(recs)} records)\n")
            for r in recs:
                out.append(f"### {r['arrangement_id']}. {md_cell(r['local_name']) or name}\n")
                out += [f"- **{lab}:** {md_cell(r.get(k))}" for k, lab in FIELDS if (r.get(k) or "").strip()]
                out.append("")
        return "\n".join(out)

    def b(self) -> str:
        nd = int(self.cfg.get("annex_b_sensitive_precision", 2))
        out = ["# Annex B. Points Gazetteer\n",
               f"Records with coordinates stated by a source. Coordinates of records typed {', '.join(sorted(SENSITIVE))} "
               f"are rounded to {nd} decimal places in this annex; exact points stay in the internal catalogue.\n",
               "| ID | Local name | Tenure type | Place | Lat | Lon | Sources |", "|---|---|---|---|---|---|---|"]
        for r in self.A:
            c = coords_of(r)
            if not c:
                continue
            lon, lat = c
            if r["tenure_type"] in SENSITIVE:
                lon, lat = round(lon, nd), round(lat, nd)
            place = " > ".join(r["location_admin"].split(">")[-2:]).strip()
            out.append(f"| {r['arrangement_id']} | {md_cell(r['local_name'], 40)} | {r['tenure_type']} | {md_cell(place, 60)} | "
                       f"{lat} | {lon} | {md_cell(r['source_ids'])} |")
        return "\n".join(out) + "\n"

    def c(self) -> str:
        present = [k for k, _ in TYPES if any(r["tenure_type"] == k for r in self.A)]
        out = ["# Annex C. Coverage by Map Unit and Tenure Type\n",
               "Primary records per map unit and tenure type. A record naming several units counts once in each. "
               "Area-level records and records naming many units are listed in the last row.\n",
               "| Unit | " + " | ".join(present) + " | Total |", "|---|" + "---|" * (len(present) + 1)]
        for u in self.units + ["(area-level or many units)"]:
            def hit(r):
                us = [x for x in r["units"].split(";") if x]
                return (u in us) if not u.startswith("(") else not us
            row = [sum(1 for r in self.A if r["tenure_type"] == k and hit(r)) for k in present]
            out.append(f"| {u} | " + " | ".join(str(n) if n else "" for n in row) + f" | {sum(row)} |")
        absent = [TYPE_LABEL[k] for k, _ in TYPES if k not in present and k != "unclassified"]
        out += ["", "**Types with no primary record:** " + (", ".join(absent) or "none") +
                ". The report must say for each whether it is absent from the area or was not looked for.", ""]
        return "\n".join(out)

    def d(self) -> str:
        groups = collections.OrderedDict()
        for key, _ in TYPES:
            for r in self.A:
                if r["tenure_type"] == key and r["legal_flag"].strip():
                    groups.setdefault(r["legal_flag"].strip(), []).append(r)
        out = ["# Annex D. Questions for Legal Assessment\n",
               "Every legal question recorded against a catalogue record, grouped where the wording is identical. These are "
               "questions, not findings: the field catalogue does not decide what the law requires. Lawyers receive the "
               "questions with the records they rest on.\n"]
        for i, (q, recs) in enumerate(groups.items(), 1):
            out.append(f"{i}. {md_cell(q)} Records: {', '.join(r['arrangement_id'] for r in recs)} "
                       f"({', '.join(sorted({r['tenure_type'] for r in recs}))}).")
        return "\n".join(out) + "\n"

    def e(self) -> str:
        out = ["# Annex E. Source Register\n",
               "Every registered source with its reference, type and evidence grade. Grades describe the kind of source, not "
               "its truth: " + "; ".join(GRADE_LABEL[g] for g in GRADES) + ".\n",
               "| Id | Reference | Type | Grade | Origin |", "|---|---|---|---|---|"]
        for k, s in self.S.items():
            out.append(f"| {k} | {md_cell(s['ref'])} | {s['type']} | {s['grade']} | {s['origin']} |")
        g = collections.Counter(s["grade"] for s in self.S.values())
        out += ["", "| Grade | Sources |", "|---|---|"] + [f"| {GRADE_LABEL[x]} | {g.get(x, 0)} |" for x in GRADES]
        return "\n".join(out) + "\n"

    def f(self) -> str:
        out = ["# Annex F. Contested and Layered Classifications\n",
               "Records graded contested, records carrying conflicting accounts, and records with secondary tenure types. "
               "Each keeps both readings with their sources.\n",
               "| ID | Primary | Secondary | Confidence | Classification basis | Contradictions |", "|---|---|---|---|---|---|"]
        for r in self.A:
            if r["confidence"] == "contested" or r["contradictions"].strip() or secondary_of(r):
                out.append(f"| {r['arrangement_id']} | {r['tenure_type']} | {', '.join(secondary_of(r)) or '-'} | "
                           f"{r['confidence']} | {md_cell(r['classification_basis'], 300)} | {md_cell(r['contradictions'], 220) or '-'} |")
        return "\n".join(out) + "\n"

    def g(self) -> str:
        out = ["# Annex G. Seasonal Fieldwork Calendar\n",
               "Records grouped by the season their arrangement refers to (keyword coding of the period field), so that "
               "fieldwork can be timed to observe each arrangement when it operates.\n"]
        for s in SEASONS:
            recs = [r for r in self.A if season_of(r) == s]
            if not recs:
                continue
            out += [f"## {s} ({len(recs)} records)\n", "| ID | Tenure type | Place | Period as recorded |", "|---|---|---|---|"]
            out += [f"| {r['arrangement_id']} | {r['tenure_type']} | {md_cell(r['location_admin'].split('>')[-1], 50)} | "
                    f"{md_cell(r['period_season'], 120)} |" for r in recs]
            out.append("")
        return "\n".join(out)

    def h(self) -> str:
        ai = self.cfg.get("ai_use", {}) or {}
        out = ["# Annex H. AI Use and Provenance\n", (ai.get("statement") or "").strip() + "\n"]
        dirs = ai.get("directions") or []
        if dirs:
            out += ["## H.1 Directions given by the human orchestrator (paraphrased)\n", "| When | Session | Direction |", "|---|---|---|"]
            out += [f"| {md_cell(a)} | {md_cell(b)} | {md_cell(c)} |" for a, b, c in dirs]
            out.append("")
        sj = self.cfg.rel(ai.get("sessions_json")) or (self.cfg.work / "data" / "sessions.json")
        if sj.exists():
            ses = json.loads(sj.read_text(encoding="utf-8"))
            out += ["## H.2 Agent sessions\n", "| Session | Start | End | Models | Human turns | Subagent transcripts | Skills used |",
                    "|---|---|---|---|---|---|---|"]
            for k, v in ses.items():
                out.append(f"| {k} | {v.get('start')} | {v.get('end')} | {', '.join(m for m in (v.get('models') or {}) if m)} | "
                           f"{v.get('human_turns')} | {v.get('subagent_transcripts')} | {', '.join(sorted(set(v.get('skills') or [])))} |")
            out.append("")
        nv = ai.get("not_verified_by_a_person") or []
        if nv:
            out += ["## H.3 Not verified by a person\n"] + [f"- {md_cell(x)}" for x in nv] + [""]
        out += ["## H.4 Checks on this report\n", "{{CITECHECK-SUMMARY}}\n"]
        return "\n".join(out)

    def i(self) -> str:
        by_src = collections.defaultdict(list)
        for r in self.A:
            for s in r["source_ids"].split(";"):
                by_src[s].append(r)
        out = ["# Annex I. Social-Media Clue Register\n",
               "Every source graded E5 (social media), the records citing it, and whether other evidence (E1-E4) supports those "
               "records. An E5 source never supports a finding on its own: where a record also rests on E1-E4 evidence the post is "
               "triangulating; otherwise it is a lead for follow-up. Private accounts are not identified.\n",
               "| Source | Account | Date | Records | Other evidence | Status | Follow-up |", "|---|---|---|---|---|---|---|"]
        for k, s in self.S.items():
            if s["grade"] != "E5":
                continue
            rs = by_src.get(k, [])
            other = sorted({g for r in rs for g in r["grades"].split(";") if g not in ("E5", "D")})
            acct = "private account" if "private" in s["author"].lower() else md_cell(s["author"], 70)
            status = "triangulating" if other else ("lead only" if rs else "not used in a record")
            follow = "none beyond source check" if other else "find a press, official or field source for the same place, date and actor"
            out.append(f"| {k} | {acct} | {s['date']} | {', '.join(r['arrangement_id'] for r in rs) or '-'} | "
                       f"{', '.join(other) or 'none'} | {status} | {follow} |")
        return "\n".join(out) + "\n"

    def j(self) -> str:
        out = ["# Annex J. Unclassified Records\n",
               "Records whose tenure type the evidence did not allow the catalogue to decide, with what is known and what would "
               "decide it. Full records are in Annex A.\n",
               "| ID | Local name | Place | Use | What is known | What would decide it |", "|---|---|---|---|---|---|"]
        for r in self.A:
            if r["tenure_type"] == "unclassified":
                out.append(f"| {r['arrangement_id']} | {md_cell(r['local_name'], 60)} | {md_cell(r['location_admin'].split('>')[-1], 50)} | "
                           f"{r['water_use']} | {md_cell(r['classification_basis'], 260)} | {md_cell(r['gaps_next_steps'], 220) or '-'} |")
        return "\n".join(out) + "\n"

    def k(self) -> str:
        byu = collections.defaultdict(list)
        for r in self.A:
            if r["gaps_next_steps"].strip():
                us = [x for x in r["units"].split(";") if x]
                byu[us[0] if len(us) == 1 else "Area-level or several units"].append(r)
        out = ["# Annex K. Fieldwork Questions by Place\n",
               "Open questions recorded against each record, grouped by the map unit the record names. They are leads for "
               "fieldwork and document requests, not findings. Annex G gives the season in which each arrangement operates.\n"]
        for u in self.units + ["Area-level or several units"]:
            if byu.get(u):
                out.append(f"## {u} ({len(byu[u])} records)\n")
                out += [f"- **{r['arrangement_id']}** {md_cell(r['local_name'], 60)}: {md_cell(r['gaps_next_steps'], 400)}" for r in byu[u]]
                out.append("")
        return "\n".join(out)


def main(cfg_path: str) -> int:
    cfg = load_config(cfg_path)
    ax = Annexes(cfg)
    letters = [x.upper() for x in (cfg.get("annexes") or list("ABCDEFGHIJK"))]
    written = {}
    for L in letters:
        text = getattr(ax, L.lower())()
        (cfg.work / "annexes" / f"annex-{L.lower()}.md").write_text(text, encoding="utf-8")
        written[L] = len(text)
    print("annexes written (characters):", written)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
