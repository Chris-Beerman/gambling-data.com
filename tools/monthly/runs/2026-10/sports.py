"""Illinois Sports Betting Data page: July 2026 -> August 2026 (IGB pull 2026-10-23)."""
import re
import sys; sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2]))
from common import *

AUG = dict(handle=1013471011, bets=20220556, agr=76322466, onH=998302233, t2H=701688238, stTax=19182052, wTax=5091403)
AUG25 = dict(handle=1008134449, bets=21046972)
CY = dict(handle=9495232652, bets=191380784, agr=908453237, onH=9328707911, t2H=6418432768, stTax=295721507, wTax=74944654)   # Jan-Aug 2026
L12 = dict(handle=15594421560, bets=319425057, agr=1475123862, onH=15285494487, t2H=10198532492)                              # Sep 2025 - Aug 2026
OPS = [  # brand, master licensee (table), online AGR, online handle — twelve months to August 2026
    ('FanDuel', 'Fairmount Park', 520072745, 4429627030),
    ('DraftKings', 'Casino Queen', 502879348, 5579892158),
    ('Fanatics', 'Hawthorne, then Argosy Alton (Jan 2026)', 114820382, 1381516784),
    ('bet365', "Walker's Bluff", 69759502, 769875241),
    ('BetMGM', 'Par-A-Dice, East Peoria', 69343614, 895774963),
    ('BetRivers', 'Rivers Des Plaines', 66466983, 734182730),
    ('Caesars', 'Grand Victoria, Elgin', 45068511, 637682970),
    ('Hard Rock Bet', 'Hard Rock Rockford', 31410242, 291182883),
    ('theScore Bet', 'Hollywood Aurora (ESPN Bet to Dec 2025)', 29278631, 437373834),
    ('Bally Bet', "Bally's Quad Cities (from Jun 2026)", 853057, 6105882),
    ('Circa Sports', 'American Place, Waukegan', 798694, 122280013),
]

e = Edits('sports-betting')

h_b = AUG['handle'] / 1e9
yoy = pct(AUG['handle'], AUG25['handle'])                      # +0.5%
cy_hold = CY['agr'] / CY['handle'] * 100                       # 9.57
cy_online = CY['onH'] / CY['handle'] * 100                     # 98.25
cy_t2 = CY['t2H'] / CY['handle'] * 100                         # 67.60
cy_tax = (CY['stTax'] + CY['wTax']) / 1e6                      # 370.7
l12_online = L12['onH'] / L12['handle'] * 100                  # 98.02
l12_t2 = L12['t2H'] / L12['handle'] * 100                      # 65.40
l12_avg = L12['handle'] / L12['bets']                          # 48.82
cy_avg = CY['handle'] / CY['bets']                             # 49.61
aug_avg = AUG['handle'] / AUG['bets']                          # 50.12
assert yoy == '+0.5%' and rn(cy_hold, 1) == '9.6' and rn(cy_online, 1) == '98.2' and rn(l12_online, 1) == '98.0' and rn(l12_t2, 0) == '65' and rn(l12_avg, 0) == '49' and rn(cy_avg, 0) == '50' and rn(aug_avg, 0) == '50', (yoy, cy_hold, cy_online, l12_online, l12_t2, l12_avg, cy_avg, aug_avg)

# ---- meta / provenance ---------------------------------------------------------
e.rep('March 2020 through July 2026 (the latest month posted). Compiled and checked October 3, 2026.',
      'March 2020 through August 2026 (the latest month posted). Compiled and checked October 23, 2026.')
e.rep('<dt>Current through</dt><dd>July 2026</dd>', '<dt>Current through</dt><dd>August 2026</dd>')
e.rep('<dt>Last reviewed</dt><dd>October 3, 2026</dd>', '<dt>Last reviewed</dt><dd>October 23, 2026</dd>')

# ---- cards -----------------------------------------------------------------------
e.rep('<div class="s">Share of handle, August 2025 – July 2026</div>', '<div class="s">Share of handle, September 2025 – August 2026</div>')
e.rep('<div class="l">Handle, July 2026</div><div class="v">$1.04B</div><div class="d">+22.7% vs July 2025</div>',
      '<div class="l">Handle, August 2026</div><div class="v">%s</div><div class="d">%s vs August 2025</div>' % (money_b(AUG['handle'] / 1e6), yoy))

