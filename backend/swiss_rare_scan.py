"""
🎻 Swiss Lotto — Rare-Compact Cosmic Storm Scanner
Definition (from The Book, line 68):
    Swiss rare = P1-P5 span <= 10 AND P6 jump >= 8
    Expected rate: ~3 in 3 years.

This script finds ALL Swiss rare-compact events in the DB, then for each
rare event it digs for cycle-clues inside the next 8-10 draws:
  - Family hungry (same decade as P1-P5)
  - Outlier (P6 — the "jump" voice)
  - Outlier circle (+21 Swiss mod 42)
  - Outlier 28-mirror (Law 28, pivot 28 on Swiss 1-42)
  - Star (lucky) forward echoes
  - Rare seed raw returns
  - Date-mirror dance (Law 33 pivot 28 at d7-d9)
  - Gap hunger (missing ladder closers)
"""

from dotenv import load_dotenv
load_dotenv()

import os
from datetime import datetime
from pymongo import MongoClient
from collections import Counter, defaultdict

client = MongoClient(os.environ['MONGO_URL'])
db = client[os.environ['DB_NAME']]


def parse_date(ds):
    return datetime.strptime(ds, "%d.%m.%Y")


def swiss_circle(n):
    """Swiss circle = +21 mod 42 (half of 42)."""
    v = (n + 21) % 42
    return v if v != 0 else 42


def mirror28(n, max_n=42):
    """🪞 ONE LAW (Canon 32): Swiss mirror = circle (n + 21 wrap)."""
    from mirror_canon import mirror_of as _mc_of
    return _mc_of(n, "swiss")


