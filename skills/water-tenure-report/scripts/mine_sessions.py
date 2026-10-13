#!/usr/bin/env python3
"""Summarise Claude Code session transcripts for the AI-use and provenance annex (Annex H).

    python mine_sessions.py <config.yaml> SESSION_ID [SESSION_ID ...] [--projects-dir DIR]

SESSION_ID is the transcript file name (or a unique prefix of it) under the Claude Code projects
directory (default: ~/.claude/projects). For each session the script writes, to
<work>/data/sessions.json, only counts and labels: start and end time, models used, number of
human turns, tool calls by name, subagents spawned by type, skills invoked, and the number of
subagent transcripts. annexes.py turns that file into the session table of Annex H.

The human turns themselves are written to <work>/private/human_turns/<id>.md so that the person
who directed the work can paraphrase them for the annex. They are not published: the folder sits
inside the work directory, which is never committed, and the annex uses paraphrase only.
No file paths or working directories are recorded in sessions.json.

Standard library only.
"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import die, load_config  # noqa: E402

SKIP_PREFIXES = ("Base directory for this skill", "A session-scoped Stop hook", "[Image",
                 "<task-notification", "<local-command", "<command-", "Caveat:", "[SYSTEM",
                 "<system-reminder")


def text_of(content) -> str:
    if isinstance(content, str):
        return content
    return " ".join((x.get("text") or "") for x in content if isinstance(x, dict) and x.get("type") == "text")


def summarise(path: Path) -> tuple[dict, list[tuple[str, str]]]:
    tools, models, subagents = collections.Counter(), collections.Counter(), collections.Counter()
    skills, human = [], []
    first = last = None
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = d.get("timestamp")
            if ts:
                first = first or ts
                last = ts
            if d.get("type") == "assistant":
                m = d.get("message") or {}
                if m.get("model"):
                    models[m["model"]] += 1
                for x in m.get("content") or []:
                    if isinstance(x, dict) and x.get("type") == "tool_use":
                        tools[x.get("name", "?")] += 1
                        inp = x.get("input") or {}
                        if x.get("name") == "Skill" and inp.get("skill"):
                            skills.append(inp["skill"])
                        if x.get("name") in ("Agent", "Task"):
                            subagents[inp.get("subagent_type") or "general"] += 1
            if d.get("type") == "user" and not d.get("isMeta") and not d.get("toolUseResult"):
                c = (d.get("message") or {}).get("content")
                if isinstance(c, list) and any(isinstance(x, dict) and x.get("type") == "tool_result" for x in c):
                    continue
                t = text_of(c).strip()
                if t and not t.startswith(SKIP_PREFIXES):
                    human.append((ts or "", t))
    sub_dir = path.parent / path.stem / "subagents"
    n_sub = len(list(sub_dir.glob("*.jsonl"))) if sub_dir.is_dir() else 0
    return dict(start=first, end=last, models=dict(models), tools=dict(tools), subagents=dict(subagents),
                subagent_transcripts=n_sub, skills=sorted(set(skills)), human_turns=len(human)), human


def main(argv: list[str]) -> int:
    projects = Path.home() / ".claude" / "projects"
    if "--projects-dir" in argv:
        i = argv.index("--projects-dir")
        if i + 1 >= len(argv):
            print(__doc__)
            return 2
        projects = Path(argv[i + 1]).expanduser()
        argv = argv[:i] + argv[i + 2:]
    if len(argv) < 2:
        print(__doc__)
        return 2
    cfg = load_config(argv[0])
    out = cfg.work / "data" / "sessions.json"
    private = cfg.work / "private" / "human_turns"
    private.mkdir(parents=True, exist_ok=True)
    result = {}
    for sid in argv[1:]:
        hits = sorted(projects.glob(f"*/{sid}*.jsonl")) + sorted(projects.glob(f"{sid}*.jsonl"))
        if len(hits) != 1:
            die(f"session {sid}: {len(hits)} matching transcripts under {projects}; give a longer prefix")
        summary, human = summarise(hits[0])
        key = hits[0].stem[:8]
        result[key] = summary
        with open(private / f"{key}.md", "w", encoding="utf-8") as fh:
            for ts, t in human:
                fh.write(f"## {ts}\n\n{t[:4000]}\n\n")
        print(f"{key}: {summary['start']} to {summary['end']}, {summary['human_turns']} human turns, "
              f"{sum(summary['subagents'].values())} subagents, skills {summary['skills'][:6]}")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1)
    print(f"wrote {out}; human turns for paraphrase in {private} (do not publish them)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
