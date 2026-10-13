---
name: water-tenure-assessment
description: 'Orchestrates an end-to-end water tenure assessment of a basin, district or scheme: scope, corpus, catalogue (from field material or a hyperresearch desk run), optional recent-media scan, merged long-form report by FAO tenure type, cite-check, referral of legal questions, and publication to a tenure map, with human review gates between phases and an honest account of AI use. Says which sub-skill to use when, how to delegate to subagents, and what a person must decide. This skill should be used when the user asks for a water tenure assessment, a full or end-to-end water tenure analysis or study, a water tenure assessment plan, or asks where to start, what to run next, or how the water tenure skills fit together ("asesmen tenurial air", "kajian tenurial air", "water tenure assessment").'
license: MIT
metadata:
  version: "1.0.0"
  author: "CRPG - Center for Regulation, Policy and Governance (vibe-coded with AI agents, orchestrated by Mohamad Mova Al'Afghani)"
---

# Water tenure assessment

A water tenure assessment asks who uses which water, where, under what rules, and how secure those
arrangements are. FAO's approach separates the empirical stream (what happens on the ground) from the
legal stream (what the law says about it). This pack serves the empirical stream end to end, and
hands the legal questions over. This skill is the map of the pack: it decides which skill runs when,
and where a person must decide.

## The skills and when to use them

| Skill | Use it to | Output |
|---|---|---|
| `water-tenure-analysis` | Catalogue arrangements from any evidence, under the FAO typology, with cited and checked records. The core of everything else | `sources.csv`, `arrangements.csv`, `matrix.md`, `report.md` |
| `water-tenure-hyperresearch` | Run an exhaustive desk assessment of an area with hyperresearch, building the catalogue inside the run | A catalogue and a report divided by tenure type |
| `water-tenure-media-scan` | Add the last N days of news, agency notices and social media at named places | A second catalogue and a scan log |
| `water-tenure-report` | Merge catalogues and build the long-form report, one chapter per tenure type, with annexes A-K and footnotes | Two .docx volumes and a build report |
| `tenure-storymap-publish` | Put the catalogue on a public map with the protection rules applied | Map records for the storymap engine |

A small job needs only the first skill: a village inventory from field transcripts is a catalogue and
its `report.md`. Add skills as the scope grows.

## The workflow

```
G0 scope -> corpus -> catalogue -> G1 -> [media scan] -> report (draft, cite-check, build) -> G2
         -> legal referral (G3) -> [publish to map] (G4)
```

1. **Scope (gate G0).** Fill the scope sheet with the person directing the work:
   [references/scope-sheet.md](references/scope-sheet.md). Nothing runs before it is signed off.
2. **Corpus.** Register the team's material before reading it for content; separate originals from
   digests and AI-generated files.
3. **Catalogue (gate G1).** Field or small desk: `water-tenure-analysis`. Exhaustive desk:
   `water-tenure-hyperresearch`. The checker must report no errors; a person reads a sample of
   records against their sources.
4. **Media scan (optional).** `water-tenure-media-scan` for the scope's window and places.
5. **Report (gate G2).** `water-tenure-report`: merge, figures, packs, drafting, annexes, cite-check,
   build. A person reads the whole main text before anyone else does.
6. **Legal referral (gate G3).** Annex D goes, with its records, to whoever does the legal
   assessment. The field stream does not answer it.
7. **Publish (gate G4, optional).** `tenure-storymap-publish`, after a person approves the
   publication copy and, for sacred or customary sites, the community agrees.

Inputs, outputs and commands for every phase: [references/workflow.md](references/workflow.md).
What each gate checks: [references/review-gates.md](references/review-gates.md).

## Delegating to agents

- **The orchestrating session** (the strongest model available) holds the scope, runs every script
  itself, merges, writes the introduction, methodology and synthesis, and prepares each gate.
- **Subagents** do bounded jobs with a written brief and a fixed output path: catalogue agents per
  tenure-type group, local-ingest and search agents, chapter drafters per Part, cite-check agents per
  batch of chapters. Give each its brief file from the relevant skill; never let two agents write the
  same file.
- **Model choice:** fast models for extraction, ingestion and searching; the strongest for
  classification calls, depth investigation, synthesis and cite-check judgements. Scripts need no
  model at all: prefer a script whenever a step is mechanical.
- **Long runs** keep their state on disk (run manifests, revision logs, the provenance log), so a
  resumed session reads where it is instead of guessing.

## Rules that are not negotiable

- Every record and every statement traces to a source a person can open, at a pinpoint.
- AI-generated material is never evidence. Digests point to originals.
- Legal questions are referred, never answered, in the field stream.
- People are protected: no names, allegations as patterns, sensitive locations generalised.
- A person decides at every gate. Nothing is sent, posted or published without that person's explicit
  approval.
- AI use is disclosed honestly: who directed, which agents and models drafted, what a person checked,
  what no one has yet verified. See [references/provenance.md](references/provenance.md).
- No emoji or status icons in deliverables. In Indonesian deliverables, "tenurial" for tenure.

## Reference files

| File | Read when |
|---|---|
| [references/scope-sheet.md](references/scope-sheet.md) | Starting an assessment |
| [references/workflow.md](references/workflow.md) | Planning or running any phase |
| [references/review-gates.md](references/review-gates.md) | Preparing or holding a gate |
| [references/provenance.md](references/provenance.md) | From the first session: what to log, and the AI-use statement |
