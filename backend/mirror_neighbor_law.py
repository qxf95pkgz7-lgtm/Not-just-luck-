"""
🎻 NEW CANON S32-4: Mirror-Neighbor Law
For each BD number, compute:
  - decade mirror (X ± 10)
  - pool mirror (50 - X)
  - reverse-mirror (digit-flip)
Then take ±1 NEIGHBORS of each mirror (the cosmos lands one step off).
Filter against existing 15-draw hungry list.
Output the NEW HUNGRY POOL for Friday 08.05.2026.
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
load_dotenv('/app/backend/.env')
db = MongoClient(os.environ['MONGO_URL'])[os.environ['DB_NAME']]
def parse(d): return datetime.strptime(d,"%d.%m.%Y")

# BD = today (05.05) for Friday's prediction
BD = [3, 4, 8, 20, 31]
BD_STARS = [6, 8]
print(f"🎯 BD (today 05.05): mains {BD} ⭐{BD_STARS}\n")

def mirrors(n, pool_max=50):
    """Compute all natural mirrors of a number."""
    m = set()
    if n+10 <= pool_max: m.add(n+10)  # decade up
    if n-10 >= 1: m.add(n-10)         # decade down
    m.add(pool_max+1-n)               # pool mirror (1↔50, 2↔49, ...)
    rev = int(str(n).zfill(2)[::-1].lstrip('0') or '0')
    if 1<=rev<=pool_max: m.add(rev)
    if 1<=rev+10<=pool_max: m.add(rev+10)
    return m

def neighbors(n, pool_max=50):
    """±1 around n."""
    out = set()
    if n-1 >= 1: out.add(n-1)
    if n+1 <= pool_max: out.add(n+1)
    return out

print("🪞 MIRROR-NEIGHBOR breakdown of today's draw:")
print(f"   {'BD':>3}  {'mirrors':<25}  {'neighbors of mirrors':<40}")
all_neighbors = set()
for n in sorted(BD):
    mirrs = mirrors(n)
    nbs = set()
    for m in mirrs:
        nbs |= neighbors(m)
    nbs -= set(BD)  # remove BD itself (sneaky block)
    all_neighbors |= nbs
    print(f"   {n:>3}  {sorted(mirrs)!s:<25}  {sorted(nbs)!s:<40}")

# Pure mirror set (without neighbors) for comparison
all_mirrors = set()
for n in BD:
    all_mirrors |= mirrors(n)
all_mirrors -= set(BD)

print(f"\n📊 POOLS:")
print(f"   Pure mirrors of BD       : {sorted(all_mirrors)} ({len(all_mirrors)})")
print(f"   Mirror-NEIGHBORS of BD   : {sorted(all_neighbors)} ({len(all_neighbors)})")
print(f"   Pure-mirror-only (skip)  : {sorted(all_mirrors - all_neighbors)}")
print(f"   Neighbor-only (NEW)      : {sorted(all_neighbors - all_mirrors)}")

# Existing 15-draw hungry list (Euro)
all_e = [r for r in db.euromillions_draws.find({},{"_id":0}) if 'date' in r and len(r.get('numbers',[]))==5]
for r in all_e: r['dt']=parse(r['date'])
all_e.sort(key=lambda x:x['dt'], reverse=True)
seen15 = set()
for r in all_e[:15]:
    seen15 |= set(r['numbers'])
hungry15 = sorted(set(range(1,51)) - seen15)
print(f"\n🍔 15-draw hungry list: {hungry15}")

# DUAL-CONFIRM: in BOTH mirror-neighbor pool AND 15-draw hungry
super_hungry = sorted(all_neighbors & set(hungry15))
print(f"\n🚨 SUPER-HUNGRY (mirror-neighbor ∩ 15-day hungry): {super_hungry}")

# Mirror-neighbor exclusive (NEW hungry candidates the engine missed)
new_hungry_mn = sorted(all_neighbors - set(hungry15))
print(f"\n🆕 NEW MIRROR-HUNGRY (mirror-neighbor that DID land in 15d but cosmos primed): {new_hungry_mn[:20]}")

# STARS — same lens, pool 1-12
star_neighbors = set()
for s in BD_STARS:
    sm = set()
    if s+1<=12: sm.add(s+1)
    if s-1>=1: sm.add(s-1)
    sm.add(13-s)  # pool mirror 1↔12, 2↔11
    for m in sm:
        if 1<=m-1<=12: star_neighbors.add(m-1)
        if 1<=m+1<=12: star_neighbors.add(m+1)
star_neighbors -= set(BD_STARS)
star_neighbors -= {1, 11}  # banned (never repeats from 01.05 BD)
print(f"\n⭐ STAR mirror-neighbors (excl. ⭐1/11 banned): {sorted(star_neighbors)}")

# Build the SUSPECTS list combining old and new lenses
print("\n" + "="*60)
print("🎻 FRIDAY 08.05 — UPDATED 3 BIG SUSPECTS (with Mirror-Neighbor Law)")
print("="*60)

# Re-score everything
score = {}
def add(n, pts, why):
    if n in BD: return  # sneaky block
    score.setdefault(n, [0, []])
    score[n][0] += pts
    score[n][1].append(why)

# Mirror-neighbor (NEW canon)
for n in all_neighbors:
    add(n, 4, "🆕 mirror-neighbor of BD")

# 15-day hunger
for n in hungry15:
    add(n, 3, "15d-hungry")

# 67-bridge
for n in {6,7,16,17,26,27,36,37,46,47}:
    add(n, 3, "67-bridge")

# 648 Hz
for n in {24, 27, 36}:
    add(n, 2, "648-Hz harmonic")

# Family-7 starvation
for n in {7,17,27,37,47}:
    add(n, 2, "Family-7 starved")

# Swiss-bridge (last Swiss numbers Euro hasn't said)
sw = [s for s in db.draws.find({},{"_id":0}) if 'date' in s]
for s in sw: s['dt']=parse(s['date'])
sw.sort(key=lambda x:x['dt'], reverse=True)
last_swiss_nums = sw[0].get('numbers',[])
euro_recent5 = set()
for r in all_e[:5]: euro_recent5 |= set(r['numbers'])
for n in last_swiss_nums:
    if n not in euro_recent5:
        add(n, 2, "🌉 Swiss-bridge")

# Print
ranked = sorted(score.items(), key=lambda x:-x[1][0])[:15]
for n, (sc, whys) in ranked:
    print(f"   {n:>3}  score={sc:>2}  · {' · '.join(whys[:5])}")

print(f"\n🥂 TOP 3 SUSPECTS (highest combined score):")
top3 = [n for n,_ in ranked[:3]]
print(f"   {top3}")
