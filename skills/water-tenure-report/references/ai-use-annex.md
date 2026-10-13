# The AI-use and provenance annex (Annex H)

A report drafted with AI agents says so, plainly, and says what a person did and did not check.
Annex H is where that account lives; the authorship line and the methodology chapter summarise it.

## What the annex contains

| Section | Content | Source |
|---|---|---|
| Statement | Who directed the work and set the method; which AI agents and models drafted which parts; who reviewed what | `ai_use.statement` in the config |
| H.1 Directions | The human directions that shaped scope and method, paraphrased, with date and session | `ai_use.directions` |
| H.2 Agent sessions | Per session: start, end, models, human turns, subagent transcripts, skills used | `mine_sessions.py` output |
| H.3 Not verified by a person | Everything no person has read against its sources | `ai_use.not_verified_by_a_person` |
| H.4 Checks on this report | The cite-check summary (n of N checked, by verdict and chapter) and the rule checks | the cite-check summary file |

A fuller account can add a role matrix (tasks against the human orchestrator, the orchestrating
agent, subagents and tools, each marked directed, executed, reviewed or approved), a dated timeline,
and the run statistics of a research pipeline (for example the hyperresearch run manifest).

## Rules

1. **Paraphrase directions; never publish transcripts.** Session transcripts contain the
   orchestrator's working conversation, other projects, file paths and sometimes personal
   information. `mine_sessions.py` writes only counts to `sessions.json` and keeps the human turns in
   `<work>/private/` for the person who paraphrases them.
2. **Honesty about review.** Where the record cannot show that a person reviewed something, write
   "not evidenced", not "reviewed". Machine checks by agents and scripts are named as such.
3. **Name the models and tools.** Give the model family and version the agents ran on, the skills and
   pipelines used (with versions), and the third-party tools.
4. **Say what AI did not do.** If no fieldwork was done, say so. If a figure comes from an unchecked
   machine transcript, say so where the figure is used.
5. **Authorship line.** Credit the human orchestrator for goals, method and direction, and the agents
   for drafting, in the same line. For example: "Drafted by <agent name> (an AI research agent of
   <organisation>), with <person> setting the method, directing and reviewing."

## Making sessions.json

```bash
python scripts/mine_sessions.py <config.yaml> <session-id> [<session-id> ...]
# default transcript folder: ~/.claude/projects; override with --projects-dir
```

Then fill `ai_use.directions` by paraphrasing the private human-turn files, and delete the private
folder when the report is final if the project's data-retention rules require it.
