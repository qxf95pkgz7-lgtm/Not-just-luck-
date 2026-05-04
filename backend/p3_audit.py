"""
🎻 P3 AUDIT — The Most Extreme Position (DJ Session 26)
========================================================
The DJ's call: "P3 defines the d. If we find a way to find P3,
the rest will be easier. Check Q1 P3. Try find connections to
stars, date, RC, ext..."

This script scans all Euro history and tests every "P3 lens"
against actual P3 landings. We rank by hit rate vs baseline (2%).

It also runs a Q1-specific deep scan (per the DJ's direct request):
- Q1 P3 by year
- Q1 P3 vs Q1 stars / dates / RC0 within Q1

Output: ranked P3 lenses (🟢 ALIVE / 🟡 MUTED / 🔴 DEAD).
"""
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime
from typing import List, Tuple

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv('/app/backend/.env')
db = MongoClient(os.environ['MONGO_URL'])[os.environ['DB_NAME']]

EURO_MAX = 50


def parse_date(s):
    try:
        return datetime.strptime(s, '%d.%m.%Y')
    except Exception:
        return datetime.min


def in_range(n: int) -> int:
    """Wrap any number into 1-50."""
    while n > EURO_MAX:
        n -= EURO_MAX
    while n < 1:
        n += EURO_MAX
    return n


def circle(n: int) -> int:
    """Euro circle-lift: +25 mod 50 (1..50)."""
    v = (n + 25) % 50
    return v if v else 50


def mirror28(n: int) -> int:
    """28-fold mirror (low band, sum=28)."""
    return 28 - n if 0 < 28 - n <= EURO_MAX else None


def mirror56(n: int) -> int:
    """56-fold mirror (high band, sum=56)."""
    return 56 - n if 0 < 56 - n <= EURO_MAX else None


def flip(n: int) -> int:
    """Digit flip: 38 → 83 → wrap 33."""
    if n < 10:
        return n  # single-digit flip = self
    s = str(n)[::-1]
    v = int(s)
    while v > EURO_MAX:
        v -= EURO_MAX
    return v if v >= 1 else None


