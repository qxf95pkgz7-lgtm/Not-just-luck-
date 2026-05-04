"""
🎻 STORY-SEED DETECTOR — Last 2 Years of Euro
==============================================
The DJ asked: locate the SAME kind of analysis we just did
on BD 01.05.2026 — find draws where ONE nucleus number
expressed through 3+ independent cosmic doors.

We hunt:
1. Extreme-gap draws (any gap ≥ 20) — does the gap value
   land in the very next draw?
2. BD-P3 + d2-P3 flip-wrap → 33-style chains
3. Inner-circle of stars → main of NEXT draw
4. Drunk-Cosmos detector (Law 7): 3+ self-referential conditions
5. Story-Seed walk: a small seed (1-15) wearing N masks
   across 3-8 consecutive draws before landing raw

Output: ranked HINTS + frequency stats. No engine changes yet.
"""
import os
from collections import Counter, defaultdict
from datetime import datetime
from itertools import combinations

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


def in_range(n):
    if n is None:
        return None
    while n > EURO_MAX:
        n -= EURO_MAX
    while n < 1:
        n += EURO_MAX
    return n


def circle(n):
    v = (n + 25) % 50
    return v if v else 50


def flip_wrap(n):
    if n < 10:
        return n
    s = str(n)[::-1]
    v = int(s)
    while v > EURO_MAX:
        v -= EURO_MAX
    return v if v >= 1 else None


# ═══════════════════════════════════════════════════════════
# Load last 2 years
# ═══════════════════════════════════════════════════════════
all_euro = list(db.euromillions_draws.find({}, {'_id': 0}))
all_euro.sort(key=lambda x: parse_date(x.get('date', '')))
all_euro = [d for d in all_euro if parse_date(d.get('date', '')) > datetime.min
            and len(d.get('numbers', [])) >= 5]

cutoff = datetime(2024, 1, 1)
recent = [d for d in all_euro if parse_date(d['date']) >= cutoff]
print(f"\n🎻 STORY-SEED DETECTOR — last 2 years")
print(f"   {len(recent)} draws since {cutoff.date()} → "
      f"{recent[-1]['date']}\n")


# ═══════════════════════════════════════════════════════════
# 1️⃣  EXTREME-GAP SCAN
#     For every draw, compute 4 inner gaps. Flag any ≥20.
#     Then check: did the gap-value land in next 1-3 draws?
# ═══════════════════════════════════════════════════════════
print("=" * 80)
print("1️⃣  EXTREME-GAP SCAN (any gap ≥ 20)")
print("=" * 80)

big_gap_events = []
for i, d in enumerate(recent):
    nums = sorted(d['numbers'])
    gaps = [(nums[j + 1] - nums[j], j) for j in range(4)]
    big = [(g, j) for g, j in gaps if g >= 20]
    if big:
        big_gap_events.append({
            'i': i, 'date': d['date'], 'nums': nums,
            'gaps': gaps, 'big': big,
        })

print(f"   Found {len(big_gap_events)} extreme-gap draws "
      f"({100*len(big_gap_events)/len(recent):.1f}% of last 2yrs)\n")

# Did the gap value land in next 1-3 draws?
hit_1d = hit_2d = hit_3d = 0
for ev in big_gap_events:
    i = ev['i']
    gap_vals = {g for g, _ in ev['big']}
    next_nums = set()
    for k in range(1, 4):
        if i + k >= len(recent):
            break
        nxt = set(recent[i + k]['numbers'])
        next_nums |= nxt
        if k == 1 and gap_vals & nxt:
            hit_1d += 1
        if k == 2 and gap_vals & set(recent[i + k]['numbers']):
            hit_2d += 1
        if k == 3 and gap_vals & set(recent[i + k]['numbers']):
            hit_3d += 1

print(f"📊 Gap value landed at:")
print(f"   d+1: {hit_1d}/{len(big_gap_events)} ({100*hit_1d/len(big_gap_events):.1f}%)")
print(f"   d+2: {hit_2d}/{len(big_gap_events)} ({100*hit_2d/len(big_gap_events):.1f}%)")
print(f"   d+3: {hit_3d}/{len(big_gap_events)} ({100*hit_3d/len(big_gap_events):.1f}%)")
print("   Baseline (5 mains/50): ~10% per draw\n")

