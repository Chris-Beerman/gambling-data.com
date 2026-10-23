"""Shared helpers for the October 2026 Illinois data-page update.

Each page script produces two things:
  * the updated gambling-data.com content file (src/content/<slug>.html), and
  * a JSON edit spec for the Squarespace Markdown block, applied in the browser:
      {"text": [{"find": ..., "replace": ...}, ...],      # each must occur exactly once
       "svg":  [{"tid": "t1604", "svg": "<svg ...>...</svg>"}, ...]}  # whole-SVG swaps by <title id>
"""
import json
import re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'tools' / 'monthly' / 'out'
OUT.mkdir(parents=True, exist_ok=True)


class Edits:
    def __init__(self, slug):
        self.slug = slug
        path = ROOT / 'src' / 'content' / (slug + '.html')
        raw = path.read_text()
        self.front, self.body = raw.split('meta-->\n', 1)
        self.path = path
        self.text = []
        self.svg = []

    # ---- text -------------------------------------------------------------
    def rep(self, find, replace, count=1):
        n = self.body.count(find)
        if n != count:
            raise SystemExit('%s: expected %d, found %d for: %r' % (self.slug, count, n, find[:120]))
        self.body = self.body.replace(find, replace)
        self.text.append({'find': find, 'replace': replace, 'count': count})

    # ---- svg --------------------------------------------------------------
    def get_svg(self, tid):
        m = re.search(r'<svg[^>]*aria-labelledby="%s [^"]*"[^>]*>[\s\S]*?</svg>' % tid, self.body)
        if not m:
            raise SystemExit('%s: no svg with title id %s' % (self.slug, tid))
        return m.group(0)

    def put_svg(self, tid, new):
        old = self.get_svg(tid)
        assert self.body.count(old) == 1
        new = new.replace('viewbox=', 'viewBox=')
        assert '\n' not in new
        self.body = self.body.replace(old, new)
        self.svg.append({'tid': tid, 'svg': new})

    # ---- output -----------------------------------------------------------
    def save(self):
        self.path.write_text(self.front + 'meta-->\n' + self.body)
        spec = {'slug': self.slug, 'text': self.text, 'svg': self.svg}
        (OUT / (self.slug + '.spec.json')).write_text(json.dumps(spec, ensure_ascii=False))
        print(self.slug, 'text edits', len(self.text), 'svg swaps', len(self.svg), 'body', len(self.body))


def r1(x):
    """Round like JS toFixed(1) (half up)."""
    return str(Decimal(str(x)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))


