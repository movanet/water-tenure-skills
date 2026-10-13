"""Repository-level checks: skill front matter, links, manifests, citation metadata."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

from conftest import ROOT, SKILLS

SKILL_DIRS = sorted(p.parent for p in SKILLS.glob("*/SKILL.md"))
EXPECTED = {"water-tenure-analysis", "water-tenure-report", "water-tenure-hyperresearch",
            "water-tenure-media-scan", "water-tenure-assessment", "tenure-storymap-publish"}
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")


def front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{path} has no front matter"
    end = text.index("\n---", 4)
    return yaml.safe_load(text[4:end])


def test_all_six_skills_present():
    assert {p.name for p in SKILL_DIRS} == EXPECTED


@pytest.mark.parametrize("skill", SKILL_DIRS, ids=lambda p: p.name)
def test_skill_front_matter_and_length(skill: Path):
    fm = front_matter(skill / "SKILL.md")
    assert fm["name"] == skill.name
    assert isinstance(fm["description"], str) and len(fm["description"]) > 100
    assert "should be used when" in fm["description"]
    assert fm.get("license") == "MIT"
    lines = (skill / "SKILL.md").read_text(encoding="utf-8").count("\n")
    assert lines < 500, f"{skill.name}/SKILL.md has {lines} lines"


@pytest.mark.parametrize("skill", SKILL_DIRS, ids=lambda p: p.name)
def test_scripts_named_in_skill_exist(skill: Path):
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    for rel in sorted(set(re.findall(r"`(scripts/[A-Za-z0-9_]+\.py)", text))):
        assert (skill / rel).exists(), f"{skill.name}: {rel} is mentioned but missing"


def markdown_files() -> list[Path]:
    files = [p for p in ROOT.rglob("*.md") if ".git" not in p.parts and "_build" not in p.parts]
    return sorted(files)


@pytest.mark.parametrize("md", markdown_files(), ids=lambda p: str(p.relative_to(ROOT)))
def test_relative_links_resolve(md: Path):
    text = md.read_text(encoding="utf-8")
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    for target in LINK.findall(text):
        if re.match(r"^[a-z]+:", target) or target.startswith("#") or "<" in target:
            continue
        path = (md.parent / target.split("#", 1)[0]).resolve()
        assert path.exists(), f"{md.relative_to(ROOT)}: link to {target} does not resolve"


def test_plugin_and_marketplace_manifests():
    plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    assert plugin["name"] == "water-tenure-skills"
    assert re.match(r"^\d+\.\d+\.\d+$", plugin["version"])
    assert plugin["license"] == "MIT"
    entry = market["plugins"][0]
    assert market["name"] == "water-tenure-skills"
    assert entry["name"] == plugin["name"] and entry["source"] == "./"
    assert entry["version"] == plugin["version"]


def test_citation_cff():
    cff = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    assert cff["cff-version"] == "1.2.0"
    assert str(cff["version"]) == "1.0.0"
    assert str(cff["date-released"]) == "2026-10-13"
    assert cff["license"] == "MIT"
    assert cff["repository-code"] == "https://github.com/movanet/water-tenure-skills"
    people = [a for a in cff["authors"] if "family-names" in a]
    entities = [a for a in cff["authors"] if "name" in a]
    assert people[0]["family-names"] == "Al'Afghani" and people[0]["given-names"] == "Mohamad Mova"
    assert entities and "CRPG" in entities[0]["name"]
    assert "vibe-coded" in cff["abstract"] and "orchestration" in cff["abstract"]
    assert "orcid" not in json.dumps(cff, default=str).lower() and "doi" not in cff


def test_readme_states_authorship_and_citation():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    head = text[:2500]
    assert "vibe-coded" in head and "Mohamad Mova Al'Afghani" in head
    assert "## How to cite" in text and "@software{" in text
    assert "/plugin marketplace add movanet/water-tenure-skills" in text
    assert "/plugin install water-tenure-skills@water-tenure-skills" in text
    assert "```mermaid" in text


def test_no_emoji_in_docs():
    emoji = re.compile("[\U0001F300-\U0001FAFF☀-➿✅❌]")
    for md in markdown_files():
        assert not emoji.search(md.read_text(encoding="utf-8")), f"emoji or status icon in {md}"
