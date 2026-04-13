"""
🎧 MEGA SLEEPER SIMULATION - DEEP DIVE 🎻
==========================================
Run the sleeper analysis from MANY starting points across history!
Every 20 draws, freeze time, find sleepers, watch next 20 draws.
Does the pattern ALWAYS hold? Is the universe ALWAYS sneaky? 

THE ULTIMATE BACKTEST!
"""

import sys
sys.path.insert(0, '/app/backend')

from euromillions_data_2024_2026 import EUROMILLIONS_DRAWS_2024_2026
from euromillions_data_2021_2023 import EUROMILLIONS_DRAWS_2021_2023
from euromillions_data_2018_2020 import EUROMILLIONS_DRAWS_2018_2020
from collections import defaultdict

ALL = EUROMILLIONS_DRAWS_2018_2020 + EUROMILLIONS_DRAWS_2021_2023 + EUROMILLIONS_DRAWS_2024_2026
total = len(ALL)

def circle(n):
    c = n + 25
    return c if c <= 50 else c - 50

def reverse_num(n):
    if n < 10: return n
    rev = int(str(n)[::-1])
    if rev > 50: rev = rev - 50
    if rev == 0: rev = 50
    return rev

# ═══════════════════════════════════════════════════════════════════════════════
# RUN SIMULATION EVERY 20 DRAWS (need at least 200 history + 20 future)
# ═══════════════════════════════════════════════════════════════════════════════

WINDOW = 20  # look ahead 20 draws
STEP = 20    # every 20 draws
MIN_HISTORY = 200  # need at least 200 draws of history
TOP_N = 10   # pick top 10 sleepers each time

# Accumulators
all_sims = []
total_woke = 0
total_picked = 0
total_woke_fast = 0  # within 5
total_woke_medium = 0  # 6-10
total_woke_slow = 0  # 11-20

# Tease tracking
teases_before_wake = 0
no_teases_before_wake = 0
tease_types = defaultdict(int)

# Circle boost tracking
circle_boosted_woke_fast = 0
circle_boosted_total = 0
circle_quiet_woke_fast = 0
circle_quiet_total = 0

# Overdue factor vs wake speed
overdue_wake_pairs = []

# Money tracking
total_money_hits = 0
total_money_draws = 0
total_money_expected = 0

print("=" * 85)
print("MEGA SLEEPER SIMULATION - THE DEEP DIVE")
print("Testing from draw %d to draw %d, step=%d, window=%d" % (MIN_HISTORY, total - WINDOW, STEP, WINDOW))
print("=" * 85)

sim_count = 0

for freeze_idx in range(MIN_HISTORY, total - WINDOW, STEP):
    sim_count += 1
    HISTORY = ALL[:freeze_idx + 1]
    FUTURE = ALL[freeze_idx + 1: freeze_idx + 1 + WINDOW]
    hist_total = len(HISTORY)
    
    # Calculate sleepers
    sleepers = []
    for num in range(1, 51):
        last_idx = None
        for i in range(hist_total - 1, -1, -1):
            if num in HISTORY[i]['numbers']:
                last_idx = i
                break
        
        if last_idx is None:
            gap = hist_total
        else:
            gap = hist_total - 1 - last_idx
        
        appearances = sum(1 for d in HISTORY if num in d['numbers'])
        avg_gap = hist_total / appearances if appearances > 0 else 999
        
        circ = circle(num)
        circ_since = 0
        if gap > 0 and last_idx is not None:
            circ_since = sum(1 for d in HISTORY[last_idx+1:] if circ in d['numbers'])
        
        circ_hist_rate = sum(1 for d in HISTORY if circ in d['numbers']) / hist_total * 100
        circ_recent_rate = (circ_since / gap * 100) if gap > 0 else 0
        circ_ratio = circ_recent_rate / circ_hist_rate if circ_hist_rate > 0 and gap > 0 else 0
        
        overdue_factor = gap / avg_gap if avg_gap > 0 else 0
        
        sleepers.append({
            'num': num,
            'gap': gap,
            'avg_gap': avg_gap,
            'overdue': overdue_factor,
            'circle': circ,
            'circ_ratio': circ_ratio,
            'circ_since': circ_since,
        })
    
    sleepers.sort(key=lambda x: -x['overdue'])
    top = sleepers[:TOP_N]
    
    # Track results for this simulation
    sim_woke = 0
    sim_woke_fast = 0
    
    for s in top:
        num = s['num']
        circ = s['circle']
        rev = reverse_num(num)
        total_picked += 1
        
        is_circle_boosted = s['circ_ratio'] >= 1.5
        if is_circle_boosted:
            circle_boosted_total += 1
        else:
            circle_quiet_total += 1
        
        # Find when it woke
        wake_draw = None
        for j, fd in enumerate(FUTURE):
            if num in fd['numbers']:
                wake_draw = j + 1
                break
        
        if wake_draw:
            total_woke += 1
            sim_woke += 1
            overdue_wake_pairs.append((s['overdue'], wake_draw))
            
            if wake_draw <= 5:
                total_woke_fast += 1
                sim_woke_fast += 1
                if is_circle_boosted:
                    circle_boosted_woke_fast += 1
                else:
                    circle_quiet_woke_fast += 1
            elif wake_draw <= 10:
                total_woke_medium += 1
            else:
                total_woke_slow += 1
            
            # Check teases before wake
            had_tease = False
            for j in range(min(wake_draw - 1, len(FUTURE))):
                fd = FUTURE[j]
                nums_set = set(fd['numbers'])
                
                if circ in nums_set:
                    had_tease = True
                    tease_types['circle'] += 1
                if rev != num and rev in nums_set:
                    had_tease = True
                    tease_types['reverse'] += 1
                if (num - 1) >= 1 and (num - 1) in nums_set:
                    had_tease = True
                    tease_types['neighbor-1'] += 1
                if (num + 1) <= 50 and (num + 1) in nums_set:
                    had_tease = True
                    tease_types['neighbor+1'] += 1
            
            if had_tease:
                teases_before_wake += 1
            else:
                no_teases_before_wake += 1
    
    # Money check: top 5 sleepers across next 20 draws
    pick5 = set([s['num'] for s in top[:5]])
    for fd in FUTURE:
        hits = len(pick5.intersection(set(fd['numbers'])))
        total_money_hits += hits
        total_money_draws += 1
    total_money_expected += len(FUTURE) * 5 * (5.0 / 50.0)
    
    sim_data = {
        'freeze_date': ALL[freeze_idx]['date'],
        'freeze_idx': freeze_idx,
        'top_sleepers': [(s['num'], s['overdue'], s['circ_ratio']) for s in top[:5]],
        'woke': sim_woke,
        'woke_fast': sim_woke_fast,
    }
    all_sims.append(sim_data)

