#!/usr/bin/env python3
"""Render the per-run inputs that make a hyperresearch run produce a water tenure catalogue.

    python make_run_inputs.py <scope.yaml> --out DIR [--vault-tag TAG]

hyperresearch itself is generic. A water tenure run gets its tenure-specific behaviour from files
written for that run: the canonical query, additions to the scaffold, a decomposition to check step 1
against, the `domain_notes` lever (rendered by hyperresearch into the agents' shims), and run-local
protocols the orchestrator hands to its subagents. This script renders all of them from one scope
file (see examples/synthetic-scope.yaml), into DIR:

  query.md                         the canonical research query (paste it as the /hyperresearch prompt)
  scaffold-additions.md            sections to append to research/runs/<tag>/scaffold.md
  prompt-decomposition.seed.json   what step 1's prompt-decomposition.json must contain
  domain-notes.txt                 the domain_notes lever text
  levers-commands.sh               the hyperresearch commands that set the levers and re-render shims
  temp/*.md                        catalogue, local-ingest, fetch, source-analysis, search-plan,
                                   draft-angle and synthesis-plan protocols for research/runs/<tag>/temp/
  APPLY.md                         the order in which to use them

Needs PyYAML for a YAML scope (a JSON scope works with the standard library). Writes nothing
outside DIR and calls nothing on the network.
"""
from __future__ import annotations

import json
import pathlib
import sys
from string import Template

HERE = pathlib.Path(__file__).resolve().parent
SKILL = HERE.parent
TEMPLATES = SKILL / "templates"
ANALYSIS = SKILL.parent / "water-tenure-analysis"

FAMILY1 = ["traditional-formal-right", "modern-permit", "regulatory-licence", "agency-control",
           "water-supply-contract", "commonhold", "investment-contract", "de-minimis",
           "exempt-declared-commercial", "reserve-minimum-flow"]
FAMILY2 = ["customary", "religious-law", "informal", "assumed", "impossible", "unrecognised"]

# The "divide by tenure type" partition of stage C: every type in exactly one group.
DEFAULT_GROUPS = [
    ("C1", "Permits and licences", ["modern-permit", "regulatory-licence", "exempt-declared-commercial",
                                    "traditional-formal-right"], "A100-A199"),
    ("C2", "State allocation and contracts", ["agency-control", "water-supply-contract", "investment-contract",
                                              "reserve-minimum-flow"], "A200-A299"),
    ("C3", "Collective tenure", ["commonhold"], "A300-A399"),
    ("C4", "Custom and religion", ["customary", "religious-law"], "A400-A499"),
    ("C5", "Outside the state", ["informal", "assumed", "impossible", "unrecognised"], "A500-A599"),
    ("C6", "Small and household uses; invisible users", ["de-minimis"], "A600-A699"),
]
REQUIRED = ("area", "coverage_question")


def load(path: str) -> dict:
    text = pathlib.Path(path).read_text(encoding="utf-8")
    if path.lower().endswith(".json"):
        return json.loads(text)
    import yaml
    return yaml.safe_load(text) or {}


def as_list(v) -> list[str]:
    if v is None:
        return []
    return [str(x) for x in v] if isinstance(v, (list, tuple)) else [str(v)]


def groups_of(scope: dict) -> list[tuple[str, str, list[str], str]]:
    raw = scope.get("groups")
    groups = DEFAULT_GROUPS if not raw else [(g["id"], g["name"], as_list(g["types"]), g.get("ids", "")) for g in raw]
    seen = [t for _, _, ts, _ in groups for t in ts]
    missing = [t for t in FAMILY1 + FAMILY2 if t not in seen]
    dupes = sorted({t for t in seen if seen.count(t) > 1})
    if missing or dupes:
        raise ValueError(f"groups must cover every tenure type exactly once (missing {missing}, repeated {dupes})")
    return groups


def variables(scope: dict, tag: str) -> dict[str, str]:
    for k in REQUIRED:
        if not scope.get(k):
            raise ValueError(f"scope is missing '{k}'")
    groups = groups_of(scope)
    table = ["| Group | Name | Tenure types | Arrangement ids |", "|---|---|---|---|"]
    table += [f"| {g} | {n} | {', '.join(ts)} | {ids} |" for g, n, ts, ids in groups]
    return {
        "vault_tag": tag,
        "area": scope["area"],
        "coverage_question": scope["coverage_question"].strip(),
        "languages": ", ".join(as_list(scope.get("languages")) or ["the local languages", "English"]),
        "period": scope.get("period", "current arrangements, with historical origins where they explain present tenure"),
        "as_of": str(scope.get("as_of", "the current year")),
        "source_priorities": "; ".join(as_list(scope.get("source_priorities"))) or
                             "primary official documents first, then peer-reviewed and university work, NGO reports, and credible press",
        "local_corpus": scope.get("local_corpus", "the project's own notes, transcripts, decks and reports"),
        "local_terms": ", ".join(as_list(scope.get("local_terms"))) or "(none listed)",
        "out_of_scope": "; ".join(as_list(scope.get("out_of_scope"))) or "areas outside the anchor list",
        "citation_style": scope.get("citation_style", "OSCOLA"),
        "catalogue_dir": scope.get("catalogue_dir", "tenure-catalogue/<area>-<date>"),
        "gear": scope.get("gear", "premier"),
        "hpr": scope.get("hpr", "hyperresearch"),
        "analysis_skill": str(pathlib.Path(scope.get("analysis_skill") or ANALYSIS)),
        "framework_sources": "; ".join(as_list(scope.get("framework_sources"))) or
                             "AlAfghani and Susetyo (2023); AlAfghani, Lee and Yasuda (2025)",
        "groups_table": "\n".join(table),
    }