# Where in the next draw did it land? (P-position bias)
pos_landings = Counter()
for ev in big_gap_events:
    i = ev['i']
    if i + 1 >= len(recent):
        continue
    nxt = sorted(recent[i + 1]['numbers'])
    for g, _ in ev['big']:
        if g in nxt:
            pos_landings[nxt.index(g)] += 1

print("📍 When the big gap landed in d+1, position bias:")
for p in range(5):
    c = pos_landings.get(p, 0)
    total = sum(pos_landings.values())
    if total:
        pct = 100 * c / total
        marker = '🔥' if pct >= 25 else ''
        print(f"   P{p+1}: {c} ({pct:.0f}%) {marker}")
print()


# ═══════════════════════════════════════════════════════════
# 2️⃣  CONSECUTIVE-P3 FLIP-WRAP — does P3+P3prev wrap to a number
#     that appears in the next 1-2 draws?
# ═══════════════════════════════════════════════════════════
print("=" * 80)
print("2️⃣  CONSECUTIVE-P3 FLIP-WRAP (BD.P3 + d-2.P3 → wrap)")
print("=" * 80)

fw_events = []
for i in range(2, len(recent)):
    p3_a = sorted(recent[i - 2]['numbers'])[2]
    p3_b = sorted(recent[i - 1]['numbers'])[2]
    s = p3_a + p3_b
    wrap = s - 50 if s > 50 else (s if s <= 50 else None)
    if wrap is None or wrap < 1:
        continue
    fw_events.append({
        'i': i, 'date': recent[i]['date'],
        'p3_a': p3_a, 'p3_b': p3_b, 'sum': s, 'wrap': wrap,
        'nd_nums': sorted(recent[i]['numbers']),
    })

# Does wrap land in the i-th draw?
landed = sum(1 for e in fw_events if e['wrap'] in e['nd_nums'])
within2 = sum(1 for e in fw_events
              if any(abs(n - e['wrap']) <= 2 for n in e['nd_nums']))
print(f"   {len(fw_events)} pairs scanned")
print(f"   wrap-value landed EXACT in next draw: "
      f"{landed} ({100*landed/len(fw_events):.1f}%)")
print(f"   wrap-value within ±2 of any main:    "
      f"{within2} ({100*within2/len(fw_events):.1f}%)")
print("   Baseline EXACT ≈ 10%, ±2 ≈ 50%\n")


# ═══════════════════════════════════════════════════════════
# 3️⃣  STAR INNER-CIRCLE → MAIN OF NEXT DRAW
#     For BD draws, compute every star's circle (+25). Check
#     hit rate vs ND mains.
# ═══════════════════════════════════════════════════════════
print("=" * 80)
print("3️⃣  STAR INNER-CIRCLE (BD ⭐ + 25) → ND mains")
print("=" * 80)

s_events = 0
s_landed = 0
s_pos = Counter()
for i in range(1, len(recent)):
    bs = sorted(recent[i - 1]['stars'])
    nn = sorted(recent[i]['numbers'])
    targets = {circle(s) for s in bs}
    s_events += 1
    hit = targets & set(nn)
    if hit:
        s_landed += 1
        for n in hit:
            s_pos[nn.index(n)] += 1

print(f"   Pairs: {s_events}")
print(f"   Any ⭐+25 → ND main: {s_landed} "
      f"({100*s_landed/s_events:.1f}%)  [baseline ~19% for 2 cands hitting 5/50]")
print("\n📍 Position landing of ⭐+25 hits:")
for p in range(5):
    c = s_pos.get(p, 0)
    total = sum(s_pos.values())
    pct = 100 * c / total if total else 0
    marker = '🔥' if pct >= 25 else ''
    print(f"   P{p+1}: {c} ({pct:.0f}%) {marker}")
print()


# ═══════════════════════════════════════════════════════════
# 4️⃣  DRUNK-COSMOS DETECTOR (Law 7)
#     A draw is "drunk" if 3+ self-referential conditions fire.
# ═══════════════════════════════════════════════════════════
print("=" * 80)
print("4️⃣  DRUNK-COSMOS draws (Law 7: 3+ self-references)")
print("=" * 80)