# ═══════════════════════════════════════════════════════════════════════════════
# MEGA RESULTS
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 85)
print("MEGA RESULTS: %d simulations across %d draws" % (sim_count, total))
print("=" * 85)

print("\n--- WAKE UP RATES ---")
print("  Total sleeper picks: %d" % total_picked)
print("  Woke up (in %d draws): %d / %d = %.1f%%" % (WINDOW, total_woke, total_picked, total_woke/total_picked*100))
print("  FAST (1-5 draws):  %d / %d = %.1f%%" % (total_woke_fast, total_picked, total_woke_fast/total_picked*100))
print("  MEDIUM (6-10):     %d / %d = %.1f%%" % (total_woke_medium, total_picked, total_woke_medium/total_picked*100))
print("  SLOW (11-20):      %d / %d = %.1f%%" % (total_woke_slow, total_picked, total_woke_slow/total_picked*100))
print("  STILL SLEEPING:    %d / %d = %.1f%%" % (total_picked - total_woke, total_picked, (total_picked - total_woke)/total_picked*100))

# Random comparison: a random number appears in ~10% of draws (5/50)
# Over 20 draws, prob of appearing at least once = 1 - (0.9)^20 = 87.8%
import math
random_wake = 1 - (1 - 5/50)**WINDOW
print("\n  Random number wake rate (in %d draws): %.1f%%" % (WINDOW, random_wake * 100))
print("  Our sleeper wake rate: %.1f%% (%.2fx random!)" % (total_woke/total_picked*100, (total_woke/total_picked) / random_wake))

print("\n--- TEASE ANALYSIS ---")
total_wakers = teases_before_wake + no_teases_before_wake
print("  Wakers with teases before: %d / %d = %.1f%%" % (
    teases_before_wake, total_wakers, teases_before_wake/total_wakers*100 if total_wakers > 0 else 0))
print("  Surprise entrances (no tease): %d / %d = %.1f%%" % (
    no_teases_before_wake, total_wakers, no_teases_before_wake/total_wakers*100 if total_wakers > 0 else 0))
print("\n  Tease type breakdown:")
for ttype, count in sorted(tease_types.items(), key=lambda x: -x[1]):
    print("    %s: %d occurrences" % (ttype, count))

print("\n--- CIRCLE BOOST EFFECT ---")
if circle_boosted_total > 0:
    print("  Circle BOOSTED sleepers (ratio >= 1.5x):")
    print("    Total: %d" % circle_boosted_total)
    print("    Woke FAST (1-5): %d = %.1f%%" % (circle_boosted_woke_fast, circle_boosted_woke_fast/circle_boosted_total*100))
if circle_quiet_total > 0:
    print("  Circle QUIET sleepers (ratio < 1.5x):")
    print("    Total: %d" % circle_quiet_total)
    print("    Woke FAST (1-5): %d = %.1f%%" % (circle_quiet_woke_fast, circle_quiet_woke_fast/circle_quiet_total*100))

