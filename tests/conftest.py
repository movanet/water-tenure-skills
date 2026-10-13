"""Shared helpers for the test suite. Every test runs offline on the synthetic examples."""
from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
ANALYSIS = SKILLS / "water-tenure-analysis"
REPORT = SKILLS / "water-tenure-report"
SCAN = SKILLS / "water-tenure-media-scan"
HYPER = SKILLS / "water-tenure-hyperresearch"
PUBLISH = SKILLS / "tenure-storymap-publish"
CATALOGUE = ANALYSIS / "examples" / "synthetic-catalogue"
SCAN_EXAMPLE = SCAN / "examples" / "synthetic-media-scan"


def run(script: Path, *args, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run a skill script with the current interpreter and return the completed process."""
    return subprocess.run([sys.executable, str(script), *[str(a) for a in args]], cwd=cwd,
                          capture_output=True, text=True, encoding="utf-8", errors="replace")


def read_csv(path: Path) -> list[dict[str, str]]:
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


@pytest.fixture
def catalogue_copy(tmp_path: Path) -> Path:
    """A writable copy of the synthetic field catalogue."""
    d = tmp_path / "catalogue"
    shutil.copytree(CATALOGUE, d)
    return d


@pytest.fixture
def scan_copy(tmp_path: Path) -> Path:
    """A writable copy of the synthetic media scan, with its page cache."""
    d = tmp_path / "scan"
    shutil.copytree(SCAN_EXAMPLE, d)
    return d


def check_json(d: Path) -> dict:
    r = run(ANALYSIS / "scripts" / "check_catalogue.py", d, "--json")
    return json.loads(r.stdout)
