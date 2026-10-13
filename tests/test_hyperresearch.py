"""water-tenure-hyperresearch: run-input rendering, partial merge, wikilink conversion."""
from __future__ import annotations

import json
import shutil

import yaml

from conftest import CATALOGUE, HYPER, check_json, read_csv, run, write_csv

SCRIPTS = HYPER / "scripts"
SCOPE = HYPER / "examples" / "synthetic-scope.yaml"
EXPECTED = {"query.md", "scaffold-additions.md", "domain-notes.txt", "prompt-decomposition.seed.json",
            "levers-commands.sh", "APPLY.md", "temp/catalogue-protocol.md", "temp/local-ingest-protocol.md",
            "temp/fetch-protocol.md", "temp/source-analysis-focus.md", "temp/search-plan.md",
            "temp/draft-angles.md", "temp/synthesis-plan.md"}


def test_render_run_inputs(tmp_path):
    out = tmp_path / "inputs"
    r = run(SCRIPTS / "make_run_inputs.py", SCOPE, "--out", out, "--vault-tag", "kali-wening-water-tenure-0a1b2c")
    assert r.returncode == 0, r.stderr
    files = {p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file()}
    assert files == EXPECTED
    for p in out.rglob("*"):
        if p.is_file():
            text = p.read_text(encoding="utf-8")
            assert "${" not in text, f"unrendered placeholder in {p.name}"
    for name in ("query.md", "levers-commands.sh", "temp/catalogue-protocol.md"):
        assert "kali-wening-water-tenure-0a1b2c" in (out / name).read_text(encoding="utf-8")
    dec = json.loads((out / "prompt-decomposition.seed.json").read_text(encoding="utf-8"))
    assert dec["required_section_headings"][0] == "## 1. Scope and Sources"
    assert dec["sub_questions"][0].startswith("Which districts")
    assert dec["levers"]["register"] == "survey" and dec["levers"]["inference_depth"] == "deep"
    query = (out / "query.md").read_text(encoding="utf-8")
    assert "Kali Wening" in query and "Divide the report by tenure type" in query
    protocol = (out / "temp" / "catalogue-protocol.md").read_text(encoding="utf-8")
    for key in ("C1", "C6", "impossible", "de-minimis", "check_catalogue.py"):
        assert key in protocol


def test_partition_must_cover_every_type(tmp_path):
    scope = yaml.safe_load(SCOPE.read_text(encoding="utf-8"))
    scope["groups"] = [{"id": "C1", "name": "Only permits", "types": ["modern-permit"]}]
    bad = tmp_path / "bad.yaml"
    bad.write_text(yaml.safe_dump(scope), encoding="utf-8")
    r = run(SCRIPTS / "make_run_inputs.py", bad, "--out", tmp_path / "o")
    assert r.returncode == 1 and "every tenure type exactly once" in r.stderr


def split_partials(tmp_path):
    p = tmp_path / "partials"
    p.mkdir()
    rows = read_csv(CATALOGUE / "arrangements.csv")
    write_csv(p / "arrangements-C1.csv", rows[:9])
    write_csv(p / "arrangements-C2.csv", rows[9:])
    shutil.copy(CATALOGUE / "sources.csv", p / "sources-C1.csv")
    shutil.copy(CATALOGUE / "sources.csv", p / "sources-C2.csv")
    return p


def test_merge_partials_rebuilds_a_valid_catalogue(tmp_path):
    p = split_partials(tmp_path)
    out = tmp_path / "merged"
    r = run(SCRIPTS / "merge_partials.py", p, "--out", out)
    assert r.returncode == 0, r.stdout + r.stderr
    res = check_json(out)
    assert res["passed"] and res["arrangements"] == 18 and res["sources"] == 20


def test_merge_partials_stops_on_id_collision(tmp_path):
    p = split_partials(tmp_path)
    rows = read_csv(p / "arrangements-C2.csv")
    rows[0]["arrangement_id"] = "A001"
    write_csv(p / "arrangements-C2.csv", rows)
    r = run(SCRIPTS / "merge_partials.py", p, "--out", tmp_path / "merged")
    assert r.returncode == 1 and "A001" in r.stdout


def test_wikilinks_become_tokens(tmp_path):
    src = tmp_path / "report.md"
    src.write_text("# R\n\nSix pumps [[INT-V2-03|l.46]] [[S04|p.3]]. Unknown [[nope|p.1]].\n", encoding="utf-8")
    out = tmp_path / "ch01.md"
    r = run(SCRIPTS / "wikilinks_to_tokens.py", src, CATALOGUE, "--out", out, "--prefix", "")
    assert r.returncode == 1 and "UNREGISTERED nope" in r.stdout
    text = out.read_text(encoding="utf-8")
    assert "Six pumps^[{{INT-V2-03}} l 46; {{S04}} 3.]." in text
    assert "[[nope|p.1]]" in text
