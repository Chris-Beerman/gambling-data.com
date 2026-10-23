"""Illinois Casino Data page: August 2026 -> September 2026 (IGB Casino Summary, pulled 2026-10-23)."""
import re
import sys; sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2]))
from common import *

SEP26 = dict(agr=178171046.07, adm=1343362, state=45611833.46, local=11319221.98)
SEP25 = dict(agr=158085250.57, adm=1294711)
CY26 = dict(agr=1626791411.32, adm=12089981, state=314920843.29, local=100104161.3, table=390484650.77)   # Jan-Sep 2026
CY25_9 = dict(agr=1454.1e6)   # Jan-Sep 2025 (from the Oct 23 pull, $M)

e = Edits('casinos')

agr_m = SEP26['agr'] / 1e6               # 178.17
yoy = pct(SEP26['agr'], SEP25['agr'])    # +12.7%
cy_m = CY26['agr'] / 1e6                 # 1626.8
cy_yoy = pct(CY26['agr'], CY25_9['agr']) # +11.9%
adm_m = CY26['adm'] / 1e6                # 12.09
per_adm = CY26['agr'] / CY26['adm']      # 134.56
table_share = CY26['table'] / CY26['agr'] * 100   # 24.0
assert yoy == '+12.7%' and cy_yoy == '+11.9%' and rn(per_adm, 0) == '135', (yoy, cy_yoy, per_adm)

# ---- meta / provenance ----------------------------------------------------------
e.rep('July 2020 through August 2026 (the latest month posted), with FY2013 to FY2020 totals from the Commission on Government Forecasting and Accountability. Compiled and checked October 3, 2026.',
      'July 2020 through September 2026 (the latest month posted), with FY2013 to FY2020 totals from the Commission on Government Forecasting and Accountability. Compiled and checked October 23, 2026.')
e.rep('<dt>Current through</dt><dd>August 2026</dd>', '<dt>Current through</dt><dd>September 2026</dd>')
e.rep('<dt>Last reviewed</dt><dd>October 3, 2026</dd>', '<dt>Last reviewed</dt><dd>October 23, 2026</dd>')

# ---- cards ------------------------------------------------------------------------
e.rep('<div class="l">Lost at Illinois casinos, August 2026</div><div class="v">$192.8M</div><div class="d">+10.8% vs August 2025</div><div class="s">Latest month posted. Tied with May 2026 as the highest month since July 2020.</div>',
      '<div class="l">Lost at Illinois casinos, September 2026</div><div class="v">%s</div><div class="d">%s vs September 2025</div><div class="s">Latest month posted. The highest months since July 2020 remain May and August 2026, $192.8M each.</div>' % (money_m(agr_m), yoy))
e.rep('<div class="l">Calendar 2026 so far</div><div class="v">$1.45B</div><div class="d">+11.8% vs Jan–Aug 2025</div><div class="s">January – August 2026</div>',
      '<div class="l">Calendar 2026 so far</div><div class="v">%s</div><div class="d">%s vs Jan–Sep 2025</div><div class="s">January – September 2026</div>' % (money_b(cy_m), cy_yoy))

# ---- monthly AGR line (t102): 1.21 px per $1M, baseline 266, Jul 2020 = x 56, 74 points -> 75 ------
s = e.get_svg('t102')
n_old, n_new = 74, 75
step_old, step_new = 688 / (n_old - 1), 688 / (n_new - 1)
idx = lambda x: int(round((x - 56) / step_old))
nx = lambda i: 56 + i * step_new
new_y = 266 - 1.21 * agr_m
# polyline
m = re.search(r'(<polyline[^>]*points=")([^"]+)(")', s)
pts = [p.split(',') for p in m.group(2).split()]
assert len(pts) == n_old
pts = ['%s,%s' % (r1(nx(idx(float(x)))), y) for x, y in pts] + ['%s,%s' % (r1(nx(n_new - 1)), r1(new_y))]
s = s[:m.start(2)] + ' '.join(pts) + s[m.end(2):]
# hover circles
def fix_circle(mm):
    tag = mm.group(0)
    if 'fill="transparent"' not in tag:
        return tag
    cx = re.search(r'cx="([^"]+)"', tag).group(1)
    return tag.replace('cx="%s"' % cx, 'cx="%s"' % r1(nx(idx(float(cx)))))
