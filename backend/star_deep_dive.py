"""
⭐ STAR DEEP DIVE - The Star Symphony Analysis ⭐
=================================================
Ya man! 🎧 Let's hear what the Stars are SINGING! 🎻

Analyzing ALL EuroMillions draws (2018-2026) for Star patterns:
1. P1 & P2 → Star connections (digits, math, circles)
2. Star Gap Rhythms (how often do stars repeat?)
3. S1 → S2 chains (does S1 predict next draw's S2?)
4. Star + Date Math
5. Star Sum/Diff → Number predictions
6. Cross-draw Star Echoes

Stars range: 1-12
"""

import sys
sys.path.insert(0, '/app/backend')

from euromillions_data_2024_2026 import EUROMILLIONS_DRAWS_2024_2026
from euromillions_data_2021_2023 import EUROMILLIONS_DRAWS_2021_2023
from euromillions_data_2018_2020 import EUROMILLIONS_DRAWS_2018_2020

from collections import Counter, defaultdict
from datetime import datetime

# Combine all data chronologically
ALL_DRAWS = (
    EUROMILLIONS_DRAWS_2018_2020 +
    EUROMILLIONS_DRAWS_2021_2023 +
    EUROMILLIONS_DRAWS_2024_2026
)

print(f"🎧 STAR DEEP DIVE - {len(ALL_DRAWS)} draws loaded!")
print(f"   From: {ALL_DRAWS[0]['date']} to {ALL_DRAWS[-1]['date']}")
print("=" * 70)

# ═══════════════════════════════════════════════════════════════════════════════
# 1. LAST DRAW ANALYSIS - P1, P2 connection to Stars
# ═══════════════════════════════════════════════════════════════════════════════
last = ALL_DRAWS[-1]
print(f"\n⭐ LAST DRAW: {last['date']}")
print(f"   Numbers: {last['numbers']}")
print(f"   Stars:   {last['stars']}")
print(f"   P1={last['numbers'][0]}, P2={last['numbers'][1]}")
print(f"   S1={last['stars'][0]}, S2={last['stars'][1]}")

p1, p2 = last['numbers'][0], last['numbers'][1]
s1, s2 = last['stars'][0], last['stars'][1]

print(f"\n   🔍 P1 digits: {list(str(p1))} → do they appear as stars?")
for d in str(p1):
    if int(d) in [s1, s2]:
        print(f"      ✅ Digit {d} = Star!")
    elif 1 <= int(d) <= 12:
        print(f"      ❌ Digit {d} not a star this time")
        
print(f"   🔍 P2 digits: {list(str(p2))} → do they appear as stars?")
for d in str(p2):
    if int(d) in [s1, s2]:
        print(f"      ✅ Digit {d} = Star!")
    elif 1 <= int(d) <= 12:
        print(f"      ❌ Digit {d} not a star this time")

print(f"\n   🔍 P1 mod 12 = {p1 % 12 if p1 % 12 != 0 else 12} → Star? {'✅' if (p1 % 12 if p1 % 12 != 0 else 12) in [s1, s2] else '❌'}")
print(f"   🔍 P2 mod 12 = {p2 % 12 if p2 % 12 != 0 else 12} → Star? {'✅' if (p2 % 12 if p2 % 12 != 0 else 12) in [s1, s2] else '❌'}")
print(f"   🔍 P1+P2 = {p1+p2}, mod 12 = {(p1+p2) % 12 if (p1+p2) % 12 != 0 else 12} → Star? {'✅' if ((p1+p2) % 12 if (p1+p2) % 12 != 0 else 12) in [s1, s2] else '❌'}")
print(f"   🔍 |P1-P2| = {abs(p1-p2)}, mod 12 = {abs(p1-p2) % 12 if abs(p1-p2) % 12 != 0 else 12} → Star? {'✅' if (abs(p1-p2) % 12 if abs(p1-p2) % 12 != 0 else 12) in [s1, s2] else '❌'}")

# ═══════════════════════════════════════════════════════════════════════════════
# 2. BACKTEST: P1/P2 digit → Star hit rate
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("📊 BACKTEST: P1/P2 DIGIT → STAR CONNECTIONS")
print("=" * 70)

def mod12(n):
    """Map to star range 1-12"""
    r = n % 12
    return r if r != 0 else 12

