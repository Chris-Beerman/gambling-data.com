# gambling-data.com

Illinois gambling statistics compiled from Illinois Gaming Board and other state public records, by Chris Beerman, LCSW, CADC. A static site served by GitHub Pages from the `docs/` folder of this repository.

## How it is put together

```
src/content/      one file per page: a JSON block between <!--meta and meta-->, then the page body (HTML)
src/templates/    base.html, the shared header, footer and <head>
src/static/       style.css (site), data.css (the content system shared with the practice site), fonts, images
tools/            import_from_cat.py (bring the data pages over from chicagoaddictiontherapy.com),
                  social_cards.py (render the 1200x630 sharing images)
build.py          renders src/ into docs/ (no dependencies beyond Python 3)
docs/             the built site, committed; GitHub Pages serves it
```

Pages: `/` (home), `/illinois/` (all four products side by side), `/illinois/video-gambling/`, `/illinois/casinos/`, `/illinois/sports-betting/`, `/about/`, plus `404.html`, `sitemap.xml`, `robots.txt` and `CNAME`.

The four data pages are the same compilations that live on chicagoaddictiontherapy.com (`/illinois-gambling-statistics`, `/illinois-gambling-data`, `/illinois-casino-data`, `/illinois-sports-betting-data`), published here under the site's own name with the links rewritten: the four pages point at each other on this domain, and everything else (assessments, guides, therapy pages, CSV downloads, editorial standards) points at the practice site by absolute URL. The `.cat-igd` class names are kept on purpose so a page body can move between the two sites unchanged.

## Building

```
python3 build.py                      # writes docs/
python3 -m http.server -d docs 8000   # look at it locally
```

The home page's figures, "current through" months and chart are read from the data pages at build time, so they cannot go stale on their own.

## Monthly update

The Illinois Gaming Board posts a new month in the first days of the next month. The practice site's pages are updated first (that routine is documented in the practice's project notes); then:

1. In a browser tab on `https://www.chicagoaddictiontherapy.com/`, run the capture snippet below. It saves `cat-data-pages.json` to Downloads.
2. `python3 tools/import_from_cat.py ~/Downloads/cat-data-pages.json` rewrites `src/content/{illinois,video-gambling,casinos,sports-betting}.html`.
3. `python3 tools/social_cards.py` (optional; only the headline figures change) and `python3 build.py`.
4. Commit and push `main`. Pages redeploys in about a minute.

Capture snippet:

```js
(async () => {
  const paths = ['/illinois-gambling-statistics','/illinois-gambling-data','/illinois-casino-data','/illinois-sports-betting-data'];
  const pages = [];
  for (const p of paths) { const r = await fetch(p, {cache:'no-store'}); pages.push({path:p, status:r.status, html: await r.text()}); }
  const blob = new Blob([JSON.stringify({capturedAt:new Date().toISOString(), origin:location.origin, pages})], {type:'application/json'});
  const a = Object.assign(document.createElement('a'), {href: URL.createObjectURL(blob), download: 'cat-data-pages.json'});
  document.body.appendChild(a); a.click();
})();
```

If the pages are ever edited here first instead, the same body can be pasted back into the practice site's Markdown block after reversing the link rewrites (`/illinois/` → `/illinois-gambling-statistics`, and so on).

## Things still to do

- Host the CSV downloads here (they are currently linked from the practice site's `/s/` files) and point the Dataset `distribution` entries at them.
- Casino page CSV, promised on the page "with the next quarterly update".
- Search Console: add the property, submit `sitemap.xml`, request indexing for the six URLs.
- Decide, after a couple of months of Search Console data, whether the practice site's copies should carry a cross-domain canonical to these pages or stay as they are.

## Hosting

GitHub Pages, source `main` branch `/docs`, custom domain `gambling-data.com` (the `CNAME` file is written by `build.py`). DNS at GoDaddy: A records for `@` to 185.199.108.153, 185.199.109.153, 185.199.110.153 and 185.199.111.153; CNAME for `www` to `chris-beerman.github.io`. Tick "Enforce HTTPS" in the repository's Pages settings once the certificate has been issued.

## Licences

Code (build script, tools, templates, stylesheet): MIT. Text, charts and tables: CC BY 4.0. The underlying figures are Illinois public records. Archivo is used under the SIL Open Font License (`src/static/fonts/LICENSE-Archivo-OFL.txt`).
