"""Render selected SVG charts from a content file to a PNG for visual checking.
Usage: python3 render.py <slug> <tid> [<tid> ...] -> out/<slug>-charts.png"""
import re
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'tools' / 'monthly' / 'out'
OUT.mkdir(parents=True, exist_ok=True)
slug = sys.argv[1]
tids = sys.argv[2:]
body = (ROOT / 'src' / 'content' / (slug + '.html')).read_text().split('meta-->\n', 1)[1]
css = (ROOT / 'src' / 'static' / 'data.css').read_text()
parts = []
for tid in tids:
    m = re.search(r'<svg[^>]*aria-labelledby="%s [^"]*"[^>]*>[\s\S]*?</svg>' % tid, body)
    if not m:
        raise SystemExit('no ' + tid)
    parts.append('<figure style="margin:0 0 24px"><figcaption style="font:600 14px Archivo,sans-serif;margin:0 0 6px">%s</figcaption>%s</figure>' % (tid, m.group(0)))
html = '<!doctype html><html><head><meta charset="utf-8"><style>%s body{margin:0;padding:16px;background:#fff} .cat-igd{max-width:860px}</style></head><body><div class="cat-igd">%s</div></body></html>' % (css, ''.join(parts))
p = OUT / (slug + '-charts.html')
p.write_text(html)
with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page(viewport={'width': 900, 'height': 800}, device_scale_factor=1)
    pg.goto('file://' + str(p))
    pg.wait_for_timeout(300)
    png = OUT / (slug + '-charts.png')
    pg.screenshot(path=str(png), full_page=True)
    b.close()
print('wrote', png)
