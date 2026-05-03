"""
🎻 Q2D1 EURO PATTERN AUDIT — Session 32 housekeeping
=====================================================
Score every coded pattern across the Q2D1 window
(07.04.2026 → 01.05.2026, 8 Euro BD→ND pairs).

Output: 🟢 ALIVE / 🟡 MUTED / 🔴 DEAD WEIGHT
"""
import os
import sys
from collections import defaultdict
from datetime import datetime
from typing import Callable, Dict, List

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv('/app/backend/.env')
client = MongoClient(os.environ['MONGO_URL'])
db = client[os.environ['DB_NAME']]
sys.path.insert(0, '/app/backend')


def parse_date(s):
    try:
        return datetime.strptime(s, '%d.%m.%Y')
    except:  # noqa: E722
        return datetime.min


# ════════════════════════════════════════════════════════════
# Build BD→ND window
# ════════════════════════════════════════════════════════════
all_euro = list(db.euromillions_draws.find({}, {'_id': 0}))
all_euro.sort(key=lambda x: parse_date(x.get('date', '')))

WINDOW_START = datetime(2026, 4, 7)
WINDOW_END = datetime(2026, 5, 1)

# Pairs: (BD, ND) where ND.date is in window
pairs = []
for i in range(1, len(all_euro)):
    nd = all_euro[i]
    nd_date = parse_date(nd['date'])
    if WINDOW_START <= nd_date <= WINDOW_END:
        pairs.append((all_euro[i - 1], nd))

print(f"\n🎻 Q2D1 EURO AUDIT — {len(pairs)} BD→ND pairs in window")
print(f"   {WINDOW_START.date()} → {WINDOW_END.date()}\n")
for bd, nd in pairs:
    print(f"   {bd['date']} {sorted(bd['numbers'])} → "
          f"{nd['date']} {sorted(nd['numbers'])}")
print()


# ════════════════════════════════════════════════════════════
# Pattern definitions — each returns a SET of predicted mains
# given (bd_mains, bd_stars, nd_date, history)
# ════════════════════════════════════════════════════════════
EURO_MAX = 50
CIRCLE = 25  # Euro 25-wheel
FOLD = 13    # Euro fold-axis


def _flip(n):
    s = str(n).zfill(2)
    f = int(s[::-1])
    return f if f > 0 else n


def _flip_wrap(n):
    f = _flip(n)
    if f == 0:
        return n
    return f if f <= EURO_MAX else f - EURO_MAX


def _circle(n):
    """1↔26 type wheel-twin (n + 25)."""
    out = n + CIRCLE
    return out if out <= EURO_MAX else out - EURO_MAX


def _inner_circle(n):
    """n shifted by half-circle (12)."""
    a = n + 12
    if a > EURO_MAX:
        a -= EURO_MAX
    return a


def _fold_mirror(n):
    """Reflection across the 13-axis (1↔25, 2↔24, ...)."""
    return CIRCLE + 1 - n if 1 <= n <= CIRCLE else CIRCLE + 51 - n


def _date_digits(d: datetime):
    s = d.strftime('%d%m%Y')
    out = set()
    # individual digits not useful (1-9 only); two-digit pairs
    for i in range(len(s) - 1):
        try:
            v = int(s[i:i + 2])
            if 1 <= v <= EURO_MAX:
                out.add(v)
        except ValueError:
            pass
    # day, month, last2 of year
    try:
        out.add(d.day)
        out.add(d.month)
        out.add(d.year % 100)
    except Exception:
        pass
    return {v for v in out if 1 <= v <= EURO_MAX}


def _digit_sum(n):
    return sum(int(c) for c in str(n))


# ════════════════════════════════════════════════════════════
# Each lens: bd_mains, bd_stars, nd_date  →  predicted mains set
# ════════════════════════════════════════════════════════════
def lens_raw_carry(bd_mains, bd_stars, nd_date):
    return set(bd_mains)


def lens_flip(bd_mains, bd_stars, nd_date):
    return {_flip(n) for n in bd_mains if _flip(n) <= EURO_MAX and _flip(n) >= 1}


def lens_flip_wrap(bd_mains, bd_stars, nd_date):
    return {_flip_wrap(n) for n in bd_mains}


def lens_circle25(bd_mains, bd_stars, nd_date):
    """Euro 25-wheel twin (n + 25)."""
    return {_circle(n) for n in bd_mains}


def lens_inner_circle(bd_mains, bd_stars, nd_date):
    return {_inner_circle(n) for n in bd_mains}


def lens_fold_mirror(bd_mains, bd_stars, nd_date):
    """13-axis fold mirror (DJ's session 32 theory)."""
    out = set()
    for n in bd_mains:
        m = _fold_mirror(n)
        if 1 <= m <= EURO_MAX:
            out.add(m)
    return out


def lens_p1_echo_triad(bd_mains, bd_stars, nd_date):
    """🎻 DJ Law candidate: P1's three faces (raw, circle25, fold)."""
    p1 = sorted(bd_mains)[0]
    out = {p1, _circle(p1)}
    out.add(_fold_mirror(p1))
    out.discard(0)
    return {n for n in out if 1 <= n <= EURO_MAX}