def decade_family(nums):
    """Return the decade family if 4+ of the 5 mains share a decade."""
    tens = [n // 10 for n in nums]
    c = Counter(tens).most_common(1)[0]
    return c[0] if c[1] >= 4 else None


def load_draws():
    draws = list(db.draws.find({}, {'_id': 0, 'date': 1, 'numbers': 1,
                                    'lucky_number': 1, 'replay_number': 1}))
    # de-dup on date just in case
    seen = set()
    clean = []
    for d in draws:
        if d['date'] in seen:
            continue
        seen.add(d['date'])
        try:
            d['_dt'] = parse_date(d['date'])
        except Exception:
            continue
        if not d.get('numbers') or len(d['numbers']) != 6:
            continue
        clean.append(d)
    clean.sort(key=lambda x: x['_dt'])
    return clean


def find_rares(draws):
    """Find all Swiss rare-compact events."""
    rares = []
    for i, d in enumerate(draws):
        nums = sorted(d['numbers'])
        p1_p5 = nums[:5]
        p6 = nums[5]
        span = p1_p5[-1] - p1_p5[0]
        jump = p6 - p1_p5[-1]
        if span <= 10 and jump >= 8:
            rares.append({
                'idx': i,
                'date': d['date'],
                'numbers': nums,
                'p1_p5': p1_p5,
                'p6': p6,
                'span': span,
                'jump': jump,
                'lucky': d.get('lucky_number'),
                'replay': d.get('replay_number'),
                'family': decade_family(p1_p5),
            })
    return rares


def dig_clues(draws, rare, window=10):
    """For a rare at index rare['idx'], analyze the next `window` draws."""
    start = rare['idx'] + 1
    next_draws = draws[start:start + window]
    clues = []

    outlier = rare['p6']
    family = rare['family']
    seed_mains = set(rare['numbers'])
    seed_lucky = rare['lucky']

    # Hungry ladder-closer candidates from the P1-P5 span
    span_lo, span_hi = min(rare['p1_p5']), max(rare['p1_p5'])
    inside_span = set(range(span_lo, span_hi + 1)) - set(rare['p1_p5'])
    # Ladder extension (above/below)
    ladder_ext = {span_hi + 1, span_hi + 2, span_lo - 1, span_lo - 2}
    ladder_ext = {x for x in ladder_ext if 1 <= x <= 42}

    out_circle = swiss_circle(outlier)
    out_mirror = mirror28(outlier)
    seed_circles = {swiss_circle(n) for n in rare['numbers']}
    seed_mirrors = {mirror28(n) for n in rare['numbers']}

    for k, d in enumerate(next_draws, start=1):
        nums = set(d['numbers'])
        hits = {
            'd': k,
            'date': d['date'],
            'draw': sorted(d['numbers']),
            'lucky': d.get('lucky_number'),
            'family_hungry_hit': sorted(nums & inside_span),
            'ladder_ext_hit': sorted(nums & ladder_ext),
            'outlier_raw': outlier in nums,
            'outlier_circle': (out_circle in nums, out_circle),
            'outlier_mirror28': (out_mirror in nums, out_mirror),
            'seed_raw_return': sorted(nums & seed_mains),
            'seed_circle_hit': sorted(nums & seed_circles),
            'seed_mirror_hit': sorted(nums & seed_mirrors),
            'lucky_echo': d.get('lucky_number') == seed_lucky,
        }
        # Date-mirror pivot 28 (Law 33, for d7-d9)
        try:
            dt = parse_date(d['date'])
            day_mirror = mirror28(dt.day)
            month_mirror = mirror28(dt.month)
            hits['date_day_mirror28'] = (day_mirror in nums, day_mirror)
            hits['date_month_mirror28'] = (month_mirror in nums, month_mirror)
        except Exception:
            pass
        clues.append(hits)

    return {
        'rare': rare,
        'outlier_path': {
            'raw': outlier,
            'swiss_circle': out_circle,
            'mirror28': out_mirror,
        },
        'hungry_inside_span': sorted(inside_span),
        'ladder_extensions': sorted(ladder_ext),
        'seed_circles': sorted(seed_circles),
        'seed_mirrors': sorted(seed_mirrors),
        'next_window': clues,
    }


def aggregate_rates(clue_bundles):
    """Aggregate which laws fire across the rares (at any point in 8-draw window)."""
    W = 8
    totals = defaultdict(int)
    n = len(clue_bundles)
    for b in clue_bundles:
        fires = {
            'family_hungry_any': False,
            'outlier_raw_any': False,
            'outlier_circle_any': False,
            'outlier_mirror28_any': False,
            'seed_return_any': False,
            'seed_circle_any': False,
            'seed_mirror_any': False,
            'lucky_echo_any': False,
            'date_day_mirror28_d7d9': False,
            'date_month_mirror28_d7d9': False,
        }
        for w in b['next_window'][:W]:
            if w['family_hungry_hit']:
                fires['family_hungry_any'] = True
            if w['outlier_raw']:
                fires['outlier_raw_any'] = True
            if w['outlier_circle'][0]:
                fires['outlier_circle_any'] = True
            if w['outlier_mirror28'][0]:
                fires['outlier_mirror28_any'] = True
            if w['seed_raw_return']:
                fires['seed_return_any'] = True
            if w['seed_circle_hit']:
                fires['seed_circle_any'] = True
            if w['seed_mirror_hit']:
                fires['seed_mirror_any'] = True
            if w['lucky_echo']:
                fires['lucky_echo_any'] = True
            if 7 <= w['d'] <= 9:
                if w.get('date_day_mirror28', (False,))[0]:
                    fires['date_day_mirror28_d7d9'] = True
                if w.get('date_month_mirror28', (False,))[0]:
                    fires['date_month_mirror28_d7d9'] = True
        for k, v in fires.items():
            if v:
                totals[k] += 1
    return {k: (v, n, f"{100*v/n:.1f}%") for k, v in totals.items()}


def pretty_print_clue_bundle(b):
    r = b['rare']
    print(f"\n{'='*78}")
    print(f"🌀 RARE COMPACT STORM  {r['date']}  →  {r['numbers']}  🍀{r['lucky']}  R:{r['replay']}")
    print(f"   span P1-P5 = {r['span']} (P1-P5: {r['p1_p5']})")
    print(f"   P6 jump    = {r['jump']} (outlier = {r['p6']})")
    print(f"   family     = {r['family']*10}s" if r['family'] is not None else "   family     = none (mixed)")
    print(f"   outlier paths: raw={b['outlier_path']['raw']} · Swiss-circle+21={b['outlier_path']['swiss_circle']} · 28-mirror={b['outlier_path']['mirror28']}")
    print(f"   hungry inside span: {b['hungry_inside_span']}")
    print(f"   ladder extensions: {b['ladder_extensions']}")
    print(f"   seed Swiss-circles: {b['seed_circles']}")
    print(f"   seed 28-mirrors:    {b['seed_mirrors']}")
    print(f"\n   Next {len(b['next_window'])} draws:")
    for w in b['next_window']:
        hits = []
        if w['family_hungry_hit']:
            hits.append(f"🌾fam-hungry={w['family_hungry_hit']}")
        if w['ladder_ext_hit']:
            hits.append(f"🪜ladder={w['ladder_ext_hit']}")
        if w['outlier_raw']:
            hits.append("🎯out-RAW")
        if w['outlier_circle'][0]:
            hits.append(f"🌀out-circle({w['outlier_circle'][1]})")
        if w['outlier_mirror28'][0]:
            hits.append(f"🪞out-mirror28({w['outlier_mirror28'][1]})")
        if w['seed_raw_return']:
            hits.append(f"↩seed-return={w['seed_raw_return']}")
        if w['seed_circle_hit']:
            hits.append(f"🌀seed-circle={w['seed_circle_hit']}")
        if w['seed_mirror_hit']:
            hits.append(f"🪞seed-mirror={w['seed_mirror_hit']}")
        if w['lucky_echo']:
            hits.append("🍀lucky-echo")
        if 'date_day_mirror28' in w and w['date_day_mirror28'][0]:
            hits.append(f"📅day-mirror28({w['date_day_mirror28'][1]})")
        if 'date_month_mirror28' in w and w['date_month_mirror28'][0]:
            hits.append(f"📅mon-mirror28({w['date_month_mirror28'][1]})")
        print(f"     d{w['d']}  {w['date']}  {w['draw']} 🍀{w['lucky']}   " +
              (" · ".join(hits) if hits else "—"))


if __name__ == "__main__":
    draws = load_draws()
    print(f"🎧 Loaded {len(draws)} Swiss draws (chronological, de-duped)")
    print(f"   Range: {draws[0]['date']}  →  {draws[-1]['date']}")

    rares = find_rares(draws)
    print(f"\n🌀 Found {len(rares)} Swiss RARE COMPACT storms (span≤10, P6-jump≥8)")
    for r in rares:
        print(f"   {r['date']}  {r['numbers']}  span={r['span']}  jump={r['jump']}  family={r['family']}")

    # Dig clues for ALL rares (full history) + pretty print the 3 most recent
    bundles = [dig_clues(draws, r, window=10) for r in rares]

    print("\n" + "="*78)
    print("🎻 3 MOST RECENT SWISS RARE COMPACT STORMS — DEEP CLUE DIG")
    print("="*78)
    for b in bundles[-3:]:
        pretty_print_clue_bundle(b)

    print("\n" + "="*78)
    print(f"📊 AGGREGATE LAW-FIRE RATES across ALL {len(bundles)} Swiss rare storms (8-draw window)")
    print("="*78)
    rates = aggregate_rates(bundles)
    for k, (hits, n, pct) in sorted(rates.items(), key=lambda x: -x[1][0]):
        print(f"   {k:35s}  {hits:3d}/{n}  ({pct})")
