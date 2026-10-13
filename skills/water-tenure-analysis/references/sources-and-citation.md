# Sources and citation

Contents: 1. Evidence types and what each can carry · 2. Citation format · 3. Getting text out
of files · 4. Verification · 5. Failure modes seen in practice · 6. People and sensitive material

## 1. Evidence types and what each can carry

Water tenure in practice is mostly undocumented. FAO's guidance notes that informal, assumed and
impossible tenure can usually be identified only through interviews and field research. Records and
desk sources describe the formal layer and its gaps; people describe what actually happens. Use each
for what it can carry.

| Type | Good for | Watch for |
|---|---|---|
| Interview, group interview | How an arrangement works, who decides, payments, perceived security, conflicts | One voice; speaker's interest; ASR errors in transcripts; translation |
| FGD | Shared rules, schedules, disagreements surfaced in the room | Dominant voices; women and the poor silent in mixed groups; summaries replacing verbatim |
| Validation workshop | Officials' positions, confirmation or contradiction of field findings | Officials grading their own reforms; earlier findings fed back and returned as "confirmation" |
| Observation, photo, video, drone, community map | Existence, location and count of structures (pumps, canal openings, pipes, wells), condition of canals | Captions written later; counts from one walk |
| Admin record, permit register, statistics | What is formally recorded: permits, expiry dates, coverage, scheme areas, user group registration | Missing and stale fields (blank permit numbers and dates are common); a register shows paper, not water |
| Archive (colonial irrigation records, old reports, village records) | Origins and history of schemes and offices, past allocations | Terms that changed meaning; scheme names that changed |
| News | Events, conflicts, dates, official statements, cases outside the field area | Second-hand; check the outlet, date and jurisdiction; headlines exaggerate |
| NGO report | Cases and testimony from affected people | Advocacy framing; often the only source for remote cases; cite as such |
| Academic, grey report | Context, prior typologies, comparison | Out-of-area sources cited for local claims |
| Project deliverable, slide deck | The team's own observations (mapping counts, photos); pointers to originals for quotes | Digest drift: in real assessment corpora this is where most errors live |
| Derived summary (wiki page, thematic summary, JSON extraction) | Pointers to originals | Summarisers drop context and insert generalities. If a summary contains claims its inputs do not support ("a common pattern in Java"), or marks its inputs unreadable and still reports on them, register it as `ai-generated` |
| Social media | Leads, dates and places of events, institutional announcements | Anonymous authors, wrong place or date, reposts. A clue, never a finding on its own (see the `water-tenure-media-scan` skill) |
| AI-generated | Leads only | Never evidence; see section 5 |

When describing a remote case from news and NGO sources, record each claim with its outlet, date and
URL, record the hop chain if you got it second-hand ("poster > news site"), and do not infer tenure
types the sources do not describe. Inferring "customary sago-grove tenure" from a story about forest
clearing is the inference this skill must not make; write "customary use of sago groves is reported
(source); its tenure arrangement is not described".

## 2. Citation format

In `arrangements.csv`: `source_ids` + `locators`, paired one-to-one. In prose (`report.md`):
`[<source_id> <locator>]`, e.g. `[INT-V1-04 l.212]`, `[S07 p.34]`, `[S12 slide 14]`,
`[FGD-AG-2501 00:41:10]`. Several: `[INT-V1-04 l.212; S21 p.12]`. For a long report with footnotes,
the `water-tenure-report` skill uses `{{S07}} p 34` tokens that its build script expands into OSCOLA
or APA references.

Every `source_id` must resolve to a row of `sources.csv` with an absolute path or URL. That is what
makes the citation checkable by someone who was not in the room.

Rules that came out of reviewer comments on real assessment reports:

- Quotes carry speaker role, place, date and context. "Who said this?" and "Who is 'they'?" are
  typical reviewer comments.
- Original language first, translation second, marked as such.
- A dataset is named with its custodian, method and date, not "the data".
- A target or plan stated by an agency ("full compliance by next year") is reported as the agency's
  statement.
- One numbering scheme per document; no Ibid or Op. Cit. chains, which break when a source moves.
- Draft guidance marked "do not cite" is used as method only; in published text cite FAO 2016 (Land
  and Water Discussion Paper 10) for definitions and the published FAO works where the content
  matches.

## 3. Getting text out of files

- **PDF**: PyMuPDF first, page by page, keeping `## Page N` markers so pinpoints survive. Only if a
  page returns no text, OCR it. Record in `reliability_notes` which pages were OCR'd.

  ```python
  import fitz  # PyMuPDF
  doc = fitz.open(path)
  text = "\n".join(f"## Page {i+1}\n{p.get_text()}" for i, p in enumerate(doc))
  ```

- **PPTX**: `python-pptx`, slide text, tables and speaker notes, with `## Slide N` markers. Slides
  that are a single image (infographics, triangulation diagrams) yield almost no text: extract the
  image from `ppt/media/` and read it, and say in `notes` that the content came from an image.