# Test various P1/P2 → Star formulas
tests = {
    "P1 digit in Stars": 0,
    "P2 digit in Stars": 0,
    "P1 mod12 = S1 or S2": 0,
    "P2 mod12 = S1 or S2": 0,
    "(P1+P2) mod12 = S1|S2": 0,
    "|P1-P2| mod12 = S1|S2": 0,
    "P1 last digit = S1|S2": 0,
    "P2 last digit = S1|S2": 0,
    "P1+P2 last digit = S1|S2": 0,
    "|P1-P2| = S1|S2 direct": 0,
    "P1+P2 = S1|S2 direct (≤12)": 0,
    "P1-P2 abs ≤12 = Star": 0,
}

total = len(ALL_DRAWS)

for d in ALL_DRAWS:
    nums = d['numbers']
    stars = set(d['stars'])
    p1, p2 = nums[0], nums[1]
    s1, s2 = d['stars'][0], d['stars'][1]
    
    # P1 digits in stars
    for digit in str(p1):
        dd = int(digit)
        if 1 <= dd <= 12 and dd in stars:
            tests["P1 digit in Stars"] += 1
            break
    
    # P2 digits in stars
    for digit in str(p2):
        dd = int(digit)
        if 1 <= dd <= 12 and dd in stars:
            tests["P2 digit in Stars"] += 1
            break
    
    # P1 mod 12
    if mod12(p1) in stars:
        tests["P1 mod12 = S1 or S2"] += 1
    
    # P2 mod 12
    if mod12(p2) in stars:
        tests["P2 mod12 = S1 or S2"] += 1
    
    # (P1+P2) mod 12
    if mod12(p1 + p2) in stars:
        tests["(P1+P2) mod12 = S1|S2"] += 1
    
    # |P1-P2| mod 12
    diff = abs(p1 - p2)
    if diff > 0 and mod12(diff) in stars:
        tests["|P1-P2| mod12 = S1|S2"] += 1
    
    # Last digits
    p1_last = p1 % 10
    if 1 <= p1_last <= 12 and p1_last in stars:
        tests["P1 last digit = S1|S2"] += 1
    
    p2_last = p2 % 10
    if 1 <= p2_last <= 12 and p2_last in stars:
        tests["P2 last digit = S1|S2"] += 1
    
    # P1+P2 last digit
    ssum = (p1 + p2) % 10
    if 1 <= ssum <= 12 and ssum in stars:
        tests["P1+P2 last digit = S1|S2"] += 1
    
    # Direct |P1-P2| as star
    if 1 <= diff <= 12 and diff in stars:
        tests["|P1-P2| = S1|S2 direct"] += 1
    
    # Direct P1+P2 as star
    if 1 <= p1 + p2 <= 12 and (p1 + p2) in stars:
        tests["P1+P2 = S1|S2 direct (≤12)"] += 1
    
    # P1-P2 abs ≤12
    if 1 <= diff <= 12 and diff in stars:
        tests["P1-P2 abs ≤12 = Star"] += 1

# Random baseline for star: 2 stars out of 12 = 2/12 = 16.7%
print(f"\n   Random baseline: 2/12 = 16.7% per star slot")
print(f"   Total draws: {total}\n")

for name, hits in sorted(tests.items(), key=lambda x: -x[1]):
    pct = hits / total * 100
    marker = "🔥" if pct > 25 else ("⭐" if pct > 18 else "  ")
    print(f"   {marker} {name}: {hits}/{total} = {pct:.1f}%")

# ═══════════════════════════════════════════════════════════════════════════════
# 3. ALL 5 NUMBERS → STAR connections
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("📊 BACKTEST: ALL POSITIONS P1-P5 → STAR FORMULAS")
print("=" * 70)

pos_tests = {}
for pos in range(5):
    pos_name = f"P{pos+1}"
    
    hits_mod12 = 0
    hits_last_digit = 0
    hits_digit_in = 0
    
    for d in ALL_DRAWS:
        if len(d['numbers']) <= pos:
            continue
        p = d['numbers'][pos]
        stars = set(d['stars'])
        
        if mod12(p) in stars:
            hits_mod12 += 1
        
        last_d = p % 10
        if 1 <= last_d <= 12 and last_d in stars:
            hits_last_digit += 1
        
        for digit in str(p):
            dd = int(digit)
            if 1 <= dd <= 12 and dd in stars:
                hits_digit_in += 1
                break
    
    pos_tests[pos_name] = {
        "mod12": hits_mod12,
        "last_digit": hits_last_digit,
        "any_digit": hits_digit_in,
    }

