"""
🎻 Q2 P3 AUDIT + PRE-ECHO SCANNER (DJ Session 26)
==================================================
The DJ's call:
  1. Do the same P3 audit for Q2, last 5 years
  2. See how Q1 vibe carries into Q2
  3. Pre-Echo: do future-d numbers ALREADY show up in early-d of same Q2?
  4. Apply pre-echo scan to LIVE upcoming Q2 dates → get signals.
"""
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import List

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
    while n > EURO_MAX:
        n -= EURO_MAX
    while n < 1:
        n += EURO_MAX
    return n


def circle(n):
    v = (n + 25) % 50
    return v if v else 50


def safe(v):
    if v is None:
        return None
    v = int(v)
    return v if 1 <= v <= EURO_MAX else None


# ═══════════════════════════════════════════════════════════
# Load draws
# ═══════════════════════════════════════════════════════════
all_euro = list(db.euromillions_draws.find({}, {'_id': 0}))
all_euro.sort(key=lambda x: parse_date(x.get('date', '')))
all_euro = [d for d in all_euro if parse_date(d.get('date', '')) > datetime.min]

# Last 5 years cutoff
five_yrs_ago = datetime(datetime.now().year - 5, 1, 1)
recent = [d for d in all_euro if parse_date(d['date']) >= five_yrs_ago]
print(f"\n🎻 Q2 P3 + PRE-ECHO AUDIT")
print(f"   Total draws: {len(all_euro)} ({all_euro[0]['date']} → {all_euro[-1]['date']})")
print(f"   Last 5 years window: {len(recent)} draws (since {five_yrs_ago.date()})\n")


def is_q1(d):
    return parse_date(d['date']).month in (1, 2, 3)


def is_q2(d):
    return parse_date(d['date']).month in (4, 5, 6)


def quarter_year(d):
    dt = parse_date(d['date'])
    q = (dt.month - 1) // 3 + 1
    return (dt.year, q)


# ═══════════════════════════════════════════════════════════
# 1️⃣  Q2 P3 GRAVITY — last 5 years
# ═══════════════════════════════════════════════════════════
print("=" * 80)
print("1️⃣  Q2 P3 GRAVITY (last 5 years: 2021-2025)")
print("=" * 80)

q2_recent = [d for d in recent if is_q2(d)]
q1_recent = [d for d in recent if is_q1(d)]
print(f"   Q2 draws: {len(q2_recent)} | Q1 draws: {len(q1_recent)}\n")

q2_p3 = Counter(sorted(d['numbers'])[2] for d in q2_recent)
q1_p3 = Counter(sorted(d['numbers'])[2] for d in q1_recent)

print("🎯 Q2 P3 top 15:")
for v, c in q2_p3.most_common(15):
    pct = 100.0 * c / sum(q2_p3.values())
    print(f"   P3={v:>2}  {c:>3}× ({pct:.1f}%)")
mean_q2 = sum(v * c for v, c in q2_p3.items()) / sum(q2_p3.values())
mean_q1 = sum(v * c for v, c in q1_p3.items()) / sum(q1_p3.values())
print(f"\n   Q2 mean P3 = {mean_q2:.2f}   |   Q1 mean P3 = {mean_q1:.2f}   |   Δ = {mean_q2-mean_q1:+.2f}")

