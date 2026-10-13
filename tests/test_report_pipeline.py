"""water-tenure-report: the whole pipeline on the synthetic config, in a temporary work directory."""
from __future__ import annotations

import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

import pytest
import yaml

from conftest import REPORT, run

pytest.importorskip("matplotlib")
pytest.importorskip("numpy")
sys.path.insert(0, str(REPORT / "scripts"))

SCRIPTS = REPORT / "scripts"
EXAMPLES = REPORT / "examples"


def make_config(tmp_path: Path, **changes) -> Path:
    """Copy the synthetic config with absolute input paths and a temporary work directory."""
    cfg = yaml.safe_load((EXAMPLES / "synthetic-config.yaml").read_text(encoding="utf-8"))
    for inp in cfg["inputs"]:
        inp["path"] = str((EXAMPLES / inp["path"]).resolve())
    cfg["chapters_dir"] = str(changes.pop("chapters_dir", EXAMPLES / cfg["chapters_dir"]))
    cfg["work_dir"] = str(tmp_path / "work")
    cfg["gis"]["admin"] = str(EXAMPLES / cfg["gis"]["admin"])
    cfg["gis"]["rivers"] = str(EXAMPLES / cfg["gis"]["rivers"])
    for k, v in changes.items():
        cfg["report"][k] = v
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return path


def step(script: str, *args) -> str:
    r = run(SCRIPTS / script, *args)
    assert r.returncode == 0, f"{script} failed:\n{r.stdout}\n{r.stderr}"
    return r.stdout


@pytest.fixture(scope="module")
def built(tmp_path_factory) -> Path:
    tmp = tmp_path_factory.mktemp("report")
    cfg = make_config(tmp)
    step("merge.py", cfg)
    step("figures.py", cfg)
    step("annexes.py", cfg)
    step("build.py", cfg, "--annexes", "--check-only", "--strict")
    return tmp


def test_merge_outputs(built):
    data = built / "work" / "data"
    sources = json.loads((data / "sources.json").read_text(encoding="utf-8"))
    assert len(sources) == 27 and "NK01" in sources and "S01" in sources
    packs = {p.stem for p in (built / "work" / "packs").glob("*.md")}
    assert {"informal", "customary", "agency-control", "impossible"} <= packs


def test_merge_follows_prefixed_ids_in_text(built):
    annex_a = (built / "work" / "annexes" / "annex-a.md").read_text(encoding="utf-8")
    assert "NK01 para 3-6" in annex_a
    assert "(K01 para" not in annex_a


def test_figures_and_annexes(built):
    figs = {p.name for p in (built / "work" / "figures").glob("*.png")}
    assert {"fig-location.png", "fig-records-map.png", "fig-heatmap.png", "type-informal-map.png"} <= figs
    annexes = sorted(p.name for p in (built / "work" / "annexes").glob("annex-*.md"))
    assert annexes == [f"annex-{c}.md" for c in "abcdefghijk"]
    annex_d = (built / "work" / "annexes" / "annex-d.md").read_text(encoding="utf-8")
    assert annex_d.count("?") >= 10
    annex_i = (built / "work" / "annexes" / "annex-i.md").read_text(encoding="utf-8")
    assert "private account" in annex_i and "@" not in annex_i


def test_build_report_is_clean(built):
    rep = json.loads((built / "work" / "out" / "build-report.json").read_text(encoding="utf-8"))
    assert rep["unresolved"] == [] and rep["tokens_outside_footnotes"] == [] and rep["figures_missing"] == []
    assert rep["e5_only_footnotes"] == [] and rep["record_ids_unknown"] == [] and rep["vocab_hits"] == {}
    assert rep["footnotes"] > 80 and rep["figures"] >= 15


def test_oscola_first_full_then_short(built):
    main = (built / "work" / "out" / "main.md").read_text(encoding="utf-8")
    assert "{{" not in main
    assert "Interview INT-V1-01, water user group chair" in main
    assert re.search(r"\(n \d+\)", main), "later citations must use the short form with (n X)"
    assert "Post by a private account" in main
    assert "SYNTHETIC EXAMPLE, NOT REAL DATA" in main
    assert "# List of Figures" in main and "# Part I. Rights Granted or Held by the State" in main


def test_apa_style(tmp_path):
    cfg = make_config(tmp_path, citation_style="apa")
    step("merge.py", cfg)
    step("figures.py", cfg)
    step("build.py", cfg, "--check-only")
    main = (tmp_path / "work" / "out" / "main.md").read_text(encoding="utf-8")
    assert "# References {.unnumbered}" in main and "(n " not in main


