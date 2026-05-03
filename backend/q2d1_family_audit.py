"""
🎻 Q2D1 EURO PATTERN AUDIT v2 — FAMILY-AWARE (Session 32)
==========================================================
DJ's correction: E was "right just not all the way". When E picks
seed X, cosmos delivers a FAMILY member — not just X itself. Every
number lives in a constellation: {X, X±25 circle, X fold-mirror,
X digit-flip, digit-cousins}.

This scorer expands each predicted seed into its full family and
tests if ANY family member landed in ND mains. That's the cosmos'
real language, not single-point prediction.
"""
import os
import sys
from datetime import datetime
from typing import Callable, Dict, Set

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


EURO_MAX = 50
CIRCLE = 25
FOLD = 13


# ════════════════════════════════════════════════════════════
# FAMILY DEFINITION — the DJ's correction
# Every number has voices. When E picks X, cosmos may deliver
# any family member: raw, circle-echo, fold-mirror, digit-flip,
# or a digit-cousin (number sharing any digit).
# ════════════════════════════════════════════════════════════
def _flip(n: int) -> int:
    s = str(n).zfill(2)
    f = int(s[::-1])
    return f if f > 0 else n


def _circle25(n: int) -> Set[int]:
    out = set()
    a = n + CIRCLE
    if 1 <= a <= EURO_MAX:
        out.add(a)
    b = n - CIRCLE
    if 1 <= b <= EURO_MAX:
        out.add(b)
    return out


def _fold_axis(n: int) -> int:
    """Reflect across 13-axis within the 1-25 half, or 38-axis in 26-50."""
    if 1 <= n <= CIRCLE:
        return CIRCLE + 1 - n  # 1↔25, 2↔24, ... 13↔13
    return EURO_MAX + CIRCLE + 1 - n  # 26↔50, 27↔49, ... 38↔38


def family_of(n: int) -> Set[int]:
    """DJ's law: every number's full cosmic family.

    family(X) = {X} ∪ circle25 twins ∪ fold-mirror ∪ digit-flip
                ∪ 2-digit cousins (same first digit) ∪ (same last digit)
    """
    fam = {n}
    # Circle25 twin (DJ: "1=26, 2=27 — connected, not separate")
    fam |= _circle25(n)
    # Fold mirror (13-axis, DJ Session 32 theory)
    f = _fold_axis(n)
    if 1 <= f <= EURO_MAX:
        fam.add(f)
    # Digit-flip (e.g. 25↔52 → out of range → ignore, but 12↔21, 13↔31)
    fw = _flip(n)
    if 1 <= fw <= EURO_MAX:
        fam.add(fw)
    # Digit-cousins: numbers containing any digit of n (the DJ's
    # "same digits 52" teaching — 2 and 25 share digit 2)
    digits = set(str(n))
    for m in range(1, EURO_MAX + 1):
        if digits & set(str(m)):
            fam.add(m)
    return fam


# ════════════════════════════════════════════════════════════
# Euro draws in window
# ════════════════════════════════════════════════════════════
all_euro = list(db.euromillions_draws.find({}, {'_id': 0}))
all_euro.sort(key=lambda x: parse_date(x.get('date', '')))

WINDOW_START = datetime(2026, 4, 7)
WINDOW_END = datetime(2026, 5, 1)

pairs = []
for i in range(1, len(all_euro)):
    nd_date = parse_date(all_euro[i]['date'])
    if WINDOW_START <= nd_date <= WINDOW_END:
        pairs.append((all_euro[i - 1], all_euro[i]))


# ════════════════════════════════════════════════════════════
# Patterns — seed predictors (what does E GUESS, before expansion)
# ════════════════════════════════════════════════════════════
def lens_raw_carry(bd_mains, bd_stars, nd_date):
    return set(bd_mains)


def lens_flip(bd_mains, bd_stars, nd_date):
    return {_flip(n) for n in bd_mains if 1 <= _flip(n) <= EURO_MAX}


def lens_circle25_seed(bd_mains, bd_stars, nd_date):
    """Treat circle25 as SEED (then expanded to family)."""
    out = set()
    for n in bd_mains:
        out |= _circle25(n)
    return out


