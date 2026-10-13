"""Shared helpers for the water tenure report pipeline.

Every script takes one argument, the path to a report config (YAML or JSON; see
references/config.md). Paths inside the config are relative to the config file.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# FAO typology order (water-tenure-analysis, references/typology.md section 2).
TYPES: list[tuple[str, str]] = [
    ("traditional-formal-right", "Traditional formal rights"),
    ("modern-permit", "Modern permits"),
    ("regulatory-licence", "Regulatory licences"),
    ("agency-control", "Agency control"),
    ("water-supply-contract", "Water supply contracts"),
    ("investment-contract", "Investment contracts"),
    ("exempt-declared-commercial", "Declared or exempt commercial uses"),
    ("reserve-minimum-flow", "Reserves and minimum flows"),
    ("de-minimis", "De minimis rights"),
    ("commonhold", "Commonhold"),
    ("customary", "Customary tenure"),
    ("religious-law", "Religious-law tenure"),
    ("informal", "Informal tenure"),
    ("assumed", "Assumed water rights"),
    ("unrecognised", "Unrecognised tenure"),
    ("impossible", "Impossible tenure"),
    ("unclassified", "Unclassified"),
]
TYPE_LABEL = dict(TYPES)
FAMILY1 = {k for k, _ in TYPES[:10]}

USES = ["A1", "A2", "A3", "B1", "B2", "B3", "B4", "B5", "B6", "C", "D1", "D2",
        "E1", "E2", "F", "G1", "G2", "H1", "H2", "I"]
USE_LABEL = {
    "A1": "Drinking, urban", "A2": "Drinking, rural piped", "A3": "Drinking, unimproved",
    "B1": "Estate irrigation", "B2": "Public irrigation", "B3": "Small private irrigation",
    "B4": "River-bank gardens", "B5": "Livestock", "B6": "Aquaculture", "C": "Commerce, industry",
    "D1": "Thermal power", "D2": "Hydropower", "E1": "Environment, instream",
    "E2": "Environment, diversion", "F": "Navigation", "G1": "Inland fishing", "G2": "Wetlands",
    "H1": "Recreation, instream", "H2": "Recreation, cultural", "I": "Other",
}
CONFIDENCE = ["triangulated", "corroborated", "single-source", "uncorroborated", "contested"]
GRADES = ["E1", "E2", "E3", "E4", "E5", "D"]
GRADE_LABEL = {"E1": "E1 Primary legal or official", "E2": "E2 Field primary",
               "E3": "E3 Scholarly or technical", "E4": "E4 Press",
               "E5": "E5 Social media (clue)", "D": "D Derived digest (pointer)"}
SEASONS = ["Dry season or drought", "Planting season (MT) cycle", "Wet season",
           "Year-round or continuous", "Dated event or period only", "Not stated"]
TOKEN = re.compile(r"\{\{([A-Za-z0-9][A-Za-z0-9_.-]*?)(\|anon)?\}\}")


def die(msg: str) -> None:
    print(f"ERROR {msg}", file=sys.stderr)
    sys.exit(1)


def load_config(path: str | Path) -> "Config":
    path = Path(path).resolve()
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        raw = json.loads(text)
    else:
        try:
            import yaml  # PyYAML
        except ImportError:
            die("PyYAML is needed for YAML configs: pip install pyyaml (or use a .json config)")
        raw = yaml.safe_load(text)
    return Config(path=path, raw=raw or {})


@dataclass
class Config:
    path: Path
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def base(self) -> Path:
        return self.path.parent

    def rel(self, p: str | None) -> Path | None:
        if not p:
            return None
        q = Path(p)
        return q if q.is_absolute() else (self.base / q).resolve()

    def get(self, dotted: str, default: Any = None) -> Any:
        cur: Any = self.raw
        for part in dotted.split("."):
            if not isinstance(cur, dict) or part not in cur:
                return default
            cur = cur[part]
        return cur

    @property
    def work(self) -> Path:
        w = self.rel(self.get("work_dir", "_build"))
        assert w is not None
        for sub in ("data", "packs", "figures", "annexes", "out"):
            (w / sub).mkdir(parents=True, exist_ok=True)
        return w

    @property
    def units(self) -> list[dict[str, Any]]:
        return list(self.get("area.units", []) or [])

    @property
    def groups(self) -> dict[str, list[str]]:
        return dict(self.get("area.groups", {}) or {})


def read_csv(path: Path) -> list[dict[str, str]]:
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], cols: list[str] | None = None) -> None:
    cols = cols or (list(rows[0].keys()) if rows else [])
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def split(cell: str | None) -> list[str]:
    return [x.strip() for x in re.split(r"[;,]\s*", cell or "") if x.strip()]


def uses_of(r: dict[str, str]) -> list[str]:
    return [u for u in split(r.get("water_use")) if u in USES]


def secondary_of(r: dict[str, str]) -> list[str]:
    return [s for s in split(r.get("secondary_tenure_types")) if s in TYPE_LABEL]


def units_of(cfg: Config, r: dict[str, str]) -> list[str]:
    """Admin units a record names, by the config's patterns; [] for area-level records."""
    text = (r.get("location_admin") or "").lower()
    markers = [m.lower() for m in cfg.get("area.area_level_markers", []) or []]
    if any(m in text for m in markers):
        return []
    hits = []
    for u in cfg.units:
        pats = u.get("patterns") or [re.escape(u["name"].lower())]
        if any(re.search(p, text) for p in pats):
            hits.append(u["name"])
    return hits if len(hits) <= int(cfg.get("area.max_units_per_record", 4)) else []


def group_of(cfg: Config, r: dict[str, str]) -> str:
    text = ((r.get("location_hydro") or "") + " " + (r.get("location_admin") or "")).lower()
    hits = [g for g, kws in cfg.groups.items() if any(k.lower() in text for k in kws)]
    if len(hits) > 1:
        return "several"
    return hits[0] if hits else "area-level"


def coords_of(r: dict[str, str]) -> tuple[float, float] | None:
    """(lon, lat) from a 'lat,lon' coordinates cell; None if absent or malformed."""
    m = re.match(r"^\s*(-?\d{1,2}(?:\.\d+)?)\s*,\s*(-?\d{1,3}(?:\.\d+)?)\s*$", r.get("coordinates") or "")
    if not m:
        return None
    lat, lon = float(m.group(1)), float(m.group(2))
    if -90 <= lat <= 90 and -180 <= lon <= 180:
        return lon, lat
    return None


def season_of(r: dict[str, str]) -> str:
    t = (r.get("period_season") or "").lower()
    if not t:
        return "Not stated"
    if re.search(r"kemarau|dry|drought", t):
        return "Dry season or drought"
    if re.search(r"\bmt ?[123]|planting|musim tanam|golongan", t):
        return "Planting season (MT) cycle"
    if re.search(r"rain|hujan|wet|flood", t):
        return "Wet season"
    if re.search(r"year|all|continuous|permanent|perennial|sepanjang|daily|annual", t):
        return "Year-round or continuous"
    return "Dated event or period only"


def present_types(rows: list[dict[str, str]]) -> list[str]:
    """Typology keys with primary or secondary records, in typology order."""
    have = {r["tenure_type"] for r in rows} | {s for r in rows for s in secondary_of(r)}
    return [k for k, _ in TYPES if k in have]


def md_cell(text: str | None, limit: int | None = None) -> str:
    t = (text or "").replace("|", "/").replace("\n", " ").strip()
    t = TOKEN.sub(lambda m: f"[{m.group(1)}]", t)
    return (t[:limit] + "...") if limit and len(t) > limit else t