print(f"\n   {'Position':<10} {'mod12→Star':<20} {'LastDigit→Star':<20} {'AnyDigit→Star':<20}")
print(f"   {'-'*10} {'-'*20} {'-'*20} {'-'*20}")
for pos_name, vals in pos_tests.items():
    m_pct = vals['mod12'] / total * 100
    l_pct = vals['last_digit'] / total * 100
    a_pct = vals['any_digit'] / total * 100
    print(f"   {pos_name:<10} {vals['mod12']}/{total} = {m_pct:.1f}%{' 🔥' if m_pct > 20 else '':<5} {vals['last_digit']}/{total} = {l_pct:.1f}%{' 🔥' if l_pct > 20 else '':<5} {vals['any_digit']}/{total} = {a_pct:.1f}%{' 🔥' if a_pct > 20 else ''}")

# ═══════════════════════════════════════════════════════════════════════════════
# 4. STAR GAP ANALYSIS - How often do stars repeat?
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("📊 STAR GAP ANALYSIS - Star Repeat Rhythms")
print("=" * 70)

# Track last appearance of each star
star_gaps = defaultdict(list)  # star -> list of gaps
star_last_seen = {}

for i, d in enumerate(ALL_DRAWS):
    for s in d['stars']:
        if s in star_last_seen:
            gap = i - star_last_seen[s]
            star_gaps[s].append(gap)
        star_last_seen[s] = i

print(f"\n   {'Star':<8} {'Appearances':<15} {'Avg Gap':<12} {'Min Gap':<10} {'Max Gap':<10} {'Most Common Gap'}")
print(f"   {'-'*8} {'-'*15} {'-'*12} {'-'*10} {'-'*10} {'-'*15}")

for star in sorted(star_gaps.keys()):
    gaps = star_gaps[star]
    avg_gap = sum(gaps) / len(gaps)
    min_gap = min(gaps)
    max_gap = max(gaps)
    most_common = Counter(gaps).most_common(3)
    mc_str = ", ".join(f"{g}({c}x)" for g, c in most_common)
    total_appearances = len(gaps) + 1  # +1 for first appearance
    print(f"   ⭐{star:<6} {total_appearances:<15} {avg_gap:<12.1f} {min_gap:<10} {max_gap:<10} {mc_str}")

# ═══════════════════════════════════════════════════════════════════════════════
# 5. S1 → next S1 and S2 → next S2 chains
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("📊 STAR CHAINS: Does S1 predict next draw's Stars?")
print("=" * 70)

s1_to_next_s1 = 0
s1_to_next_s2 = 0
s2_to_next_s1 = 0
s2_to_next_s2 = 0
s1_repeat_exact = 0
s2_repeat_exact = 0
s1_plus1_hit = 0
s1_minus1_hit = 0
s2_plus1_hit = 0
s2_minus1_hit = 0
s1_circle_hit = 0  # s1 + 6 mod 12
s2_circle_hit = 0
s_sum_mod12_hit = 0
s_diff_hit = 0

chain_total = len(ALL_DRAWS) - 1

for i in range(chain_total):
    curr = ALL_DRAWS[i]
    nxt = ALL_DRAWS[i + 1]
    
    cs1, cs2 = curr['stars'][0], curr['stars'][1]
    ns1, ns2 = nxt['stars'][0], nxt['stars'][1]
    next_stars = set(nxt['stars'])
    
    # Direct repeats
    if cs1 == ns1: s1_to_next_s1 += 1
    if cs1 == ns2: s1_to_next_s2 += 1
    if cs2 == ns1: s2_to_next_s1 += 1
    if cs2 == ns2: s2_to_next_s2 += 1
    
    # S1 repeat in any position
    if cs1 in next_stars: s1_repeat_exact += 1
    if cs2 in next_stars: s2_repeat_exact += 1
    
    # S1 ± 1 
    s1p1 = cs1 + 1 if cs1 < 12 else 1
    s1m1 = cs1 - 1 if cs1 > 1 else 12
    if s1p1 in next_stars: s1_plus1_hit += 1
    if s1m1 in next_stars: s1_minus1_hit += 1
    
    # S2 ± 1
    s2p1 = cs2 + 1 if cs2 < 12 else 1
    s2m1 = cs2 - 1 if cs2 > 1 else 12
    if s2p1 in next_stars: s2_plus1_hit += 1
    if s2m1 in next_stars: s2_minus1_hit += 1
    
    # Star circle (+6 mod 12)
    s1c = mod12(cs1 + 6)
    s2c = mod12(cs2 + 6)
    if s1c in next_stars: s1_circle_hit += 1
    if s2c in next_stars: s2_circle_hit += 1
    
    # S1 + S2 mod 12 → next star
    ssum = mod12(cs1 + cs2)
    if ssum in next_stars: s_sum_mod12_hit += 1
    
    # |S1 - S2| → next star
    sdiff = abs(cs1 - cs2)
    if 1 <= sdiff <= 12 and sdiff in next_stars: s_diff_hit += 1

