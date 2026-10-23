"""Illinois Gambling Statistics hub: terminal count and review dates (FY figures unchanged)."""
import sys; sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2]))
from common import *

e = Edits('illinois')
e.rep('Compiled and checked October 9, 2026. Updated quarterly.', 'Compiled and checked October 23, 2026. Updated quarterly.')
e.rep('<dt>Last reviewed</dt><dd>October 9, 2026</dd>', '<dt>Last reviewed</dt><dd>October 23, 2026</dd>')
e.rep('<div class="s">49,874 terminals at 8,755 locations (Aug 2026)</div>', '<div class="s">50,141 terminals at 8,800 locations (Sep 2026)</div>')
e.rep('32,033 terminals at the end of FY2019; 49,874 in August 2026.', '32,033 terminals at the end of FY2019; 50,141 in September 2026, the first month above 50,000.')
e.rep('Chicago lifted its ban in December 2025 but no city location had reported revenue through August 2026.',
      'Chicago lifted its ban in December 2025 but no city location had reported revenue through September 2026.')
e.save()
