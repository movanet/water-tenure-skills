---
name: water-tenure-analysis
description: 'Catalogues water tenure arrangements from empirical evidence (interview and FGD transcripts, field notes, maps, permit registers, archives, news, NGO reports, papers) into a source-cited CSV inventory of who uses which water, where, and under what rules. Classifies each arrangement on the FAO water tenure typology and FAO water-use codes, locates it administratively and hydrologically, finds invisible users, and grades confidence by triangulation. Legal questions are flagged for a separate legal assessment, never answered. This skill should be used when the user asks to map, inventory, catalogue or analyse water tenure, water rights in practice, water uses and users, irrigation, pumping, spring or well arrangements, customary or informal water practices, a water tenure assessment from field data, or to check a tenure catalogue, in any country and in English or Indonesian ("tenurial air", "pengguna air", "pompanisasi", "P3A", "mitra cai").'
license: MIT
metadata:
  version: "1.1.0"
  author: "CRPG - Center for Regulation, Policy and Governance (vibe-coded with AI agents, orchestrated by Mohamad Mova Al'Afghani)"
  built_from: "FAO water tenure publications (2016, 2020, 2024); AlAfghani and Susetyo (2023); AlAfghani, Lee and Yasuda (2025); lessons from CRPG field assessments (unpublished material is not reproduced)"
---

# Water tenure analysis

Water tenure is the relationship, whether legally or customarily defined, between people, as
individuals or groups, with respect to water resources (FAO 2016, *Exploring the concept of water
tenure*). This skill does the empirical half of a water tenure assessment: it finds every
arrangement the evidence shows, describes how each one works on the ground, and ties every statement
to a source a person can open and check.

It does **not** decide what the law says. Whether a use needs a permit, whether a water user group
can hold one, whether a custom is recognised: those go into a `legal_flag` question for whoever does
the legal assessment. FAO's assessment method runs legal research and field research as separate
streams with separate expertise; this skill is the field stream. The boundary is set out in
[references/legal-boundary.md](references/legal-boundary.md). Keep to it. A field catalogue that
quietly asserts legality ends up rating informal tenure on a statute reading inside what was meant
to be a description of practice, and then neither a lawyer nor a field researcher can review it.

## Quick start

