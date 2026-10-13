# Provenance and the AI-use statement

An assessment drafted with AI agents is only as trustworthy as the account of how it was made. Keep
that account as the work happens, not afterwards.

## What to log, as you go

Keep `provenance/log.md` in the project folder, one dated entry per event:

- **Sessions:** the agent session identifiers, the model family and version, the skills invoked, and
  one line on what the session did. Do not copy transcripts into the log.
- **Directions:** each instruction from the person directing the work that changed scope or method,
  paraphrased, with its date. A scope ruling ("no disasters, bills or taxes"; "divide the report by
  tenure type") is a direction.
- **Runs:** for a hyperresearch run, the vault tag, tier, gear, start and end, and whether its final
  verification passed (from `research/runs/<tag>/run.json`); for a media scan, the scan log.
- **Versions:** the version of every skill in this pack and of every third-party tool used
  (hyperresearch, last30days, pandoc, any diagram tool).
- **Checks:** checker results, spot-verification counts, cite-check counts, each as "n of N".
- **Gates:** each gate decision: who, when, what was read, what was decided.
- **Unverified:** a running list of what no person has read against its sources.

The report skill's `mine_sessions.py` can turn Claude Code transcripts into session counts for Annex
H; it keeps the human turns in a private folder for paraphrasing.

## The statement

Put a short statement in three places: the authorship line, the methodology chapter, and Annex H
(full account). Adapt:

> **How this was made.** This report was drafted by <agent name>, an AI research agent of
> <organisation> running <model family and version> in <tool>, with <person> setting the questions,
> the method and the scope rulings, directing the work and reviewing it. The catalogue was built with
> the water-tenure-analysis skill<, a hyperresearch run and a 30-day media scan>. <n> of <N> catalogue
> records, every figure and every quotation were checked against their sources by <agents and
> scripts | a person>. <What no person has yet verified.> Field data were collected by <team>; no AI
> system generated evidence.

Rules:

1. Say who did what. Directing, setting the method and reviewing are human contributions; drafting,
   extraction and mechanical checking were done by agents. Do not blur them.
2. Never say "reviewed" where the log does not show a review; write "not evidenced".
3. Name the models and tools with versions.
4. Paraphrase the human directions; never publish transcripts.
5. If no fieldwork was done, say so in the statement.

The software of this pack was itself written by AI coding agents under human orchestration; when you
cite the pack, use its CITATION.cff.
