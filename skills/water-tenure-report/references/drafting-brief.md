# Drafting brief: tenure-type chapters

Give this brief, with one evidence pack, to each chapter drafter (a person or an AI subagent). Fill
the placeholders in angle brackets before sending it. `<work>` is the report's work directory (the
config's `work_dir`).

Contents: 1. The task · 2. Inputs · 3. Citation through tokens · 4. Evidence grades and social
media · 5. Chapter template · 6. Hard rules · 7. What to return

## 1. The task

You are drafting Chapter `<NN>` of `<report title>`, a review and map of water tenure arrangements
in `<area>`, organised by tenure type. Write in `<language>`, in a formal analytical register:
short declarative sentences, attributed judgements, no advocacy. If an organisation has a house
style, follow it; do not imitate any individual author's personal voice.

Length target: `<words>` words. Thin types still get every section of the template, kept short.

## 2. Inputs

- `<work>/packs/<tenure-type>.md`: **the evidence.** Every record of the type, from every merged
  catalogue, with its fields, source tokens and evidence grades, and the list of sources at the end.
  Records where the type is only a secondary reading are listed after the primary ones.
- The `water-tenure-analysis` skill's `references/typology.md` (definitions and the decision order),
  `references/legal-boundary.md` (what you must not decide) and `references/field-methods.md` (the
  visibility checklist).
- `<work>/data/master_arrangements.csv`: the full merged catalogue, if you need a record outside your
  pack.
- Optional: an earlier report's section on the same type, as a starting structure. It is not
  evidence: re-cite everything with tokens from the pack.

## 3. Citation through tokens

- Every factual statement carries a footnote, written as a pandoc inline footnote: `^[...]`.
- Inside a footnote, cite a source **only by its token**, then the pinpoint:
  `^[{{S01}} 12; {{INT-V1-01}} l 15.]`. Token ids are exactly as in the pack. `build.py` expands
  them into references; **never type a reference yourself**.
- For a post by a private person, write `{{<id>|anon}}`; the build drops the account name.
- Reserved tokens for method sources (FAO publications, the skill itself) are listed in the config
  under `reserved_sources`; use them for definitions and method statements.
- OSCOLA conventions around tokens: page pinpoints without "p" (`{{S02}} 42`); other units with a
  word (`l 212`, `slide 3`, `para 4`, `row 17`, `art 5(3)`, `00:01:20`); several sources separated by
  semicolons; a footnote ends with a full stop and may carry a short explanatory clause.
- Quote the original language in the text, in single quotation marks and italics, with the
  translation in the footnote ("translation by the authors"). Quote only from the pack's
  `quote_original` or from a source you have opened.
- Cite record ids in the running text in parentheses, `(A004)`, `(N01)`, so readers can find the
  full record in Annex A. `build.py` reports record ids that do not exist.
- Copy figures exactly as the pack gives them, with their unit. Never round, average or merge
  conflicting figures: give both, each with its source.
- Tokens must sit inside footnotes. A token in the running text fails the build.

## 4. Evidence grades and social media

| Grade | Basis |
|---|---|
| E1 | Primary legal or official: decree, permit, register, allocation plan, agency document |
| E2 | Field primary: interview, focus group, workshop, observation; flag unchecked machine transcripts |
| E3 | Scholarly or technical: journal article, thesis, technical study, team mapping product |
| E4 | Press, including press agencies' photo and video |
| E5 | Social media |
| D | Derived digest: a summary, wiki page or extraction; a pointer, never evidence on its own |

- **E5 is a clue.** A statement resting only on E5 (or E5 and D) never appears as a finding in the
  body. It goes in the chapter's closing Clues section with what would corroborate it. `build.py`
  flags any footnote outside a Clues section whose tokens are all E5 or D.
- When E5 agrees with E1-E4 evidence on place, time and actor, you may say that the post
  corroborates that evidence, citing both in the same footnote.
- Name institutional accounts. Never name or give the handle of a private individual.
- Record confidence (triangulated, corroborated, single-source, uncorroborated, contested) is
  separate from source grade. Say it where it matters ("single-source", "alleged by one farmer").

