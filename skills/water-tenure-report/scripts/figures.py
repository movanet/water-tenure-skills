#!/usr/bin/env python3
"""Static figures (PNG, 300 dpi) for a water tenure report, from the merged catalogue.

    python figures.py <config.yaml>

Run merge.py first. Writes <work>/figures/:
  fig-location.png, fig-records-map.png        basemap and records by map unit (needs gis: in config)
  type-<key>-map.png, type-<key>-uses.png      one pair per tenure type present (primary or secondary)
  fig-heatmap.png, fig-grades.png, fig-confidence.png, fig-season.png, fig-typology.png
  fig-groups-by-type.png                        when area.groups is configured
  fig-verification.png                          when verification: is configured
and <work>/data/type_stats.json. Maps count records per unit named in location_admin; records that
name more units than area.max_units_per_record, or none, are counted as unmapped, and only
coordinates stated by a source are plotted. Without a basemap the map figures carry a notice.
Palette: a blue sequential ramp plus orange for points; colour-blind safe in light print.
"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import BoundaryNorm, ListedColormap  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (CONFIDENCE, FAMILY1, GRADE_LABEL, GRADES, SEASONS, TYPE_LABEL, TYPES, USE_LABEL,  # noqa: E402
                    USES, coords_of, load_config, read_csv, season_of, secondary_of, uses_of)
from geo import Basemap  # noqa: E402

INK, INK2, MUTED = "#0b0b0b", "#52514e", "#8a8984"
SEQ = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6",
       "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"]
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
POINT = "#eb6834"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": "white",
                     "savefig.facecolor": "white", "savefig.dpi": 300})


class Figs:
    def __init__(self, cfg):
        self.cfg = cfg
        self.work = cfg.work
        self.out = self.work / "figures"
        self.A = read_csv(self.work / "data" / "master_arrangements.csv")
        self.S = read_csv(self.work / "data" / "master_sources.csv")
        g = cfg.get("gis", {}) or {}
        self.bm = Basemap(cfg.rel(g.get("admin")), g.get("admin_name_field", "shapeName"),
                          cfg.rel(g.get("rivers")), g.get("river_name_field", "name"), g.get("main_rivers_regex"))
        self.extent = g.get("extent")
        self.geo_line = g.get("credit", "")
        n_cat = sum(1 for r in self.A if r["origin"] == self.A[0]["origin"]) if self.A else 0
        self.src_line = f"Source: merged catalogue, {len(self.A)} records ({n_cat} from {self.A[0]['origin'] if self.A else '-'})."
        self.units = [u["name"] for u in cfg.units]

    def save(self, fig, name: str, note: str | None = None) -> None:
        fig.text(0.01, 0.005, note if note is not None else self.src_line, fontsize=6, color=MUTED, ha="left", va="bottom")
        fig.savefig(self.out / name, bbox_inches="tight", pad_inches=0.12)
        plt.close(fig)

    def units_of(self, r) -> list[str]:
        return [u for u in (r.get("units") or "").split(";") if u]

    # ---------------------------------------------------------------- maps
    def no_basemap(self, ax, title: str) -> None:
        ax.axis("off")
        ax.text(0.5, 0.5, "No basemap configured (gis: in the report config)", ha="center", va="center",
                color=MUTED, fontsize=8, transform=ax.transAxes)
        ax.set_title(title, fontsize=9, loc="left", color=INK)

    def choropleth(self, ax, counts: dict, title: str, points=()) -> None:
        if not self.bm.ok:
            self.no_basemap(ax, title)
            return
        vmax = max(counts.values() or [1]) or 1
        edges = sorted(set([0, 1] + [int(np.ceil(x)) for x in np.linspace(1, vmax, 6)[1:]]))
        steps = [SEQ[1], SEQ[3], SEQ[5], SEQ[7], SEQ[9], SEQ[11]][:max(1, len(edges) - 1)]
        def colour(n):
            if n <= 0:
                return "#f3f2ef"
            for i, e in enumerate(edges[1:]):
                if n <= e:
                    return steps[min(i, len(steps) - 1)]
            return steps[-1]
        self.bm.draw_units(ax, default="#fafaf8", edge="#e4e3df")
        self.bm.draw_units(ax, names=self.units, colours={u: colour(counts.get(u, 0)) for u in self.units},
                           edge="white", lw=0.8)
        self.bm.draw_rivers(ax, minor=False)
        for u in self.units:
            x, y = self.bm.label_point(u)
            n = counts.get(u, 0)
            ax.text(x, y, f"{u}\n{n}", fontsize=5.6, ha="center", va="center",
                    color="white" if n > vmax * 0.6 else INK)
        for (x, y) in points:
            ax.plot(x, y, "o", ms=3, mfc=POINT, mec="white", mew=0.4)
        Basemap.frame(ax, self.extent)
        ax.set_title(title, fontsize=9, loc="left", color=INK)
        handles = [Patch(facecolor="#f3f2ef", edgecolor="#cfcfcf", label="0")]
        lo = 1
        for e, s in zip(edges[1:], steps):
            handles.append(Patch(facecolor=s, label=f"{lo}" if lo == e else f"{lo}-{e}"))
            lo = e + 1
        if points:
            handles.append(plt.Line2D([], [], marker="o", ls="", mfc=POINT, mec="white", label="Coordinates stated by a source"))
        ax.legend(handles=handles, title="Records", fontsize=6, title_fontsize=6, loc="lower left", frameon=False)

    def location(self) -> None:
        fig, ax = plt.subplots(figsize=(7.2, 4.6))
        title = f"{self.cfg.get('area.name', 'Study area')}: map units and main rivers"
        if not self.bm.ok:
            self.no_basemap(ax, title)
        else:
            groups = list(self.cfg.groups)
            gcol = {g: c for g, c in zip(groups, ["#cde2fb", "#fbdccd", "#d7f0e5", "#f7e3b5", "#ead7f0"])}
            colours = {u["name"]: gcol.get(u.get("group"), "#e9e8e4") for u in self.cfg.units}
            self.bm.draw_units(ax, default="#fafaf8", edge="#e4e3df")
            self.bm.draw_units(ax, names=self.units, colours=colours, edge="white", lw=0.8)
            self.bm.draw_rivers(ax)
            for u in self.units:
                x, y = self.bm.label_point(u)
                ax.text(x, y, u, fontsize=6, ha="center", va="center", color=INK)
            for lab in self.cfg.get("gis.label_rivers", []) or []:
                ax.text(lab["lon"], lab["lat"], lab["name"], fontsize=6, color="#104281", style="italic")
            Basemap.frame(ax, self.extent)
            hs = [Patch(facecolor=gcol[g], label=g) for g in groups]
            hs.append(plt.Line2D([], [], color="#3987e5", lw=0.9, label="Main rivers"))
            ax.legend(handles=hs, fontsize=6, loc="lower left", frameon=False)
            ax.set_title(title, fontsize=9, loc="left", color=INK)
        self.save(fig, "fig-location.png", self.geo_line)

    def records_map(self) -> None:
        counts = collections.Counter(u for r in self.A for u in self.units_of(r))
        pts = [coords_of(r) for r in self.A if coords_of(r)]
        fig, ax = plt.subplots(figsize=(7.2, 4.6))
        self.choropleth(ax, counts, f"Records by map unit, with source-stated coordinates (n = {len(pts)})", pts)
        unmapped = sum(1 for r in self.A if not self.units_of(r))
        self.save(fig, "fig-records-map.png", f"{self.geo_line} Unmapped (area-level or many units): {unmapped}.")

    # ---------------------------------------------------------------- per type
    def per_type(self) -> dict:
        stats = {}
        have = {r["tenure_type"] for r in self.A} | {s for r in self.A for s in secondary_of(r)}
        for key, name in TYPES:
            if key not in have:
                continue
            prim = [r for r in self.A if r["tenure_type"] == key]
            sec = [r for r in self.A if key in secondary_of(r)]
            recs, lab = (prim, "primary") if prim else (sec, "secondary-type")
            counts = collections.Counter(u for r in recs for u in self.units_of(r))
            fig, ax = plt.subplots(figsize=(6.4, 3.9))
            self.choropleth(ax, counts, f"{name}: {len(recs)} {lab} records by map unit",
                            [coords_of(r) for r in recs if coords_of(r)])
            self.save(fig, f"type-{key}-map.png",
                      f"{self.geo_line} Unmapped: {sum(1 for r in recs if not self.units_of(r))}.")
            uc = collections.Counter(u for r in recs for u in uses_of(r))
            items = [(u, uc[u]) for u in USES if uc[u]]
            fig, ax = plt.subplots(figsize=(6.4, 0.45 + 0.24 * max(1, len(items))))
            ys = np.arange(len(items))[::-1]
            ax.barh(ys, [v for _, v in items], color="#2a78d6", height=0.62)
            for y, (u, v) in zip(ys, items):
                ax.text(v + 0.05, y, str(v), va="center", fontsize=7, color=INK2)
            ax.set_yticks(ys, [f"{u}  {USE_LABEL[u]}" for u, _ in items], fontsize=7)
            ax.set_xticks([])
            ax.spines["bottom"].set_visible(False)
            ax.set_title(f"{name}: water uses on the {lab} records (a record may carry several codes)",
                         fontsize=8, loc="left", color=INK)
            self.save(fig, f"type-{key}-uses.png")
            stats[key] = dict(primary=len(prim), secondary=len(sec), uses=dict(uc), units=dict(counts),
                              groups=dict(collections.Counter(r["group"] for r in prim)),
                              grade=dict(collections.Counter(r["best_grade"] for r in prim)),
                              confidence=dict(collections.Counter(r["confidence"] for r in prim)),
                              origin=dict(collections.Counter(r["origin"] for r in prim)))
        return stats

    # ---------------------------------------------------------------- overview charts
    def heatmap(self) -> None:
        rows = [k for k, _ in TYPES if any(r["tenure_type"] == k for r in self.A)]
        M = np.array([[sum(1 for r in self.A if r["tenure_type"] == k and u in uses_of(r)) for u in USES] for k in rows])
        keep = M.sum(0) > 0
        cols = [u for u, kp in zip(USES, keep) if kp]
        M2 = M[:, keep]
        fig, ax = plt.subplots(figsize=(7.4, 0.9 + 0.3 * len(rows)))
        bounds = [0, 0.5, 1.5, 3.5, 7.5, 15.5, 30.5, 10000]
        cmap = ListedColormap(["#ffffff", SEQ[1], SEQ[3], SEQ[5], SEQ[7], SEQ[9], SEQ[12]])
        ax.imshow(M2, cmap=cmap, norm=BoundaryNorm(bounds, cmap.N), aspect="auto")
        for i in range(M2.shape[0]):
            for j in range(M2.shape[1]):
                if M2[i, j]:
                    ax.text(j, i, M2[i, j], ha="center", va="center", fontsize=6.5, color="white" if M2[i, j] > 15 else INK)
        ax.set_xticks(range(len(cols)), cols, fontsize=7)
        ax.set_yticks(range(len(rows)), [TYPE_LABEL[k] for k in rows], fontsize=7)
        ax.set_xticks(np.arange(-.5, len(cols)), minor=True)
        ax.set_yticks(np.arange(-.5, len(rows)), minor=True)
        ax.grid(which="minor", color="#ffffff", linewidth=1.2)
        ax.tick_params(which="minor", length=0)
        ax.xaxis.tick_top()
        for s in ax.spines.values():
            s.set_visible(False)
        ax.set_title("Tenure type by water use: records per cell (primary type)", fontsize=9, loc="left", color=INK, pad=20)
        self.save(fig, "fig-heatmap.png", self.src_line + " Use codes: FAO water tenure assessment classification. Empty use columns omitted.")

    def bars(self, name: str, title: str, labels: list[str], values: list[int], colours=None, note=None) -> None:
        fig, ax = plt.subplots(figsize=(7.2, 0.5 + 0.26 * len(labels)))
        ys = np.arange(len(labels))[::-1]
        ax.barh(ys, values, color=colours or "#2a78d6", height=0.62)
        for y, v in zip(ys, values):
            ax.text(v + max(values + [1]) * 0.01 + 0.05, y, str(v), va="center", fontsize=7, color=INK2)
        ax.set_yticks(ys, labels, fontsize=7)
        ax.set_xticks([])
        ax.spines["bottom"].set_visible(False)
        ax.set_title(title, fontsize=8.5, loc="left", color=INK)
        self.save(fig, name, note)

    def grades(self) -> None:
        gs = collections.Counter(s["grade"] for s in self.S)
        gr = collections.Counter(r["best_grade"] for r in self.A)
        fig, axs = plt.subplots(1, 2, figsize=(7.4, 2.5))
        cols = ["#104281", "#1c5cab", "#2a78d6", "#5598e7", "#86b6ef", "#b7d3f6"]
        for ax, cnt, ttl in ((axs[0], gs, f"Sources by grade (n = {len(self.S)})"),
                             (axs[1], gr, f"Records by best grade of their sources (n = {len(self.A)})")):
            ys = np.arange(len(GRADES))[::-1]
            vals = [cnt.get(o, 0) for o in GRADES]
            ax.barh(ys, vals, color=cols, height=0.62)
            for y, v in zip(ys, vals):
                ax.text(v + max(vals + [1]) * 0.015, y, str(v), va="center", fontsize=7, color=INK2)
            ax.set_yticks(ys, [GRADE_LABEL[o] for o in GRADES], fontsize=7)
            ax.set_xticks([])
            ax.spines["bottom"].set_visible(False)
            ax.set_title(ttl, fontsize=8, loc="left", color=INK)
        axs[1].set_yticks([])
        fig.tight_layout()
        self.save(fig, "fig-grades.png")

    def confidence(self) -> None:
        rows = [k for k, _ in TYPES if any(r["tenure_type"] == k for r in self.A)]
        ccol = ["#104281", "#2a78d6", "#86b6ef", "#cde2fb", "#eb6834"]
        fig, ax = plt.subplots(figsize=(7.2, 0.9 + 0.3 * len(rows)))
        for i, k in enumerate(rows[::-1]):
            recs = [r for r in self.A if r["tenure_type"] == k]
            left = 0.0
            for c, col in zip(CONFIDENCE, ccol):
                v = sum(1 for r in recs if r["confidence"] == c) / max(1, len(recs))
                if v:
                    ax.barh(i, v, left=left, color=col, height=0.66, edgecolor="white", linewidth=1)
                left += v
            ax.text(1.01, i, f"n = {len(recs)}", va="center", fontsize=6.5, color=INK2)
        ax.set_yticks(range(len(rows)), [TYPE_LABEL[k] for k in rows[::-1]], fontsize=7)
        ax.set_xlim(0, 1)
        ax.set_xticks([0, .25, .5, .75, 1], ["0%", "25%", "50%", "75%", "100%"], fontsize=7)
        ax.legend(handles=[Patch(color=c, label=l) for c, l in zip(ccol, CONFIDENCE)], ncol=5, fontsize=6.5,
                  frameon=False, loc="upper left", bbox_to_anchor=(0, 1.16))
        ax.set_title("Confidence of records, by tenure type", fontsize=9, loc="left", color=INK, pad=22)
        self.save(fig, "fig-confidence.png", self.src_line + " Triangulated = three or more independent origins across two or more primary source types.")

    def typology(self) -> None:
        keys = [k for k, _ in TYPES if k != "unclassified"]
        n = {k: sum(1 for r in self.A if r["tenure_type"] == k) for k in keys}
        top = max(n.values() or [1]) or 1
        fig, ax = plt.subplots(figsize=(7.4, 2.8))
        x = np.arange(len(keys))
        ax.bar(x, [n[k] for k in keys], color=["#2a78d6" if k in FAMILY1 else "#eb6834" for k in keys], width=0.7)
        for i, k in enumerate(keys):
            ax.text(i, n[k] + top * 0.02, str(n[k]), ha="center", fontsize=6.5, color=INK2)
        ax.set_xticks(x, [TYPE_LABEL[k] for k in keys], rotation=60, ha="right", fontsize=6.3)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.legend(handles=[Patch(color="#2a78d6", label="FAO Family 1: derived from formal law"),
                           Patch(color="#eb6834", label="FAO Family 2: not established on formal law")],
                  fontsize=6.5, frameon=False, loc="upper right")
        ax.set_title("The FAO tenure types, with primary records per type", fontsize=9, loc="left", color=INK)
        self.save(fig, "fig-typology.png")

    def season(self) -> None:
        sc = collections.Counter(season_of(r) for r in self.A)
        self.bars("fig-season.png", "Records by the season their arrangement refers to (keyword coding of the period field)",
                  SEASONS, [sc.get(c, 0) for c in SEASONS])

    def groups_by_type(self) -> None:
        groups = list(self.cfg.groups) + ["several", "area-level"]
        rows = [k for k, _ in TYPES if any(r["tenure_type"] == k for r in self.A)]
        fig, ax = plt.subplots(figsize=(7.2, 0.9 + 0.3 * len(rows)))
        for i, k in enumerate(rows[::-1]):
            left = 0
            for g, col in zip(groups, CAT):
                v = sum(1 for r in self.A if r["tenure_type"] == k and r["group"] == g)
                if v:
                    ax.barh(i, v, left=left, color=col, height=0.66, edgecolor="white", linewidth=1)
                left += v
            ax.text(left + 0.2, i, str(left), va="center", fontsize=6.5, color=INK2)
        ax.set_yticks(range(len(rows)), [TYPE_LABEL[k] for k in rows[::-1]], fontsize=7)
        ax.set_xticks([])
        ax.spines["bottom"].set_visible(False)
        ax.legend(handles=[Patch(color=c, label=g) for g, c in zip(groups, CAT)], fontsize=6.5, frameon=False,
                  ncol=min(4, len(groups)), loc="upper left", bbox_to_anchor=(0, 1.16))
        ax.set_title("Primary records by group and tenure type", fontsize=9, loc="left", color=INK, pad=22)
        self.save(fig, "fig-groups-by-type.png", self.src_line + " Groups assigned by keyword from the location fields.")

    def verification(self) -> None:
        items = self.cfg.get("verification") or []
        fig, ax = plt.subplots(figsize=(7.2, 0.6 + 0.3 * len(items)))
        ys = np.arange(len(items))[::-1]
        for y, (label, total, done) in zip(ys, items):
            ax.barh(y, total, color="#cde2fb", height=0.6)
            ax.barh(y, done, color="#2a78d6", height=0.6)
            ax.text(total + max(i[1] for i in items) * 0.01, y, f"{done} of {total}", va="center", fontsize=7, color=INK2)
        ax.set_yticks(ys, [i[0] for i in items], fontsize=7)
        ax.set_xticks([])
        ax.spines["bottom"].set_visible(False)
        ax.set_title("Verification, n of N (dark = checked or matched; light = total)", fontsize=8.5, loc="left", color=INK)
        self.save(fig, "fig-verification.png", "Source: verification record of this project (config: verification).")


def main(cfg_path: str) -> int:
    cfg = load_config(cfg_path)
    f = Figs(cfg)
    if not f.A:
        print("ERROR no records; run merge.py first", file=sys.stderr)
        return 1
    f.location()
    f.records_map()
    stats = f.per_type()
    f.heatmap()
    f.grades()
    f.confidence()
    f.typology()
    f.season()
    if cfg.groups:
        f.groups_by_type()
    if cfg.get("verification"):
        f.verification()
    with open(cfg.work / "data" / "type_stats.json", "w", encoding="utf-8") as fh:
        json.dump(stats, fh, indent=1)
    print(f"figures written: {len(list(f.out.glob('*.png')))} in {f.out.name}/; basemap: {'yes' if f.bm.ok else 'no'}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
