# How hyperresearch's checks map onto the analysis skill's rules

hyperresearch audits its own report: four critics, a patcher, a polish pass and, at step 14.5, a
cite-check that reads sampled (sentence, note) pairs and returns `supported`, `partially-supported`,
`unsupported` or `wrong-source`. Its final gate (`verify`) checks the run's artefacts. These checks
are good at one thing: whether a cited note says what the sentence claims. The analysis skill asks
for more. This table says which rule each mechanism covers and what still has to be run.

| Analysis-skill rule | Covered inside hyperresearch by | Still needed |
|---|---|---|
| No citation, no record; every statement with a pinpoint | Wikilink citations to a vault note with a pinpoint; the cite-check on sampled pairs | `check_catalogue.py` on the catalogue (every record cites a registered source with a locator) |
| Cite the original, not the digest | The fetcher's primary-source chasing; local-ingest protocol (originals, not wiki pages) | `source_type` of digests set to `derived-summary` in `sources.csv`; the checker counts them as no type |
| AI-generated material is never evidence | Local-ingest exclusions | `ai-generated` source type; the checker rejects records supported only by it |
| Numbers verbatim, with the source that states each | Cite-check rates number-bearing sentences `partially-supported` when the figure is wrong | `figures_source` in every record; spot verification of every figure (C-verify) |
| Triangulation by independent origin | Nothing: the critics do not count origins | `derived_from` in `sources.csv`; the checker counts origins, not files |
| Legal questions flagged, not answered | The register shim (survey) discourages verdicts | `legal_flag` phrased as a question; the checker rejects flags that state conclusions; the report's referral section |
| Protect people | Partly: fetchers are told not to copy private names | Respondents by code and role; allegations as patterns; the report skill's anonymity check |
| Absences are findings | `deep` inference depth: audited absences are reportable | `notes-<G>.md` per group; the report's "absent or not looked for" sentence per type |

## Citations, from vault to footnote

1. Inside the run, every statement cites `[[note-id|pinpoint]]`. The catalogue registers each vault
   note it cites as a source whose `source_id` is the note id, with the original's URL or path and
   its type, so the register can be read without the vault.
2. Inside catalogue fields, wikilinks may also appear; the report skill's `merge.py` converts
   `[[note-id|pinpoint]]` in record text into tokens when the note id is registered.
3. At delivery, `wikilinks_to_tokens.py` rewrites the final report's wikilinks into pandoc footnotes
   with tokens (`^[{{note-id}} 34.]`), reporting any note id that is not registered.
4. The `water-tenure-report` skill resolves the tokens into OSCOLA or APA references from the
   register, prints sources a reader cannot open as "on file with the research team", and builds the
   .docx.

## Verdict vocabulary across the two systems

| hyperresearch cite-check | Report cite-check brief | Action |
|---|---|---|
| supported | supported | none |
| partially-supported | partly supported | trim or soften to what the source says |
| unsupported | unsupported | re-cite or remove; never invent a source |
| wrong-source | unsupported, right source found | re-cite to the registered source that says it |
| (not covered) | pinpoint wrong | correct the pinpoint |
| (not covered) | unreachable | log; leave the text unless another checked token supports it |

The hyperresearch cite-check samples the final report; it does not check the catalogue records. The
spot verification (C-verify) and the report skill's cite-check of the long-form chapters are separate
passes and both are reported in the verification note and Annex H.
