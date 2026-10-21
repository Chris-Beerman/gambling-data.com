#!/usr/bin/env python3
"""Render the 1200x630 social-sharing images into src/static/img/.

    python3 tools/social_cards.py

Needs Playwright with Chromium (pip install playwright; playwright install chromium).
Each card takes its headline figure from the page's first key-figure card, so
re-run this after a data update and commit the PNGs.
"""
import asyncio
import json
import re
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src" / "static" / "img"
FONT = (ROOT / "src" / "static" / "fonts" / "archivo-latin-wdth-normal.woff2").as_uri()

CARDS = {
    "home": ("Illinois gambling statistics", "from the state's own records", "/illinois/", "lost to legal gambling in Illinois, July 2025 – June 2026"),
    "illinois": ("Illinois gambling statistics", "losses, taxes, growth and treatment", "/illinois/", None),
    "video-gambling": ("Illinois video gambling data", "terminals, revenue and taxes by town, 2012–2026", "/illinois/video-gambling/", None),
    "casinos": ("Illinois casino data", "revenue, admissions and taxes by casino, 2020–2026", "/illinois/casinos/", None),
    "sports-betting": ("Illinois sports betting data", "handle, revenue, hold, operators and taxes, 2020–2026", "/illinois/sports-betting/", None),
    "about": ("About Gambling Data", "who compiles it, how, and the standards it keeps", None, ("Public records only", "Compiled from Illinois state records by Chris Beerman, LCSW, CADC")),
}

HTML = """<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: Archivo; src: url({font}) format('woff2-variations'); font-weight: 100 900; font-stretch: 62% 125%; }}
html, body {{ margin: 0; }}
body {{ width: 1200px; height: 630px; background: #fff; font-family: Archivo, sans-serif; color: #1d2b33; position: relative; overflow: hidden; }}
.top {{ position: absolute; left: 0; right: 0; top: 0; height: 14px; background: #17435C; }}
.mark {{ position: absolute; left: 72px; top: 64px; display: grid; grid-template-columns: 22px 22px; gap: 5px; }}
.mark i {{ display: block; width: 22px; height: 22px; border-radius: 4px; }}
.word {{ position: absolute; left: 134px; top: 60px; font-weight: 800; font-stretch: 118%; font-size: 34px; color: #17435C; letter-spacing: -0.01em; }}
.word small {{ display: block; font-weight: 450; font-stretch: 100%; font-size: 19px; color: #7a8891; margin-top: 2px; }}
.fig {{ position: absolute; left: 72px; top: 190px; font-size: 168px; font-weight: 760; font-stretch: 112%; color: #17435C; letter-spacing: -0.03em; line-height: 1; font-variant-numeric: tabular-nums; }}
.fig.text {{ font-size: 112px; }}
.cap {{ position: absolute; left: 76px; top: 384px; font-size: 32px; color: #4a5a63; max-width: 1000px; line-height: 1.3; }}
.title {{ position: absolute; left: 72px; bottom: 112px; font-size: 46px; font-weight: 740; font-stretch: 112%; color: #1d2b33; letter-spacing: -0.015em; line-height: 1.1; max-width: 1050px; }}
.sub {{ position: absolute; left: 72px; bottom: 56px; font-size: 27px; color: #4a5a63; }}
.url {{ position: absolute; right: 72px; bottom: 56px; font-size: 27px; font-weight: 650; color: #3E7CA6; }}
</style></head><body>
<div class="top"></div>
<div class="mark"><i style="background:#17435C"></i><i style="background:#3E7CA6"></i><i style="background:#7fb0cf"></i><i style="background:#c9dde8"></i></div>
<div class="word">Gambling Data<small>Illinois gambling statistics from public records</small></div>
<div class="fig {figclass}">{figure}</div>
<div class="cap">{caption}</div>
<div class="title">{title}</div>
<div class="sub">{sub}</div>
<div class="url">gambling-data.com</div>
</body></html>"""


def first_card(slug: str):
    text = (ROOT / "src" / "content" / (slug + ".html")).read_text()
    m = re.search(r'<div class="cat-igd-card"><div class="l">(.*?)</div><div class="v">(.*?)</div>(?:<div class="d">(.*?)</div>)?', text, re.S)
    if not m:
        return None
    label, value, delta = (re.sub(r"<[^>]+>", "", x or "") for x in m.groups())
    return label, value, delta


async def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1)
        for slug, (title, sub, source, caption) in CARDS.items():
            figure, cap = "", ""
            if isinstance(caption, tuple):
                figure, cap = caption
            elif source:
                src_slug = {"/illinois/": "illinois", "/illinois/video-gambling/": "video-gambling",
                            "/illinois/casinos/": "casinos", "/illinois/sports-betting/": "sports-betting"}[source]
                card = first_card(src_slug)
                if card:
                    label, value, delta = card
                    figure = value
                    cap = caption or (label[0].lower() + label[1:] + (f" ({delta})" if delta else ""))
            figclass = "text" if figure and not re.match(r"^[\$\d]", figure) else ""
            html = HTML.format(font=FONT, figure=figure, caption=cap, title=title, sub=sub, figclass=figclass)
            tmp = OUT / f"_card-{slug}.html"
            tmp.write_text(html)
            await page.goto(tmp.as_uri(), wait_until="load")
            await page.evaluate("document.fonts.ready")
            tmp.unlink()
            await page.screenshot(path=str(OUT / f"social-{slug}.png"), type="png")
            print("wrote", f"social-{slug}.png", figure, "|", cap)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