def drunk_score(nums):
    """Returns (score, list_of_signatures)."""
    p1, p2, p3, p4, p5 = sorted(nums)
    sigs = []
    # self-circle hit
    if any(circle(x) in {p1, p2, p3, p4, p5}
           for x in {p1, p2, p3, p4, p5}):
        sigs.append('self-circle')
    # flip-wrap inner
    for x in {p1, p2, p3, p4, p5}:
        fw = flip_wrap(x)
        if fw and fw != x and fw in {p1, p2, p3, p4, p5}:
            sigs.append(f'flip-wrap({x}→{fw})')
            break
    # sum-pair = another P (sum-triangle)
    nums_set = {p1, p2, p3, p4, p5}
    for a, b in combinations(nums_set, 2):
        if a + b in nums_set and a + b not in {a, b}:
            sigs.append(f'sum-triangle({a}+{b}={a+b})')
            break
    # extreme gap matches another value's circle
    gaps = [p2 - p1, p3 - p2, p4 - p3, p5 - p4]
    for g in gaps:
        if g >= 15 and g in nums_set:
            sigs.append(f'gap-as-self({g})')
            break
    # any pair sums to 28 (mirror axis)
    for a, b in combinations(nums_set, 2):
        if a + b == 28:
            sigs.append(f'28-mirror({a},{b})')
            break
    # any pair sums to 56 (high-mirror)
    for a, b in combinations(nums_set, 2):
        if a + b == 56:
            sigs.append(f'56-mirror({a},{b})')
            break
    return len(sigs), sigs


drunk_draws = []
for d in recent:
    score, sigs = drunk_score(d['numbers'])
    if score >= 3:
        drunk_draws.append({'date': d['date'], 'nums': sorted(d['numbers']),
                            'score': score, 'sigs': sigs})

print(f"   {len(drunk_draws)} drunk-cosmos draws "
      f"({100*len(drunk_draws)/len(recent):.1f}% of last 2yrs)\n")
for ev in drunk_draws[-15:]:
    print(f"   {ev['date']}  {ev['nums']}  score={ev['score']}")
    for s in ev['sigs']:
        print(f"        · {s}")

# What happens to P1 the draw AFTER a drunk draw? (Law 11 recovery)
print("\n📊 Drunk-Cosmos recovery (next-draw P1 distribution):")
next_p1s = []
for ev in drunk_draws:
    # find ev's index in recent
    for i, d in enumerate(recent):
        if d['date'] == ev['date']:
            if i + 1 < len(recent):
                next_p1s.append(sorted(recent[i + 1]['numbers'])[0])
            break
if next_p1s:
    p1_dist = Counter()
    for v in next_p1s:
        if v <= 5: p1_dist['1-5'] += 1
        elif v <= 10: p1_dist['6-10'] += 1
        elif v <= 15: p1_dist['11-15'] += 1
        else: p1_dist['16+'] += 1
    for band, cnt in sorted(p1_dist.items()):
        pct = 100 * cnt / len(next_p1s)
        print(f"   {band}: {cnt}/{len(next_p1s)} ({pct:.0f}%)")
    print(f"   Mean next P1 = {sum(next_p1s)/len(next_p1s):.1f}")


# ═══════════════════════════════════════════════════════════
# 5️⃣  STORY-SEED WALK — does a small seed wear N masks
#     across consecutive draws before landing raw?
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("5️⃣  STORY-SEED WALK (seed s appears as raw, +25, ×2, gap)")
print("=" * 80)


def seed_masks(seed):
    """Define the masks of a seed."""
    return {
        'raw': seed,
        'circle': circle(seed),
        'double': in_range(seed * 2),
        'plus21': in_range(seed + 21),
        'minus21': in_range(seed - 21),
        'mirror28': 28 - seed if 0 < 28 - seed <= EURO_MAX else None,
        'mirror56': 56 - seed if 0 < 56 - seed <= EURO_MAX else None,
        'flip': flip_wrap(seed) if seed >= 10 else None,
    }