`<skill-dir>` is the folder that holds this SKILL.md (Claude Code prints it as "Base directory for
this skill"). The synthetic example catalogue is invented, placed in a fictional basin, and passes
the checker:

```bash
python <skill-dir>/scripts/check_catalogue.py <skill-dir>/examples/synthetic-catalogue
python <skill-dir>/scripts/build_matrix.py <skill-dir>/examples/synthetic-catalogue --out /tmp/matrix.md
```

To start a new catalogue, copy the two templates from `assets/` into an empty folder, rename them
`sources.csv` and `arrangements.csv`, and follow the order of work below. Python 3.9+ standard library
only; no packages needed.

## Why the discipline matters

Field tenure material, once it has passed through a few rounds of reports and slide decks, tends to
contain: footnotes that cite sources which do not support their sentence; a validation report that
adds its own unsourced fact; triangulation slides whose source attributions change between versions;
one set of interviews reported with two different denominators; one label covering two different
payment mechanisms with two different figures; chatbot-written notes filed beside field transcripts;
and file names that do not match their contents. None of it is malicious. All of it survives a review
that checks format instead of substance. The rules below exist to stop each of these.

## The order of work

1. **Fix the scope.** One sentence naming the area (basin, scheme, villages), the period and the
   question: "Which arrangements give the three study villages of the Kali Wening scheme their
   irrigation and household water, by season, fieldwork of January-February". Note what is out of
   scope.
2. **Register the sources before reading them for content.** Every file, record, article or
   transcript becomes a row in `sources.csv` with a type, date, path or URL and a locator scheme
   (page, line, slide, timestamp, row). Classify AI-generated and derived documents as such *now*,
   before their content contaminates the catalogue. See
   [references/sources-and-citation.md](references/sources-and-citation.md).
3. **Extract arrangements**, one record per rule-set x user group x source x place x season, into
   `arrangements.csv`. Copy the verbatim quote in its original language with its pinpoint, then the
   translation. Describe the mechanism: who gets water, from where, when, how much, who decides,
   who pays what, who maintains, who enforces, what happens on breach. Field definitions:
   [references/record-schema.md](references/record-schema.md).
4. **Classify** each record on the tenure typology and the use codes:
   [references/typology.md](references/typology.md). Classify on reported practice and reported
   treatment by officials; put the legal premise into `classification_basis` as a reported fact and
   the question into `legal_flag`. Use `unclassified` rather than guess.
5. **Locate** it twice: administratively (province > district > sub-district > village >
   hamlet/block) and hydrologically (basin > scheme > primary/secondary/tertiary canal > gate or
   structure, or river reach, spring, well field). Head-end or tail-end position decides access in
   irrigation systems more often than any document does, so record it. Give coordinates only where a
   source states them; never estimate them.
6. **Look for who is missing.** Run the visibility checklist in
   [references/field-methods.md](references/field-methods.md): women's household and hygiene water,
   persons with disabilities, landless labourers, tenants and seasonal lessees, non-resident
   landowners, fishers, herders, upland plots no canal reaches, groundwater users excluded from water
   accounts, ritual and sacred sources. An absence the evidence supports is a finding.
7. **Grade confidence** and record contradictions. `triangulated` needs at least three independent
   origins covering at least two primary source types. An agency official describing the agency's own
   reform and the agency's report of that reform are one leg, not two. So are two decks made from the
   same fieldwork round. Keep single-informant claims as `uncorroborated` and say so in the prose
   ("alleged by one farmer"). When sources disagree, keep both figures, each attached to its own
   source and mechanism, in `contradictions`. Never average or pick.
8. **Run the checker** and fix every error; read every warning:

   ```bash
   python <skill-dir>/scripts/check_catalogue.py <catalogue-dir>
   python <skill-dir>/scripts/build_matrix.py <catalogue-dir>
   ```

9. **Spot-verify before delivery.** Re-open the source at the pinpoint for every figure, every
   quote, and a sample of at least one in five other records, and confirm the source says what the
   record says. Report coverage as "n of N checked", never as a percentage alone.
10. **Deliver** (format below), with the legal flags gathered into one referral list.

## Deliverable

A catalogue directory, plus a short report:

```
<catalogue-dir>/
  sources.csv          source register (assets/sources.template.csv)
  arrangements.csv     one row per arrangement (assets/arrangements.template.csv)
  matrix.md            tenure type x use code, cell = record count (build_matrix.py)
  report.md            the narrative, below
```

`report.md`, in this order:

1. **Scope and sources**: area, period, question; counts of sources by type; what was not available.
2. **Catalogue by tenure type**: for each type found, its arrangements, each with local name,
   location, users, a short account of how it works, a verbatim quote where the source is an
   interview, and citations in the form `[S12 p.34]` / `[INT-V1-04 l.212]` that resolve in
   `sources.csv`.
3. **Water uses and users**: by use code, with the users and where they are, including absent users.
4. **The tenure x use matrix** and what its empty rows and columns mean (absent, or not looked for).
5. **Patterns** across arrangements: layering, seasonality, upstream-downstream position, land-water
   links, toleration, economic power, conflict hotspots. Attribute analytical lenses to their origin.
6. **Contradictions and gaps**: conflicting figures, unresolved classifications, what fieldwork
   should ask next.
7. **Referral for legal assessment**: every `legal_flag`, grouped by question, with the records it
   affects. Questions only.
8. **Verification note**: what was spot-checked (n of N), what remains UNVERIFIED.

Write in the neutral register of FAO's guidance: describe the use, attribute any judgement
("described by the gate keeper as *maling air*", water theft), and avoid the judgmental label
"illegal water use". No status icons or emoji. In Indonesian deliverables, use "tenurial" for
tenure. For a long report organised by tenure type, hand the catalogue to the `water-tenure-report`
skill.

## Rules that are not negotiable

- **No citation, no record.** A statement without a source and a pinpoint stays out of the
  catalogue, or goes into `gaps_next_steps` as a question.
- **Cite the original, not the digest, whenever it can be opened.** If a claim reaches you through a
  summary, a wiki page, a slide, a JSON extraction or an AI-written note, look for the original
  transcript, record or article and cite that. If the original is out of reach, cite the team
  deliverable that quotes it, set `derived_from` so several deliverables from one fieldwork round
  count as one origin, and put the hop chain in `notes` ("deck > INT-V1-04, transcript not opened").
  [record-schema.md](references/record-schema.md) says how far confidence can go in that case. Ask
  the user before downloading anything.
- **AI-generated material is never evidence.** Files written by a chatbot (signs: "You raise an
  interesting point", "AI Generated" in the name, unsourced fluent synthesis, references that do not
  resolve) are registered as `ai-generated` and may point you to originals; they never support a
  record alone. The checker enforces this.
- **Numbers match the source verbatim**, unit included, or are marked UNVERIFIED. A "semantic match"
  is not a match. Record which source states each figure in `figures_source`.
- **Denominators always.** "0 of 20 women interviewed attend water user group meetings (village A 10,
  village B 10)", not "no women participate". Do not generalise a small sample to "universally".