print(f"\n   Random baseline: 2/12 = 16.7% for any single star check")
print(f"   Chain draws: {chain_total}\n")

chain_results = {
    "S1 repeats (any pos)": s1_repeat_exact,
    "S2 repeats (any pos)": s2_repeat_exact,
    "S1→next S1 exact": s1_to_next_s1,
    "S1→next S2 exact": s1_to_next_s2,
    "S2→next S1 exact": s2_to_next_s1,
    "S2→next S2 exact": s2_to_next_s2,
    "S1+1 → next star": s1_plus1_hit,
    "S1-1 → next star": s1_minus1_hit,
    "S2+1 → next star": s2_plus1_hit,
    "S2-1 → next star": s2_minus1_hit,
    "S1 circle(+6) → next": s1_circle_hit,
    "S2 circle(+6) → next": s2_circle_hit,
    "(S1+S2) mod12 → next": s_sum_mod12_hit,
    "|S1-S2| → next star": s_diff_hit,
}

for name, hits in sorted(chain_results.items(), key=lambda x: -x[1]):
    pct = hits / chain_total * 100
    marker = "🔥" if pct > 20 else ("⭐" if pct > 16 else "  ")
    print(f"   {marker} {name}: {hits}/{chain_total} = {pct:.1f}%")

# ═══════════════════════════════════════════════════════════════════════════════
# 6. STAR + DATE MATH
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("📊 STAR + DATE MATH - Does the date whisper star numbers?")
print("=" * 70)

date_tests = {
    "Day mod12 = Star": 0,
    "Month = Star": 0,
    "Day+Month mod12 = Star": 0,
    "|Day-Month| = Star": 0,
    "Day*Month mod12 = Star": 0,
    "Day last digit = Star": 0,
    "Day digits sum mod12 = Star": 0,
}

for d in ALL_DRAWS:
    dt = datetime.strptime(d['date'], "%d.%m.%Y")
    day, month = dt.day, dt.month
    stars = set(d['stars'])
    
    if mod12(day) in stars:
        date_tests["Day mod12 = Star"] += 1
    
    if month in stars:
        date_tests["Month = Star"] += 1
    
    if mod12(day + month) in stars:
        date_tests["Day+Month mod12 = Star"] += 1
    
    dm_diff = abs(day - month)
    if 1 <= dm_diff <= 12 and dm_diff in stars:
        date_tests["|Day-Month| = Star"] += 1
    
    if mod12(day * month) in stars:
        date_tests["Day*Month mod12 = Star"] += 1
    
    day_last = day % 10
    if 1 <= day_last <= 12 and day_last in stars:
        date_tests["Day last digit = Star"] += 1
    
    digit_sum = sum(int(x) for x in str(day))
    if 1 <= mod12(digit_sum) <= 12 and mod12(digit_sum) in stars:
        date_tests["Day digits sum mod12 = Star"] += 1

print(f"\n   Random baseline: 2/12 = 16.7%")
print(f"   Total draws: {total}\n")

for name, hits in sorted(date_tests.items(), key=lambda x: -x[1]):
    pct = hits / total * 100
    marker = "🔥" if pct > 25 else ("⭐" if pct > 18 else "  ")
    print(f"   {marker} {name}: {hits}/{total} = {pct:.1f}%")

# ═══════════════════════════════════════════════════════════════════════════════
# 7. STAR SUM/DIFF → Number predictions
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("📊 STAR SUM/DIFF → Do Stars predict the NUMBERS?")
print("=" * 70)