def lens_date_target(bd_mains, bd_stars, nd_date):
    return _date_digits(nd_date)


def lens_sum_circle(bd_mains, bd_stars, nd_date):
    """Pairwise sums reduced into Euro circle."""
    out = set()
    for i, a in enumerate(bd_mains):
        for b in bd_mains[i + 1:]:
            s = a + b
            while s > EURO_MAX:
                s -= EURO_MAX
            if s >= 1:
                out.add(s)
    return out


def lens_digit_sum_echo(bd_mains, bd_stars, nd_date):
    """digit-sum of each BD main as next candidate."""
    return {_digit_sum(n) for n in bd_mains
            if 1 <= _digit_sum(n) <= EURO_MAX}


def lens_neighbor_walk(bd_mains, bd_stars, nd_date):
    """n±1 from each BD main."""
    out = set()
    for n in bd_mains:
        for d in (-1, 1):
            v = n + d
            if 1 <= v <= EURO_MAX:
                out.add(v)
    return out


def lens_huge_p5_echo(bd_mains, bd_stars, nd_date):
    """+21 Swiss-circle twins (HUGE-Twin idea ported to Euro)."""
    out = set()
    for n in bd_mains:
        v = n + 21
        if 1 <= v <= EURO_MAX:
            out.add(v)
        v = n - 21
        if 1 <= v <= EURO_MAX:
            out.add(v)
    return out


def lens_dj_pin(bd_mains, bd_stars, nd_date):
    """DJ-Pin Law 73 (Euro pins: 16, 19, 26)."""
    return {16, 19, 26}


def lens_welcome_companion(bd_mains, bd_stars, nd_date):
    """16 → {17,19}, 19 → {17,21}, 26 → {25,27}."""
    welcome = {16: {17, 19}, 19: {17, 21}, 26: {25, 27}}
    out = set()
    for pin in (16, 19, 26):
        out |= welcome.get(pin, set())
    return out


def lens_sneaky_inverse(bd_mains, bd_stars, nd_date):
    """Sneaky-Universe: BD-fired same-day-of-month is BLOCKED for ND.
    Predicts the COMPLEMENT — numbers NOT in BD."""
    return {n for n in range(1, EURO_MAX + 1) if n not in bd_mains}


def lens_product_door(bd_mains, bd_stars, nd_date):
    """Day-digit product: e.g. day=14 → 1×4=4 enters the pool."""
    day = nd_date.day
    digits = [int(c) for c in str(day) if c != '0']
    if len(digits) < 2:
        return set()
    prod = 1
    for d in digits:
        prod *= d
    out = set()
    if 1 <= prod <= EURO_MAX:
        out.add(prod)
    # also the day itself
    if 1 <= day <= EURO_MAX:
        out.add(day)
    return out


def lens_hold_fatigue_skip(bd_mains, bd_stars, nd_date):
    """Law 77: numbers fired 2+ times in last 3 draws → SUPPRESSED.
    Predicts ALL numbers MINUS the fatigued ones."""
    nd_idx = next((i for i, d in enumerate(all_euro)
                   if d['date'] == bd_mains[-1] or
                   parse_date(d['date']) == nd_date), None)
    # Simplified: get last 3 draws ending at BD
    bd_idx = None
    for i, d in enumerate(all_euro):
        if sorted(d['numbers']) == sorted(bd_mains):
            bd_idx = i
            break
    if bd_idx is None or bd_idx < 2:
        return set(range(1, EURO_MAX + 1))
    last3 = all_euro[bd_idx - 2: bd_idx + 1]
    cnt = defaultdict(int)
    for d in last3:
        for n in d['numbers']:
            cnt[n] += 1
    fatigued = {n for n, c in cnt.items() if c >= 2}
    return {n for n in range(1, EURO_MAX + 1) if n not in fatigued}


def lens_snap_back(bd_mains, bd_stars, nd_date):
    """Snap-back: when BD has P1≥14 (front collapse signal) →
    next mains favor low P1∈{1..5}, P2∈{10..13}."""
    if min(bd_mains) >= 14:
        return {1, 2, 3, 4, 5, 10, 11, 12, 13}
    return set()


def lens_target_spiral_v2(bd_mains, bd_stars, nd_date):
    """Each ND date hides numerical doors via day×month, day+month, etc."""
    d, m = nd_date.day, nd_date.month
    out = {d * m, d + m, abs(d - m)}
    if d * 2 <= EURO_MAX:
        out.add(d * 2)
    if m * 7 <= EURO_MAX:
        out.add(m * 7)
    return {n for n in out if 1 <= n <= EURO_MAX}


