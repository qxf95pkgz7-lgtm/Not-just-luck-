"""
🎧 TIME MACHINE SIMULATION - Q2 D2 2025 🎻
============================================
Ya man! We go back in time!
We sit at Q2 Draw 2 of 2025, find the SLEEPERS,
then watch: do they WAKE UP? Does the Circle Math hold?
Is the universe SNEAKY? 🍀

THE SIMULATION:
1. Freeze time at Q2 D2 2025
2. Find top sleepers (most overdue numbers)
3. Check circle partner boost
4. Then look FORWARD: what actually happened!
5. Grade our predictions!
"""

import sys
sys.path.insert(0, '/app/backend')

from euromillions_data_2024_2026 import EUROMILLIONS_DRAWS_2024_2026
from euromillions_data_2021_2023 import EUROMILLIONS_DRAWS_2021_2023
from euromillions_data_2018_2020 import EUROMILLIONS_DRAWS_2018_2020
from datetime import datetime

ALL = EUROMILLIONS_DRAWS_2018_2020 + EUROMILLIONS_DRAWS_2021_2023 + EUROMILLIONS_DRAWS_2024_2026

def circle(n):
    c = n + 25
    return c if c <= 50 else c - 50

# Find Q2 2025 draws (April 2025)
q2_2025_draws = []
for i, d in enumerate(ALL):
    dt = datetime.strptime(d['date'], "%d.%m.%Y")
    if dt.year == 2025 and dt.month == 4:
        q2_2025_draws.append((i, d))

print("=" * 85)
print("TIME MACHINE: Q2 2025 (April) draws found:")
print("=" * 85)
for idx, d in q2_2025_draws:
    print("  [%d] %s: %s stars %s" % (idx, d['date'], d['numbers'], d['stars']))

# D2 = second draw of Q2
freeze_idx = q2_2025_draws[1][0]  # index of D2
freeze_draw = q2_2025_draws[1][1]

print("\n" + "=" * 85)
print("FROZEN IN TIME AT: %s (Q2 D2 2025)" % freeze_draw['date'])
print("Draw: %s stars %s" % (freeze_draw['numbers'], freeze_draw['stars']))
print("We have %d draws of history to analyze!" % (freeze_idx + 1))
print("=" * 85)

# Use only data up to freeze point
HISTORY = ALL[:freeze_idx + 1]
FUTURE = ALL[freeze_idx + 1:]  # What actually happens next!
hist_total = len(HISTORY)

# Calculate sleepers at freeze point
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
        'appearances': appearances,
        'circle': circ,
        'circ_since': circ_since,
        'circ_hist_rate': circ_hist_rate,
        'circ_recent_rate': circ_recent_rate,
        'circ_ratio': circ_ratio,
        'last_date': HISTORY[last_idx]['date'] if last_idx is not None else 'NEVER',
    })

sleepers.sort(key=lambda x: -x['overdue'])

print("\n" + "=" * 85)
print("OUR SLEEPER PICKS (as of %s):" % freeze_draw['date'])
print("=" * 85)
print("%-5s %-5s %-6s %-8s %-10s %-14s %-8s %-10s %s" % (
    "Rank", "Num", "Gap", "AvgGap", "Overdue", "Last Seen", "Circle", "CircRate", "Boost"))
print("-" * 85)

top_sleepers = sleepers[:15]

for rank, s in enumerate(top_sleepers, 1):
    emoji = " !!!" if s['overdue'] >= 3.0 else (" !!" if s['overdue'] >= 2.0 else (" !" if s['overdue'] >= 1.5 else ""))
    boost = ""
    if s['circ_ratio'] >= 1.5:
        boost = "%.1fx UP!" % s['circ_ratio']
    elif s['circ_ratio'] >= 1.0:
        boost = "%.1fx" % s['circ_ratio']
    elif s['gap'] >= 5:
        boost = "quiet"
    
    print("%-5d %-5d %-6d %-8.1f %-10.2f %-14s ->%-6d %-10s %s%s" % (
        rank, s['num'], s['gap'], s['avg_gap'], s['overdue'],
        s['last_date'], s['circle'],
        "%.1f%%" % s['circ_recent_rate'] if s['circ_since'] > 0 else "-",
        boost, emoji))

