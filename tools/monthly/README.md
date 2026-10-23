# Monthly update tooling

Used from the October 2026 run onward. The four Illinois data pages live in two places —
the Squarespace Markdown blocks on chicagoaddictiontherapy.com and `src/content/*.html` here —
and both copies must get the same edits. The approach: compute every edit **once**, as a JSON
spec, from the repo copy; apply it to the repo copy with Python and to the Squarespace block with
one JavaScript call in a browser tab that has the block editor open. Nothing has to be moved
between the browser and the workspace except the spec itself (a gzip+base64 string pasted into
the JavaScript call), so the routine works even when the workspace cannot reach the practice site
and no download folder is connected.

## Files

- `common.py` — `Edits` (text replacements that must match exactly once; whole-SVG swaps located
  by the chart's `<title id>`), rounding helpers that behave like JS `toFixed`, `extend_line()` for
  the monthly line charts (rescales every x so the new month fits, appends the point, moves the end
  dot, label and hover rect) and `bar()` for the rounded "2026†" year-to-date bars.
- `runs/<year-month>/{vgt,sports,casino,hub}.py` — one script per page per run, holding that
  month's IGB figures at the top. Copy the previous month's scripts and change the figures and
  month names; the asserts catch most arithmetic slips.
- `render.py <slug> <tid> …` — renders the named charts from `src/content/<slug>.html` to
  `out/<slug>-charts.png` with Playwright, for a visual check before anything is published.
- `make_payload.py <slug> dry|apply` — writes `out/<slug>.<mode>.js`, the self-contained
  JavaScript to run in the browser. `dry` reports whether every find string and chart matches
  exactly once; `apply` performs the edit.

## The run

1. Pull the new month from `igbapps.illinois.gov` in a browser tab (the `igbPost()` helper in the
   practice's project notes: `VideoReports_AEM.aspx` statewide summary and municipality file,
   `SportsReports_AEM.aspx` Detail and Tax Summary reports (month, calendar year to date, rolling
   twelve months), `CasinoReports_AEM.aspx` Casino Summary, one month per POST).
2. Write the run scripts, run them (`python3 tools/monthly/runs/2026-10/vgt.py` and so on), render
   the changed charts and look at them. The scripts rewrite `src/content/*.html` and write
   `out/<slug>.spec.json`.
3. In Squarespace: Pages → the page → Edit → double-click the block. The editor is CodeMirror 6;
   the view is `document.querySelector('.cm-content').cmTile.view`. Run `out/<slug>.dry.js`, then
   `out/<slug>.apply.js`, then click Save. The apply script strips Squarespace's
   `data-preserve-html-node="true"` attributes before matching (the renderer puts them back).
4. Page settings → SEO (if a figure in the description changed) and Advanced: update
   `temporalCoverage`, `dateModified` and the description in the Dataset JSON-LD. That pane is
   still CodeMirror 5: `setValue()` (twice if the first is reverted), type one real space, remove
   it with `replaceRange`, Save.
5. Patch the same dataset fields in the front matter of `src/content/*.html`, then
   `python3 build.py`, `python3 tools/social_cards.py` (keep only the PNGs whose figure changed),
   commit and push.
6. Verify both sites with cache-busted fetches: counts of `<svg>`, `<h2>`, tables and cards, the
   new figures present, the old month absent.