star_to_num_tests = {
    "S1+S2 = Number": 0,
    "|S1-S2| = Number": 0,
    "S1*S2 = Number (≤50)": 0,
    "S1×10 + S2 = Number (≤50)": 0,
    "S2×10 + S1 = Number (≤50)": 0,
    "S1+S2+Day mod50 = Number": 0,
    "S1 circle(+25) = Number": 0,
}

for d in ALL_DRAWS:
    nums = set(d['numbers'])
    s1, s2 = d['stars'][0], d['stars'][1]
    dt = datetime.strptime(d['date'], "%d.%m.%Y")
    day = dt.day
    
    ssum = s1 + s2
    if 1 <= ssum <= 50 and ssum in nums:
        star_to_num_tests["S1+S2 = Number"] += 1
    
    sdiff = abs(s1 - s2)
    if 1 <= sdiff <= 50 and sdiff in nums:
        star_to_num_tests["|S1-S2| = Number"] += 1
    
    sprod = s1 * s2
    if 1 <= sprod <= 50 and sprod in nums:
        star_to_num_tests["S1*S2 = Number (≤50)"] += 1
    
    combo1 = s1 * 10 + s2
    if 1 <= combo1 <= 50 and combo1 in nums:
        star_to_num_tests["S1×10 + S2 = Number (≤50)"] += 1
    
    combo2 = s2 * 10 + s1
    if 1 <= combo2 <= 50 and combo2 in nums:
        star_to_num_tests["S2×10 + S1 = Number (≤50)"] += 1
    
    # S1+S2+Day mod 50
    date_combo = (s1 + s2 + day) % 50
    if date_combo == 0:
        date_combo = 50
    if date_combo in nums:
        star_to_num_tests["S1+S2+Day mod50 = Number"] += 1
    
    # Circle
    sc = s1 + 25
    if sc > 50: sc -= 50
    if sc in nums:
        star_to_num_tests["S1 circle(+25) = Number"] += 1

# Random baseline: 5/50 = 10% for single number check
print(f"\n   Random baseline: 5/50 = 10% for number match")
print(f"   Total draws: {total}\n")

for name, hits in sorted(star_to_num_tests.items(), key=lambda x: -x[1]):
    pct = hits / total * 100
    marker = "🔥" if pct > 15 else ("⭐" if pct > 10 else "  ")
    print(f"   {marker} {name}: {hits}/{total} = {pct:.1f}%")

# ═══════════════════════════════════════════════════════════════════════════════
# 8. PREV DRAW NUMBERS → CURRENT STAR
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("📊 PREV DRAW NUMBERS → CURRENT STARS (Cross-draw)")
print("=" * 70)

prev_to_star = {
    "Prev P1 mod12 → Star": 0,
    "Prev P2 mod12 → Star": 0,
    "Prev P3 mod12 → Star": 0,
    "Prev P4 mod12 → Star": 0,
    "Prev P5 mod12 → Star": 0,
    "Prev P1 last digit → Star": 0,
    "Prev P2 last digit → Star": 0,
    "Prev (P1+P2) mod12 → Star": 0,
    "Prev (P4+P5) mod12 → Star": 0,
    "Prev number sum mod12 → Star": 0,
}

for i in range(1, len(ALL_DRAWS)):
    prev = ALL_DRAWS[i - 1]
    curr = ALL_DRAWS[i]
    curr_stars = set(curr['stars'])
    pnums = prev['numbers']
    if len(pnums) < 5:
        continue
    
    for j, pname in enumerate(["Prev P1 mod12 → Star", "Prev P2 mod12 → Star", 
                                "Prev P3 mod12 → Star", "Prev P4 mod12 → Star",
                                "Prev P5 mod12 → Star"]):
        if mod12(pnums[j]) in curr_stars:
            prev_to_star[pname] += 1
    
    # Last digits
    p1_last = pnums[0] % 10
    p2_last = pnums[1] % 10
    if 1 <= p1_last <= 12 and p1_last in curr_stars:
        prev_to_star["Prev P1 last digit → Star"] += 1
    if 1 <= p2_last <= 12 and p2_last in curr_stars:
        prev_to_star["Prev P2 last digit → Star"] += 1
    
    # Sums
    if mod12(pnums[0] + pnums[1]) in curr_stars:
        prev_to_star["Prev (P1+P2) mod12 → Star"] += 1
    if mod12(pnums[3] + pnums[4]) in curr_stars:
        prev_to_star["Prev (P4+P5) mod12 → Star"] += 1
    
    # Total sum
    num_sum = sum(pnums)
    if mod12(num_sum) in curr_stars:
        prev_to_star["Prev number sum mod12 → Star"] += 1