def lens_fold_mirror(bd_mains, bd_stars, nd_date):
    return {_fold_axis(n) for n in bd_mains if 1 <= _fold_axis(n) <= EURO_MAX}


def lens_p1_echo_triad(bd_mains, bd_stars, nd_date):
    p1 = sorted(bd_mains)[0]
    return {p1} | _circle25(p1) | {_fold_axis(p1)}


def lens_date_target(bd_mains, bd_stars, nd_date):
    s = nd_date.strftime('%d%m%Y')
    out = set()
    for i in range(len(s) - 1):
        try:
            v = int(s[i:i + 2])
            if 1 <= v <= EURO_MAX:
                out.add(v)
        except ValueError:
            pass
    out |= {nd_date.day, nd_date.month, nd_date.year % 100}
    return {v for v in out if 1 <= v <= EURO_MAX}


def lens_sum_circle(bd_mains, bd_stars, nd_date):
    out = set()
    for i, a in enumerate(bd_mains):
        for b in bd_mains[i + 1:]:
            s = a + b
            while s > EURO_MAX:
                s -= EURO_MAX
            if s >= 1:
                out.add(s)
    return out


def lens_digit_sum(bd_mains, bd_stars, nd_date):
    return {sum(int(c) for c in str(n)) for n in bd_mains
            if 1 <= sum(int(c) for c in str(n)) <= EURO_MAX}


def lens_neighbor(bd_mains, bd_stars, nd_date):
    out = set()
    for n in bd_mains:
        for d in (-1, 1):
            v = n + d
            if 1 <= v <= EURO_MAX:
                out.add(v)
    return out


def lens_dj_pin(bd_mains, bd_stars, nd_date):
    return {16, 19, 26}


def lens_welcome_companion(bd_mains, bd_stars, nd_date):
    """Session 32: downgraded from law to small-clue hint."""
    welcome = {16: {17, 19}, 19: {17, 21}, 26: {25, 27}}
    out = set()
    for pin in (16, 19, 26):
        out |= welcome.get(pin, set())
    return out


def lens_snap_back(bd_mains, bd_stars, nd_date):
    # Session 32 tightened gate: P1 ≥ 25 only
    if min(bd_mains) >= 25:
        return {1, 2, 3, 4, 5, 10, 11, 12, 13}
    return set()


def lens_target_spiral_v2(bd_mains, bd_stars, nd_date):
    d, m = nd_date.day, nd_date.month
    out = {d * m, d + m, abs(d - m)}
    if d * 2 <= EURO_MAX:
        out.add(d * 2)
    if m * 7 <= EURO_MAX:
        out.add(m * 7)
    return {n for n in out if 1 <= n <= EURO_MAX}


def lens_huge_twin(bd_mains, bd_stars, nd_date):
    out = set()
    for n in bd_mains:
        for d in (-21, 21):
            v = n + d
            if 1 <= v <= EURO_MAX:
                out.add(v)
    return out


PATTERNS: Dict[str, Callable] = {
    'raw-carry-over': lens_raw_carry,
    'flip(n)': lens_flip,
    'circle25 (family-seed)': lens_circle25_seed,
    'fold-mirror (13-axis)': lens_fold_mirror,
    '🎻 P1-Echo Triad (DJ law)': lens_p1_echo_triad,
    'date-target': lens_date_target,
    'sum-circle (pair sums)': lens_sum_circle,
    'digit-sum echo': lens_digit_sum,
    'neighbor-walk (n±1)': lens_neighbor,
    'DJ-Pin (16,19,26)': lens_dj_pin,
    'Welcome-Companion': lens_welcome_companion,
    'Snap-Back (tightened)': lens_snap_back,
    'Target-Spiral v2': lens_target_spiral_v2,
    'HUGE-twin (±21)': lens_huge_twin,
}