# ---- growth -----------------------------------------------------------------------
e.rep('<figcaption>Monthly handle, March 2020 – July 2026<span>', '<figcaption>Monthly handle, March 2020 – August 2026<span>')
e.rep('Adjusted gross receipts — what bettors lost. 2026 is January–July only.', 'Adjusted gross receipts — what bettors lost. 2026 is January–August only.')

s = e.get_svg('t9585')   # handle line: 128 px per $1B, baseline 280; 77 months Mar 2020 - Jul 2026 -> 78
s = extend_line(s, 56, 744, 77, 280 - 128 * h_b, 'Aug 2026: %s' % money_b(AUG['handle'] / 1e6), money_b(AUG['handle'] / 1e6), 4.5, label_dy=20)
s = s.replace('handle by month, March 2020 – July 2026', 'handle by month, March 2020 – August 2026')
s = s.replace('July 2026 handle was $1.04B.', 'August 2026 handle was %s.' % money_b(AUG['handle'] / 1e6))
assert 'August 2026 handle was' in s
e.put_svg('t9585', s)

s = e.get_svg('t2197')   # AGR by CY: 172 px per $1B, baseline 286
agr_b = CY['agr'] / 1e9
s = bar(s, '2026: AGR', '2026: AGR %s' % money_b(CY['agr'] / 1e6), 286 - 172 * agr_b, money_b(CY['agr'] / 1e6))
s = s.replace('2026 shows January–July only.', '2026 shows January–August only.').replace('2026 = January–July only (lighter).', '2026 = January–August only (lighter).')
assert s.count('January–August') == 2
e.put_svg('t2197', s)

s = e.get_svg('t9600')   # hold by CY: 19.8 px per point, baseline 226
s = bar(s, '2026: Hold', '2026: Hold %s%%' % rn(cy_hold, 1), 226 - 19.8 * cy_hold, '%s%%' % rn(cy_hold, 1))
s = s.replace('2026 is January–July.', '2026 is January–August.')
assert 'January–August' in s
e.put_svg('t9600', s)

# ---- bets section --------------------------------------------------------------------
e.rep('The average bet is small: $49 in the year to July 2026.', 'The average bet is small: $%s in the year to August 2026.' % rn(l12_avg, 0))
e.rep('<b>98.0%</b> of Illinois handle in the year to July 2026 was placed online.', '<b>%s%%</b> of Illinois handle in the year to August 2026 was placed online.' % rn(l12_online, 1))

s = e.get_svg('t7400')   # bets per month: 256/60 px per million, baseline 280
bets_m = AUG['bets'] / 1e6
s = extend_line(s, 56, 744, 77, 280 - 256 / 60 * bets_m, 'Aug 2026: %sM' % rn(bets_m, 1), '%sM' % rn(bets_m, 1), 4.5, label_dy=20)
s = s.replace('July 2026 had 21.6 million.', 'August 2026 had %s million.' % rn(bets_m, 1))
assert 'August 2026 had' in s
e.put_svg('t7400', s)

s = e.get_svg('t320')    # average bet: 196/60 px per $, baseline 220
s = extend_line(s, 56, 744, 77, 220 - 196 / 60 * aug_avg, 'Aug 2026: $%s' % rn(aug_avg, 0), '$%s' % rn(aug_avg, 0), 4.5, label_dy=-10)
s = s.replace('$50 in January–July 2026', '$%s in January–August 2026' % rn(cy_avg, 0))
assert 'January–August 2026' in s
e.put_svg('t320', s)

s = e.get_svg('t5624')   # Tier 2 share by CY: 2.475 px per point, baseline 226
s = bar(s, '2026: Tier 2 share', '2026: Tier 2 share %s%%' % rn(cy_t2, 1), 226 - 2.475 * cy_t2, '%s%%' % rn(cy_t2, 1))
e.put_svg('t5624', s)

# ---- operators --------------------------------------------------------------------------
e.rep('<figcaption>Online sportsbook revenue by operator, August 2025 – July 2026<span>', '<figcaption>Online sportsbook revenue by operator, September 2025 – August 2026<span>')
e.rep('<small>Twelve months to July 2026, online only.</small>', '<small>Twelve months to August 2026, online only.</small>')
tot = sum(o[2] for o in OPS)
PX = 520 / 523.94
rows = []
n = len(OPS)
parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 %d" role="img" aria-labelledby="t2007 d2007" class="cat-igd-chart">' % (12 + 26 * n + 4),
         '<title id="t2007">Online sportsbook revenue by operator, September 2025 – August 2026</title>',
         '<desc id="d2007">FanDuel took %s%% and DraftKings %s%% of Illinois online sportsbook revenue in the twelve months to August 2026; %s other brands shared the rest.</desc>' % (rn(OPS[0][2] / tot * 100, 0), rn(OPS[1][2] / tot * 100, 0), 'nine' if n == 11 else str(n - 2))]