- **One code stream per respondent group.** Interview codes collide across teams. Namespace them
  (`INT-V1-04`, `FGD-AG-2501`) and keep the code-to-person key private, outside the catalogue.
- **Protect people.** Cite respondents by code and role, never by name, in anything that leaves the
  team. Report sensitive allegations (bribery, "water mafia", threats) as patterns without naming
  individuals or offices that would identify them. See
  [sources-and-citation.md section 6](references/sources-and-citation.md).
- **Stay out of the law.** See [references/legal-boundary.md](references/legal-boundary.md).

## Housekeeping

- **Write the catalogue where the user says**, by default a `tenure-catalogue/<area>-<date>/` folder
  inside the project. Keep project state (what was delivered, what is next) in the project's own
  tracker, not inside the catalogue.
- If running as a subagent and writing `report.md` is refused, return the report text in the final
  message so the caller can save it.
- **Reading budget.** Always read [typology.md](references/typology.md) sections 2-4 and
  [record-schema.md](references/record-schema.md). Read the others when their trigger in the table
  below applies.

## Reference files

| File | Read when |
|---|---|
| [references/typology.md](references/typology.md) | Classifying tenure type and use code; deciding between candidate types |
| [references/record-schema.md](references/record-schema.md) | Filling `sources.csv` and `arrangements.csv` |
| [references/sources-and-citation.md](references/sources-and-citation.md) | Registering sources, citing, extracting text from PDFs and decks, verifying, the failure modes |
| [references/field-methods.md](references/field-methods.md) | Planning or reading fieldwork; interview prompts; the visibility checklist; local terms |
| [references/legal-boundary.md](references/legal-boundary.md) | Anything that smells like a legal question |
| [references/calibration-cases.md](references/calibration-cases.md) | Worked patterns (synthetic, and from published cases in Indonesia and other countries) to calibrate classification and detail |

## Scripts and examples

| Path | What it does |
|---|---|
| `scripts/check_catalogue.py <dir> [--json] [--strict]` | Validates both CSVs: vocabularies, citations paired with locators, triangulation counts by independent origin, AI-only support, legal flags phrased as questions. Exit 1 on errors (or on warnings with `--strict`) |
| `scripts/build_matrix.py <dir> [--out FILE]` | Writes the tenure type x use code matrix, each cell traced to record IDs |
| `scripts/export_storymap.py <dir> --out FILE.geojson` | Optional. Map records for a storymap (see the `tenure-storymap-publish` skill): only records with source-stated coordinates; no names; sensitive types, sacred sites, allegations and records citing consent-restricted sources rounded and marked `aggregate_only` |
| `assets/*.template.csv` | Empty CSVs with the header rows |
| `examples/synthetic-catalogue/` | A small invented catalogue that passes the checker; read it to see the grain of a good record |

## Tools

- **PDFs**: extract with PyMuPDF (`fitz`) page by page, keeping page markers so pinpoints survive;
  OCR only pages that return no text, and say which in `reliability_notes`.
- **Slide decks**: `python-pptx`, slide numbers and speaker notes included; image-only slides need
  the embedded image read, and say so in `notes`.
- **Notes and knowledge bases**: a local search index over project notes finds material fast, but
  wiki pages are digests: follow them to the originals before citing.
- **Regulations**, when a legal flag needs an identifier: use an official regulation database to
  confirm the instrument's number and title. The analysis of it belongs to the legal stage.