## 5. Chapter template

Keep every section; thin types compress each section but skip none.

```
# Chapter N. <Tenure type name>

<A lead of one or two sentences: what this type is and the headline for the area.>

## N.1 Definition and legal anchor
## N.2 At a glance
## N.3 Where it occurs
## N.4 How the arrangements work
## N.5 Who holds it, and who is left out
## N.6 Interaction with other tenure types
## N.7 Contested classifications and gaps
## N.8 Questions for legal assessment
## N.9 Clues from social media and unverified reports   (omit only if there are none)
```

- **N.1 Definition and legal anchor.** The FAO definition, cited to a reserved token. Then which
  instruments or practices the records map to, named as the pack names them. Do not quote a
  provision unless the pack gives its text with a pinpoint. Do not state what the law requires.
- **N.2 At a glance.** One compact table: records (primary and secondary), by area group, water-use
  codes with counts, best evidence grade with counts, confidence with counts. Compute the counts from
  the pack. Then the two standard figures, exactly:
  `![<Type>: records by map unit](figures/type-<key>-map.png)` and
  `![<Type>: water uses on the primary records](figures/type-<key>-uses.png)`.
- **N.3 Where it occurs.** Group places hydrologically (basin > sub-basin or aquifer > point) and
  administratively, down to the village or structure. Coordinates only where the pack gives them.
- **N.4 How the arrangements work.** The core: three to six vignettes of named places, each headed in
  bold, `**Place, district (A004, N01).**`. For each: access, allocation, payment, labour,
  decision-making, enforcement, recognition as reported, perceived security. Analyse: say what the
  arrangements share and where they differ.
- **N.5 Who holds it, and who is left out.** Holders against users. Women, tenants, tail-end farmers,
  landless people, fishers, upland households, with denominators where the source gives them.
  Absences the evidence supports.
- **N.6 Interaction with other tenure types.** Layering at the same point, conflict with other
  arrangements, paper water against wet water. Use the secondary-type list in the pack.
- **N.7 Contested classifications and gaps.** Counter-readings, duplicates, audited absences. For a
  thin type, say plainly whether it is absent from the area or was not looked for, and why.
- **N.8 Questions for legal assessment.** A numbered list of questions only, taken from the records'
  `legal_flag`, each with its record ids, ending "See Annex D." Never answer them.
- **N.9 Clues.** A table: Clue | Source (token in a footnote) | What would corroborate it.

A worked example of every section is in [../examples/synthetic-chapters/](../examples/synthetic-chapters/)
(invented data).

## 6. Hard rules

1. No citation, no statement. Never invent a source, a figure, a place or a quotation.
2. No legal conclusions. Never write "illegal", "unlawful" or "violates" in your own voice;
   attribute such labels to whoever used them. In Indonesian text use "tenurial" for tenure.
3. No respondent names. Officials are named by office or role only. Public figures acting in a
   public role may be named if the pack names them.
4. Flag unverified material where you first use it in a chapter: machine (ASR) transcripts that no
   one has checked, page text loaded by script, figures marked UNVERIFIED in the pack.
5. No emoji or status icons. No em dashes, no "delve", "tapestry", "robust", "crucial", no rule-of-three
   padding. Plain, precise sentences.
6. Italicise local terms on first use and gloss them in the same sentence: *ulu-ulu* (village
   irrigation official).
7. Write the chapter to `<chapters_dir>/ch<NN>-<slug>.md`, UTF-8. Do not write anywhere else and do
   not edit the packs.

## 7. What to return

- The file path and word count of the chapter.
- The list of tokens used.
- Three to five cross-cutting observations for the synthesis chapter (layering, paper against wet
  water, seasonality, head and tail, land and water, toleration, economic power, invisible users,
  conflict hotspots), each with its record ids.
- Every place where the evidence conflicted and both figures were kept.
- Optionally, one mechanism diagram for the chapter: up to ten nodes, each a named actor, instrument
  or structure from the pack with its token, and the edges between them (see
  [diagram-brief.md](diagram-brief.md)).
