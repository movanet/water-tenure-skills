#!/usr/bin/env python3
"""Run the whole report pipeline for one config, stopping at the first failure.

    python run_all.py <config.yaml> [--no-docx] [--no-annexes]

Steps: check every input catalogue with the water-tenure-analysis checker (when that skill is
installed beside this one), merge.py, figures.py, annexes.py, make_reference.py (when pandoc and
python-docx are present), build.py. With --no-docx the build stops at main.md and the checks
(useful without pandoc). Chapters are not written by this script: they are drafted by people or
agents from the evidence packs (see references/drafting-brief.md) before the build step.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build import find_pandoc  # noqa: E402
from common import load_config  # noqa: E402

CHECKER = HERE.parents[1] / "water-tenure-analysis" / "scripts" / "check_catalogue.py"


def run(args: list[str]) -> int:
    print("$", " ".join(Path(a).name if i < 2 else a for i, a in enumerate(args)), flush=True)
    return subprocess.run([sys.executable, *args]).returncode


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    flags = {a for a in argv if a.startswith("--")}
    if len(args) != 1 or flags - {"--no-docx", "--no-annexes"}:
        print(__doc__)
        return 2
    cfg_path = args[0]
    cfg = load_config(cfg_path)
    if CHECKER.exists():
        for inp in cfg.get("inputs") or []:
            if run([str(CHECKER), str(cfg.rel(inp["path"]))]) != 0:
                print("ERROR an input catalogue fails check_catalogue.py; fix it before building", file=sys.stderr)
                return 1
    else:
        print(f"note: {CHECKER} not found; input catalogues were not re-checked")
    for step in ("merge.py", "figures.py") + (() if "--no-annexes" in flags else ("annexes.py",)):
        if run([str(HERE / step), cfg_path]) != 0:
            return 1
    build = [str(HERE / "build.py"), cfg_path] + ([] if "--no-annexes" in flags else ["--annexes"])
    if "--no-docx" in flags:
        build.append("--check-only")
    else:
        try:
            import docx  # noqa: F401
            have_docx = True
        except ImportError:
            have_docx = False
        if have_docx and find_pandoc(cfg) and not cfg.get("docx.reference_doc"):
            if run([str(HERE / "make_reference.py"), cfg_path]) != 0:
                return 1
    return run(build)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