# For each potential seed (1-25), trace masks across last 12 draws
# Count seeds that wore 4+ masks BEFORE landing raw, then landed raw
seed_walks = defaultdict(list)
for seed in range(1, 26):
    masks = seed_masks(seed)
    walks = []
    for window_start in range(0, len(recent) - 7):
        window = recent[window_start:window_start + 8]
        masks_seen = set()
        landed_raw_at = None
        for j, d in enumerate(window):
            nums = set(d['numbers'])
            if seed in nums and landed_raw_at is None:
                landed_raw_at = j
            for mname, mval in masks.items():
                if mname == 'raw':
                    continue
                if mval and mval in nums:
                    masks_seen.add(mname)
        if landed_raw_at is not None and len(masks_seen) >= 3:
            walks.append({
                'window_start': recent[window_start]['date'],
                'landed_at': landed_raw_at,
                'masks': sorted(masks_seen),
            })
    if walks:
        seed_walks[seed] = walks

print(f"\n📜 Seeds that wore ≥3 masks AND landed raw within 8-draw window:\n")
print(f"   {'seed':<5} {'walks':<7} {'avg_masks':<10} {'avg_raw_d':<10}")
for s in sorted(seed_walks, key=lambda x: -len(seed_walks[x]))[:15]:
    walks = seed_walks[s]
    avg_m = sum(len(w['masks']) for w in walks) / len(walks)
    avg_d = sum(w['landed_at'] for w in walks) / len(walks)
    print(f"   {s:<5} {len(walks):<7} {avg_m:<10.1f} {avg_d:<10.1f}")


# ═══════════════════════════════════════════════════════════
# 6️⃣  THE 33-SIGNATURE FAMILY — how often does a draw
#     express the same nucleus through ≥3 doors AT ONCE?
#     (the exact pattern of 01.05.2026)
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("6️⃣  NUCLEUS-CONVERGENCE (one number through 3+ doors in same draw)")
print("=" * 80)


def find_nucleus(d, prev_d=None, prev2_d=None, prev_stars=None):
    """For a single draw, find numbers that emerge from ≥3 of:
    A) gap (any internal gap = nucleus)
    B) flip-wrap from prev draw P3
    C) circle of any prev star (+25)
    D) sum of P1+P2 (+optional circle)
    E) raw appearance in this draw
    """
    nums = sorted(d['numbers'])
    candidates = defaultdict(list)
    # A) internal gaps
    for j in range(4):
        g = nums[j + 1] - nums[j]
        if 1 <= g <= EURO_MAX:
            candidates[g].append(f'gap{j+1}')
    # B) flip-wrap of prev P3
    if prev_d is not None:
        prev_p3 = sorted(prev_d['numbers'])[2]
        prev2_p3 = sorted(prev2_d['numbers'])[2] if prev2_d else None
        if prev2_p3 is not None:
            s = prev_p3 + prev2_p3
            wrap = s - 50 if s > 50 else (s if 1 <= s <= 50 else None)
            if wrap:
                candidates[wrap].append('flipwrap(prevP3+prev2P3)')
    # C) circle of prev stars
    if prev_stars:
        for s in prev_stars:
            candidates[circle(s)].append(f'circle(⭐{s})')
    # D) sum of P1+P2
    s12 = nums[0] + nums[1]
    if s12 <= EURO_MAX:
        candidates[s12].append('P1+P2')
    if circle(s12) <= EURO_MAX:
        candidates[circle(s12)].append('circle(P1+P2)')
    # E) raw appearance
    for n in nums:
        candidates[n].append('raw')
    return candidates


nucleus_events = []
for i in range(2, len(recent)):
    cur = recent[i]
    prev = recent[i - 1]
    prev2 = recent[i - 2]
    cands = find_nucleus(cur, prev, prev2, prev['stars'])
    # Find candidates with 3+ doors
    triple = {n: doors for n, doors in cands.items() if len(set(doors)) >= 3}
    if triple:
        nucleus_events.append({
            'date': cur['date'], 'nums': sorted(cur['numbers']),
            'nuclei': triple,
        })

print(f"\n   {len(nucleus_events)} draws had a nucleus with ≥3 independent doors "
      f"({100*len(nucleus_events)/len(recent):.1f}% of last 2yrs)\n")

# Show last 10 examples
print("   Recent examples (last 10):")
for ev in nucleus_events[-10:]:
    print(f"\n   {ev['date']}  {ev['nums']}")
    for n, doors in ev['nuclei'].items():
        marker = '🔥' if len(set(doors)) >= 4 else ''
        print(f"      nucleus {n:>2}: {len(set(doors))} doors → "
              f"{', '.join(doors)} {marker}")


print("\n🎻 Story-Seed audit complete. Discuss before any E adjustments.\n")