- **DOCX**: `python-docx` or pandoc to Markdown; keep paragraph numbers if you will cite them.
- **Audio**: cite the timestamp of the original recording. A transcript is a derived source: name
  who or what transcribed it and whether anyone checked it.
- **JSON extractions**: some do not parse. Read them as text if needed, and treat every value as a
  pointer back to the transcript.
- **Web pages**: save the extracted text with the access date. Pages whose article body loads by
  script may return only a shell; mark figures from them UNVERIFIED until a human reads the page.

## 4. Verification

Before delivery, for every figure and every quote, and for at least one in five other records:

1. Open the source at the pinpoint.
2. Confirm the source says what the record says, number and unit verbatim, attributed to the right
   speaker and place.
3. Confirm the source is about this place and period (a website of a village in another district does
   not evidence a practice in the study village).
4. Mark the record `[verified YYYY-MM-DD]` in `notes`, or correct it, or downgrade `confidence`.

Report as "n of N records spot-verified; all figures and quotes verified" or say exactly what was
not. A format check (the citation exists and looks right) is not verification. Footnote "validation"
that confirms that every footnote has a definition says nothing about whether the footnotes support
their sentences.

When a verifier, human or model, adds a fact during checking, that fact needs its own source too.

## 5. Failure modes seen in practice

These were found in the working folders of real water tenure assessments, including material produced
with AI assistance. They are the reason for the rules above. The examples are generalised.

| Failure | Example | Rule |
|---|---|---|
| Footnotes offset from their claims | A note on utility coverage cites a zoning article about a power plant; a note on spring custom cites an article about a geothermal plant | Check the source supports the sentence, not just that a footnote exists |
| Duplicate footnote labels | The same labels defined three times in one file | One numbering per document |
| Citation to a derived, deleted file | Citations point to a team document that no longer exists, "accessed via" another derived file | Cite originals |
| Validator added its own fact | A validation report gives a power plant's water source and capacity that contradict the catalogue, with no source | Facts added in checking need sources |
| Coverage reported as accuracy | A high "validation accuracy" percentage where under a third of quotes were checked | Report n of N |
| "Semantic match" accepted | A figure not found verbatim was accepted as matching | Verbatim or UNVERIFIED |
| AI desk reports filed as fieldwork | Deep-research outputs saved in the fieldwork folder; one leaks its own prompt, one cites a repealed law, one invents a local institution | Classify by content, not folder; `ai-generated` never supports a record |
| Chatbot prose in imported notes | A note opens a section with "You raise an interesting point" and cites references that were never checked | Same |
| LLM summaries treated as data | Village summaries list interviews as "unable to read" yet are cited for them; generic claims inserted | Summaries are pointers |
| ASR artefacts minted as terms | A local term misheard into a new word; village and canal names misheard; a land unit misheard as a number | Keep a variants list; confirm terms in two sources |
| Same figure, different denominators | One set of women's interviews reported with two different denominators in two decks | Denominators always; trace to the transcript set |
| Two mechanisms merged under one label | One label covering a per-village gate-diversion fee and pump operators' charges, with very different figures | Attach each figure to its mechanism |
| Triangulation legs swapped | Two versions of a triangulation slide attribute the same quote to different events, and the label moves from "confirmed" to "triangulated" with no new evidence | Each leg independent, with its own pinpoint |
| One term, three definitions | A canal opening described as a sack-and-stone structure built by a village official, as unauthorised taps, and as cloth barriers at tertiary level | Keep the field description with its source; list variants in `contradictions` |
| File names do not match content | A file named for one chapter holds another; wiki pages cite the wrong file | Cite by heading and line in the file actually opened |
| Legal annex imports contradicting field claims | An annex asserts customary prohibitions at a sacred source "per the field report", while the field chapter says access rules were not documented | A legal annex is not field evidence |
| Misquoted framework source | A blog cites the wrong FAO discussion paper, the wrong number of categories and an extended definition | Check framework citations against the primary text |
| Sample generalised | Drinking water said to come "universally" from refill bottles, based on 20 interviews in two villages | Scope claims to the sample |
| Same person in several roles | One name appears as interviewer, facilitator, FGD participant and agency staff across files | Resolve identities before counting sources as independent |

## 6. People and sensitive material

- Respondents are cited by code and role. Keep the code-to-person key out of the catalogue.
- Village names: follow the project's agreement. Many projects replace village names with codes
  (V-01, V-02) for publication; internal catalogues may keep names if the consent terms allow. Check
  the project's anonymisation strategy and the consent script actually read to respondents (a promise
  that names will not appear in the report binds the catalogue too).
- Allegations of bribery, extortion, threats or "water mafia" are described as patterns, attributed
  to the kind of informant ("farmers in two villages allege..."), confidence `uncorroborated` until
  independently corroborated, with no names of individuals or units that would identify them.
- Never copy phone numbers, ID numbers or addresses from source files into the catalogue.
- Exact coordinates of sensitive points (informal abstraction, sacred sites, places tied to
  allegations) are kept in the internal catalogue only; anything published gets aggregated or fuzzed
  locations (see the `tenure-storymap-publish` skill).
