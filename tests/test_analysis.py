"""water-tenure-analysis: checker, matrix and map export on the synthetic catalogue."""
from __future__ import annotations

import json

from conftest import ANALYSIS, CATALOGUE, check_json, read_csv, run, write_csv

SCRIPTS = ANALYSIS / "scripts"


def test_synthetic_catalogue_passes_strict():
    r = run(SCRIPTS / "check_catalogue.py", CATALOGUE, "--strict")
    assert r.returncode == 0, r.stdout
    assert "20 sources, 18 arrangements, 0 errors, 0 warnings" in r.stdout


def test_templates_match_example_headers():
    for name in ("arrangements", "sources"):
        template = (ANALYSIS / "assets" / f"{name}.template.csv").read_text(encoding="utf-8").strip().split(",")
        example = list(read_csv(CATALOGUE / f"{name}.csv")[0].keys())
        assert template == example


def test_matrix_matches_committed(tmp_path):
    out = tmp_path / "matrix.md"
    r = run(SCRIPTS / "build_matrix.py", CATALOGUE, "--out", out)
    assert r.returncode == 0, r.stderr
    assert out.read_text(encoding="utf-8").splitlines() == (CATALOGUE / "matrix.md").read_text(encoding="utf-8").splitlines()


def test_ai_only_support_is_an_error(catalogue_copy):
    rows = read_csv(catalogue_copy / "arrangements.csv")
    rows[0]["source_ids"], rows[0]["locators"], rows[0]["confidence"] = "S09", "p.1", "single-source"
    write_csv(catalogue_copy / "arrangements.csv", rows)
    res = check_json(catalogue_copy)
    assert not res["passed"]
    assert any("only by AI-generated" in e for e in res["errors"])


def test_triangulation_counts_origins_not_files(catalogue_copy):
    rows = read_csv(catalogue_copy / "arrangements.csv")
    # S04 and S05 share the fieldwork origin FW-1, so with one interview they are two origins, not three.
    rows[0]["source_ids"], rows[0]["locators"], rows[0]["confidence"] = "S04;S05;INT-V1-01", "p.1;slide 1;l.1", "triangulated"
    write_csv(catalogue_copy / "arrangements.csv", rows)
    res = check_json(catalogue_copy)
    assert any("'triangulated' needs" in e for e in res["errors"])


def test_legal_flag_must_ask_not_decide(catalogue_copy):
    rows = read_csv(catalogue_copy / "arrangements.csv")
    rows[2]["legal_flag"] = "The openings are illegal."
    write_csv(catalogue_copy / "arrangements.csv", rows)
    errors = check_json(catalogue_copy)["errors"]
    assert any("phrased as a question" in e for e in errors)
    assert any("states a legal conclusion" in e for e in errors)


def test_unpaired_locators_and_unknown_codes(catalogue_copy):
    rows = read_csv(catalogue_copy / "arrangements.csv")
    rows[1]["locators"] = "l.30"
    rows[1]["water_use"] = "B2;Z9"
    write_csv(catalogue_copy / "arrangements.csv", rows)
    errors = check_json(catalogue_copy)["errors"]
    assert any("pair them one-to-one" in e for e in errors)
    assert any("not in the FAO list" in e for e in errors)


def test_storymap_export_protects_people_and_places(tmp_path):
    out = tmp_path / "map.geojson"
    r = run(SCRIPTS / "export_storymap.py", CATALOGUE, "--out", out)
    assert r.returncode == 0, r.stderr
    fc = json.loads(out.read_text(encoding="utf-8"))
    ids = {f["properties"]["catalogue_id"] for f in fc["features"]}
    assert "A013" not in ids, "uncorroborated hearsay must not be mapped"
    text = json.dumps(fc, ensure_ascii=False)
    assert "INT-" not in text and "FGD-" not in text, "respondent codes leaked"
    for f in fc["features"]:
        p = f["properties"]
        if p["tenure_type"] in {"informal", "impossible", "unrecognised", "assumed"}:
            assert p["sensitivity"] == "aggregate_only"
            lon, lat = f["geometry"]["coordinates"]
            assert round(lon, 2) == lon and round(lat, 2) == lat
