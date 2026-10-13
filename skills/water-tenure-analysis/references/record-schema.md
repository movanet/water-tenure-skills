# Record schema

Two CSV files, UTF-8, comma-separated, header row first. Templates:
[../assets/sources.template.csv](../assets/sources.template.csv) and
[../assets/arrangements.template.csv](../assets/arrangements.template.csv). Multi-valued cells use
`;`. CSV rather than JSON because a human verifier opens it in a spreadsheet, filters by source or
village, and ticks rows; machine-written JSON extractions of field data also fail to parse more often
than one would expect. A complete worked example is in
[../examples/synthetic-catalogue/](../examples/synthetic-catalogue/) (invented data).

## sources.csv: one row per source

| Column | Required | Content |
|---|---|---|
| `source_id` | yes | Short stable key used in citations: `S01`..., or a namespaced interview code such as `INT-V1-04`, `FGD-AG-2501`. Namespace by collection team or stream so codes cannot collide |
| `source_type` | yes | One of: `interview`, `group-interview`, `fgd`, `workshop`, `observation`, `photo-video`, `map-drone`, `community-mapping`, `admin-record`, `permit-register`, `statistics`, `archive`, `news`, `ngo-report`, `academic`, `grey-report`, `project-deliverable`, `derived-summary`, `social-media`, `ai-generated`. Use `project-deliverable` for the team's own reports and decks, which may contain first-hand observation (mapping counts, photos). Use `derived-summary` for documents that only restate other sources: thematic summaries, wiki pages, JSON extractions written by a person or a model from transcripts. Use `ai-generated` for documents a model composed with no traceable inputs |
| `title` | yes | Transcript file name, document title, article headline, dataset name |
| `author_org` | | Author, outlet, agency, or collecting team. For news, `Author; Outlet` lets the report builder format references |
| `date` | yes | Date of the interview, event, record or publication (`YYYY-MM-DD`, or `YYYY-MM` / `YYYY` if that is all there is). Not the date you read it |
| `path_or_url` | yes | Absolute local path, shared-drive URL or web URL a reviewer can open |
| `locator_scheme` | yes | How pinpoints work in this source: `line`, `page`, `slide`, `timestamp`, `row`, `paragraph`, `article-section`, `json-path` (e.g. `pumping_costs.payment_system[0]`), `char-offset` (for transcript text held in one long string: `para 9 c.20072`) |
| `derived_from` | | The origin this source shares with others: the original's `source_id`, or a label for one round of fieldwork (`FW-2025-02`) when several decks and summaries all come from it. The checker counts sources with the same `derived_from` as one origin when grading `triangulated` and `corroborated` |
| `language` | | `id`, `jv`, `su`, `en`... (ISO 639-1 where one exists). Needed to judge translations |
| `respondent_code` | | For interviews: the code and role (`INT-V1-03, water user group chair`), never a name |
| `collected_by` | | Team or role that collected it; matters for independence of triangulation legs |
| `anonymised` | | `yes` / `no` / `partial`; whether the file itself carries names |
| `verifiability` | | `open` (anyone can check), `team` (local team folder), `drive-only` (exists on a shared drive, not opened locally), `restricted` (consent-limited), `lost` (cited but not found) |
| `reliability_notes` | | Known problems: ASR transcript not checked, LLM summary, desk source outside the area, retracted, translation unverified, page text loaded by script and not verified |

Derived documents (summaries, wiki pages, JSON extractions, slide decks summarising interviews) get
their own row with `source_type` describing what they are, plus a `reliability_notes` entry naming
the original they derive from. They are pointers. Cite the original wherever it can be opened.

## arrangements.csv: one row per arrangement

One rule-set governing one user group's use of one source, at one place, in one period. Split rows
when any of these differ; link them in `notes`.