def test_unresolved_token_fails_the_build(tmp_path):
    chapters = tmp_path / "chapters"
    shutil.copytree(EXAMPLES / "synthetic-chapters", chapters)
    (chapters / "ch10-bad.md").write_text("# Chapter 10. Bad\n\nA claim.^[{{NOPE}} 3.] And {{S01}} in the text.\n",
                                          encoding="utf-8")
    cfg = make_config(tmp_path, chapters_dir=chapters)
    step("merge.py", cfg)
    step("figures.py", cfg)
    r = run(SCRIPTS / "build.py", cfg, "--check-only")
    assert r.returncode == 1
    rep = json.loads((tmp_path / "work" / "out" / "build-report.json").read_text(encoding="utf-8"))
    assert rep["unresolved"][0][0] == "NOPE" and rep["tokens_outside_footnotes"] == ["S01"]


def test_docx_build(built):
    from build import find_pandoc
    from common import load_config
    pytest.importorskip("docx")
    cfg_path = built / "config.yaml"
    if not find_pandoc(load_config(cfg_path)):
        pytest.skip("pandoc not installed")
    step("make_reference.py", cfg_path)
    step("build.py", cfg_path, "--annexes")
    out = built / "work" / "out"
    rep = json.loads((out / "build-report.json").read_text(encoding="utf-8"))
    main_docx = out / "kali-wening-water-tenure-SYNTHETIC.docx"
    assert main_docx.exists() and (out / "kali-wening-water-tenure-SYNTHETIC-annexes.docx").exists()
    with zipfile.ZipFile(main_docx) as z:
        refs = z.read("word/document.xml").decode("utf-8").count("w:footnoteReference")
        media = [n for n in z.namelist() if n.startswith("word/media/")]
        core = z.read("docProps/core.xml").decode("utf-8")
    assert refs == rep["footnotes"]
    assert len(media) == rep["figures"]
    assert "lastModifiedBy" not in core or "<cp:lastModifiedBy></cp:lastModifiedBy>" in core or \
        "<cp:lastModifiedBy/>" in core


def test_mine_sessions_publishes_counts_only(tmp_path):
    projects = tmp_path / "projects" / "some-project"
    projects.mkdir(parents=True)
    lines = [
        {"type": "user", "timestamp": "2026-10-01T10:00:00Z", "cwd": "/private/path",
         "message": {"content": "Catalogue the basin, divided by tenure type."}},
        {"type": "assistant", "timestamp": "2026-10-01T10:01:00Z",
         "message": {"model": "claude-test", "content": [
             {"type": "tool_use", "name": "Skill", "input": {"skill": "water-tenure-analysis"}},
             {"type": "tool_use", "name": "Agent", "input": {"subagent_type": "general-purpose"}}]}},
    ]
    (projects / "abcdef12-0000.jsonl").write_text("\n".join(json.dumps(x) for x in lines), encoding="utf-8")
    cfg = make_config(tmp_path)
    out = step("mine_sessions.py", cfg, "abcdef12", "--projects-dir", tmp_path / "projects")
    assert "1 human turns" in out
    data = json.loads((tmp_path / "work" / "data" / "sessions.json").read_text(encoding="utf-8"))
    s = data["abcdef12"]
    assert s["models"] == {"claude-test": 1} and s["skills"] == ["water-tenure-analysis"]
    assert "private" not in json.dumps(data) and "Catalogue the basin" not in json.dumps(data)
    assert "Catalogue the basin" in (tmp_path / "work" / "private" / "human_turns" / "abcdef12.md").read_text(encoding="utf-8")


def test_basemap_helpers_offline():
    import fetch_basemap as fb
    fc = {"features": [
        {"geometry": {"type": "Polygon", "coordinates": [[[100.0, -12.0], [100.1, -12.0], [100.1, -12.1], [100.0, -12.0]]]}},
        {"geometry": {"type": "Polygon", "coordinates": [[[120.0, 5.0], [120.1, 5.0], [120.1, 5.1], [120.0, 5.0]]]}}]}
    assert len(fb.clip_features(fc, [99.0, 101.0, -13.0, -11.0])["features"]) == 1
    data = {"elements": [{"type": "way", "id": 7, "tags": {"name": "Kali Test"},
                          "geometry": [{"lat": -12.0, "lon": 100.0}, {"lat": -12.1, "lon": 100.2}]}]}
    gj = fb.overpass_to_geojson(data)
    assert gj["features"][0]["properties"]["name"] == "Kali Test"
    assert gj["features"][0]["geometry"]["coordinates"][1] == [100.2, -12.1]
    assert "waterway" in fb.overpass_query([100.0, 101.0, -13.0, -12.0])
