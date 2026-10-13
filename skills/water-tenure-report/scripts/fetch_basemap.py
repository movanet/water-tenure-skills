#!/usr/bin/env python3
"""Optional: download basemap layers for the report maps (network access required).

    python fetch_basemap.py <config.yaml> --iso3 IDN [--adm ADM2]            show what would be fetched
    python fetch_basemap.py <config.yaml> --iso3 IDN [--adm ADM2] --download  fetch and write

Boundaries come from geoBoundaries (https://www.geoboundaries.org, gbOpen release; the licence
varies by country and is printed from the API's metadata) and are clipped to the config's
`gis.extent`. Rivers come from OpenStreetMap through the Overpass API (waterway=river inside
`gis.extent`; data (c) OpenStreetMap contributors, ODbL). The files are written to the paths in
`gis.admin` and `gis.rivers`. Nothing is downloaded without --download, so the user can approve
the sources first. The pipeline never needs this script: maps fall back to a notice when no
basemap is configured, and the synthetic example ships its own invented layers.

Standard library only.
"""
from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import die, load_config  # noqa: E402

GB_API = "https://www.geoboundaries.org/api/current/gbOpen/{iso3}/{adm}/"
OVERPASS = "https://overpass-api.de/api/interpreter"
UA = {"User-Agent": "water-tenure-report/1.0 (fetch_basemap.py)"}


def bbox_of(geom: dict) -> tuple[float, float, float, float]:
    xs, ys = [], []

    def walk(c):
        if c and isinstance(c[0], (int, float)):
            xs.append(c[0])
            ys.append(c[1])
        else:
            for x in c:
                walk(x)
    walk(geom.get("coordinates") or [])
    return (min(xs), min(ys), max(xs), max(ys)) if xs else (0, 0, 0, 0)


def clip_features(fc: dict, extent: list[float]) -> dict:
    """Keep features whose bounding box intersects extent [lon_min, lon_max, lat_min, lat_max]."""
    x0, x1, y0, y1 = extent
    keep = []
    for f in fc.get("features", []):
        a, b, c, d = bbox_of(f.get("geometry") or {})
        if a <= x1 and c >= x0 and b <= y1 and d >= y0:
            keep.append(f)
    return {"type": "FeatureCollection", "features": keep}


def overpass_query(extent: list[float]) -> str:
    x0, x1, y0, y1 = extent
    return f'[out:json][timeout:120];(way["waterway"="river"]({y0},{x0},{y1},{x1}););out geom;'


def overpass_to_geojson(data: dict) -> dict:
    feats = []
    for el in data.get("elements", []):
        geom = el.get("geometry")
        if el.get("type") != "way" or not geom:
            continue
        coords = [[p["lon"], p["lat"]] for p in geom]
        if len(coords) < 2:
            continue
        name = (el.get("tags") or {}).get("name", "")
        feats.append({"type": "Feature", "properties": {"name": name, "osm_id": el.get("id")},
                      "geometry": {"type": "LineString", "coordinates": coords}})
    return {"type": "FeatureCollection", "features": feats}


def get(url: str, data: bytes | None = None) -> bytes:
    req = urllib.request.Request(url, data=data, headers=UA)
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    opts = {}
    for k in ("--iso3", "--adm"):
        if k in argv:
            i = argv.index(k)
            if i + 1 >= len(argv):
                print(__doc__)
                return 2
            opts[k] = argv[i + 1]
            args = [a for a in args if a != argv[i + 1]]
    if len(args) != 1 or "--iso3" not in opts:
        print(__doc__)
        return 2
    cfg = load_config(args[0])
    extent = cfg.get("gis.extent")
    admin, rivers = cfg.rel(cfg.get("gis.admin")), cfg.rel(cfg.get("gis.rivers"))
    if not extent or not admin or not rivers:
        die("set gis.extent, gis.admin and gis.rivers in the config first")
    iso3, adm = opts["--iso3"].upper(), opts.get("--adm", "ADM2").upper()
    api = GB_API.format(iso3=iso3, adm=adm)
    print(f"boundaries: {api} (geoBoundaries gbOpen {iso3} {adm}), clipped to {extent} -> {admin}")
    print(f"rivers:     {OVERPASS} query {overpass_query(extent)} -> {rivers}")
    if "--download" not in argv:
        print("nothing downloaded; re-run with --download once the sources are approved")
        return 0

    meta = json.loads(get(api))
    url = meta.get("simplifiedGeometryGeoJSON") or meta.get("gjDownloadURL")
    if not url:
        die(f"geoBoundaries metadata has no GeoJSON link: {list(meta)[:10]}")
    fc = clip_features(json.loads(get(url)), extent)
    admin.parent.mkdir(parents=True, exist_ok=True)
    admin.write_text(json.dumps(fc), encoding="utf-8")
    print(f"wrote {admin}: {len(fc['features'])} units; licence: {meta.get('boundaryLicense', 'see geoBoundaries')}; "
          f"source: {meta.get('boundarySource', '')}")

    body = urllib.parse.urlencode({"data": overpass_query(extent)}).encode()
    rv = overpass_to_geojson(json.loads(get(OVERPASS, body)))
    rivers.parent.mkdir(parents=True, exist_ok=True)
    rivers.write_text(json.dumps(rv), encoding="utf-8")
    print(f"wrote {rivers}: {len(rv['features'])} river ways; credit: (c) OpenStreetMap contributors (ODbL)")
    print("Set gis.credit in the config to name both sources and the download date.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