| Column | Required | Content |
|---|---|---|
| `arrangement_id` | yes | `A001`... |
| `local_name` | | The term used locally, spelled as the source spells it; variants after `;` (`bobokan; bobok`). Never mint a term from one ASR occurrence |
| `local_name_language` | | `jv`, `su`, `id`... |
| `tenure_type` | yes | One key from [typology.md](typology.md) section 2, or `unclassified` |
| `classification_basis` | yes | Why this type, stated as reported facts with citations: "no permit reported by users (INT-V1-04 l.212); agency staff describe it as tolerated (FGD-AG-2501 l.401)" |
| `secondary_tenure_types` | | Other types layered on the same use (an unregistered group pumping without a permit: `informal` primary, `impossible` secondary) |
| `water_source` | yes | River, canal (name and level), drain, spring, dug well, borehole, small reservoir, sea, rain, purchased (refill bottles, tanker) |
| `water_use` | yes | FAO use code(s) from [typology.md](typology.md) section 4, `;`-separated; sub-use in `arrangement` |
| `users` | yes | Who uses the water, in plain words |
| `user_attributes` | | Controlled list, [typology.md](typology.md) section 5 |
| `holder_controller` | | Who controls access (water user group, village water official, gate operator, utility, landowner, pump owner, customary steward) |
| `location_admin` | yes | `Province > District > Sub-district > Village > block`; mark unverified levels `(unverified)` |
| `location_hydro` | | `Basin > scheme > canal level/name > structure` or river reach, spring, aquifer |
| `coordinates` | | `lat,lon` in decimal degrees WGS84 where the source gives them (GPS, drone map); otherwise empty, never guessed |
| `upstream_downstream` | | `head-end`, `middle`, `tail-end`, `upland-not-served`, `upstream-of-intake`... |
| `period_season` | | `year-round`, `MT1`, `MT2`, `MT3` (planting seasons), `dry season`, `maintenance closure (Oct)`, `since 1990s` |
| `arrangement` | yes | The account of how it works, in prose, 2-6 sentences. Attribute every judgement |
| `access_rule` | | Who may take water and how (membership, land in the block, kinship, payment, turn) |
| `allocation_rule` | | Rotation, hours per week, priority groups, share of flow, first-come |
| `payment` | | Fees in money or kind, with unit and rate exactly as the source gives them |
| `labour_contribution` | | Communal work, canal cleaning, guarding at night |
| `decision_making` | | Who decides and how (village deliberation, group chair, irrigation commission, ritual calendar) |
| `enforcement_sanction` | | What happens on breach, as reported; "no consequence reported" is a finding |
| `recognition_reported` | | How officials and others treat it, as reported ("mapped and tolerated by the basin agency"); not a legal finding |
| `perceived_security` | | How secure users say they are, with their reasons, cited; free text, not a legal score |
| `conflicts` | | Disputes, with whom, where (gate, border, block), how settled |
| `gedsi_notes` | | Who is excluded or burdened (gender, disability, social inclusion), with denominators |
| `source_ids` | yes | `;`-separated keys from `sources.csv` |
| `locators` | yes | Pinpoints paired one-to-one with `source_ids`: `l.212;p.8;slide 14` |
| `figures_source` | if figures | Which source states each number in `arrangement` (`Rp 300,000 per season: S07 l.4`) |
| `quote_original` | if interview | Verbatim, original language, with its own pinpoint |
| `quote_translation` | | English (or other working-language) translation; mark `[translation unverified]` if not checked by a speaker |
| `confidence` | yes | `triangulated`, `corroborated`, `single-source`, `uncorroborated`, `contested` (definitions below) |
| `contradictions` | | Conflicting accounts, each with its own source |
| `legal_flag` | | A question for the legal stage, ending in `?`. See [legal-boundary.md](legal-boundary.md) |
| `gaps_next_steps` | | What would settle the open points: whom to ask, which record to pull |
| `notes` | | Why triangulation legs are independent; hop chain for second-hand claims ("deck > INT-V1-04, transcript not opened"); `[verified YYYY-MM-DD]` marks; links to related records |

## Confidence

| Value | Meaning |
|---|---|
| `triangulated` | 3+ sources, 2+ source types, collected independently; each leg has its own pinpoint |
| `corroborated` | 2+ independent sources agree |
| `single-source` | One source, first-hand (the speaker describes their own practice, or a record documents it) |
| `uncorroborated` | One source, second-hand or hearsay ("locals assume the herders pay someone off"); allegations stay here until corroborated |
| `contested` | Sources disagree on a material point; both versions in `contradictions` |

Independence: two legs are not independent when one derives from the other (a slide summarising an
interview), when the same person speaks in both, or when the party being assessed grades its own
conduct. Set `derived_from` in `sources.csv` so the checker can count origins rather than files. It
also ignores `derived-summary` and `ai-generated` when counting source types. The rest of
independence is your judgement, explained in `notes` for every `triangulated` record.

Confidence is a property of the **record**. The report builder (`water-tenure-report` skill) adds a
separate **evidence grade** for each **source** (E1 primary legal or official, E2 field primary, E3
scholarly or technical, E4 press, E5 social media, D derived). The two do not substitute for each
other: a record can be `triangulated` from press reports alone, and a single E1 decree can make a
record `single-source`.

**When the originals cannot be opened** (transcripts held only on a shared drive, recordings not
transcribed), do not stall and do not pretend:

1. Register the originals anyway, with `verifiability` set to `drive-only` or `lost`.
2. Cite the team's deliverables that quote them, with `derived_from` set to the fieldwork round.
3. Cap confidence. Several deliverables from one fieldwork round are one origin. Agreement with a
   source from a different origin can still lift a record to `corroborated` or `triangulated`: an
   official's verbatim interview, an FGD note, a record.
4. In `notes`, say which original would confirm the record.
5. Ask the user before downloading files from a shared drive or elsewhere, and list the originals
   worth pulling in the report's gaps section.

## Worked row (synthetic)

From the synthetic example catalogue (invented data in a fictional basin):

```
arrangement_id: A004
local_name: pompanisasi
local_name_language: id
tenure_type: informal
classification_basis: users report pumping from the river without an abstraction permit (INT-V2-03 l.41); the basin agency's field officer says the pumps are known and not acted on (INT-AG-01 l.77)
secondary_tenure_types: impossible
water_source: Kali Wening, left bank
water_use: B3
users: rice and chilli farmers of an upland block not reached by the tertiary canal
user_attributes: upland-not-served;smallholder;tenant-or-lessee;collective-unregistered
holder_controller: an unregistered pump group of members
location_admin: Arunika Province > Mekarsari District > Sukarukun > Karangwangi > Blok 3
location_hydro: Kali Wening basin > mainstem below the Wening weir offtake
period_season: MT2;MT3, since the 2000s (INT-V2-03 l.44)
arrangement: The pump group runs 6 diesel pumps in two shifts. Members agree the fee by deliberation each season and pay in unhusked rice at harvest ...
payment: 50 kg of unhusked rice per 0.1 ha per season; halved on crop failure (INT-V2-03 l.52)
source_ids: INT-V2-03;INT-AG-01;S04
locators: l.41;l.77;p.3
figures_source: 6 pumps: INT-V2-03 l.46; S04 p.3 | 50 kg per 0.1 ha: INT-V2-03 l.52
confidence: triangulated
contradictions: pump count 6 (INT-V2-03 l.46) vs 7 (S04 p.3, mapping walk)
legal_flag: Does collective pumping from the Kali Wening by an unregistered farmer group require an abstraction permit, and could such a group apply for one?
```
