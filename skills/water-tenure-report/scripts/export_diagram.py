#!/usr/bin/env python3
"""Optional: export an HTML diagram (for example one made with Archify) to a PNG for the report.

    python export_diagram.py <diagram.html> <out.png> [--selector CSS] [--scale 2.5] [--channel chrome]

Opens the HTML in a headless browser in light theme with animations off, screenshots the element
matched by --selector (default `.diagram-container`, then `svg`), trims the white margin and saves
a 300 dpi PNG under <work>/figures/ for build.py to number. Needs `pip install playwright pillow`
and `playwright install chromium` (or an installed Chrome with --channel chrome).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("html")
    ap.add_argument("out")
    ap.add_argument("--selector", default=".diagram-container")
    ap.add_argument("--scale", type=float, default=2.5)
    ap.add_argument("--channel", default=None, help="browser channel, e.g. chrome; default: bundled chromium")
    a = ap.parse_args(argv)
    try:
        from PIL import Image, ImageOps
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR needs playwright and pillow: pip install playwright pillow && playwright install chromium",
              file=sys.stderr)
        return 1
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel=a.channel) if a.channel else p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1600, "height": 1100}, device_scale_factor=a.scale,
                                  color_scheme="light", reduced_motion="reduce")
        page = ctx.new_page()
        page.goto(Path(a.html).resolve().as_uri())
        page.wait_for_timeout(1500)
        page.evaluate("document.documentElement.setAttribute('data-theme','light')")
        page.add_style_tag(content="[class*=zoom],[class*=toolbar],[class*=controls]{visibility:hidden !important}")
        page.wait_for_timeout(300)
        loc = page.locator(a.selector).first
        if loc.count() == 0:
            loc = page.locator("svg").first
        loc.screenshot(path=str(out), animations="disabled")
        browser.close()
    im = Image.open(out).convert("RGB")
    box = ImageOps.grayscale(im).point(lambda v: 255 if v < 185 else 0).getbbox()
    if box:
        pad = 40
        im = im.crop((max(0, box[0] - pad), max(0, box[1] - pad), min(im.width, box[2] + pad), min(im.height, box[3] + pad)))
    im.save(out, dpi=(300, 300))
    print(f"wrote {out} {im.size}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