def decomposition(scope: dict, v: dict) -> dict:
    area = v["area"]
    return {
        "_note": "Seed for step 1. After hyperresearch-1-decompose writes prompt-decomposition.json, check that it "
                 "contains these items and merge any that are missing before step 2. Keys follow the run file.",
        "sub_questions": [
            f"{v['coverage_question']} (must be established FIRST and used to bound all later searches)",
            f"What water tenure arrangements exist in {area}, across surface water, groundwater, springs, reservoirs, "
            "canals and any other sources present?",
            "PLACE FOCUS: at which named place or point does each arrangement operate, and what place-specific issues "
            "(conflicts, overlaps, exclusions) arise there?",
            "How is each arrangement classified on the FAO water tenure typology (formal-law types and non-formal types)?",
            "For each arrangement: who gets water, from where, when, how much, who decides, who pays, who maintains, who "
            "enforces, what happens on breach, how officials treat it, how secure users feel, conflicts, and who is excluded?",
            "Which water uses (FAO use codes) and user groups are present, including absent or invisible users?",
            "What does the tenure x use matrix look like, and what do its empty rows and columns mean (absent or not looked for)?",
            "What patterns cut across arrangements: layering, seasonality, upstream-downstream position, land-water links, "
            "toleration, economic power, conflict hotspots?",
            "What contradictions and gaps exist in the evidence, and what should fieldwork ask next?",
            "Which legal questions does the catalogue raise for a separate legal assessment (questions only)?",
        ],
        "entities": [
            {"name": f"{area} coverage", "type": "jurisdiction",
             "required_fields": ["sub-basins", "provinces and districts", "schemes by level of government",
                                 "dams, reservoirs, weirs and intakes", "legal basis for coverage"]},
            {"name": "Formal-law tenure types (10)", "type": "category", "members": FAMILY1,
             "required_fields": ["local name", "location (admin + hydro)", "users",
                                 "mechanism: access, allocation, payment, labour, decision, enforcement",
                                 "recognition", "perceived security", "conflicts", "exclusion", "evidence and confidence"]},
            {"name": "Non-formal tenure types (6)", "type": "category", "members": FAMILY2,
             "required_fields": ["local name", "location (admin + hydro)", "users",
                                 "mechanism: access, allocation, payment, labour, decision, enforcement",
                                 "recognition", "perceived security", "conflicts", "exclusion", "evidence and confidence"]},
            {"name": "Water uses (FAO codes A1-I)", "type": "category",
             "required_fields": ["users", "locations", "tenure types attached", "absent users"]},
            {"name": "Gazetteer of tenure points", "type": "place-list",
             "required_fields": ["place or point", "type of point", "administrative location", "hydrological location",
                                 "coordinates if sourced", "tenure types present", "issues at the point", "sources"]},
        ],
        "required_formats": [
            "The water-tenure-analysis skill's report order (binding): 1 Scope and sources (opening with the area); "
            "2 Catalogue by tenure type, one H3 per FAO type (formal-law, then non-formal, then types searched and not "
            "found), each arrangement named by its place; 3 Water uses and users; 4 Tenure x use matrix; 5 Patterns; "
            "6 Contradictions and gaps; 7 Referral for legal assessment (questions only); 8 Verification note (n of N). "
            "Catalogue files built BEFORE drafting and passed by check_catalogue.py.",
            f"{v['citation_style']} citations in the delivered report",
            "Markdown output",
            "Catalogue: sources.csv, arrangements.csv, matrix.md, report.md",
            "Place-based framing: every arrangement anchored to a named place or point; a gazetteer annex",
        ],
        "required_sections": ["Area covered (established first)", "Catalogue by tenure type", "Annexes",
                              "Gazetteer of place- and point-based tenure issues"],
        "required_section_headings": ["## 1. Scope and Sources", "## 2. Catalogue by Tenure Type",
                                      "## 3. Water Uses and Users", "## 4. The Tenure and Use Matrix",
                                      "## 5. Patterns Across Arrangements", "## 6. Contradictions and Gaps",
                                      "## 7. Referral for Legal Assessment", "## 8. Verification Note", "## Annexes"],
        "time_horizons": [v["period"]],
        "scope_conditions": [
            f"Geographically limited to {area} as established by the anchor question; other areas only where an "
            "arrangement crosses into it",
            "Describe practice; do not decide legality: legal premises go to a referral list as questions",
            "All water sources and all uses in scope, including livelihoods water law does not address",
            "Place focus: prefer site-specific evidence over generic national statements; generic law only as frame",
        ] + [f"Out of scope: {x}" for x in as_list(scope.get("out_of_scope"))],
        "pipeline_tier": "full",
        "response_format": "argumentative",
        "citation_style": "wikilink",
        "levers": {"register": "survey", "inference_depth": "deep", "domain_notes": "<see domain-notes.txt>"},
    }