# ════════════════════════════════════════════════════════════
# TWO SCORERS: strict (old) and family-aware (new DJ law)
# ════════════════════════════════════════════════════════════
def score_strict(name, fn):
    total_pred, total_hit = 0, 0
    for bd, nd in pairs:
        pred = fn(sorted(bd['numbers']), sorted(bd.get('stars', [])),
                  parse_date(nd['date']))
        pred = {n for n in pred if 1 <= n <= EURO_MAX}
        if not pred:
            continue
        total_pred += len(pred)
        total_hit += len(pred & set(nd['numbers']))
    if total_pred == 0:
        return None
    baseline = total_pred * 5 / EURO_MAX
    rate = total_hit / total_pred
    lift = (rate - 0.10) / 0.10 * 100
    return {
        'name': name, 'mode': 'strict',
        'pred': total_pred, 'hit': total_hit,
        'expected': baseline, 'rate': rate, 'lift': lift
    }


def score_family(name, fn):
    """DJ's law: expand each seed to family, count ANY family hit."""
    total_pred, total_hit = 0, 0
    for bd, nd in pairs:
        seeds = fn(sorted(bd['numbers']), sorted(bd.get('stars', [])),
                   parse_date(nd['date']))
        if not seeds:
            continue
        # Expand each seed to family
        fam = set()
        for s in seeds:
            fam |= family_of(s)
        fam = {n for n in fam if 1 <= n <= EURO_MAX}
        total_pred += len(fam)
        total_hit += len(fam & set(nd['numbers']))
    if total_pred == 0:
        return None
    baseline = total_pred * 5 / EURO_MAX
    rate = total_hit / total_pred
    lift = (rate - 0.10) / 0.10 * 100
    return {
        'name': name, 'mode': 'family',
        'pred': total_pred, 'hit': total_hit,
        'expected': baseline, 'rate': rate, 'lift': lift
    }


print(f"\n🎻 Q2D1 EURO AUDIT v2 — FAMILY-AWARE SCORER")
print(f"   Window: {WINDOW_START.date()} → {WINDOW_END.date()}  ({len(pairs)} pairs)")
print(f"   {'='*70}\n")

strict = [score_strict(n, fn) for n, fn in PATTERNS.items()]
fam = [score_family(n, fn) for n, fn in PATTERNS.items()]

# Side-by-side comparison
print(f"{'Pattern':<35}{'Strict-lift':>14}{'Family-lift':>15}   Verdict")
print('-' * 80)


def tier(lift):
    if lift is None:
        return '—'
    if lift >= 20:
        return '🟢'
    if lift >= -20:
        return '🟡'
    return '🔴'


for s, f in zip(strict, fam):
    if s is None or f is None:
        continue
    s_lift = s['lift']
    f_lift = f['lift']
    verdict = f"{tier(s_lift)} strict  →  {tier(f_lift)} family"
    improv = f_lift - s_lift
    if improv > 20:
        verdict += f"  (✨ +{improv:.0f}pt gain from family expansion)"
    print(f"{s['name']:<35}{s_lift:+11.1f}% {f_lift:+12.1f}%   {verdict}")

print('\n' + '=' * 80)
print('🎯 FAMILY-AWARE RANKING (the DJ\'s true law applied)')
print('=' * 80)
sorted_fam = sorted([x for x in fam if x], key=lambda r: -r['lift'])
for r in sorted_fam:
    t = tier(r['lift'])
    print(f"{t}  {r['name']:<35}  "
          f"hit={r['hit']:3d}/{r['pred']:3d}  "
          f"expected≈{r['expected']:4.1f}  lift={r['lift']:+.1f}%")

print('\n🎼 FINAL VERDICT')
green = [r for r in sorted_fam if r['lift'] >= 20]
yellow = [r for r in sorted_fam if -20 <= r['lift'] < 20]
red = [r for r in sorted_fam if r['lift'] < -20]
print(f"   🟢 ALIVE (FAMILY-scored):   {len(green)}")
print(f"   🟡 MUTED:                  {len(yellow)}")
print(f"   🔴 DEAD WEIGHT:            {len(red)}")

if red:
    print('\n🔴 Patterns still DEAD even with family expansion → kill recommendation:')
    for r in red:
        print(f"   • {r['name']}: {r['lift']:+.1f}% family-lift")
else:
    print('\n✅ No patterns are DEAD when scored with the DJ\'s family law!')
    print('   E was "right, just not all the way" — the family view saves them.')