for i, (brand, lic, a, h) in enumerate(OPS):
    y = 12 + 26 * i
    a_m = a / 1e6
    w = a_m * PX
    H = r1(170 + w - 4)
    share = rn(a / tot * 100, 1)
    parts.append('<text x="160" y="%s" text-anchor="end" class="cat">%s</text>' % (r1(y + 13), brand))
    parts.append('<path d="M170,%s H%s a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 H170 Z" fill="#3E7CA6"><title>%s: $%sM — %s%% of online AGR; handle %s</title></path>' % (r1(y), H, brand, rn(a_m, 0), share, money_b(h / 1e6)))
    parts.append('<text x="%s" y="%s" class="lbl">$%sM</text>' % (r1(170 + w + 8), r1(y + 13), rn(a_m, 0)))
    rows.append('<tr><td>%s</td><td>%s</td><td>$%sM</td><td>%s%%</td><td>%s</td></tr>' % (brand, lic, rn(a_m, 1), share, money_b(h / 1e6)))
parts.append('</svg>')
e.put_svg('t2007', ''.join(parts))

old_tbody = re.search(r'(<tbody><tr><td>FanDuel</td>[\s\S]*?</tbody>)', e.body)
assert old_tbody and old_tbody.group(1).count('<tr>') == 10
e.rep(old_tbody.group(1), '<tbody>' + ''.join(rows) + '</tbody>')
e.rep('Fanatics moved from Hawthorne Race Course to Argosy Casino Alton after Hawthorne\'s racing licence was suspended in January 2026. Bally Bet launched in June 2026.</small>',
      'Fanatics moved from Hawthorne Race Course to Argosy Casino Alton after Hawthorne\'s racing licence was suspended in January 2026. Bally Bet launched in June 2026 and is shown for the three months it has reported.</small>')

# ---- taxes paragraph -----------------------------------------------------------------------
e.rep('jumped to $44 in 2025 and $50 in January–July 2026.', 'jumped to $44 in 2025 and $%s in January–August 2026.' % rn(cy_avg, 0))

# ---- tables ---------------------------------------------------------------------------------
e.rep('<tr><td>2026</td><td>7</td><td>$8.48B</td><td>171.2M</td><td>$832M</td><td>9.8%</td><td>98.2%</td><td>$346M</td></tr>',
      '<tr><td>2026</td><td>8</td><td>%s</td><td>%sM</td><td>$%sM</td><td>%s%%</td><td>%s%%</td><td>$%sM</td></tr>' % (
          money_b(CY['handle'] / 1e6), rn(CY['bets'] / 1e6, 1), rn(CY['agr'] / 1e6, 0), rn(cy_hold, 1), rn(cy_online, 1), rn(cy_tax, 0)))
e.rep('2026 runs January–July; FY2026 is complete', '2026 runs January–August; FY2026 is complete')

# ---- methodology -------------------------------------------------------------------------------
e.rep('retrieved October 3, 2026. The latest month posted is July 2026. Fiscal-year AGR reconciles to the Commission on Government Forecasting and Accountability\'s <em>Wagering in Illinois: 2025 Update</em> within 0.1%.',
      'retrieved October 23, 2026. The latest month posted is August 2026. Fiscal-year AGR reconciles to the Commission on Government Forecasting and Accountability\'s <em>Wagering in Illinois: 2026 Update</em> within 0.1%.')
e.rep('for the twelve months to June 2026, mapped to brands', 'for the twelve months to August 2026, mapped to brands')

e.save()
print('Aug handle', money_b(AUG['handle']/1e6), yoy, '| CY', money_b(CY['handle']/1e6), rn(CY['bets']/1e6,1), rn(CY['agr']/1e6,0), rn(cy_hold,1), rn(cy_online,1), rn(cy_tax,0), rn(cy_t2,1), '| L12', rn(l12_online,1), rn(l12_t2,1), rn(l12_avg,2), '| aug avg', rn(aug_avg,2), 'bets', rn(bets_m,2))
