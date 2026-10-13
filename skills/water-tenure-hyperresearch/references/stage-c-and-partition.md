# Stage C: building the catalogue inside the run, divided by tenure type

hyperresearch writes a report from a vault of notes. A water tenure assessment needs a **catalogue**
first: one checked record per arrangement, which the report then describes. The reference run
inserted a catalogue stage into the pipeline and divided the work, and the report, by tenure type.

## Where stage C sits

| When | Stage | What happens |
|---|---|---|
| After step 2 (width sweep) | **C** | One subagent per tenure-type group extracts records from the vault under `temp/catalogue-protocol.md`; the orchestrator merges the partials (`merge_partials.py`), runs `check_catalogue.py` until it reports no errors, and builds `matrix.md` |
| After step 9 (evidence digest) | **C-revision** | The depth investigators' interim notes and `comparisons.md` are applied: new records, records split by place, corrected figures and classifications, contradictions recorded. Every change goes into `group-notes/revision-log.md` (record id, change, reason, the interim note that prompted it). Interim notes are named as provenance only, never cited as evidence |
| Before step 10 | **C-verify** | Spot verification under the analysis skill's step 9: every figure and every quote checked against its source, and at least one record in five read in full against its sources. Results logged as "n of N" with verdicts (supported, partly supported and fixed, not supported) in `group-notes/spot-verification-<date>.md` |
| Step 10 onwards | Drafting | The three drafters receive `arrangements.csv` and `matrix.md` as the spine. Section 2 of the report has one subsection per tenure type, in typology order |

Steps 3 to 9 run as usual between C and C-revision; the loci analysts and depth investigators work on
the hardest classification questions the catalogue raised.

## The partition

Each group is a set of tenure types small enough for one agent and coherent enough that the agent
learns one body of evidence. The default partition (`make_run_inputs.py`, overridable in the scope
file with `groups:`):

| Group | Tenure types | Typical evidence |
|---|---|---|
| C1 Permits and licences | modern-permit, regulatory-licence, exempt-declared-commercial, traditional-formal-right | Permit registers, permit decisions, agency news, industry reports |
| C2 State allocation and contracts | agency-control, water-supply-contract, investment-contract, reserve-minimum-flow | Allocation plans, basin plans, operating rules, bulk supply and concession agreements |
| C3 Collective tenure | commonhold | Water user association records, rotation schedules, interviews and workshops |
| C4 Custom and religion | customary, religious-law | Ethnography, local news, interviews, village regulations |
| C5 Outside the state | informal, assumed, impossible, unrecognised | Interviews, mapping, agency statements on toleration, press on conflicts and livelihoods |
| C6 Small and household uses | de-minimis, plus the visibility checklist | Household surveys, interviews with women, statistics |

Rules for the partition:

- Every one of the sixteen types belongs to exactly one group; the script refuses a partition that
  misses or repeats a type.
- An arrangement is written by the group of its **primary** type. When an agent finds a record that
  belongs to another group, it passes the evidence on rather than writing it.
- Layered readings go in `secondary_tenure_types`, so a pump group without legal personality is one
  record (informal, with impossible as secondary), not two.
- Each group gives a disjoint range of arrangement ids, so partials merge without renumbering.
- Each group writes `notes-<G>.md` with its audited absences: the types searched for and not found,
  with what was searched. A report section for an absent type is written from these notes.

## Dividing the report by tenure type

The report keeps the analysis skill's eight-part order. Section 2, the body, is subdivided by type:
formal-law types, then non-formal types, then unclassified, each subsection opening with the FAO
definition and the record count, then the arrangements grouped by sub-basin and named point. Types
with no record keep a subsection that says whether the type is absent or was not looked for. The
long-form report (the `water-tenure-report` skill) carries the same division further: one chapter
per type, grouped into three Parts.

## Merging partials

```bash
python scripts/merge_partials.py research/runs/<tag>/temp/catalogue --out <catalogue-dir>
python <analysis-skill>/scripts/check_catalogue.py <catalogue-dir>
python <analysis-skill>/scripts/build_matrix.py <catalogue-dir>
```

`merge_partials.py` de-duplicates sources registered by several groups (the vault note id is the
source id), reports any field on which two groups disagree, and stops on an arrangement-id collision.
