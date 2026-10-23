"""Illinois Video Gambling Data page: August 2026 -> September 2026 (IGB posted 2026-10-23 pull)."""
import re
import sys; sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2]))
from common import *

# ---- figures (IGB statewide summary, pulled 2026-10-23) --------------------
SEP26 = dict(est=8800, vgt=50141, played=2996921850.44, nti=278448178.41, tax=97456256.5)
SEP25 = dict(est=8758, vgt=49552, nti=258268564.87)
AUG26 = dict(est=8755, vgt=49874, nti=286760000)  # for reference only
CY26 = dict(played=27594026670.33, nti=2555500257.03, tax=894420010.89, state=769481360.56, muni=124938650.33)  # Jan-Sep
CY25_9 = dict(nti=2372098590.63)

e = Edits('video-gambling')
B = e.body

nti_m = SEP26['nti'] / 1e6          # 278.448
yoy_nti = pct(SEP26['nti'], SEP25['nti'])          # +7.8%
yoy_vgt = SEP26['vgt'] - SEP25['vgt']               # 589
yoy_est = SEP26['est'] - SEP25['est']               # 42
cy_growth = pct(CY26['nti'], CY25_9['nti'])         # +7.7%
assert yoy_nti == '+7.8%' and cy_growth == '+7.7%', (yoy_nti, cy_growth)

# ---- lede / meta / provenance ------------------------------------------------
e.rep('world: nearly 50,000 slot-style machines in bars', 'world: more than 50,000 slot-style machines in bars')
e.rep('September 2012 through August 2026 (the latest month posted). Compiled and checked October 3, 2026.',
      'September 2012 through September 2026 (the latest month posted). Compiled and checked October 23, 2026.')
e.rep('<dt>Current through</dt><dd>August 2026</dd>', '<dt>Current through</dt><dd>September 2026</dd>')
e.rep('<dt>Last reviewed</dt><dd>October 3, 2026</dd>', '<dt>Last reviewed</dt><dd>October 23, 2026</dd>')

# ---- cards -------------------------------------------------------------------
e.rep('<div class="v">49,874</div><div class="d">+377 vs August 2025</div><div class="s">Statewide, August 2026</div>',
      '<div class="v">50,141</div><div class="d">+%d vs September 2025</div><div class="s">Statewide, September 2026 — the first month above 50,000</div>' % yoy_vgt)
e.rep('<div class="v">8,755</div><div class="d">+2 vs August 2025</div><div class="s">Bars, restaurants, gas stations, truck stops, fraternal clubs — August 2026</div>',
      '<div class="v">8,800</div><div class="d">+%d vs September 2025</div><div class="s">Bars, restaurants, gas stations, truck stops, fraternal clubs — September 2026</div>' % yoy_est)
e.rep('<div class="l">Net terminal income, August 2026</div><div class="v">$286.8M</div><div class="d">+5.8% vs August 2025</div>',
      '<div class="l">Net terminal income, September 2026</div><div class="v">%s</div><div class="d">%s vs September 2025</div>' % (money_m(nti_m), yoy_nti))
e.rep('No Chicago establishment appears in IGB revenue data through August 2026',
      'No Chicago establishment appears in IGB revenue data through September 2026')

# ---- growth section ----------------------------------------------------------
e.rep('What players lost on Illinois video gaming terminals, 2013–2026. 2026 is January–July only.',
      'What players lost on Illinois video gaming terminals, 2013–2026. 2026 is January–September only.')
e.rep('net terminal income grew 6.0% in 2025 and is running 7.7% ahead through August 2026.',
      'net terminal income grew 6.0% in 2025 and is running ' + cy_growth.lstrip('+') + ' ahead through September 2026. The terminal count passed 50,000 for the first time in September 2026.')

# CY NTI bars (t1604): 64.5 px per $1B, baseline 286
s = e.get_svg('t1604')
cy_b = CY26['nti'] / 1e9
top = 286 - 64.5 * cy_b
s = bar(s, '2026†: Net terminal income', '2026†: Net terminal income %s' % money_b(CY26['nti'] / 1e6), top, money_b(CY26['nti'] / 1e6))
s = s.replace('2026 shows January through July only.', '2026 shows January through September only.')
s = s.replace('†2026 is January–August only (8 months).', '†2026 is January–September only (9 months).')
assert '(9 months)' in s and 'through September only' in s
e.put_svg('t1604', s)

