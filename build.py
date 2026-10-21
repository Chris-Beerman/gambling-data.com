#!/usr/bin/env python3
"""Build gambling-data.com into docs/ (served by GitHub Pages).

    python3 build.py

No dependencies beyond the standard library. Pages are src/content/*.html,
each starting with a JSON block between <!--meta and meta-->; the rest of the
file is the page body. src/templates/base.html supplies the chrome.
"""
import datetime as dt
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
OUT = ROOT / "docs"
SITE = "https://gambling-data.com"
TODAY = dt.date.today()

NAV = [("/illinois/", "Illinois"), ("/illinois/video-gambling/", "Video gambling"),
       ("/illinois/casinos/", "Casinos"), ("/illinois/sports-betting/", "Sports betting"),
       ("/about/", "About")]
PRODUCT_PAGES = ["/illinois/video-gambling/", "/illinois/casinos/", "/illinois/sports-betting/"]
BREADCRUMB_NAMES = {"/illinois/video-gambling/": "Video gambling", "/illinois/casinos/": "Casinos",
                    "/illinois/sports-betting/": "Sports betting"}
PAGE_NAMES = {"/illinois/": "Illinois gambling statistics", "/illinois/video-gambling/": "Illinois video gambling data",
              "/illinois/casinos/": "Illinois casino data", "/illinois/sports-betting/": "Illinois sports betting data"}


def long_date(d: dt.date) -> str:
    return d.strftime("%B ") + str(d.day) + d.strftime(", %Y")


def read_page(path: Path):
    text = path.read_text()
    m = re.match(r"<!--meta\n(.*?)\nmeta-->\n?(.*)\Z", text, re.S)
    if not m:
        raise SystemExit(f"{path}: missing meta block")
    return json.loads(m.group(1)), m.group(2)


def nav_html(current: str) -> str:
    out = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href == current else ""
        cls = ' class="about"' if href == "/about/" else ""
        out.append(f'<a href="{href}"{cur}{cls}>{label}</a>')
    return "\n      ".join(out)


def ld_script(obj) -> str:
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>"


def breadcrumb_ld(path: str, name: str):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Gambling Data", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "Illinois gambling statistics", "item": SITE + "/illinois/"},
        {"@type": "ListItem", "position": 3, "name": name, "item": SITE + path}]}


WEBSITE_LD = {"@context": "https://schema.org", "@type": "WebSite", "@id": SITE + "/#website",
              "name": "Gambling Data", "url": SITE + "/",
              "description": "Illinois gambling statistics compiled from Illinois Gaming Board and other state public records.",
              "inLanguage": "en",
              "publisher": {"@type": "Organization", "@id": SITE + "/#publisher", "name": "Gambling Data", "url": SITE + "/",
                            "founder": {"@type": "Person", "@id": SITE + "/about/#editor", "name": "Chris Beerman", "url": SITE + "/about/"}}}


def first(pattern: str, text: str, flags=re.S):
    m = re.search(pattern, text, flags)
    return m.group(1) if m else ""


def card_figs(body: str, n: int = 3) -> str:
    cards = re.findall(r'<div class="cat-igd-card">(.*?)</div>\s*</div>', body, re.S)
    out = []
    for c in cards[:n]:
        label = first(r'<div class="l">(.*?)</div>', c)
        value = first(r'<div class="v">(.*?)</div>', c)
        delta = first(r'<div class="d">(.*?)</div>', c)
        out.append(f'<span class="pg-fig"><span class="l">{label}</span><span class="v">{value}</span>'
                   f'<span class="d">{delta or "&nbsp;"}</span></span>')
    return "".join(out)


def prov(body: str, key: str) -> str:
    return first(r"<dt>" + re.escape(key) + r"</dt><dd>(.*?)</dd>", body)


def strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s)


def render(template: str, **fields) -> str:
    out = template
    for k, v in fields.items():
        out = out.replace("{{" + k + "}}", v)
    leftover = re.findall(r"{{\w+}}", out)
    if leftover:
        raise SystemExit("unfilled placeholders: " + ", ".join(leftover))
    return out