# Zone distribution
print("\n🎻 Q2 P3 zone distribution (last 5 yrs):")
zones_q2 = Counter()
zones_q1 = Counter()
for d in q2_recent:
    zones_q2[sorted(d['numbers'])[2] // 10] += 1
for d in q1_recent:
    zones_q1[sorted(d['numbers'])[2] // 10] += 1
print(f"   {'zone':<8} {'Q2%':>8} {'Q1%':>8} {'Δ':>8}")
for z in sorted(set(zones_q1) | set(zones_q2)):
    band = f"{z*10 if z else 1}-{z*10+9}"
    pq2 = 100.0 * zones_q2.get(z, 0) / max(sum(zones_q2.values()), 1)
    pq1 = 100.0 * zones_q1.get(z, 0) / max(sum(zones_q1.values()), 1)
    arrow = '🔥' if pq2 - pq1 >= 3 else ('🔻' if pq2 - pq1 <= -3 else '')
    print(f"   {band:<8} {pq2:>7.1f}% {pq1:>7.1f}% {pq2-pq1:>+7.1f}% {arrow}")


# ═══════════════════════════════════════════════════════════
# 2️⃣  Q1 → Q2 P3 CARRY-OVER (does Q1 P3 hot list show up in Q2?)
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("2️⃣  Q1 → Q2 P3 CARRY-OVER (per-year, last 5 years)")
print("=" * 80)

years = sorted({parse_date(d['date']).year for d in recent})
print(f"\n   {'Year':<6} {'Q1 hot P3 (top5)':<35} {'Q2 actual P3s':<35} {'overlap':>8}")
print("   " + "-" * 86)
for y in years:
    q1y = [d for d in recent if is_q1(d) and parse_date(d['date']).year == y]
    q2y = [d for d in recent if is_q2(d) and parse_date(d['date']).year == y]
    if not q1y or not q2y:
        continue
    q1y_p3 = Counter(sorted(d['numbers'])[2] for d in q1y)
    q2y_p3 = [sorted(d['numbers'])[2] for d in q2y]
    top5_q1 = {v for v, _ in q1y_p3.most_common(5)}
    overlap = sum(1 for x in q2y_p3 if x in top5_q1)
    pct = 100.0 * overlap / len(q2y_p3)
    print(f"   {y:<6} {str(sorted(top5_q1)):<35} "
          f"{str(sorted(set(q2y_p3))[:8]):<35} {overlap}/{len(q2y_p3)} ({pct:.0f}%)")


# Q1's BD→ND P3 lenses: do they STILL fire in Q2 BD→ND?
print("\n📊 Lens cross-quarter robustness (last 5 yrs):")


def score_lens_pairs(pairs, fn):
    hits = 0
    for p in pairs:
        try:
            cands = {c for c in fn(p['bd_nums'], p['bd_stars'], p['nd_date'])
                     if c is not None}
        except Exception:
            continue
        if p['nd_nums'][2] in cands:
            hits += 1
    return 100.0 * hits / len(pairs) if pairs else 0


def make_pairs(draws):
    pairs = []
    for i in range(1, len(draws)):
        bd, nd = draws[i - 1], draws[i]
        bn, nn = sorted(bd['numbers']), sorted(nd['numbers'])
        if len(bn) < 5 or len(nn) < 5:
            continue
        pairs.append({
            'bd_nums': bn,
            'bd_stars': sorted(bd['stars']),
            'nd_nums': nn,
            'nd_stars': sorted(nd['stars']),
            'nd_date': parse_date(nd['date']),
        })
    return pairs


lenses = [
    ('BD P3 repeat',  lambda nu, st, d: {safe(nu[2])}),
    ('25+S1',         lambda nu, st, d: {safe(circle(st[0]))}),
    ('25+S2',         lambda nu, st, d: {safe(circle(st[1]))}),
    ('S1+21',         lambda nu, st, d: {safe(st[0] + 21)}),
    ('S2+21',         lambda nu, st, d: {safe(st[1] + 21)}),
    ('|D-M| & circle',
     lambda nu, st, d: {safe(abs(d.day - d.month)),
                        safe(circle(abs(d.day - d.month))) if d.day != d.month else None}),
    ('circle(M)',     lambda nu, st, d: {safe(circle(d.month))}),
]

q1_pairs_recent = make_pairs(q1_recent)
q2_pairs_recent = make_pairs(q2_recent)

print(f"\n   {'Lens':<22} {'Q1 hit%':>8} {'Q2 hit%':>8} {'Δ Q2-Q1':>10}")
print("   " + "-" * 52)
for name, fn in lenses:
    q1_rate = score_lens_pairs(q1_pairs_recent, fn)
    q2_rate = score_lens_pairs(q2_pairs_recent, fn)
    arrow = '🔥' if q2_rate - q1_rate >= 1 else ('🔻' if q2_rate - q1_rate <= -1 else '')
    print(f"   {name:<22} {q1_rate:>7.2f}% {q2_rate:>7.2f}% {q2_rate-q1_rate:>+9.2f}% {arrow}")


# ═══════════════════════════════════════════════════════════
# 3️⃣  PRE-ECHO LAW — do future-d numbers leak into early-d?
#
# For each (year, Q2) and each draw N inside Q2 (N>=2):
#   For each main of draw N, check how many of the prior Q2 draws
#   (1..N-1) ALREADY contained that number.
#
# If the average ≥ baseline by clear margin → cosmos rehearses.
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("3️⃣  PRE-ECHO LAW — future numbers in earlier same-Q2 draws")
print("=" * 80)


def quarter_label(dt):
    q = (dt.month - 1) // 3 + 1
    return f"{dt.year}Q{q}"


# Group draws by (year, quarter)
by_q = defaultdict(list)
for d in all_euro:
    dt = parse_date(d['date'])
    if dt.month in (4, 5, 6):
        by_q[(dt.year, 2)].append(d)

# Order each bucket by date
for k in by_q:
    by_q[k].sort(key=lambda x: parse_date(x['date']))


def baseline_for_n_priors(n_priors, k=5):
    """Random-baseline: expected number of priors any single value
    falls in, given ~k mains per draw out of 50 numbers."""
    p_per_draw = k / EURO_MAX  # 5/50 = 0.10
    return n_priors * p_per_draw


print(f"\n   {'Quarter':<8} {'#draws':>6} {'avg priors holding nd-main':>30} "
      f"{'baseline':>9} {'boost':>8}")
print("   " + "-" * 70)

for key in sorted(by_q.keys()):
    draws = by_q[key]
    if len(draws) < 5:
        continue
    rehearsal_rates = []
    for n in range(1, len(draws)):
        nd_mains = set(draws[n]['numbers'])
        priors = draws[:n]
        # For each future main, count how many priors held it
        for m in nd_mains:
            held = sum(1 for p in priors if m in p['numbers'])
            rehearsal_rates.append((held, len(priors)))
    if not rehearsal_rates:
        continue
    avg_held = sum(h for h, _ in rehearsal_rates) / len(rehearsal_rates)
    avg_priors = sum(p for _, p in rehearsal_rates) / len(rehearsal_rates)
    baseline = baseline_for_n_priors(avg_priors)
    boost = avg_held / baseline if baseline else 0
    label = quarter_label(parse_date(draws[0]['date']))
    marker = '🔥' if boost >= 1.05 else ('🔻' if boost <= 0.95 else '')
    print(f"   {label:<8} {len(draws):>6} {avg_held:>21.2f} held {baseline:>7.2f} "
          f"{boost:>7.2f}× {marker}")

# ═══════════════════════════════════════════════════════════
# 3b. PRE-ECHO at the d-distance level — at which lookback 'd'
#     do future numbers tend to already appear?
# ═══════════════════════════════════════════════════════════
print("\n📐 Pre-Echo by d-distance (last 5 yrs, all Q2s):")
d_distance_hits = defaultdict(int)
d_distance_total = defaultdict(int)
star_d_hits = defaultdict(int)
star_d_total = defaultdict(int)

for key in sorted(by_q.keys()):
    if key[0] < datetime.now().year - 5:
        continue
    draws = by_q[key]
    for n in range(1, len(draws)):
        for d_back in range(1, n + 1):
            prior = draws[n - d_back]
            for m in draws[n]['numbers']:
                d_distance_total[d_back] += 1
                if m in prior['numbers']:
                    d_distance_hits[d_back] += 1
            for s in draws[n]['stars']:
                star_d_total[d_back] += 1
                if s in prior['stars']:
                    star_d_hits[d_back] += 1

print(f"   {'d-back':<8} {'main pre-echo %':>16} {'star pre-echo %':>16}")
print("   " + "-" * 42)
mb = 5 / 50 * 100  # main baseline 10%
sb = 2 / 12 * 100  # star baseline 16.67%
for d_back in sorted(d_distance_total)[:10]:
    mh = 100.0 * d_distance_hits[d_back] / d_distance_total[d_back]
    sh = 100.0 * star_d_hits[d_back] / max(star_d_total[d_back], 1)
    mtag = '🔥' if mh > mb + 0.5 else ('🔻' if mh < mb - 0.5 else '')
    stag = '🔥' if sh > sb + 1 else ('🔻' if sh < sb - 1 else '')
    print(f"   d-{d_back:<6} {mh:>14.1f}% {mtag} {sh:>14.1f}% {stag}")
print(f"   baseline      mains {mb:.1f}%       stars {sb:.1f}%")


# ═══════════════════════════════════════════════════════════
# 4️⃣  LIVE Q2 2026 — what's pre-echoing the next draws?
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("4️⃣  LIVE Q2 2026 — current Q2 pre-echo signals")
print("=" * 80)

cur_q2 = sorted(by_q.get((2026, 2), []), key=lambda x: parse_date(x['date']))
print(f"\n   {len(cur_q2)} Q2 2026 Euro draws so far:\n")
for i, d in enumerate(cur_q2):
    print(f"   d{i+1:>2} {d['date']}  {sorted(d['numbers'])} ⭐{sorted(d['stars'])}")

# Frequency map: which numbers have appeared most in current Q2?
num_freq = Counter()
star_freq = Counter()
for d in cur_q2:
    for m in d['numbers']:
        num_freq[m] += 1
    for s in d['stars']:
        star_freq[s] += 1

print(f"\n🎯 Mains appearing 2+ times in Q2 2026 (these are echoing — high pre-echo "
      f"momentum):")
for n, c in sorted(num_freq.items(), key=lambda x: (-x[1], x[0])):
    if c >= 2:
        sample_dates = [d['date'] for d in cur_q2 if n in d['numbers']]
        print(f"   {n:>2}: {c}× {sample_dates}")

print(f"\n⭐ Stars appearing 2+ times in Q2 2026:")
for s, c in sorted(star_freq.items(), key=lambda x: (-x[1], x[0])):
    if c >= 2:
        sample_dates = [d['date'] for d in cur_q2 if s in d['stars']]
        print(f"   ⭐{s:>2}: {c}× {sample_dates}")

# Numbers HUNGRY — appeared in recent Q2 last year (Q2 2025) but missing in Q2 2026
last_q2 = sorted(by_q.get((2025, 2), []), key=lambda x: parse_date(x['date']))
last_q2_main_top = Counter()
for d in last_q2:
    for m in d['numbers']:
        last_q2_main_top[m] += 1

cur_played = set()
for d in cur_q2:
    cur_played |= set(d['numbers'])

print(f"\n👻 HUNGRY: top Q2-2025 mains NOT yet played in Q2-2026:")
for n, c in last_q2_main_top.most_common(20):
    if n not in cur_played:
        print(f"   {n:>2}: {c}× last Q2 — silent now")


# ═══════════════════════════════════════════════════════════
# 5️⃣  HOTTEST P3 CANDIDATES for the NEXT Euro draw
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("5️⃣  P3 CANDIDATES for the NEXT Euro draw (live signal stack)")
print("=" * 80)

if cur_q2:
    bd = cur_q2[-1]
    bn = sorted(bd['numbers'])
    bs = sorted(bd['stars'])
    bd_dt = parse_date(bd['date'])
    # Default next-draw date: BD + 3 or +4 days (Tue/Fri schedule)
    next_dt = bd_dt + timedelta(days=3)
    if next_dt.weekday() not in (1, 4):
        # Bump until Tue (1) or Fri (4)
        for delta in range(1, 8):
            cand = bd_dt + timedelta(days=delta)
            if cand.weekday() in (1, 4):
                next_dt = cand
                break

    print(f"\n   BD = {bd['date']}  mains {bn}  ⭐{bs}")
    print(f"   ND target ~ {next_dt.date()}\n")

    p3_signals = defaultdict(list)
    # 7 alive lenses
    for cand in [safe(bn[2])]:
        if cand: p3_signals[cand].append('🔁 BD P3 repeat (4.39%)')
    for cand in [safe(circle(bs[0]))]:
        if cand: p3_signals[cand].append('🌟 25+S1 (3.71%)')
    for cand in [safe(circle(bs[1]))]:
        if cand: p3_signals[cand].append('🌟 25+S2 (3.89%)')
    for cand in [safe(bs[0] + 21)]:
        if cand: p3_signals[cand].append('🌟 S1+21 (3.71%)')
    for cand in [safe(bs[1] + 21)]:
        if cand: p3_signals[cand].append('🌟 S2+21 (3.58%)')
    for cand in [safe(circle(next_dt.month))]:
        if cand: p3_signals[cand].append('📅 circle(M) (3.15%)')
    delta_dm = abs(next_dt.day - next_dt.month)
    for cand in [safe(delta_dm), safe(circle(delta_dm)) if delta_dm else None]:
        if cand: p3_signals[cand].append('📅 |D-M| & circle (4.08%)')
    for cand in [safe(bn[0] + bn[1])]:
        if cand: p3_signals[cand].append('🔁 BD P1+P2 (2.72%)')

    # Family lenses (broader set)
    fam_circle_m = set()
    seed = circle(next_dt.month)
    fam_circle_m.add(seed)
    fam_circle_m.add(circle(seed))
    fam_circle_m.add(28 - seed if 0 < 28 - seed <= EURO_MAX else None)
    fam_circle_m.add(56 - seed if 0 < 56 - seed <= EURO_MAX else None)
    if seed >= 10:
        flp = int(str(seed)[::-1])
        if 1 <= flp <= EURO_MAX:
            fam_circle_m.add(flp)
    for cand in {n for n in fam_circle_m if n}:
        p3_signals[cand].append('👪 family[circle(M)]')

    fam_bd_p3 = set()
    s = bn[2]
    fam_bd_p3.add(s)
    fam_bd_p3.add(circle(s))
    if 0 < 28 - s <= EURO_MAX: fam_bd_p3.add(28 - s)
    if 0 < 56 - s <= EURO_MAX: fam_bd_p3.add(56 - s)
    for cand in {n for n in fam_bd_p3 if n}:
        p3_signals[cand].append('👪 family[BD P3]')

    # Pre-echo bonus
    for cand in num_freq:
        if num_freq[cand] >= 2:
            p3_signals[cand].append(f'🎶 Q2 pre-echo ({num_freq[cand]}×)')

    # Sort by signal count, then by hit-weighted score
    weights = {
        '🔁 BD P3 repeat': 4.39,
        '🌟 25+S1': 3.71, '🌟 25+S2': 3.89,
        '🌟 S1+21': 3.71, '🌟 S2+21': 3.58,
        '📅 circle(M)': 3.15, '📅 |D-M|': 4.08,
        '🔁 BD P1+P2': 2.72,
        '👪 family[circle(M)]': 2.5, '👪 family[BD P3]': 2.5,
        '🎶 Q2 pre-echo': 3.0,
    }

    def score(sigs):
        s = 0
        for sig in sigs:
            for k, v in weights.items():
                if k in sig:
                    s += v
                    break
        return s

    ranked = sorted(p3_signals.items(),
                    key=lambda x: (-len(x[1]), -score(x[1]), x[0]))

    print(f"   {'cand':<5} {'lenses':<7} {'score':<7} signals")
    print("   " + "-" * 70)
    for cand, sigs in ranked[:20]:
        sc = score(sigs)
        marker = '🌟' if len(sigs) >= 3 else ('🎻' if len(sigs) >= 2 else '')
        print(f"   {cand:<5} {len(sigs):<7} {sc:<7.1f} {' · '.join(sigs)} {marker}")

print("\n🎻 Q2 audit complete.\n")