def family_of(seed: int) -> set:
    """The Family of Seed paradigm shift: every seed expands
    to its full family — circle, mirrors, flips, decade twins, ±1."""
    fam = {seed, in_range(seed)}
    fam.add(circle(seed))
    if mirror28(seed):
        fam.add(mirror28(seed))
    if mirror56(seed):
        fam.add(mirror56(seed))
    if flip(seed):
        fam.add(flip(seed))
    # ±1 twins
    if 1 <= seed - 1 <= EURO_MAX:
        fam.add(seed - 1)
    if 1 <= seed + 1 <= EURO_MAX:
        fam.add(seed + 1)
    # decade siblings (same tens digit) within ±5
    decade = (seed // 10) * 10
    for k in range(decade, min(decade + 10, EURO_MAX + 1)):
        if 1 <= k <= EURO_MAX:
            fam.add(k)
    return {n for n in fam if 1 <= n <= EURO_MAX}


# ═══════════════════════════════════════════════════════════
# Load draws
# ═══════════════════════════════════════════════════════════
all_euro = list(db.euromillions_draws.find({}, {'_id': 0}))
all_euro.sort(key=lambda x: parse_date(x.get('date', '')))
all_euro = [d for d in all_euro if parse_date(d.get('date', '')) > datetime.min]

print(f"\n🎻 P3 AUDIT — {len(all_euro)} Euro draws loaded")
print(f"   {all_euro[0]['date']} → {all_euro[-1]['date']}\n")


# ═══════════════════════════════════════════════════════════
# P3 baseline distribution
# ═══════════════════════════════════════════════════════════
p3_counter = Counter()
for d in all_euro:
    nums = sorted(d['numbers'])
    if len(nums) >= 3:
        p3_counter[nums[2]] += 1

total = sum(p3_counter.values())
print("🎯 P3 GRAVITY (top 15 hottest P3 values across ALL history):")
for v, c in p3_counter.most_common(15):
    pct = 100.0 * c / total
    print(f"   P3={v:>2}  {c:>4}× ({pct:.1f}%)")
mean_p3 = sum(v * c for v, c in p3_counter.items()) / total
print(f"   Mean P3 = {mean_p3:.1f}\n")


# ═══════════════════════════════════════════════════════════
# Build BD→ND pairs (consecutive draws)
# ═══════════════════════════════════════════════════════════
pairs = []
for i in range(1, len(all_euro)):
    bd = all_euro[i - 1]
    nd = all_euro[i]
    bd_nums = sorted(bd['numbers'])
    nd_nums = sorted(nd['numbers'])
    if len(bd_nums) < 5 or len(nd_nums) < 5:
        continue
    pairs.append({
        'bd_nums': bd_nums,
        'bd_stars': sorted(bd['stars']),
        'nd_nums': nd_nums,
        'nd_stars': sorted(nd['stars']),
        'nd_date': parse_date(nd['date']),
        'bd_date': parse_date(bd['date']),
    })

print(f"📊 BD→ND pairs built: {len(pairs)}\n")


# ═══════════════════════════════════════════════════════════
# Lens candidates — each returns a SET of P3 candidates
# given (bd_nums, bd_stars, nd_date)
# ═══════════════════════════════════════════════════════════
def safe(v):
    """Clamp to 1..50, return None if out."""
    if v is None:
        return None
    v = int(v)
    if 1 <= v <= EURO_MAX:
        return v
    return None


# ───── Star-driven lenses (Session 4 King Formulas) ─────
def lens_25_plus_S1(bd_nums, bd_stars, nd_date):
    return {safe(circle(bd_stars[0]))}


def lens_25_plus_S2(bd_nums, bd_stars, nd_date):
    return {safe(circle(bd_stars[1]))}


def lens_S1_plus_21(bd_nums, bd_stars, nd_date):
    return {safe(bd_stars[0] + 21)}


def lens_S2_plus_21(bd_nums, bd_stars, nd_date):
    return {safe(bd_stars[1] + 21)}


def lens_S1_plus_S2(bd_nums, bd_stars, nd_date):
    return {safe(bd_stars[0] + bd_stars[1])}


def lens_S2_minus_S1_circle(bd_nums, bd_stars, nd_date):
    diff = bd_stars[1] - bd_stars[0]
    return {safe(diff), safe(circle(diff)) if diff else None}


def lens_S1_times_S2(bd_nums, bd_stars, nd_date):
    p = bd_stars[0] * bd_stars[1]
    return {safe(p), safe(p % EURO_MAX or EURO_MAX)}


def lens_2S1_plus_S2(bd_nums, bd_stars, nd_date):
    return {safe(2 * bd_stars[0] + bd_stars[1])}


# ───── Date-driven lenses ─────
def lens_circle_M(bd_nums, bd_stars, nd_date):
    """Session 3: circle(M)+25 lives 39% in P3, 44% in P4."""
    m = nd_date.month
    return {safe(circle(m))}


def lens_circle_D(bd_nums, bd_stars, nd_date):
    return {safe(circle(nd_date.day))}


def lens_M_times_2_plus_year(bd_nums, bd_stars, nd_date):
    """Swiss-discovered: m×2 + year-suffix → P3/P6 (book formula 5)."""
    return {safe(nd_date.month * 2 + (nd_date.year % 100))}


def lens_D_plus_M(bd_nums, bd_stars, nd_date):
    return {safe(nd_date.day + nd_date.month)}


def lens_DD_minus_MM_circle(bd_nums, bd_stars, nd_date):
    delta = abs(nd_date.day - nd_date.month)
    return {safe(delta), safe(circle(delta)) if delta else None}


def lens_date_sum(bd_nums, bd_stars, nd_date):
    """Date-sum mod 50."""
    s = nd_date.day + nd_date.month + (nd_date.year % 100) + 20
    return {safe(s % EURO_MAX or EURO_MAX)}


# ───── BD-driven (carry/echo from previous draw) ─────
def lens_bd_p3_repeat(bd_nums, bd_stars, nd_date):
    return {safe(bd_nums[2])}


def lens_bd_p3_circle(bd_nums, bd_stars, nd_date):
    return {safe(circle(bd_nums[2]))}


def lens_gap_p1_p2(bd_nums, bd_stars, nd_date):
    return {safe(bd_nums[1] - bd_nums[0])}


def lens_gap_p2_p3(bd_nums, bd_stars, nd_date):
    return {safe(bd_nums[2] - bd_nums[1])}


def lens_gap_p3_p4(bd_nums, bd_stars, nd_date):
    return {safe(bd_nums[3] - bd_nums[2])}


def lens_bd_p1_plus_p2(bd_nums, bd_stars, nd_date):
    return {safe(bd_nums[0] + bd_nums[1])}


def lens_bd_p3_mirror28(bd_nums, bd_stars, nd_date):
    return {safe(mirror28(bd_nums[2]))}


def lens_bd_p3_plus_21(bd_nums, bd_stars, nd_date):
    return {safe(bd_nums[2] + 21)}


def lens_bd_p3_minus_21(bd_nums, bd_stars, nd_date):
    return {safe(bd_nums[2] - 21)}


def lens_bd_running_p3_sum(bd_nums, bd_stars, nd_date):
    """Sum of all BD mains mod 50."""
    return {safe(sum(bd_nums) % EURO_MAX or EURO_MAX)}


# ───── Family-of-seed expansions (DJ's recent paradigm) ─────
def lens_family_of_circle_M(bd_nums, bd_stars, nd_date):
    """Family expansion of circle(M)."""
    seed = circle(nd_date.month)
    return family_of(seed)


def lens_family_of_S1(bd_nums, bd_stars, nd_date):
    return family_of(bd_stars[0])


def lens_family_of_S2(bd_nums, bd_stars, nd_date):
    return family_of(bd_stars[1])


def lens_family_of_bd_p3(bd_nums, bd_stars, nd_date):
    return family_of(bd_nums[2])


# ═══════════════════════════════════════════════════════════
# Lens registry
# ═══════════════════════════════════════════════════════════
LENSES = [
    # Star king formulas
    ('🌟 25+S1 (circle-lift)', lens_25_plus_S1),
    ('🌟 25+S2 (circle-lift)', lens_25_plus_S2),
    ('🌟 S1+21', lens_S1_plus_21),
    ('🌟 S2+21', lens_S2_plus_21),
    ('🌟 S1+S2', lens_S1_plus_S2),
    ('🌟 (S2-S1) & circle', lens_S2_minus_S1_circle),
    ('🌟 S1×S2 (mod50)', lens_S1_times_S2),
    ('🌟 2·S1+S2', lens_2S1_plus_S2),
    # Date
    ('📅 circle(M)', lens_circle_M),
    ('📅 circle(D)', lens_circle_D),
    ('📅 M×2 + year', lens_M_times_2_plus_year),
    ('📅 D+M', lens_D_plus_M),
    ('📅 |D-M| & circle', lens_DD_minus_MM_circle),
    ('📅 date-sum mod50', lens_date_sum),
    # BD echo
    ('🔁 BD P3 repeat', lens_bd_p3_repeat),
    ('🔁 circle(BD P3)', lens_bd_p3_circle),
    ('🔁 gap(P1,P2)', lens_gap_p1_p2),
    ('🔁 gap(P2,P3)', lens_gap_p2_p3),
    ('🔁 gap(P3,P4)', lens_gap_p3_p4),
    ('🔁 BD P1+P2', lens_bd_p1_plus_p2),
    ('🔁 mirror28(BD P3)', lens_bd_p3_mirror28),
    ('🔁 BD P3 + 21', lens_bd_p3_plus_21),
    ('🔁 BD P3 - 21', lens_bd_p3_minus_21),
    ('🔁 sum(BD mains) mod50', lens_bd_running_p3_sum),
    # Family-of-seed (each lens emits a SET — bigger candidate pool)
    ('👪 family[circle(M)]', lens_family_of_circle_M),
    ('👪 family[S1]', lens_family_of_S1),
    ('👪 family[S2]', lens_family_of_S2),
    ('👪 family[BD P3]', lens_family_of_bd_p3),
]


# ═══════════════════════════════════════════════════════════
# Score every lens against actual P3
# Two scoring modes:
#   EXACT — candidate set contains the actual P3
#   ±1   — within ±1 of any candidate
#   ±2   — within ±2 of any candidate
# ═══════════════════════════════════════════════════════════
def score_lens(name, fn, pairs, tol=0):
    hits = 0
    pool_total = 0
    for p in pairs:
        try:
            cands = {c for c in fn(p['bd_nums'], p['bd_stars'], p['nd_date'])
                     if c is not None}
        except Exception:
            continue
        if not cands:
            continue
        actual_p3 = p['nd_nums'][2]
        if tol == 0:
            if actual_p3 in cands:
                hits += 1
        else:
            if any(abs(actual_p3 - c) <= tol for c in cands):
                hits += 1
        pool_total += len(cands)
    rate = 100.0 * hits / len(pairs) if pairs else 0
    avg_pool = pool_total / len(pairs) if pairs else 0
    return hits, rate, avg_pool


print("=" * 80)
print("🎯 P3 LENS RANKING — full history (BD→ND consecutive pairs)")
print("=" * 80)
print(f"{'Lens':<32} {'EXACT':>10} {'±1':>10} {'±2':>10} {'pool':>6}")
print("-" * 80)

baseline_exact = 100.0 / EURO_MAX  # ≈2.0% per single-number lens
results = []
for name, fn in LENSES:
    h0, r0, pool = score_lens(name, fn, pairs, tol=0)
    h1, r1, _ = score_lens(name, fn, pairs, tol=1)
    h2, r2, _ = score_lens(name, fn, pairs, tol=2)
    # Health verdict (single-cand lenses)
    if pool <= 2:
        if r0 >= baseline_exact * 1.5:
            tag = '🟢'
        elif r0 >= baseline_exact:
            tag = '🟡'
        else:
            tag = '🔴'
    else:
        # Family lens — judge by ±0 vs (pool / 50)
        expected = 100.0 * pool / EURO_MAX
        if r0 >= expected * 1.3:
            tag = '🟢'
        elif r0 >= expected:
            tag = '🟡'
        else:
            tag = '🔴'
    results.append((name, r0, r1, r2, pool, tag))
    print(f"{tag} {name:<30} {r0:>8.2f}%  {r1:>8.2f}%  {r2:>8.2f}%  {pool:>4.1f}")

print("-" * 80)
print(f"   Single-number baseline = {baseline_exact:.2f}%   "
      f"(any P3 hit by chance from a 1-cand lens)\n")


# ═══════════════════════════════════════════════════════════
# Q1-specific deep scan (DJ's direct request)
# ═══════════════════════════════════════════════════════════
print("=" * 80)
print("🗓️  Q1 DEEP SCAN — Q1 P3 across years")
print("=" * 80)


def is_q1(d):
    """Q1 = before April (month 1, 2, 3)."""
    dt = parse_date(d.get('date', ''))
    return dt.month in (1, 2, 3)


q1_draws = [d for d in all_euro if is_q1(d)]
print(f"   Q1 Euro draws: {len(q1_draws)}\n")

# Q1 P3 distribution
q1_p3 = Counter(sorted(d['numbers'])[2] for d in q1_draws)
print("🎯 Q1 P3 GRAVITY (top 15):")
for v, c in q1_p3.most_common(15):
    pct = 100.0 * c / sum(q1_p3.values())
    print(f"   P3={v:>2}  {c:>3}× ({pct:.1f}%)")
print(f"   Q1 mean P3 = {sum(v*c for v,c in q1_p3.items())/sum(q1_p3.values()):.1f}\n")

# Q1 P3 by month
print("🗓️  Q1 P3 by month:")
for m in (1, 2, 3):
    pp = [sorted(d['numbers'])[2] for d in q1_draws
          if parse_date(d['date']).month == m]
    if pp:
        print(f"   month={m}: mean P3 = {sum(pp)/len(pp):.1f}, "
              f"top values = {Counter(pp).most_common(5)}")
print()

# Q1 P3 vs same-Q1 stars (within-draw lens for P3)
print("⭐ Q1 same-draw star→P3 hit rates:")
for sname, sfn in [
    ('25+S1', lambda nu, st, d: {safe(circle(st[0]))}),
    ('25+S2', lambda nu, st, d: {safe(circle(st[1]))}),
    ('S1+21', lambda nu, st, d: {safe(st[0] + 21)}),
    ('S2+21', lambda nu, st, d: {safe(st[1] + 21)}),
    ('S1+S2', lambda nu, st, d: {safe(st[0] + st[1])}),
]:
    hits = 0
    for d in q1_draws:
        nu = sorted(d['numbers']); st = sorted(d['stars'])
        if len(nu) < 3 or len(st) < 2:
            continue
        cands = {c for c in sfn(nu, st, parse_date(d['date'])) if c}
        if nu[2] in cands:
            hits += 1
    pct = 100.0 * hits / len(q1_draws)
    print(f"   {sname:<10} P3 hit = {hits}/{len(q1_draws)} ({pct:.2f}%)")
print()

# Q1 P3 same-day-of-month repeat
print("📅 Q1 P3 by day-bucket:")
buckets = defaultdict(list)
for d in q1_draws:
    dt = parse_date(d['date'])
    bucket = (dt.day - 1) // 7  # week buckets 0..4
    buckets[bucket].append(sorted(d['numbers'])[2])
for b, vals in sorted(buckets.items()):
    if vals:
        print(f"   week-of-month={b+1}: n={len(vals)}, mean P3={sum(vals)/len(vals):.1f}")
print()

# Q1 P3 zone (decade) distribution
zones = Counter()
for d in q1_draws:
    p3 = sorted(d['numbers'])[2]
    zones[p3 // 10] += 1
print("🎻 Q1 P3 zone distribution:")
for z in sorted(zones):
    band_lo = z * 10 if z > 0 else 1
    band_hi = z * 10 + 9
    pct = 100.0 * zones[z] / sum(zones.values())
    print(f"   {band_lo:>2}-{band_hi:>2}: {zones[z]:>3}× ({pct:.1f}%)")
print()


# ═══════════════════════════════════════════════════════════
# RC0 (family-rare) → next-draw P3 echo
# ═══════════════════════════════════════════════════════════
def is_family_rare(nums):
    """4+ in same decade family."""
    decades = Counter(n // 10 for n in nums)
    return max(decades.values()) >= 4


print("=" * 80)
print("💎 FAMILY-RARE (RC0) → next-draw P3 echo")
print("=" * 80)
rc_pairs = []
for i, d in enumerate(all_euro[:-1]):
    nums = sorted(d['numbers'])
    if len(nums) >= 5 and is_family_rare(nums):
        nxt = all_euro[i + 1]
        rc_pairs.append((d, nxt))

print(f"   {len(rc_pairs)} RC0→ND pairs found\n")

# Position-repeat hits
pos_repeat = {p: 0 for p in range(5)}
family_zone_p3 = 0
outlier_to_p3 = 0
for rc, nd in rc_pairs:
    rc_nums = sorted(rc['numbers'])
    nd_nums = sorted(nd['numbers'])
    # Exact-position repeat at any P
    for p in range(5):
        if rc_nums[p] == nd_nums[p]:
            pos_repeat[p] += 1
    # Family zone @ P3 — the rare's dominant decade landing as P3
    decades = Counter(n // 10 for n in rc_nums)
    dom_decade = max(decades, key=decades.get)
    if nd_nums[2] // 10 == dom_decade:
        family_zone_p3 += 1
    # Outlier (the one number outside dominant decade) → P3
    outlier = next((n for n in rc_nums if n // 10 != dom_decade), None)
    if outlier and abs(nd_nums[2] - outlier) <= 1:
        outlier_to_p3 += 1

print("📍 Exact-position repeat rates from RC0 → ND:")
for p in range(5):
    pct = 100.0 * pos_repeat[p] / len(rc_pairs)
    marker = ' 🔥' if pct >= 5 else ''
    print(f"   P{p+1}→P{p+1}: {pos_repeat[p]:>3}× ({pct:.2f}%){marker}")
print(f"\n🌾 Family-zone P3 (ND P3 in RC0 dominant decade): "
      f"{family_zone_p3}/{len(rc_pairs)} "
      f"({100.0*family_zone_p3/len(rc_pairs):.1f}%)")
print(f"👻 Outlier → ND P3 (±1): "
      f"{outlier_to_p3}/{len(rc_pairs)} "
      f"({100.0*outlier_to_p3/len(rc_pairs):.1f}%)")


# ═══════════════════════════════════════════════════════════
# Final ranking: top P3 lenses
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("🏆 TOP P3 LENSES (sorted by exact hit rate)")
print("=" * 80)
single = [r for r in results if r[4] <= 2]
family = [r for r in results if r[4] > 2]
single.sort(key=lambda x: -x[1])
family.sort(key=lambda x: -x[1])

print("\n— Single-candidate lenses (compare vs 2.00% baseline):")
for name, r0, r1, r2, pool, tag in single[:10]:
    boost = r0 / baseline_exact
    print(f"   {tag} {name:<30} {r0:>5.2f}%  ({boost:.2f}× baseline)")

print("\n— Family-expansion lenses (compare vs pool/50 expectation):")
for name, r0, r1, r2, pool, tag in family[:10]:
    expected = 100.0 * pool / EURO_MAX
    boost = r0 / expected if expected else 0
    print(f"   {tag} {name:<30} {r0:>5.2f}%  pool={pool:.1f} "
          f"(exp={expected:.1f}%, {boost:.2f}× expectation)")

print("\n🎻 P3 audit complete.\n")