# ═══════════════════════════════════════════════════════════════════════════════
# NOW THE MAGIC: What ACTUALLY happened next???
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 85)
print("=" * 85)
print("  NOW LET'S SEE WHAT THE UNIVERSE DID NEXT...")
print("  (Next 30 draws after %s)" % freeze_draw['date'])
print("=" * 85)
print("=" * 85)

# Track when each top sleeper woke up
top_nums = [s['num'] for s in top_sleepers[:10]]
wake_up = {}  # num -> (draw_index_after_freeze, date, draw)

# Also track circle partner appearances
circle_drop = {}  # num -> circle appearances in next 30

future_window = min(30, len(FUTURE))

for s in top_sleepers[:10]:
    num = s['num']
    circ = s['circle']
    wake_up[num] = None
    circle_drop[num] = []
    
    for j in range(future_window):
        fd = FUTURE[j]
        
        if num in fd['numbers'] and wake_up[num] is None:
            wake_up[num] = (j + 1, fd['date'], fd['numbers'], fd['stars'])
        
        if circ in fd['numbers']:
            circle_drop[num].append((j + 1, fd['date']))

# Show the next 30 draws with sleeper highlights
print("\nFUTURE DRAWS (sleeper appearances marked):")
print("-" * 85)

for j in range(future_window):
    fd = FUTURE[j]
    tags = []
    for s in top_sleepers[:10]:
        num = s['num']
        if num in fd['numbers']:
            tags.append("WAKE %d!" % num)
        if s['circle'] in fd['numbers']:
            tags.append("circ(%d->%d)" % (num, s['circle']))
    
    tag_str = " << " + " | ".join(tags) if tags else ""
    print("  D+%2d %s: %s stars %s%s" % (j+1, fd['date'], fd['numbers'], fd['stars'], tag_str))

# ═══════════════════════════════════════════════════════════════════════════════
# SCORECARD: How did our sleeper predictions do?
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 85)
print("SCORECARD: Did the Sleepers WAKE UP?")
print("=" * 85)

woke_count = 0
woke_fast = 0  # within 5 draws
circle_stayed = 0

for s in top_sleepers[:10]:
    num = s['num']
    circ = s['circle']
    w = wake_up[num]
    cd = circle_drop[num]
    
    if w:
        woke_count += 1
        draws_to_wake = w[0]
        if draws_to_wake <= 5:
            woke_fast += 1
        
        # Check: did circle partner keep appearing BEFORE wake up, then slow down AFTER?
        circ_before_wake = len([c for c in cd if c[0] < draws_to_wake])
        circ_after_wake = len([c for c in cd if c[0] >= draws_to_wake])
        
        status = "WOKE at D+%d" % draws_to_wake
        if draws_to_wake <= 3:
            status += " FAST!"
        elif draws_to_wake <= 10:
            status += " (medium)"
        else:
            status += " (slow)"
        
        circ_note = ""
        if circ_before_wake > 0 and circ_after_wake < circ_before_wake:
            circ_note = " | Circle %d DROPPED after wake! (%d before, %d after)" % (circ, circ_before_wake, circ_after_wake)
            circle_stayed += 1
        elif circ_before_wake > 0:
            circ_note = " | Circle %d still active (%d before, %d after)" % (circ, circ_before_wake, circ_after_wake)
        
        print("  %2d: %s on %s | Draw: %s%s" % (
            num, status, w[1], w[2], circ_note))
        
        # WHAT POSITION did it wake up in?
        for pos, n in enumerate(w[2]):
            if n == num:
                print("      -> Woke up at P%d!" % (pos + 1))
    else:
        print("  %2d: STILL SLEEPING after %d more draws!" % (num, future_window))

