"""water-tenure-media-scan: scan rules and figure verification on the synthetic scan."""
from __future__ import annotations

import json

from conftest import ANALYSIS, SCAN, SCAN_EXAMPLE, read_csv, run, write_csv

SCRIPTS = SCAN / "scripts"
SCOPE = SCAN / "examples" / "synthetic-scan-scope.yaml"


def scan_check(d, *extra):
    r = run(SCRIPTS / "scan_check.py", d, "--scope", SCOPE, "--json", *extra)
    return r.returncode, json.loads(r.stdout)


def test_synthetic_scan_passes_both_checkers():
    assert run(ANALYSIS / "scripts" / "check_catalogue.py", SCAN_EXAMPLE, "--strict").returncode == 0
    code, res = scan_check(SCAN_EXAMPLE, "--strict")
    assert code == 0 and res["passed"], res


def test_social_only_record_cannot_be_corroborated(scan_copy):
    rows = read_csv(scan_copy / "arrangements.csv")
    a04 = next(r for r in rows if r["arrangement_id"] == "A04")
    a04["confidence"] = "corroborated"
    write_csv(scan_copy / "arrangements.csv", rows)
    code, res = scan_check(scan_copy)
    assert code == 1 and any("social media are clues" in e for e in res["errors"])


def test_private_handle_is_an_error(scan_copy):
    rows = read_csv(scan_copy / "sources.csv")
    t01 = next(r for r in rows if r["source_id"] == "T01")
    t01["author_org"] = "@somebody_private; TikTok"
    write_csv(scan_copy / "sources.csv", rows)
    code, res = scan_check(scan_copy)
    assert code == 1 and any("@handle" in e for e in res["errors"])


def test_unread_page_figure_needs_unverified_mark(scan_copy):
    rows = read_csv(scan_copy / "arrangements.csv")
    a02 = next(r for r in rows if r["arrangement_id"] == "A02")
    a02["figures_source"] = "Rp 150,000 per tank: K02 para 4"
    write_csv(scan_copy / "arrangements.csv", rows)
    code, res = scan_check(scan_copy)
    assert code == 1 and any("not marked UNVERIFIED" in e for e in res["errors"])


def test_window_and_exclusion_warnings(scan_copy):
    src = read_csv(scan_copy / "sources.csv")
    src[0]["date"] = "2024-01-05"
    write_csv(scan_copy / "sources.csv", src)
    arr = read_csv(scan_copy / "arrangements.csv")
    arr[0]["arrangement"] += " The banjir of last year was also mentioned."
    write_csv(scan_copy / "arrangements.csv", arr)
    code, res = scan_check(scan_copy)
    assert code == 0
    assert any("outside the scan window" in w for w in res["warnings"])
    assert any("exclusion term" in w for w in res["warnings"])


def test_verify_figures_finds_cached_figures(tmp_path):
    out = tmp_path / "v.json"
    r = run(SCRIPTS / "verify_figures.py", SCAN_EXAMPLE, "--cache", SCAN_EXAMPLE / "page-cache", "--json", out)
    assert r.returncode == 0, r.stdout
    res = json.loads(out.read_text(encoding="utf-8"))
    assert res["counts"].get("found") == 3 and "NOT FOUND" not in res["counts"]
    assert any(x["marked_unverified"] and x["status"] == "found" for x in res["results"])


def test_verify_figures_reports_missing_figure(scan_copy):
    (scan_copy / "page-cache" / "K01.txt").write_text("No numbers here.", encoding="utf-8")
    r = run(SCRIPTS / "verify_figures.py", scan_copy, "--cache", scan_copy / "page-cache")
    assert r.returncode == 1 and "NOT FOUND" in r.stdout