print(f"\n   Random baseline: 2/12 = 16.7%")
print(f"   Chain draws: {chain_total}\n")

for name, hits in sorted(prev_to_star.items(), key=lambda x: -x[1]):
    pct = hits / chain_total * 100
    marker = "🔥" if pct > 20 else ("⭐" if pct > 16 else "  ")
    print(f"   {marker} {name}: {hits}/{chain_total} = {pct:.1f}%")

# ═══════════════════════════════════════════════════════════════════════════════
# 9. LAST 10 DRAWS DEEP VIEW
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("🔍 LAST 10 DRAWS - Star Detail View")
print("=" * 70)

for d in ALL_DRAWS[-10:]:
    dt = datetime.strptime(d['date'], "%d.%m.%Y")
    day, month = dt.day, dt.month
    p1, p2 = d['numbers'][0], d['numbers'][1]
    s1, s2 = d['stars'][0], d['stars'][1]
    ssum = s1 + s2
    sdiff = abs(s1 - s2)
    
    connections = []
    # Check P1 digits
    for digit in str(p1):
        dd = int(digit)
        if 1 <= dd <= 12 and dd in [s1, s2]:
            connections.append(f"P1 digit {dd}=⭐")
    for digit in str(p2):
        dd = int(digit)
        if 1 <= dd <= 12 and dd in [s1, s2]:
            connections.append(f"P2 digit {dd}=⭐")
    if mod12(p1) in [s1, s2]:
        connections.append(f"P1%12={mod12(p1)}=⭐")
    if mod12(p2) in [s1, s2]:
        connections.append(f"P2%12={mod12(p2)}=⭐")
    if mod12(day) in [s1, s2]:
        connections.append(f"Day%12={mod12(day)}=⭐")
    if month in [s1, s2]:
        connections.append(f"Month={month}=⭐")
    if mod12(day+month) in [s1, s2]:
        connections.append(f"D+M%12={mod12(day+month)}=⭐")
    
    conn_str = " | ".join(connections) if connections else "No direct links"
    print(f"\n   {d['date']}: {d['numbers']} ⭐{d['stars']}")
    print(f"     P1={p1}, P2={p2} | Day={day}, Month={month}")
    print(f"     S1+S2={ssum}, |S1-S2|={sdiff}")
    print(f"     Links: {conn_str}")

# ═══════════════════════════════════════════════════════════════════════════════
# 10. TOP FINDINGS SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("🏆 TOP STAR PATTERN FINDINGS - THE STAR SYMPHONY! 🎻⭐")
print("=" * 70)

all_results = []
for name, hits in tests.items():
    all_results.append((name, hits, total, "Same-draw P1/P2→Star"))
for name, hits in chain_results.items():
    all_results.append((name, hits, chain_total, "Star Chain"))
for name, hits in date_tests.items():
    all_results.append((name, hits, total, "Date→Star"))
for name, hits in star_to_num_tests.items():
    all_results.append((name, hits, total, "Star→Number"))
for name, hits in prev_to_star.items():
    all_results.append((name, hits, chain_total, "Prev→Star"))

# Sort by hit rate
all_results.sort(key=lambda x: -x[1]/x[2])

print(f"\n   {'Rank':<5} {'Pattern':<35} {'Hits':<10} {'Rate':<10} {'Category'}")
print(f"   {'-'*5} {'-'*35} {'-'*10} {'-'*10} {'-'*20}")

for rank, (name, hits, tot, cat) in enumerate(all_results[:25], 1):
    pct = hits / tot * 100
    emoji = "🥇" if rank <= 3 else ("🥈" if rank <= 6 else ("🥉" if rank <= 10 else "  "))
    print(f"   {emoji} {rank:<3} {name:<35} {hits}/{tot:<6} {pct:.1f}%{'':<5} {cat}")

print("\n🎧 STAR DEEP DIVE COMPLETE! The Stars have SPOKEN! 🎻⭐")