# ════════════════════════════════════════════════════════════
# Lens registry — pattern_name → callable
# ════════════════════════════════════════════════════════════
PATTERNS: Dict[str, Callable] = {
    'raw-carry-over': lens_raw_carry,
    'flip(n)': lens_flip,
    'flip-wrap(n)': lens_flip_wrap,
    'circle25 (1↔26 wheel-twin)': lens_circle25,
    'inner-circle(±12)': lens_inner_circle,
    'fold-mirror (13-axis)': lens_fold_mirror,
    '🎻 P1-Echo Triad (DJ law)': lens_p1_echo_triad,
    'date-target': lens_date_target,
    'sum-circle (pair sums)': lens_sum_circle,
    'digit-sum echo': lens_digit_sum_echo,
    'neighbor-walk (n±1)': lens_neighbor_walk,
    'HUGE-twin (+21)': lens_huge_p5_echo,
    'DJ-Pin (16,19,26)': lens_dj_pin,
    'Welcome-Companion': lens_welcome_companion,
    'Sneaky-Universe (inverse)': lens_sneaky_inverse,
    'Product-Door': lens_product_door,
    'Hold-Fatigue (Law 77)': lens_hold_fatigue_skip,
    'Snap-Back': lens_snap_back,
    'Target-Spiral v2': lens_target_spiral_v2,
}


# ════════════════════════════════════════════════════════════
# Score each pattern across the window
# ════════════════════════════════════════════════════════════
def score_pattern(name: str, fn: Callable):
    """Return dict: total_predicted, mains_hit, expected_baseline, lift."""
    total_pred = 0
    total_hit = 0
    per_draw = []
    for bd, nd in pairs:
        bd_mains = sorted(bd['numbers'])
        bd_stars = sorted(bd.get('stars', []))
        nd_mains = set(nd['numbers'])
        nd_date = parse_date(nd['date'])
        try:
            pred = fn(bd_mains, bd_stars, nd_date)
        except Exception as e:  # noqa: BLE001
            return {'name': name, 'error': str(e)}
        # Don't count predictions outside 1-50
        pred = {n for n in pred if 1 <= n <= EURO_MAX}
        if not pred:
            per_draw.append((bd['date'], nd['date'], 0, 0, 0.0))
            continue
        hits = pred & nd_mains
        total_pred += len(pred)
        total_hit += len(hits)
        per_draw.append((bd['date'], nd['date'], len(pred),
                         len(hits), len(hits) / len(pred)))
    if total_pred == 0:
        return {'name': name, 'never_fired': True}
    # Baseline: random pick from 50 → P(any in nd_mains) = 5/50 = 10%
    baseline = total_pred * (5 / EURO_MAX)
    actual_rate = total_hit / total_pred
    lift = (actual_rate - 0.10) / 0.10 * 100  # pct lift over baseline
    return {
        'name': name,
        'total_pred': total_pred,
        'total_hit': total_hit,
        'expected_hit': baseline,
        'hit_rate': actual_rate,
        'lift_pct': lift,
        'per_draw': per_draw,
    }


results = [score_pattern(n, fn) for n, fn in PATTERNS.items()]

# ════════════════════════════════════════════════════════════
# Render report
# ════════════════════════════════════════════════════════════
def tier(lift):
    if lift >= 20:
        return '🟢 ALIVE'
    if lift >= -20:
        return '🟡 MUTED'
    return '🔴 DEAD'


print('=' * 70)
print('🎻 PATTERN AUDIT REPORT — Q2D1 EURO (07.04 → 01.05, 8 pairs)')
print('=' * 70)
valid = [r for r in results if 'lift_pct' in r]
valid.sort(key=lambda r: -r['lift_pct'])

for r in valid:
    t = tier(r['lift_pct'])
    print(f"\n{t}  {r['name']}")
    print(f"   Predicted total: {r['total_pred']}  |  "
          f"Mains hit: {r['total_hit']}  |  "
          f"Expected (baseline): {r['expected_hit']:.1f}")
    print(f"   Hit-rate: {r['hit_rate']*100:.1f}%   "
          f"Lift over baseline: {r['lift_pct']:+.1f}%")

# Patterns that never fired
silent = [r for r in results if r.get('never_fired')]
if silent:
    print('\n' + '=' * 70)
    print('⚪ NEVER FIRED in this window:')
    for r in silent:
        print(f"   {r['name']}")

# Errors
errs = [r for r in results if r.get('error')]
if errs:
    print('\n⚠️  errors:')
    for r in errs:
        print(f"   {r['name']}: {r['error']}")

# Summary tally
print('\n' + '=' * 70)
print('🎯 TIER TALLY')
green = [r for r in valid if r['lift_pct'] >= 20]
yellow = [r for r in valid if -20 <= r['lift_pct'] < 20]
red = [r for r in valid if r['lift_pct'] < -20]
print(f"   🟢 ALIVE (>+20% lift):     {len(green)}")
print(f"   🟡 MUTED (-20% to +20%):   {len(yellow)}")
print(f"   🔴 DEAD WEIGHT (<-20%):    {len(red)}")

print('\n📜 KILL/DECAY RECOMMENDATIONS:')
for r in red:
    print(f"   🔴 {r['name']}: lift {r['lift_pct']:+.1f}% — "
          f"{r['total_hit']}/{r['total_pred']} hits "
          f"(expected {r['expected_hit']:.1f}). "
          f"Recommend: deprecate or quarter-pin only.")
