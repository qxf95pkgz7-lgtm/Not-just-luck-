"""
🎧 SLEEPER ANALYSIS - Who's about to WAKE UP? 🎻
=================================================
Find numbers sleeping longest + check if their Circle partner is absorbing the energy!
"""

import sys
sys.path.insert(0, '/app/backend')

from euromillions_data_2024_2026 import EUROMILLIONS_DRAWS_2024_2026
from euromillions_data_2021_2023 import EUROMILLIONS_DRAWS_2021_2023
from euromillions_data_2018_2020 import EUROMILLIONS_DRAWS_2018_2020

ALL = EUROMILLIONS_DRAWS_2018_2020 + EUROMILLIONS_DRAWS_2021_2023 + EUROMILLIONS_DRAWS_2024_2026
total = len(ALL)

def circle(n):
    c = n + 25
    return c if c <= 50 else c - 50

print("=" * 85)
print("SLEEPER ANALYSIS: Every number 1-50 - gap since last appearance")
print("Total draws: %d | Last draw: %s" % (total, ALL[-1]['date']))
print("=" * 85)

sleepers = []

for num in range(1, 51):
    last_idx = None
    for i in range(total - 1, -1, -1):
        if num in ALL[i]['numbers']:
            last_idx = i
            break
    
    if last_idx is None:
        gap = total
    else:
        gap = total - 1 - last_idx
    
    appearances = sum(1 for d in ALL if num in d['numbers'])
    avg_gap = total / appearances if appearances > 0 else 999
    
    circ = circle(num)
    circ_since = 0
    if gap > 0 and last_idx is not None:
        circ_since = sum(1 for d in ALL[last_idx+1:] if circ in d['numbers'])
    
    circ_hist_rate = sum(1 for d in ALL if circ in d['numbers']) / total * 100
    circ_recent_rate = (circ_since / gap * 100) if gap > 0 else 0
    
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
        'last_date': ALL[last_idx]['date'] if last_idx is not None else 'NEVER',
    })

sleepers.sort(key=lambda x: -x['overdue'])

header = "%-5s %-5s %-6s %-8s %-10s %-14s %-8s %-12s %s" % (
    "Rank", "Num", "Gap", "AvgGap", "Overdue", "Last Seen", "Circle", "Circ Since", "Circ Boost?")
print("\n" + header)
print("-" * 85)

for rank, s in enumerate(sleepers[:30], 1):
    emoji = " 🔥🔥🔥" if s['overdue'] >= 3.0 else (" 🔥🔥" if s['overdue'] >= 2.0 else (" 🔥" if s['overdue'] >= 1.5 else ""))
    
    boost = ''
    if s['gap'] >= 5 and s['circ_since'] > 0:
        ratio = s['circ_recent_rate'] / s['circ_hist_rate'] if s['circ_hist_rate'] > 0 else 0
        if ratio >= 1.5:
            boost = "%.1fx UP!" % ratio
        elif ratio >= 1.0:
            boost = "%.1fx" % ratio
        else:
            boost = "%.1fx down" % ratio
    
    line = "%-5d %-5d %-6d %-8.1f %-10.2f %-14s ->%-6d %-12s %s%s" % (
        rank, s['num'], s['gap'], s['avg_gap'], s['overdue'], 
        s['last_date'], s['circle'], 
        "%dx" % s['circ_since'] if s['circ_since'] > 0 else "-",
        boost, emoji)
    print(line)

print()
print("=" * 85)
print("TOP SLEEPERS WITH CIRCLE BOOST (The ones about to WAKE UP!)")
print("=" * 85)

hot_sleepers = [s for s in sleepers if s['overdue'] >= 1.5 and s['gap'] >= 5]
hot_sleepers.sort(key=lambda x: -x['overdue'])

for s in hot_sleepers[:10]:
    circ_ratio = (s['circ_recent_rate'] / s['circ_hist_rate']) if s['circ_hist_rate'] > 0 and s['gap'] > 0 else 0
    print("  Number %d - sleeping for %d draws (%.1fx overdue!)" % (s['num'], s['gap'], s['overdue']))
    print("     Last seen: %s | Circle partner: %d" % (s['last_date'], s['circle']))
    print("     Circle %d appeared %dx since (rate: %.1f%% vs hist %.1f%%)" % (
        s['circle'], s['circ_since'], s['circ_recent_rate'], s['circ_hist_rate']))
    if circ_ratio >= 1.5:
        print("     CIRCLE IS PUMPING AT %.1fx - %d about to SNAP BACK!" % (circ_ratio, s['num']))
    elif circ_ratio >= 1.0:
        print("     Circle running normal")
    else:
        print("     Circle also quiet...")
    print()

# Also check: for the TOP 5 sleepers, when they woke up before, did the circle partner drop?
print("=" * 85)
print("CIRCLE PROOF: When a sleeper wakes, does its circle DROP?")
print("=" * 85)

for s in hot_sleepers[:5]:
    num = s['num']
    circ = s['circle']
    
    # Find all gaps for this number
    appearances_idx = [i for i, d in enumerate(ALL) if num in d['numbers']]
    
    if len(appearances_idx) < 3:
        continue
    
    # After each long sleep (>avg_gap), check if circle was active during sleep
    long_sleeps = 0
    circle_active_during = 0
    
    for k in range(1, len(appearances_idx)):
        gap = appearances_idx[k] - appearances_idx[k-1]
        if gap >= s['avg_gap'] * 1.5:  # long sleep
            long_sleeps += 1
            circ_hits = sum(1 for d in ALL[appearances_idx[k-1]+1:appearances_idx[k]] if circ in d['numbers'])
            circ_rate = circ_hits / gap * 100
            if circ_rate > s['circ_hist_rate']:
                circle_active_during += 1
    
    if long_sleeps > 0:
        print("  Number %d: %d long sleeps, circle %d was boosted in %d/%d (%.0f%%)" % (
            num, long_sleeps, circ, circle_active_during, long_sleeps, 
            circle_active_during/long_sleeps*100))

# STAR SLEEPERS
print()
print("=" * 85)
print("STAR SLEEPERS (Stars 1-12)")
print("=" * 85)

for star in range(1, 13):
    last_idx = None
    for i in range(total - 1, -1, -1):
        if star in ALL[i]['stars']:
            last_idx = i
            break
    
    gap = total - 1 - last_idx if last_idx is not None else total
    appearances = sum(1 for d in ALL if star in d['stars'])
    avg_gap = total / appearances if appearances > 0 else 999
    overdue = gap / avg_gap if avg_gap > 0 else 0
    
    # Star circle: +6 mod 12
    star_circ = ((star + 6 - 1) % 12) + 1
    
    emoji = " 🔥🔥" if overdue >= 2.0 else (" 🔥" if overdue >= 1.5 else "")
    last_date = ALL[last_idx]['date'] if last_idx is not None else 'NEVER'
    
    print("  Star %2d | Gap: %2d | Avg: %4.1f | Overdue: %.2fx | Last: %s | Circle(+6): Star %d%s" % (
        star, gap, avg_gap, overdue, last_date, star_circ, emoji))