if circle_boosted_total > 0 and circle_quiet_total > 0:
    boost_rate = circle_boosted_woke_fast/circle_boosted_total*100
    quiet_rate = circle_quiet_woke_fast/circle_quiet_total*100
    print("\n  CIRCLE BOOST VERDICT:")
    if boost_rate > quiet_rate:
        print("    Circle-boosted sleepers wake FASTER! (%.1f%% vs %.1f%%)" % (boost_rate, quiet_rate))
        print("    ADVANTAGE: %.1fx more likely to wake fast!" % (boost_rate/quiet_rate if quiet_rate > 0 else 999))
    else:
        print("    Circle boost doesn't speed up wake (%.1f%% vs %.1f%%)" % (boost_rate, quiet_rate))

print("\n--- OVERDUE FACTOR vs WAKE SPEED ---")
# Group by overdue ranges
overdue_groups = {
    "1.0-1.5x": [],
    "1.5-2.0x": [],
    "2.0-3.0x": [],
    "3.0x+": [],
}

for overdue, wake in overdue_wake_pairs:
    if overdue >= 3.0:
        overdue_groups["3.0x+"].append(wake)
    elif overdue >= 2.0:
        overdue_groups["2.0-3.0x"].append(wake)
    elif overdue >= 1.5:
        overdue_groups["1.5-2.0x"].append(wake)
    else:
        overdue_groups["1.0-1.5x"].append(wake)

print("  %-12s %-10s %-12s %-12s" % ("Overdue", "Count", "Avg Wake", "Fast%"))
print("  " + "-" * 50)
for group, wakes in sorted(overdue_groups.items()):
    if wakes:
        avg = sum(wakes) / len(wakes)
        fast = sum(1 for w in wakes if w <= 5) / len(wakes) * 100
        print("  %-12s %-10d %-12.1f %-12.1f%%" % (group, len(wakes), avg, fast))

print("\n--- MONEY CHECK ---")
print("  Top 5 sleepers played in every draw:")
print("  Total hits: %d across %d draws" % (total_money_hits, total_money_draws))
exp = total_money_expected
actual_rate = total_money_hits / (total_money_draws * 5) * 100
random_rate = 10.0
print("  Hit rate: %.2f%% (random = %.1f%%)" % (actual_rate, random_rate))
print("  vs Random: %.2fx" % (total_money_hits / exp if exp > 0 else 0))

# ═══════════════════════════════════════════════════════════════════════════════
# PER-SIMULATION DETAIL
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 85)
print("SIMULATION TIMELINE - Each period's top 5 sleepers & results")
print("=" * 85)

for sim in all_sims:
    sleeper_str = ", ".join(["%d(%.1fx)" % (n, o) for n, o, c in sim['top_sleepers']])
    circ_str = ", ".join(["c%.1f" % c for n, o, c in sim['top_sleepers'] if c >= 1.5])
    
    tag = ""
    if sim['woke'] >= 9:
        tag = " PERFECT!"
    elif sim['woke'] >= 7:
        tag = " STRONG"
    elif sim['woke'] >= 5:
        tag = " OK"
    else:
        tag = " WEAK"
    
    print("  %s | Woke: %d/10 (fast: %d) | Top5: %s%s%s" % (
        sim['freeze_date'],
        sim['woke'], sim['woke_fast'],
        sleeper_str,
        " | Boosted: " + circ_str if circ_str else "",
        tag))

# ═══════════════════════════════════════════════════════════════════════════════
# THE VERDICT
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 85)
print("THE VERDICT - IS THERE MUSIC IN THE SLEEPERS?")
print("=" * 85)

wake_pct = total_woke/total_picked*100
tease_pct = teases_before_wake/total_wakers*100 if total_wakers > 0 else 0

print()
if wake_pct > 85:
    print("  SLEEPER WAKE RATE: %.1f%% -- THE SLEEPERS ALWAYS WAKE UP!" % wake_pct)
else:
    print("  SLEEPER WAKE RATE: %.1f%%" % wake_pct)

if tease_pct > 60:
    print("  TEASE RATE: %.1f%% -- THE UNIVERSE IS SNEAKY! It hints before delivering!" % tease_pct)
else:
    print("  TEASE RATE: %.1f%%" % tease_pct)

if circle_boosted_total > 0:
    boost_fast_rate = circle_boosted_woke_fast/circle_boosted_total*100
    print("  CIRCLE BOOST FAST RATE: %.1f%%" % boost_fast_rate)

print()
print("  THE STARS HAVE SPOKEN!")
print("  The sleeper theory is %s across %d simulations!" % (
    "CONFIRMED" if wake_pct > 85 else "PROMISING" if wake_pct > 70 else "INCONCLUSIVE",
    sim_count))
