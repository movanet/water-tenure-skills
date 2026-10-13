# The per-run inputs, and where each one goes

hyperresearch (https://github.com/jordan-gibbs/hyperresearch) is a generic deep-research harness: a
router skill, sixteen step skills and sixteen subagents that build a source vault, draft, criticise,
patch and cite-check a report. Nothing in it is about water tenure. CRPG's water tenure runs made it
tenure-specific without editing it, through files written for each run. `make_run_inputs.py` renders
all of them from one scope file.

| Rendered file | Goes to | Read by | Purpose |
|---|---|---|---|
| `query.md` | The `/hyperresearch` prompt (or `research/prompt.txt`); the bootstrap writes it to `research/runs/<tag>/query.md` | Every step and subagent, as the canonical query | Asks for a catalogue by tenure type, anchored on the area, place-based, using the analysis skill |
| `scaffold-additions.md` | Appended to `research/runs/<tag>/scaffold.md` | The orchestrator only | Wrapper requirements (output, citation, structure), the skill's rules, the inserted catalogue stage |
| `prompt-decomposition.seed.json` | Compared with, and merged into, `research/runs/<tag>/prompt-decomposition.json` after step 1 | The instruction critic (step 12) and the drafters | Sub-questions, required headings in the skill's report order, scope conditions, levers |
| `domain-notes.txt` | The run's `domain_notes` lever (`levers-commands.sh`) | Rendered into the research and drafting shims | Source priorities, evidence norms, place focus, local terms, exclusions |
| `temp/local-ingest-protocol.md` | `research/runs/<tag>/temp/` | Local-ingest agents in step 2 | Registers the project's own evidence as vault notes with pinpoints |
| `temp/search-plan.md` | same | Search agents in step 2 | Themes T1-T8 by tenure family, four lenses each, anchor first |
| `temp/fetch-protocol.md` | same | Extra fetch waves and step 8 gap fill | Search fallbacks, scope, place focus, audited absences |
| `temp/source-analysis-focus.md` | same | Source analysts (long sources) | A table of tenure arrangements at named places in every digest |
| `temp/catalogue-protocol.md` | same | Stage C group agents | The catalogue build, partitioned by tenure type |
| `temp/draft-angles.md` | same | Step 10 | Three drafts: breadth by type, contested classifications, place and practitioner |
| `temp/synthesis-plan.md` | same | Step 11 | Organising claim, beats, the literal H2 headings, per-section commitments |

## Levers and shims

hyperresearch records three levers per run in the decomposition and renders them into four "shim"
files that are prepended to the agents' prompts (`research`, `drafting`, `critics`, `polish`):

- `register`: the shape of the product. Use **`survey`**: a water tenure catalogue is a map of
  arrangements, so coverage and organisation outrank a committed thesis, disagreements are charted and
  attributed rather than resolved, and comparison tables are preferred.
- `inference_depth`: how far to dig. Use **`deep`**: customary custody, informal pumping and local
  permits live in grey literature, theses, local news and agency pages rather than on the clear web,
  and audited absences (what should be published and is not) are findings.
- `domain_notes`: free text for the research and drafting shims. The rendered `domain-notes.txt`
  carries the source priorities, the evidence norms of the analysis skill, the place focus, the local
  terms and the exclusions.

Set them after step 1 (step 1 chooses defaults; step 4 may raise `inference_depth`):

```bash
hyperresearch levers set <tag> register=survey inference_depth=deep --json
hyperresearch levers set <tag> "domain_notes=$(cat domain-notes.txt)" --rerender --json
```

`--rerender` rewrites the shim files from the levers; `hyperresearch levers render <tag>` does the
same on its own.

## The query, generalised

The reference run started from a short prompt and three follow-ups given during the run: deliver
Markdown; focus on place- and point-based issues; use the skill correctly and divide the report by
tenure type. Follow-ups given mid-run had to be pushed to fourteen running fetchers and patched into
the decomposition and shims. `query.md` folds all four into the opening prompt so that every step
sees them from the start.

## When the run is already going

A follow-up that changes scope mid-run is binding but expensive. Record it verbatim in
`query.md` under a "User follow-up (verbatim, binding)" line, message the running subagents, patch
`prompt-decomposition.json` (sub-questions, required headings, scope conditions), update the
`domain_notes` lever with `--rerender`, and note in the scaffold how it was applied.