def rn(x, nd):
    return str(Decimal(str(x)).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


def pct(new, old, nd=1):
    v = (new / old - 1) * 100
    s = rn(v, nd)
    return ('+' if v >= 0 else '') + s + '%'


def money_b(x_m, nd=2):
    """$ millions -> '$1.23B'"""
    return '$' + rn(x_m / 1000, nd) + 'B'


def money_m(x_m, nd=1):
    return '$' + rn(x_m, nd) + 'M'


def comma(n):
    return '{:,}'.format(int(round(n)))


# ---- line-chart helper -----------------------------------------------------
def extend_line(svg, x0, x1, n_old, new_y, hover_title, label, hover_half, label_dy=-10, label_anchor_x=None,
                point_class_rect=True, circle=True):
    """Add one point at the end of a monthly line chart whose points are spread
    evenly from x0 to x1 over n_old months. Every x coordinate is rescaled from
    index i*(x1-x0)/(n_old-1) to i*(x1-x0)/n_old. Returns the new svg string."""
    n_new = n_old + 1
    step_old = (x1 - x0) / (n_old - 1)
    step_new = (x1 - x0) / (n_new - 1)

    def idx(x):
        return int(round((x - x0) / step_old))

    def nx(i):
        return x0 + i * step_new

    def f1(v):
        return r1(v)

    # polylines
    def fix_poly(m):
        pts = m.group(2).split()
        out = []
        for p in pts:
            x, y = p.split(',')
            out.append('%s,%s' % (f1(nx(idx(float(x)))), y))
        return m.group(1) + ' '.join(out) + m.group(3)

    polys = list(re.finditer(r'(<polyline[^>]*points=")([^"]+)("[^>]*>)', svg))
    assert polys, 'no polylines'
    svg = re.sub(r'(<polyline[^>]*points=")([^"]+)("[^>]*>)', fix_poly, svg)
    # append new point to the last polyline
    last = list(re.finditer(r'(<polyline[^>]*points=")([^"]+)("[^>]*>)', svg))[-1]
    pts = last.group(2) + ' %s,%s' % (f1(nx(n_new - 1)), f1(new_y))
    svg = svg[:last.start(2)] + pts + svg[last.end(2):]

    # shaded rects (fill="#e3e9ed" ... x= width=) and hover rects (class="h" x=)
    def fix_rect(m):
        tag = m.group(0)
        if 'class="h"' in tag:
            xm = re.search(r' x="([^"]+)"', tag)
            i = idx(float(xm.group(1)) + hover_half)
            return tag.replace(xm.group(0), ' x="%s"' % f1(nx(i) - hover_half))
        if 'fill="#e3e9ed"' in tag and ' width=' in tag:
            xm = re.search(r' x="([^"]+)"', tag)
            wm = re.search(r' width="([^"]+)"', tag)
            i = idx(float(xm.group(1)))
            w = float(wm.group(1)) * step_new / step_old
            tag = tag.replace(xm.group(0), ' x="%s"' % f1(nx(i)))
            tag = tag.replace(wm.group(0), ' width="%s"' % f1(w))
            return tag
        return tag
    svg = re.sub(r'<rect[^>]*>', fix_rect, svg)

    # year labels: <text class="ax" text-anchor="middle" x=".." y="..">YYYY</text>
    def fix_year(m):
        x = float(m.group(2))
        return m.group(1) + f1(nx(idx(x))) + m.group(3)
    svg = re.sub(r'(<text class="ax" text-anchor="middle" x=")([^"]+)(" y="[^"]+">\d{4}</text>)', fix_year, svg)

    # end circle
    if circle:
        cm = re.search(r'<circle[^>]*cx="([^"]+)"[^>]*cy="([^"]+)"[^>]*>', svg)
        assert cm, 'no circle'
        tag = cm.group(0)
        tag2 = tag.replace('cx="%s"' % cm.group(1), 'cx="%s"' % f1(x1)).replace('cy="%s"' % cm.group(2), 'cy="%s"' % f1(new_y))
        svg = svg.replace(tag, tag2)
    # label: <text class="lbl" text-anchor="end" x=".." y="..">$287M</text> (first lbl)
    lm = re.search(r'(<text class="lbl"[^>]*y=")([^"]+)("[^>]*>)([^<]*)(</text>)', svg)
    assert lm, 'no label'
    svg = svg[:lm.start()] + lm.group(1) + f1(new_y + label_dy) + lm.group(3) + label + lm.group(5) + svg[lm.end():]
    # new hover rect after the last hover rect
    hovers = list(re.finditer(r'<rect class="h" x="[^"]+"><title>[^<]*</title></rect>', svg))
    assert hovers, 'no hover rects'
    h = hovers[-1]
    new_h = '<rect class="h" x="%s"><title>%s</title></rect>' % (f1(nx(n_new - 1) - hover_half), hover_title)
    svg = svg[:h.end()] + new_h + svg[h.end():]
    return svg


def bar(svg, title_prefix, new_title, new_value_top, new_label=None, baseline=None):
    """Move a rounded bar (path d="Mx,base Vtop a4,4 ... Z") whose <title> starts with
    title_prefix to a new top y, and rewrite its title; optionally the value label
    that sits above it (the <text class="lbl"> with the same x)."""
    m = re.search(r'<path d="M([\d.]+),([\d.]+) V([\d.]+) ([^"]+)" fill="([^"]+)"><title>' + re.escape(title_prefix) + r'[^<]*</title></path>', svg)
    assert m, 'bar not found: ' + title_prefix
    x, base, top = m.group(1), m.group(2), m.group(3)
    new_tag = '<path d="M%s,%s V%s %s" fill="%s"><title>%s</title></path>' % (x, base, r1(new_value_top + 4), m.group(4), m.group(5), new_title)
    svg = svg.replace(m.group(0), new_tag)
    if new_label is not None:
        hm = re.search(r'H([\d.]+)', m.group(4))
        cx = r1((float(x) + float(hm.group(1)) + 4) / 2)
        lm = re.search(r'(<text class="lbl" text-anchor="middle" x="%s" y=")([^"]+)(">)([^<]*)(</text>)' % re.escape(cx), svg)
        assert lm, 'label not found at x=' + cx
        svg = svg[:lm.start()] + lm.group(1) + r1(new_value_top - 7) + lm.group(3) + new_label + lm.group(5) + svg[lm.end():]
    return svg
