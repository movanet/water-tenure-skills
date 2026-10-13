# Workflow, phase by phase

Each phase lists what goes in, what comes out, the skill that does it, and the gate that closes it.
Gates G0 to G4 are human decisions; see [review-gates.md](review-gates.md).

## Phase 0: Scope (gate G0)

- **In:** the request; what is known of the area; the audience and use of the result.
- **Do:** fill the scope sheet ([scope-sheet.md](scope-sheet.md)) with the person directing the work.
  Decide which phases run: a field catalogue only, a desk assessment, a media scan, a long-form
  report, a map.
- **Out:** the signed-off scope sheet; the project folder layout:

  ```
  <project>/
    scope.md                    the scope sheet
    corpus/                     the project's own evidence, organised by source (not versioned publicly)
    tenure-catalogue/<area>-<date>/          the desk or field catalogue
    tenure-catalogue/<area>-news-<date>/     the media scan catalogue
    report/                     report config, chapters, work directory
    provenance/                 the log of sessions, runs, decisions (see provenance.md)
  ```

## Phase 1: Corpus

- **In:** the team's field material (transcripts, notes, maps, decks), documents gathered so far.
- **Do:** register what exists before reading it for content; separate originals from digests and
  AI-generated files; extract text with page, line or slide markers intact (PyMuPDF for PDFs,
  python-pptx for decks). Ask before downloading anything from shared drives.
- **Out:** an inventory of the corpus with source types and verifiability, ready for cataloguing or for
  ingestion into a research vault.
- **Skill:** `water-tenure-analysis` (step 2 and `references/sources-and-citation.md`).

## Phase 2: Catalogue (gate G1)

Two routes, which can be combined:

- **Field or small desk catalogue:** `water-tenure-analysis` steps 1 to 10 directly on the corpus.
- **Exhaustive desk assessment of an area:** `water-tenure-hyperresearch`: render the run inputs from
  the scope, run hyperresearch at the chosen gear, build the catalogue inside the run (stage C,
  C-revision, C-verify), deliver `report.md` with the catalogue.

- **Out:** `sources.csv`, `arrangements.csv`, `matrix.md`, `report.md`, group notes with audited
  absences, a revision log, the spot-verification note ("n of N").
- **Check:** `check_catalogue.py` with no errors; warnings read and answered.

## Phase 3: Recent media (optional)

- **In:** the scope sheet's places, themes, exclusions, window.
- **Do:** `water-tenure-media-scan`: query plan, last30days passes and web lanes, records under the
  analysis rules, `scan_check.py`, `verify_figures.py`.
- **Out:** a second catalogue with its scan log.

## Phase 4: Merge, draft and check the report (gate G2)

- **Do:** `water-tenure-report`: config; merge (the scan gets its own id prefix); figures; evidence
  packs; drafting by chapter or by Part under the drafting brief; annexes; check-build; cite-check
  under the cite-check brief; build.
- **Out:** the main volume and the annex volume (.docx), `build-report.json`, the cite-check summary,
  Annex H.

## Phase 5: Legal referral (gate G3)

- **In:** Annex D (every `legal_flag`, grouped, with the records it rests on).
- **Do:** hand the questions and their records to whoever does the legal assessment. The field
  stream does not answer them; see `water-tenure-analysis` `references/legal-boundary.md`.
- **Out:** a referral note listing the questions, the records, and what each question needs (the
  instrument to check, the authority to ask).

## Phase 6: Publish (gate G4)

- **Do:** `tenure-storymap-publish`: publication copy, review, import to a seed file or a running site.
- **Out:** map records with the protection rules applied; a record of what was published and when.

## Closing

Write the provenance record (sessions, runs, versions of the skills and tools, decisions at each
gate, what remains unverified) and the project's own state record. Nothing is sent, posted or
published without the explicit approval of the person responsible.