s = re.sub(r'<circle[^>]*>', fix_circle, s)
hov = list(re.finditer(r'<circle cx="[^"]+" cy="[^"]+" fill="transparent" r="5"><title>[^<]*</title></circle>', s))
assert len(hov) == n_old
h = hov[-1]
s = s[:h.end()] + '<circle cx="%s" cy="%s" fill="transparent" r="5"><title>Sep 2026: %s</title></circle>' % (r1(nx(n_new - 1)), r1(new_y), money_m(agr_m)) + s[h.end():]
# shaded closure rect: x and width scale with the axis
rm = re.search(r'<rect fill="#eef3f6" height="242.0" width="([^"]+)" x="([^"]+)" y="24.0">', s)
assert rm
s = s.replace(rm.group(0), '<rect fill="#eef3f6" height="242.0" width="%s" x="%s" y="24.0">' % (r1(float(rm.group(1)) * step_new / step_old), r1(56 + (float(rm.group(2)) - 56) * step_new / step_old)))
# year labels
s = re.sub(r'(<text class="ax" text-anchor="middle" x=")([^"]+)(" y="284.0">\d{4}</text>)', lambda mm: mm.group(1) + r1(nx(idx(float(mm.group(2))))) + mm.group(3), s)
# end dot and label (September dipped below August, so the label goes under the point)
em = re.search(r'<circle cx="744.0" cy="([^"]+)" fill="#17435C" r="3.5">', s)
assert em
s = s.replace(em.group(0), '<circle cx="744.0" cy="%s" fill="#17435C" r="3.5">' % r1(new_y))
lm = re.search(r'<text class="lbl" text-anchor="end" x="738.0" y="([^"]+)">\$193M</text>', s)
assert lm
s = s.replace(lm.group(0), '<text class="lbl" text-anchor="end" x="738.0" y="%s">$%sM</text>' % (r1(new_y + 16), rn(agr_m, 0)))
s = s.replace('by month, July 2020 to August 2026', 'by month, July 2020 to September 2026')
s = s.replace('to about $193 million in May and August 2026.', 'to about $193 million in May and August 2026; September 2026 was $%s million.' % rn(agr_m, 0))
assert 'September 2026 was' in s and 'to September 2026</title>' in s
e.put_svg('t102', s)

# ---- admissions (t105) and AGR per admission (t106) 2026† bars: 12.9 px per M / 1.29 px per $, baseline 286 ------
s = e.get_svg('t105')
s = bar(s, '2026†:', '2026†: %sM' % rn(adm_m, 2), 286 - 12.9 * adm_m, '%sM' % rn(adm_m, 1))
s = s.replace('†2026 is January to August only.', '†2026 is January to September only.')
assert 'January to September' in s
e.put_svg('t105', s)
s = e.get_svg('t106')
s = bar(s, '2026†:', '2026†: $%s' % rn(per_adm, 0), 286 - 1.29 * per_adm, '$%s' % rn(per_adm, 0))
s = s.replace('†2026 is January to August only.', '†2026 is January to September only.')
s = s.replace('then rose to $135 in January to August 2026.', 'then rose to $%s in January to September 2026.' % rn(per_adm, 0))
assert s.count('January to September') == 2
e.put_svg('t106', s)

# ---- tables -----------------------------------------------------------------------------
e.rep('<tr><td>2026 (Jan–Aug)</td><td>8</td><td>$1,448.6M</td><td>23.9%</td><td>10.75M</td><td>$135</td><td>$269.3M</td><td>$88.8M</td></tr>',
      '<tr><td>2026 (Jan–Sep)</td><td>9</td><td>$%s</td><td>%s%%</td><td>%sM</td><td>$%s</td><td>$%sM</td><td>$%sM</td></tr>' % (
          '{:,.1f}M'.format(cy_m), rn(table_share, 1), rn(adm_m, 2), rn(per_adm, 0), rn(CY26['state'] / 1e6, 1), rn(CY26['local'] / 1e6, 1)))

# ---- methodology ---------------------------------------------------------------------------
e.rep('July 2020 through August 2026, retrieved October 3, 2026.', 'July 2020 through September 2026, retrieved October 23, 2026.')

e.save()
print('Sep', money_m(agr_m), yoy, '| CY', money_b(cy_m), cy_yoy, '{:,.1f}'.format(cy_m), rn(table_share,1), rn(adm_m,2), rn(per_adm,1), rn(CY26['state']/1e6,1), rn(CY26['local']/1e6,1), '| line y', r1(new_y))