# monthly NTI line (t986): 0.64 px per $1M, baseline 280, Jan 2019 = x 56, 92 points -> 93
s = e.get_svg('t986')
new_y = 280 - 0.64 * nti_m
# September dipped below August, so the end label goes under the point (as on the sports charts in October)
s = extend_line(s, 56, 744, 92, new_y, 'Sep 2026: $%sM' % rn(nti_m, 0), '$%sM' % rn(nti_m, 0), 3.85, label_dy=18)
s = s.replace('Monthly net terminal income, January 2019 – August 2026', 'Monthly net terminal income, January 2019 – September 2026')
assert 'September 2026</title>' in s
e.put_svg('t986', s)

# year-end terminals (t1390) and locations (t4875) small multiples: 2026† bar = latest month
for tid, kind, old, new, old_top in (('t1390', 'Terminals', 49874, 50141, 64.7), ('t4875', 'Locations', 8755, 8800, 55.2)):
    s = e.get_svg(tid)
    new_top = 246 - (246 - old_top) * new / old
    s = bar(s, '2026†: %s' % kind, '2026†: %s %s' % (kind, comma(new)), new_top, comma(new))
    s = s.replace('%s in August 2026.' % comma(old), '%s in September 2026.' % comma(new))
    s = s.replace('†August 2026.', '†September 2026.')
    assert 'September 2026' in s and comma(old) not in s, tid
    e.put_svg(tid, s)

# ---- Chicago tracker -----------------------------------------------------------
e.rep('<b>Status as of August 2026 data: no City of Chicago establishment appears',
      '<b>Status as of September 2026 data: no City of Chicago establishment appears')
e.rep('<li><b>August 2026</b> — State-approved Chicago locations reach the dozens; city licenses not yet issued; no Chicago revenue reported.</li>',
      '<li><b>August 2026</b> — State-approved Chicago locations reach the dozens (42 licensed of 311 applications by late August); city licenses not yet issued; no Chicago revenue reported.</li> <li><b>September 2026</b> — Still no Chicago establishment in IGB revenue data; the city has not issued its own licenses, and the mayor\'s office has not sent the IGB the notification the ordinance requires.</li>')

# ---- self-exclusion verification date ----------------------------------------------
e.rep('Regulatory status last verified October 3, 2026.', 'Regulatory status last verified October 23, 2026.')

# ---- timeline -------------------------------------------------------------------------
e.rep('<li><b>September 2026</b> — IGB adopts a resolution to extend self-exclusion to video gaming terminals (no effective date) and proposes shorter self-exclusion terms and remote enrollment.</li>',
      '<li><b>September 2026</b> — IGB adopts a resolution to extend self-exclusion to video gaming terminals (no effective date) and proposes shorter self-exclusion terms and remote enrollment. The statewide terminal count passes 50,000 (50,141) for the first time.</li>')

# ---- data table: CY 2026 row ----------------------------------------------------------------
e.rep('<tr><td>2026 (Jan–Aug)</td><td>8,755</td><td>49,874</td><td>$24.60B</td><td>$2.277B</td><td>$797M</td><td>$686M</td><td>$111M</td></tr>',
      '<tr><td>2026 (Jan–Sep)</td><td>8,800</td><td>50,141</td><td>%s</td><td>%s</td><td>$%sM</td><td>$%sM</td><td>$%sM</td></tr>' % (
          money_b(CY26['played'] / 1e6), money_b(CY26['nti'] / 1e6, 3), rn(CY26['tax'] / 1e6, 0), rn(CY26['state'] / 1e6, 0), rn(CY26['muni'] / 1e6, 0)))

# ---- methodology --------------------------------------------------------------------------------
e.rep('retrieved October 3, 2026. The IGB publishes each month\'s figures at the end of the following month; the latest month here is August 2026.',
      'retrieved October 23, 2026. The IGB publishes each month\'s figures at the end of the following month; the latest month here is September 2026.')
e.save()
print('card NTI', money_m(nti_m), yoy_nti, '| CY', money_b(CY26['nti']/1e6), money_b(CY26['nti']/1e6,3), money_b(CY26['played']/1e6), rn(CY26['tax']/1e6,0), rn(CY26['state']/1e6,0), rn(CY26['muni']/1e6,0), '| line y', r1(new_y))
