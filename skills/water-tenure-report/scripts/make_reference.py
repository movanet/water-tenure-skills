#!/usr/bin/env python3
"""Generate a styled pandoc reference template (reference.docx) for the report build.

    python make_reference.py <config.yaml> [--out PATH]

Takes pandoc's own default reference.docx (`pandoc --print-default-data-file reference.docx`)
and restyles it with python-docx: A4 or Letter page, margins, heading and body fonts and
colours from the config's `docx:` block, compact tables and footnotes. Writes
<work>/reference.docx unless --out is given; build.py picks that file up automatically.
Needs pandoc and python-docx. Document properties are blanked so no user or machine name is
carried into reports.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import find_pandoc  # noqa: E402
from common import die, load_config  # noqa: E402


def rgb(hexstr: str):
    from docx.shared import RGBColor
    h = hexstr.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if "--out" in argv:
        i = argv.index("--out")
        if i + 1 >= len(argv):
            print(__doc__)
            return 2
        out = Path(argv[i + 1])
        args = [a for a in args if a != argv[i + 1]]
    else:
        out = None
    if len(args) != 1:
        print(__doc__)
        return 2
    cfg = load_config(args[0])
    out = out or (cfg.work / "reference.docx")
    try:
        from docx import Document
        from docx.shared import Cm, Pt
    except ImportError:
        die("python-docx is needed: pip install python-docx")
    pb = find_pandoc(cfg)
    if not pb:
        die("pandoc not found: install it or set PANDOC")

    d = cfg.get("docx") or {}
    head_c, accent_c = rgb(d.get("heading_color", "0d366b")), rgb(d.get("accent_color", "1c5cab"))
    ink, muted = rgb(d.get("body_color", "1f1f1f")), rgb("52514e")
    body_f, head_f = d.get("body_font", "Calibri"), d.get("heading_font", "Calibri Light")

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp) / "default.docx"
        r = subprocess.run([pb, "-o", str(base), "--print-default-data-file", "reference.docx"],
                           capture_output=True, text=True)
        if r.returncode != 0 or not base.exists():
            die(f"pandoc could not write its default reference.docx: {r.stderr[-500:]}")
        doc = Document(str(base))

        letter = str(d.get("page", "A4")).lower() == "letter"
        for s in doc.sections:
            s.page_height, s.page_width = (Cm(27.94), Cm(21.59)) if letter else (Cm(29.7), Cm(21.0))
            s.left_margin = s.right_margin = Cm(2.3)
            s.top_margin = s.bottom_margin = Cm(2.2)

        def style(name, size=None, bold=None, color=None, font=None, before=None, after=None, italic=None):
            try:
                st = doc.styles[name]
            except KeyError:
                return
            f = st.font
            f.name = font or body_f
            if size:
                f.size = Pt(size)
            if bold is not None:
                f.bold = bold
            if italic is not None:
                f.italic = italic
            if color is not None:
                f.color.rgb = color
            pf = st.paragraph_format
            if before is not None:
                pf.space_before = Pt(before)
            if after is not None:
                pf.space_after = Pt(after)

        for n in ("Normal", "Body Text", "First Paragraph"):
            style(n, 10.5, color=ink, after=6)
        style("Compact", 9.5, color=ink, after=2)
        style("Title", 24, True, head_c, head_f, after=6)
        style("Subtitle", 15, False, accent_c, head_f, after=18)
        style("Author", 11, False, ink)
        style("Date", 11, False, ink, italic=True)
        style("Heading 1", 18, True, head_c, head_f, before=24, after=10)
        style("Heading 2", 13.5, True, head_c, before=16, after=6)
        style("Heading 3", 11.5, True, accent_c, before=12, after=4)
        style("Heading 4", 10.5, True, accent_c, before=10, after=4)
        style("Footnote Text", 8.5, color=ink, after=1)
        style("Image Caption", 9, False, muted, italic=True, after=12)
        style("Table Caption", 9, False, muted, italic=True)
        style("Block Text", 10, False, head_c, before=6, after=6)
        style("Source Code", 9, font="Consolas")

        cp = doc.core_properties
        cp.author = cp.last_modified_by = cp.title = cp.subject = cp.keywords = cp.comments = ""
        out.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(out))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
