"""Minimal GeoJSON drawing for basemaps with matplotlib only (no geopandas, no GDAL).

Boundaries: any GeoJSON of Polygon/MultiPolygon features with a name property (for example
geoBoundaries ADM2, fetched by fetch_basemap.py). Rivers: GeoJSON LineString/MultiLineString
features with a name property (for example OpenStreetMap waterways via Overpass).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from matplotlib.collections import LineCollection, PatchCollection
from matplotlib.patches import Polygon as MplPolygon


def _rings(geom: dict) -> list[list[list[float]]]:
    if not geom:
        return []
    if geom["type"] == "Polygon":
        return [geom["coordinates"][0]]
    if geom["type"] == "MultiPolygon":
        return [p[0] for p in geom["coordinates"]]
    return []


def _lines(geom: dict) -> list[list[list[float]]]:
    if not geom:
        return []
    if geom["type"] == "LineString":
        return [geom["coordinates"]]
    if geom["type"] == "MultiLineString":
        return list(geom["coordinates"])
    return []


def ring_area_centroid(ring: list[list[float]]) -> tuple[float, float, float]:
    a = cx = cy = 0.0
    for (x0, y0), (x1, y1) in zip(ring, ring[1:] + ring[:1]):
        f = x0 * y1 - x1 * y0
        a += f
        cx += (x0 + x1) * f
        cy += (y0 + y1) * f
    if abs(a) < 1e-12:
        xs, ys = [p[0] for p in ring], [p[1] for p in ring]
        return 0.0, sum(xs) / len(xs), sum(ys) / len(ys)
    return abs(a / 2), cx / (3 * a), cy / (3 * a)


class Basemap:
    def __init__(self, admin: Path | None, name_field: str, rivers: Path | None, river_field: str,
                 main_regex: str | None):
        self.units: dict[str, list[list[list[float]]]] = {}
        if admin and admin.exists():
            for f in json.loads(admin.read_text(encoding="utf-8"))["features"]:
                name = str((f.get("properties") or {}).get(name_field, ""))
                self.units.setdefault(name, []).extend(_rings(f.get("geometry")))
        self.main, self.minor = [], []
        if rivers and rivers.exists():
            pat = re.compile(main_regex, re.I) if main_regex else None
            for f in json.loads(rivers.read_text(encoding="utf-8"))["features"]:
                nm = str((f.get("properties") or {}).get(river_field) or "")
                for ln in _lines(f.get("geometry")):
                    (self.main if pat and pat.search(nm) else self.minor).append(ln)

    @property
    def ok(self) -> bool:
        return bool(self.units)

    def label_point(self, name: str) -> tuple[float, float]:
        best = max((ring_area_centroid(r) for r in self.units.get(name, [])), default=(0, 0, 0))
        return best[1], best[2]

    def draw_units(self, ax, names: list[str] | None = None, colours: dict[str, str] | None = None,
                   default: str = "#f3f2ef", edge: str = "#d6d5d0", lw: float = 0.4) -> None:
        patches, fc = [], []
        for n, rings in self.units.items():
            if names is not None and n not in names:
                continue
            for r in rings:
                patches.append(MplPolygon(r, closed=True))
                fc.append((colours or {}).get(n, default))
        if patches:
            ax.add_collection(PatchCollection(patches, facecolor=fc, edgecolor=edge, linewidth=lw))

    def draw_rivers(self, ax, minor: bool = True) -> None:
        if minor and self.minor:
            ax.add_collection(LineCollection(self.minor, colors="#a9c9ee", linewidths=0.3, alpha=0.7))
        if self.main:
            ax.add_collection(LineCollection(self.main, colors="#3987e5", linewidths=0.9))

    @staticmethod
    def frame(ax, extent: list[float] | None) -> None:
        if extent:
            ax.set_xlim(extent[0], extent[1])
            ax.set_ylim(extent[2], extent[3])
        else:
            ax.autoscale_view()
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_visible(False)
