# The legal boundary

This skill describes practice. It does not interpret law. Legal questions are flagged and handed on.

## Why the line is here

FAO's assessment method splits a water tenure assessment into parallel streams: legal research by
water lawyers, field research by social scientists, governance research. Its legal templates keep
technical and statistical information out, and its assessment fiche keeps the details of
arrangements derived from formal law (completed during legal research) apart from arrangements not
derived from formal law (completed on the basis of field research). Each stream is better when it
does not do the other's job.

Assessment reports show what happens when the streams blur:

- an informal-tenure security rating justified by a statute reading inside a section meant to
  describe practice;
- a legal annex asserting field facts that the field chapter does not support, and citing report
  sections that do not exist;
- statutory labels for irrigation water use carried into descriptive text as if they were
  observations.

A field catalogue that contains legal conclusions cannot be reviewed by either kind of expert: the
lawyer cannot see which facts the conclusion rests on, and the field researcher cannot vouch for the
law.

## What stays in the catalogue

The examples are illustrative, with generic actors.

| Allowed: reported fact, cited | Not allowed: legal conclusion |
|---|---|
| "Farmers say they hold no abstraction permit" [source] | "The pumping is illegal" |
| "Basin agency staff call the canal openings 'technically illegal' and say they tolerate them" [source] | "The canal openings breach the Water Resources Law" |
| "The utility says a ministry rule caps its spring abstraction at a share of discharge" [source] | "Utilities may abstract only that share of discharge" |
| "The water user group has no deed of establishment, per its chair" [source] | "The water user group lacks legal personality" |
| "Industry representatives say their permits are valid for 5 years" [source] | "Industrial permits run 5 years" |
| "Users believe their access is secure because the well is on ancestral land" [source] | "Customary rights here are recognised" |

The difference is attribution: who said it, where it is written, and the pinpoint. A respondent's
legal belief is data about perceived security. It is not the law.

## Tenure types that carry a legal premise

`informal`, `assumed`, `impossible` and `unrecognised` are defined in the FAO typology by a legal
premise. Use them as **candidate** classifications:

1. Classify on the evidence of practice and of how officials treat the use.
2. Write the premise as reported facts in `classification_basis`.
3. Put the question in `legal_flag`.

The legal stage confirms or changes the classification. Say in the report that Family 2
classifications are provisional until that happens.

## Security

Record `perceived_security`: what users say, with their reasons and the source. A numeric legal
security score (FAO uses a 1-4 scale) and governance ratings are assessments of formal arrangements
and team judgement. They belong to the legal and governance stages. Do not assign them here. If a
project needs them, leave the column for the legal team.

The de facto side is still yours. Upstream position, control of a gate, money to run a pump and
political connection all decide who holds "wet water" as opposed to "paper water" (AlAfghani, Lee
and Yasuda 2025). Describe these, with evidence.

## How to write a legal flag

A legal flag is a question, specific enough that a lawyer can answer it without re-reading the
field data. It ends with `?` and the checker enforces that. It names:

- the actor
- the activity
- the place, if jurisdiction may matter
- the legal point in doubt

Do not state the answer, and do not cite an article as if it settles the question. Where an
instrument is mentioned by respondents, name it as they did, plus its identifier if an official
regulation database confirms the number and title.

Good (synthetic place names):

- `Does collective diesel pumping from the Kali Wening by an unregistered farmer group for rice and chillies require an abstraction permit, and could the group apply for one?`
- `Is the cap on spring abstraction cited by utility staff an actual rule, and which instrument sets it?`
- `Does the village water official's office have any status in district or village regulation, and does it overlap with the water user group's authority over tertiary gates?`
- `Is customary access to the sacred wells of Karangwangi recognised in any village or district instrument?`

Bad:

- `Illegal under Article 49.` (a conclusion, and no question)
- `Legal status?` (too vague to answer)
- `This violates the de minimis threshold of 2 L/s?` (smuggles in a conclusion and an unverified number)

## Referral list

`report.md` section 7 groups the flags by question and lists the arrangement IDs under each. Lawyers
receive questions plus the field facts the questions rest on. They never receive field facts
rewritten as legal findings. The `water-tenure-report` skill builds the same list as Annex D.
