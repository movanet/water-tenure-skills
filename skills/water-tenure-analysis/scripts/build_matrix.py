#!/usr/bin/env python3
"""Build the tenure-type x water-use matrix from arrangements.csv.

    python build_matrix.py <catalogue-dir>              writes <catalogue-dir>/matrix.md
    python build_matrix.py <catalogue-dir> --out FILE   writes FILE instead

Rows follow the FAO typology order (references/typology.md section 2); columns are
the FAO use codes. A cell holds the number of arrangement records with that
combination, and the arrangement IDs are listed under the table so every mark
traces back to records, and records to sources. A record with several use codes
counts once in each column; secondary_tenure_types are listed but not counted. Standard library only.
"""
import csv
import pathlib
import sys
from collections import defaultdict

ROWS = [
    "traditional-formal-right", "modern-permit", "regulatory-licence", "agency-control",
    "water-supply-contract", "commonhold", "investment-contract", "de-minimis",
    "exempt-declared-commercial", "reserve-minimum-flow", "customary", "religious-law",
    "informal", "assumed", "impossible", "unrecognised", "unclassified",
]
COLS = ["A1", "A2", "A3", "B1", "B2", "B3", "B4", "B5", "B6", "C", "D1", "D2",
        "E1", "E2", "F", "G1", "G2", "H1", "H2", "I"]


def main(d, out=None):
    d = pathlib.Path(d)
    out = pathlib.Path(out) if out else d / "matrix.md"
    with open(d / "arrangements.csv", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    cell = defaultdict(list)
    unknown_codes = set()
    secondary = defaultdict(list)
    for r in rows:
        tt = (r.get("tenure_type") or "").strip() or "unclassified"
        aid = (r.get("arrangement_id") or "").strip()
        for code in [c.strip() for c in (r.get("water_use") or "").split(";") if c.strip()]:
            if code not in COLS:
                unknown_codes.add(code)
                continue
            cell[(tt, code)].append(aid)
        for s in [x.strip() for x in (r.get("secondary_tenure_types") or "").split(";") if x.strip()]:
            secondary[s].append(aid)

    used_cols = [c for c in COLS if any((t, c) in cell for t in ROWS)]
    lines = ["# Tenure type x water use", "",
             f"Built from `arrangements.csv` in `{d.name}`: {len(rows)} records. "
             "Cell = number of records. Empty rows are listed below the table: say in the report "
             "whether each is absent from the area or was not looked for.", ""]
    lines.append("| Tenure type | " + " | ".join(used_cols) + " |")
    lines.append("|---|" + "---|" * len(used_cols))
    empty = []
    for t in ROWS:
        counts = [len(cell.get((t, c), [])) for c in used_cols]
        if not any(counts):
            empty.append(t)
            continue
        lines.append(f"| {t} | " + " | ".join(str(n) if n else "" for n in counts) + " |")
    lines += ["", "## Records per cell", ""]
    for t in ROWS:
        for c in used_cols:
            if cell.get((t, c)):
                lines.append(f"- {t} x {c}: {', '.join(cell[(t, c)])}")
    lines += ["", "## Tenure types with no records", "", ", ".join(empty) or "none"]
    if secondary:
        lines += ["", "## Secondary tenure types (layered, not counted above)", ""]
        lines += [f"- {s}: {', '.join(ids)}" for s, ids in sorted(secondary.items())]
    if unknown_codes:
        lines += ["", "## Use codes not in the FAO list (fix in arrangements.csv)", "",
                  ", ".join(sorted(unknown_codes))]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {out}: {len(rows)} records, {len(used_cols)} use columns, "
          f"{len(ROWS) - len(empty)} tenure rows" + (f", unknown codes: {sorted(unknown_codes)}" if unknown_codes else ""))
    return 0


if __name__ == "__main__":
    argv = sys.argv[1:]
    out_file = None
    if "--out" in argv:
        i = argv.index("--out")
        if i + 1 >= len(argv):
            print(__doc__)
            sys.exit(2)
        out_file = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    if len(argv) != 1:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(argv[0], out_file))
