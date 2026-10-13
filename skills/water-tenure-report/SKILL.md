---
name: water-tenure-report
description: 'Builds a long-form water tenure report, organised by FAO tenure type, from one or more checked water tenure catalogues: merges and grades the sources (E1-E5, D), writes per-type evidence packs for chapter drafters, draws maps and charts, generates annexes A-K (catalogue, gazetteer, coverage, legal-referral questions, source register, contested classifications, seasonal calendar, AI use and provenance, social-media clue register, unclassified records, fieldwork questions), resolves citation tokens into OSCOLA or APA footnotes, runs mechanical checks and builds .docx files with pandoc. This skill should be used when the user asks to write, build, assemble or format a water tenure report, a tenure-type chapter, report annexes or footnotes from a tenure catalogue, to merge a field catalogue with a media scan, or to run a cite-check on a tenure report ("laporan tenurial air", "bab per tipe tenurial").'
license: MIT
metadata:
  version: "1.0.0"
  author: "CRPG - Center for Regulation, Policy and Governance (vibe-coded with AI agents, orchestrated by Mohamad Mova Al'Afghani)"
---

# Water tenure report

This skill turns catalogues made with the `water-tenure-analysis` skill into a report a reviewer can
check line by line: one chapter per FAO tenure type, every statement footnoted to a registered source,
and annexes that carry the full catalogue. The scripts do the mechanical work (merge, grade, figures,
annexes, citations, build, checks). The chapters are written by people or by AI drafting agents from
evidence packs, under the brief in [references/drafting-brief.md](references/drafting-brief.md).

It does not create evidence, and it does not decide legal questions: those stay questions, collected
in Annex D for a separate legal assessment.

## Quick start (synthetic example)

`<skill-dir>` is the folder holding this SKILL.md. Needs Python 3.9+, the packages in
`requirements.txt`, and pandoc for the .docx step.

```bash
pip install -r <skill-dir>/requirements.txt
python <skill-dir>/scripts/run_all.py <skill-dir>/examples/synthetic-config.yaml
# writes <skill-dir>/examples/_build/out/kali-wening-water-tenure-SYNTHETIC.docx and ...-annexes.docx
```

The example merges the synthetic field catalogue of the `water-tenure-analysis` skill with the
synthetic media scan of the `water-tenure-media-scan` skill, and builds the chapters in
`examples/synthetic-chapters/`. Everything in it is invented. Without pandoc, add `--no-docx`: the
checks still run and `main.md` is written.

## The order of work

1. **Check the inputs.** Every catalogue must pass `check_catalogue.py` with no errors.
2. **Write the config** (copy `examples/synthetic-config.yaml`; every key is explained in
   [references/config.md](references/config.md)): inputs and id prefixes, map units and groups,
   Parts, reserved method sources, citation style, AI-use statement.
3. **Basemap (optional).** `scripts/fetch_basemap.py` lists the geoBoundaries and OpenStreetMap
   downloads for the configured extent and fetches them only with `--download`. Ask the user before
   downloading. Without a basemap, maps carry a notice and everything else builds.
4. **Merge** (`merge.py`): master registers, evidence grades, and one evidence pack per tenure type
   in `<work>/packs/`. Records are never deleted or fused; duplicates across catalogues are both kept
   and cited together.
5. **Figures** (`figures.py`): location map, records map, a map and a use chart per tenure type, the
   tenure-by-use heatmap, grades, confidence, season, typology, groups, verification.
6. **Draft the chapters** from the packs, one drafter per chapter or per Part, with the drafting
   brief. The orchestrating agent or the lead author writes the introduction, the methodology and
   the synthesis, and integrates. Chapter files are `ch<NN>-<slug>.md` in `chapters_dir`.
7. **Annexes** (`annexes.py`): A to K, generated from the records.
8. **Check-build** (`build.py --check-only`): every token resolves, no token outside a footnote, no
   missing figure, no footnote resting only on social media outside a Clues section, no unknown
   record id, vocabulary hits reported. Fix and repeat.
9. **Cite-check** with [references/citecheck-brief.md](references/citecheck-brief.md): agents or
   reviewers read a sample of footnoted statements against their sources and correct the chapters.
   Write the summary for Annex H.
10. **Build** (`build.py --annexes`, or `run_all.py`): `main.md`, the two .docx files and
    `build-report.json`.
11. **Human review.** Nothing leaves the team until the person responsible has read it. The report
    states what no person has yet verified (Annex H).

## Report architecture

