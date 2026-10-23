#!/usr/bin/env python3
"""Turn a capture of the four Illinois data pages on chicagoaddictiontherapy.com
into gambling-data.com content files.

Usage:
    python3 tools/import_from_cat.py path/to/cat-data-pages.json

The capture is the JSON a browser tab on the practice site writes when it
fetches the four pages (see README, "Monthly update"). For each page this
script takes the Markdown block's <div class="cat-igd"> fragment, strips
Squarespace's data-preserve attributes, rewrites links so that the four data
pages point at each other on this site and everything else points at the
practice site by absolute URL, adjusts the attribution lines, and writes
src/content/<slug>.html with a JSON front matter block that build.py reads.
The page's Dataset JSON-LD is carried over with this site's URLs.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "src" / "content"
CAT = "https://www.chicagoaddictiontherapy.com"
SITE = "https://gambling-data.com"

# CAT path -> this site's path
PAGES = {
    "/illinois-gambling-statistics": {
        "path": "/illinois/",
        "slug": "illinois",
        "nav": "Illinois",
        "title": "Illinois Gambling Statistics: Losses, Taxes, Growth and Treatment",
        "description": "Illinois gambling statistics from state records: $8.03 billion lost to legal gambling in FY2026, about $796 per adult. Video gaming, casinos, sports betting and the lottery side by side, with state revenue and treatment funding.",
        "short": "All four legal products side by side: losses, state revenue, treatment funding and what Illinois does not measure.",
        "cat_anchor": "Illinois gambling statistics",
        "subject": "statistics page",
    },
    "/illinois-gambling-data": {
        "path": "/illinois/video-gambling/",
        "slug": "video-gambling",
        "nav": "Video gambling",
        "title": "Illinois Video Gambling Data: Terminals, Revenue and Taxes by Town, 2012–2026",
        "description": "Illinois video gaming terminal data compiled from Illinois Gaming Board monthly reports: terminals, locations, amount played, net terminal income and taxes by month and municipality, September 2012 to the latest month. Free CSV downloads.",
        "short": "More than 50,000 terminals in bars, restaurants and gas stations: play, losses and taxes by month and by town since 2012.",
        "cat_anchor": "Illinois video gambling data",
        "subject": "video gambling page",
    },
    "/illinois-casino-data": {
        "path": "/illinois/casinos/",
        "slug": "casinos",
        "nav": "Casinos",
        "title": "Illinois Casino Data: Revenue, Admissions and Taxes by Casino, 2020–2026",
        "description": "Illinois casino data compiled from Illinois Gaming Board monthly reports: adjusted gross receipts, admissions and taxes for all 17 casinos and racinos by month and fiscal year, with the 2019 expansion traced casino by casino.",
        "short": "Seventeen casinos and racinos, up from ten: revenue, admissions and taxes by casino and by month.",
        "cat_anchor": "Illinois casino data",
        "subject": "casino page",
    },
    "/illinois-sports-betting-data": {
        "path": "/illinois/sports-betting/",
        "slug": "sports-betting",
        "nav": "Sports betting",
        "title": "Illinois Sports Betting Data: Handle, Revenue, Hold, Operators and Taxes, 2020–2026",
        "description": "Illinois sports wagering data compiled from Illinois Gaming Board monthly reports: handle, adjusted gross receipts, hold, number of bets, online share, operator market share and taxes, March 2020 to the latest month. Free CSV downloads.",
        "short": "$15 billion a year wagered, almost all of it on phones: handle, hold, bets, operators and taxes by month.",
        "cat_anchor": "Illinois sports betting data",
        "subject": "sports betting page",
    },
}

LINK_MAP = {cat: info["path"] for cat, info in PAGES.items()}
LINK_MAP["/editorial-standards"] = "/about/#standards"


def rewrite_href(href: str) -> str:
    if href is None:
        return href
    if href.startswith("#") or href.startswith("http") or href.startswith("mailto:"):
        return href
    base, _, frag = href.partition("#")
    if base in LINK_MAP:
        new = LINK_MAP[base]
        return new + ("#" + frag if frag and "#" not in new else "")
    if base.startswith("/"):
        return CAT + href
    return href


def transform(fragment: str, info: dict) -> str:
    h = fragment.replace(' data-preserve-html-node="true"', "")
    # links
    h = re.sub(r'href="([^"]*)"', lambda m: 'href="%s"' % rewrite_href(m.group(1)), h)
    # mailto subjects: say which site the mail came from
    h = re.sub(r'(mailto:chris@chicagoaddictiontherapy\.com\?subject=)([^"]*)',
               lambda m: m.group(1) + m.group(2).replace("Data%20correction%20(", "gambling-data.com%20correction%20(")
                                                 .replace("Illinois%20gambling%20data", "gambling-data.com%20video%20gambling%20page")
                                                 .replace("Illinois%20sports%20betting%20data", "gambling-data.com%20sports%20betting%20page"),
               h)
    # byline in the lede: name -> about page, role -> practice site
    h = h.replace('<a href="%s/about">Chris Beerman, LCSW, CADC</a>' % CAT,
                  '<a href="/about/">Chris Beerman, LCSW, CADC</a>')
    h = re.sub(r'(maintained by )(Chris Beerman, LCSW, CADC)(, a gambling addiction therapist in Chicago)',
               r'\1<a href="/about/">\2</a>\3', h)
    h = h.replace('a gambling addiction therapist in Chicago',
                  'a <a href="%s/">gambling addiction therapist in Chicago</a>' % CAT, 1)
    # the "press and media" item in the provenance box belongs to the practice site
    h = h.replace(' · <a href="%s/press">press and media</a>' % CAT, "")
    # attribution lines
    h = h.replace("Compiled by Chicago Addiction Therapy from",
                  "Compiled by Chris Beerman, LCSW, CADC, of Chicago Addiction Therapy, for gambling-data.com from")
    h = re.sub(r'compiled by Chicago Addiction Therapy, [A-Z][a-z]+ 20\d\d',
               "compiled by Chris Beerman, gambling-data.com, October 2026", h)
    h = h.replace("please link to this page.", "please link to this page (CC BY 4.0).")
    # hub page: the list of pages
    h = h.replace("<h2 id=\"cat-st-more\">The Illinois gambling data pages</h2>",
                  "<h2 id=\"cat-st-more\">More Illinois gambling data and context</h2>")
    # keep heading ids but drop Squarespace-only attributes if any remain
    h = re.sub(r"\s+data-[a-z-]+=\"[^\"]*\"", lambda m: m.group(0) if "data-" not in m.group(0) else "", h)
    return h.strip()


def dataset_ld(ld: dict, info: dict) -> dict:
    d = dict(ld)
    url = SITE + info["path"]
    d["url"] = url
    d["@id"] = url + "#dataset"
    d["sameAs"] = ld.get("url")
    d["creator"] = {
        "@type": "Person",
        "@id": SITE + "/about/#editor",
        "name": "Chris Beerman",
        "honorificSuffix": "MSW, LCSW, CADC",
        "url": SITE + "/about/",
        "sameAs": [CAT + "/about", "https://orcid.org/0009-0004-8277-2086"],
        "affiliation": {"@type": "Organization", "name": "Chicago Addiction Therapy", "url": CAT + "/"},
    }
    d["publisher"] = {"@type": "Organization", "@id": SITE + "/#publisher", "name": "Gambling Data", "url": SITE + "/"}
    return d


def main(capture_path: str) -> None:
    bundle = json.loads(Path(capture_path).read_text())
    from bs4 import BeautifulSoup  # only needed here, not by build.py

    CONTENT.mkdir(parents=True, exist_ok=True)
    for page in bundle["pages"]:
        info = PAGES.get(page["path"])
        if not info:
            print("skipping", page["path"])
            continue
        soup = BeautifulSoup(page["html"], "lxml")
        frag = soup.select_one(".cat-igd")
        if frag is None:
            raise SystemExit("no .cat-igd fragment on " + page["path"])
        ld = None
        for s in soup.find_all("script", type="application/ld+json"):
            if '"Dataset"' in s.text:
                ld = json.loads(s.text)
        body = transform(str(frag), info)
        meta = {
            "path": info["path"],
            "nav": info["nav"],
            "title": info["title"],
            "description": info["description"],
            "short": info["short"],
            "source": CAT + page["path"],
            "captured": bundle.get("capturedAt"),
            "dataset": dataset_ld(ld, info) if ld else None,
        }
        out = CONTENT / (info["slug"] + ".html")
        out.write_text("<!--meta\n" + json.dumps(meta, indent=2, ensure_ascii=False) + "\nmeta-->\n" + body + "\n")
        print("wrote", out.relative_to(ROOT), len(body), "chars")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])