def main() -> None:
    template = (SRC / "templates" / "base.html").read_text()
    pages = {}
    for f in sorted((SRC / "content").glob("*.html")):
        meta, body = read_page(f)
        pages[meta["path"]] = (meta, body, f.stem)

    # Home page pieces, derived from the data pages so they never go stale.
    hub_meta, hub_body, _ = pages["/illinois/"]
    hero_chart = first(r"(<figure>.*?</figure>)", hub_body)
    hero_chart = hero_chart.replace('aria-labelledby="t101 d101"', 'aria-labelledby="t101 d101"')  # ids are unique on the home page too
    rows = []
    for path in ["/illinois/"] + PRODUCT_PAGES:
        meta, body, _ = pages[path]
        name = PAGE_NAMES[path]
        through = prov(body, "Current through") or prov(body, "Latest complete year")
        label = "Current through" if prov(body, "Current through") else "Latest complete year"
        rows.append(f'      <li><a href="{path}"><span><span class="pg-name">{name}</span>'
                    f'<span class="pg-desc">{meta["short"]}</span>'
                    f'<span class="pg-through">{label} {through}. Reviewed {prov(body, "Last reviewed")}.</span></span>'
                    f'<span class="pg-figs">{card_figs(body)}</span></a></li>')
    stamp = (f'<span>Video gaming through <b>{prov(pages["/illinois/video-gambling/"][1], "Current through")}</b></span>'
             f'<span>Casinos through <b>{prov(pages["/illinois/casinos/"][1], "Current through")}</b></span>'
             f'<span>Sports betting through <b>{prov(pages["/illinois/sports-betting/"][1], "Current through")}</b></span>'
             f'<span>Last reviewed <b>{prov(hub_body, "Last reviewed")}</b></span>')

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(SRC / "static", OUT / "static")
    (OUT / "CNAME").write_text("gambling-data.com\n")
    (OUT / ".nojekyll").write_text("")

    sitemap = []
    for path, (meta, body, stem) in pages.items():
        content = body
        if path == "/":
            content = render(body, stamp=stamp, hero_chart=hero_chart, page_rows="\n".join(rows))
        elif path == "/illinois/":
            content = f'<div class="wrap page">\n{body}\n</div>'
        elif path in PRODUCT_PAGES:
            crumb = (f'<p class="breadcrumb measure"><a href="/illinois/">Illinois gambling statistics</a> / '
                     f'{BREADCRUMB_NAMES[path]}</p>')
            content = f'<div class="wrap page">\n{crumb}\n{body}\n</div>'

        lds = []
        if path == "/":
            lds.append(WEBSITE_LD)
        if meta.get("dataset"):
            lds.append(meta["dataset"])
        if path in PRODUCT_PAGES:
            lds.append(breadcrumb_ld(path, PAGE_NAMES[path]))
        if meta.get("schema"):
            lds.append(meta["schema"])
        ld_json = "\n".join(ld_script(x) for x in lds)
        if meta.get("noindex"):
            ld_json += '\n<meta name="robots" content="noindex">'

        canonical = SITE + (path if path != "/404.html" else "/404.html")
        og_image = SITE + "/static/img/social-" + ("home" if path == "/" else stem) + ".png"
        page_html = render(
            template,
            title=html.escape(meta["title"], quote=True),
            og_title=html.escape(meta["title"].split(": ")[0] if path in PRODUCT_PAGES or path == "/illinois/" else meta["title"], quote=True),
            description=html.escape(meta["description"], quote=True),
            canonical=canonical,
            og_type=meta.get("og_type", "article"),
            og_image=og_image,
            ld_json=ld_json,
            body_class=meta.get("body_class", "page"),
            nav=nav_html(path),
            content=content,
            updated=long_date(TODAY),
        )
        if path == "/404.html":
            dest = OUT / "404.html"
        else:
            dest = OUT / path.strip("/") / "index.html" if path != "/" else OUT / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(page_html)
        if not meta.get("noindex"):
            lastmod = (meta.get("dataset") or {}).get("dateModified") or TODAY.isoformat()
            sitemap.append((canonical, lastmod))
        print(f"{path:32s} -> {dest.relative_to(ROOT)}  ({len(page_html):,} bytes)")

    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in sorted(sitemap))
        + "</urlset>\n")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    print("sitemap:", len(sitemap), "urls")


if __name__ == "__main__":
    main()