Front matter (authorship and AI-use statement, executive summary, list of figures); Chapter 1
Introduction; Chapter 2 Methodology; **Part I**, rights granted or held by the state (traditional
formal rights, modern permits, regulatory licences, agency control, water supply contracts,
investment contracts, declared or exempt commercial uses, reserves and minimum flows, de minimis
rights); **Part II**, collective and community tenure (commonhold, customary, religious-law);
**Part III**, tenure outside or against the state (informal, assumed, unrecognised, impossible);
Synthesis (layering, paper against wet water, seasonality, head and tail, land and water,
toleration, economic power, invisible users, conflict hotspots, the legal-referral agenda). Each
tenure-type chapter follows the nine-section template in the drafting brief. A type with no record
keeps a short chapter saying whether it is absent or was not looked for.

Annexes: A catalogue by type; B points gazetteer (sensitive coordinates rounded); C coverage by map
unit; D questions for legal assessment; E source register with grades; F contested and layered
classifications; G seasonal fieldwork calendar; H AI use and provenance; I social-media clue
register; J unclassified records; K fieldwork questions by place.

## Citations, grades and confidence

- Chapters cite only by token inside pandoc footnotes: `^[{{S01}} 12; {{INT-V1-01}} l 15.]`.
  `{{ID|anon}}` drops a private account's name. OSCOLA prints the full reference at first use and
  "short form (n X)" after; APA prints author-date forms and appends a reference list.
- Sources a reader cannot open (team files, restricted, drive-only, lost) are cited as "on file
  with the research team", so internal paths never reach a report.
- **Evidence grade** belongs to a source and says what kind of source it is: E1 primary legal or
  official, E2 field primary, E3 scholarly or technical, E4 press, E5 social media, D derived digest.
  **Confidence** belongs to a record and comes from triangulation. Neither substitutes for the other.
- E5 is a clue: it may corroborate E1-E4 evidence, or appear as a lead in a Clues section and
  Annex I, never as a finding on its own.

## Rules that are not negotiable

- No citation, no statement; never invent a source, figure, place or quotation.
- No legal conclusions in the report's own voice; legal questions go to Annex D, unanswered.
- No respondent names; officials by office; private social-media accounts not identified.
- Figures exactly as the source prints them; conflicting figures side by side, never averaged.
- AI-generated material is never evidence. Derived digests point to originals.
- Disclose AI use honestly, and keep transcripts private (see
  [references/ai-use-annex.md](references/ai-use-annex.md)).
- No emoji or status icons. In Indonesian text, use "tenurial" for tenure.

## Scripts

| Script | What it does |
|---|---|
| `scripts/run_all.py <config> [--no-docx] [--no-annexes]` | Runs the checker on every input, then merge, figures, annexes, reference template and build |
| `scripts/merge.py <config>` | Master registers, evidence grades, `sources.json`, evidence packs |
| `scripts/figures.py <config>` | PNG figures at 300 dpi, colour-blind-safe palette, a source line under each |
| `scripts/annexes.py <config>` | Annexes A to K as Markdown |
| `scripts/build.py <config> [--annexes] [--check-only] [--strict]` | Assembly, token resolution, figure numbering, checks, pandoc .docx |
| `scripts/make_reference.py <config> [--out FILE]` | Styled pandoc reference template (fonts, colours, A4 or Letter) |
| `scripts/fetch_basemap.py <config> --iso3 XXX [--download]` | Optional, network: geoBoundaries units and OSM rivers clipped to the extent |
| `scripts/mine_sessions.py <config> SESSION...` | Optional: counts from Claude Code transcripts for Annex H; human turns kept private |
| `scripts/export_diagram.py <html> <png>` | Optional: HTML diagram to PNG (needs Playwright) |

`common.py`, `citations.py` and `geo.py` are shared helpers.

## Reference files

| File | Read when |
|---|---|
| [references/config.md](references/config.md) | Writing or changing a config |
| [references/drafting-brief.md](references/drafting-brief.md) | Before drafting any chapter, and to brief drafting agents |
| [references/citecheck-brief.md](references/citecheck-brief.md) | Before the cite-check, and to brief cite-check agents |
| [references/diagram-brief.md](references/diagram-brief.md) | When a chapter needs a mechanism diagram |
| [references/ai-use-annex.md](references/ai-use-annex.md) | Writing the authorship line, the methodology section on AI use, or Annex H |

## Delegation

With subagents available: one drafter per Part (or per long chapter), each given the drafting brief,
its packs and a word target; three or four cite-check agents, each with a batch of chapters; the
orchestrator writes the introduction, methodology and synthesis and runs every script itself. Drafters
and checkers write only to their assigned chapter files. Use the strongest available model for the
synthesis and for cite-check judgements; mechanical steps need no model at all.
