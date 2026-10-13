# Gears, tiers and what a run costs

hyperresearch separates the **tier** of a run (which steps run) from the **gear** of the install (how
big each step is).

## Tiers

| Tier | Steps | Use for water tenure |
|---|---|---|
| `light` | 1, 2, 10 (one draft), 15, 16 | A quick orientation on one place or one question ("what is known about spring custody in district X"). Not a catalogue |
| `full` | all sixteen, plus 14.5 cite-check | A basin or district catalogue. This is the tier the templates are written for |
| `dissertation` | chapters looped through steps 2-10, then global steps | Experimental upstream; opt-in only. A very large area may be better run as one `full` run per sub-basin, merged with the report skill |

Step 1 classifies the tier from the query. The rendered query asks for an exhaustive catalogue, which
classifies as `full`. Do not force extra steps on a `light` run, and do not drop steps from a `full`
run to save time; restart with a narrower area instead.

## Gears

| Gear | Scale (as rendered by hyperresearch 0.12.0) | When |
|---|---|---|
| `full` | about 55-80 sources, about 1.5-2.5 hours | A district, a scheme, a pilot, or a first pass |
| `premier` | about 100-130 sources, double depth budget, about 3-5 hours | A whole basin where the user asks for an exhaustive catalogue |

Switch with `hyperresearch profile use <full|premier>` in the project folder. It re-renders the
installed skills and agents, so it applies to the next run, never to a run in progress.

## What the reference run took

CRPG's reference run (a river-basin assessment in Indonesia, 2026) was a `full`-tier run at the
`premier` gear with the catalogue stage inserted. It took about seven hours of wall-clock time, built
a vault of several hundred notes from web sources and the project's own files, and spawned on the
order of eighty subagents. The catalogue stage, its revision and the spot verification were run by
the orchestrator on top of the pipeline. The run manifest does not track spend; check your plan's
usage limits before starting, and use `hyperresearch run init <tag> --budget <usd>` for a ceiling on
estimated spend.

## Practical limits met

- **Search caps.** The built-in web search tool can hit a per-session cap during a premier run.
  `temp/fetch-protocol.md` lists fallbacks (another search tool, a news feed restricted to the
  period, the Crossref and OpenAlex APIs).
- **Blocked pages.** Some sites block headless fetching or need a login; hyperresearch has a
  browser-lane escalation queue for these. Logins, two-factor prompts and CAPTCHAs are for a person,
  never for an agent.
- **Windows.** Set `PYTHONIOENCODING=utf-8` for the CLI, or non-ASCII titles break its JSON output.
- **Context.** The orchestrator's context fills on a premier run; the step-skill design reloads each
  step's procedure fresh. Keep the run's own notes in `research/runs/<tag>/temp/orchestrator-notes.md`
  so a resumed session can find its place (`hyperresearch run status <tag>`).