APPLY = """# Applying the rendered inputs (run tag: {tag})

1. In the project folder: `hyperresearch install .` (once), and `hyperresearch profile use {gear}` if
   the gear differs from the installed one (it re-renders the skills; takes effect on the next run).
2. Start the run in Claude Code with `/hyperresearch` and paste `query.md` (without its front matter)
   as the prompt. Note the vault tag the bootstrap mints; re-render with `--vault-tag <tag>` if you
   rendered with a placeholder.
3. After the bootstrap writes `research/runs/<tag>/scaffold.md`, append `scaffold-additions.md`.
4. After step 1, compare `research/runs/<tag>/prompt-decomposition.json` with
   `prompt-decomposition.seed.json`; add what is missing (sub-questions, required headings, scope
   conditions). Then set the levers: `bash levers-commands.sh`.
5. Copy `temp/*.md` into `research/runs/<tag>/temp/`. The orchestrator hands
   `local-ingest-protocol.md` to local-ingest agents and `search-plan.md` to search agents in step 2,
   `fetch-protocol.md` to extra fetch and gap-fill agents, `source-analysis-focus.md` to source
   analysts, `catalogue-protocol.md` to the stage C group agents, and uses `draft-angles.md` and
   `synthesis-plan.md` at steps 10 and 11.
6. Stage C after step 2; C-revision after step 9; spot verification before step 10 (see
   `scaffold-additions.md`). Merge partial catalogues with `merge_partials.py`.
7. At delivery: `wikilinks_to_tokens.py` on the final report, then the `water-tenure-report` skill.
"""


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    opts = {}
    for k in ("--out", "--vault-tag"):
        if k in argv:
            i = argv.index(k)
            if i + 1 >= len(argv):
                print(__doc__)
                return 2
            opts[k] = argv[i + 1]
            args = [a for a in args if a != argv[i + 1]]
    if len(args) != 1 or "--out" not in opts:
        print(__doc__)
        return 2
    scope = load(args[0])
    tag = opts.get("--vault-tag") or scope.get("vault_tag") or "<vault_tag>"
    try:
        v = variables(scope, tag)
    except ValueError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1
    out = pathlib.Path(opts["--out"])
    (out / "temp").mkdir(parents=True, exist_ok=True)
    written = []

    def render(src: pathlib.Path, dst: pathlib.Path) -> None:
        dst.write_text(Template(src.read_text(encoding="utf-8")).substitute(v), encoding="utf-8", newline="\n")
        written.append(dst.relative_to(out).as_posix())

    render(TEMPLATES / "query.md.tmpl", out / "query.md")
    render(TEMPLATES / "scaffold-additions.md.tmpl", out / "scaffold-additions.md")
    render(TEMPLATES / "domain-notes.txt.tmpl", out / "domain-notes.txt")
    for t in sorted((TEMPLATES / "protocols").glob("*.md.tmpl")):
        render(t, out / "temp" / t.name[:-len(".tmpl")])
    dec = decomposition(scope, v)
    (out / "prompt-decomposition.seed.json").write_text(json.dumps(dec, indent=2, ensure_ascii=False) + "\n",
                                                        encoding="utf-8", newline="\n")
    written.append("prompt-decomposition.seed.json")
    hpr = v["hpr"]
    (out / "levers-commands.sh").write_text(
        "#!/usr/bin/env bash\n# Set the run levers and re-render the four role shims (research, drafting, critics, polish).\n"
        "set -euo pipefail\n"
        f"TAG='{tag}'\n"
        f"{hpr} levers set \"$TAG\" register=survey inference_depth=deep --json\n"
        f"{hpr} levers set \"$TAG\" \"domain_notes=$(cat \"$(dirname \"$0\")/domain-notes.txt\")\" --rerender --json\n",
        encoding="utf-8", newline="\n")
    written.append("levers-commands.sh")
    (out / "APPLY.md").write_text(APPLY.format(tag=tag, gear=v["gear"]), encoding="utf-8", newline="\n")
    written.append("APPLY.md")
    print(json.dumps({"out": str(out), "vault_tag": tag, "files": written}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