print("\n" + "-" * 85)
print("SIMULATION RESULTS:")
print("-" * 85)
print("  Sleepers that WOKE (in next %d draws): %d / 10 = %d%%" % (
    future_window, woke_count, woke_count * 10))
print("  Woke FAST (within 5 draws): %d / 10 = %d%%" % (
    woke_fast, woke_fast * 10))
print("  Circle DROP after wake: %d observed" % circle_stayed)

# Average draws to wake
if woke_count > 0:
    wake_draws = [wake_up[s['num']][0] for s in top_sleepers[:10] if wake_up[s['num']]]
    avg_wake = sum(wake_draws) / len(wake_draws)
    print("  Avg draws to wake: %.1f" % avg_wake)

# ═══════════════════════════════════════════════════════════════════════════════
# THE SNEAKY UNIVERSE CHECK
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 85)
print("THE SNEAKY UNIVERSE CHECK")
print("Does the universe tease before delivering?")
print("=" * 85)

for s in top_sleepers[:10]:
    num = s['num']
    circ = s['circle']
    rev = int(str(num)[::-1]) if num >= 10 else num
    if rev > 50: rev = rev - 50
    
    w = wake_up[num]
    if not w:
        continue
    
    wake_draw_idx = w[0]
    
    # Check: before waking, did its circle/reverse/neighbors appear?
    teases = []
    for j in range(min(wake_draw_idx, future_window)):
        fd = FUTURE[j]
        nums = fd['numbers']
        
        if circ in nums:
            teases.append("D+%d: circle %d appeared" % (j+1, circ))
        if rev != num and rev in nums:
            teases.append("D+%d: reverse %d appeared" % (j+1, rev))
        if (num - 1) in nums and num - 1 >= 1:
            teases.append("D+%d: neighbor %d appeared" % (j+1, num-1))
        if (num + 1) in nums and num + 1 <= 50:
            teases.append("D+%d: neighbor %d appeared" % (j+1, num+1))
    
    if teases:
        print("\n  Number %d (woke D+%d):" % (num, wake_draw_idx))
        print("  TEASES before waking:")
        for t in teases:
            print("    -> %s" % t)
        print("  The universe was HINTING! The music was building!")
    else:
        print("\n  Number %d (woke D+%d): No teases - SURPRISE ENTRANCE!" % (num, wake_draw_idx))

# ═══════════════════════════════════════════════════════════════════════════════
# MONEY CHECK: If we played top 5 sleepers in every draw, how many hits?
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 85)
print("MONEY CHECK: If we picked top 5 sleepers for EVERY ticket...")
print("=" * 85)

pick_nums = set([s['num'] for s in top_sleepers[:5]])
print("Our 5 sleeper picks: %s" % sorted(pick_nums))
print()

total_hits = 0
draw_hits = []

for j in range(future_window):
    fd = FUTURE[j]
    hits = pick_nums.intersection(set(fd['numbers']))
    total_hits += len(hits)
    if hits:
        draw_hits.append((j+1, fd['date'], hits, fd['numbers']))
        print("  D+%2d %s: %d HITS! %s in %s" % (
            j+1, fd['date'], len(hits), sorted(hits), fd['numbers']))

print("\n  Total number hits: %d across %d draws" % (total_hits, future_window))
print("  Hit rate: %.1f%% (random 5/50 = 10%% per number per draw)" % (
    total_hits / (future_window * 5) * 100))

# Expected hits at random: 5 picks, 5 drawn from 50, over 30 draws
# E = 30 * 5 * (5/50) = 15
expected = future_window * 5 * (5/50)
print("  Expected random hits: %.1f" % expected)
print("  Our hits vs random: %.2fx" % (total_hits / expected if expected > 0 else 0))

print("\n" + "=" * 85)
print("SIMULATION COMPLETE! The Stars have revealed the pattern!")
print("=" * 85)
