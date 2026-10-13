"""tenure-storymap-publish: the privacy-filtered publication copy."""
from __future__ import annotations

from conftest import CATALOGUE, PUBLISH, check_json, read_csv, run

SCRIPT = PUBLISH / "scripts" / "publication_copy.py"


def test_publication_copy(tmp_path):
    out = tmp_path / "pub"
    r = run(SCRIPT, CATALOGUE, "--out", out)
    assert r.returncode == 0, r.stderr
    rows = read_csv(out / "arrangements.csv")
    ids = {a["arrangement_id"] for a in rows}
    assert "A013" not in ids, "uncorroborated hearsay must be left out"
    assert len(rows) == 17
    for a in rows:
        assert a["sensitivity"] in {"public", "aggregate_only"}
        assert not a["quote_original"] and not a["quote_translation"] and not a["gedsi_notes"]
        if a["tenure_type"] in {"informal", "impossible", "unrecognised", "assumed"}:
            assert a["sensitivity"] == "aggregate_only"
        if a["coordinates"] and a["sensitivity"] == "aggregate_only":
            lat, lon = (float(x) for x in a["coordinates"].split(","))
            assert round(lat, 2) == lat and round(lon, 2) == lon
        for col in ("arrangement", "classification_basis", "legal_flag"):
            assert "INT-" not in a[col] and "FGD-" not in a[col]
    sources = read_csv(out / "sources.csv")
    assert all(not s["respondent_code"] for s in sources)
    assert all(s["path_or_url"].startswith("http") or s["path_or_url"] == "on file with the research team"
               for s in sources)
    assert check_json(out)["errors"] == []


def test_include_uncorroborated(tmp_path):
    out = tmp_path / "pub"
    assert run(SCRIPT, CATALOGUE, "--out", out, "--include-uncorroborated").returncode == 0
    a013 = next(a for a in read_csv(out / "arrangements.csv") if a["arrangement_id"] == "A013")
    assert a013["sensitivity"] == "aggregate_only"
