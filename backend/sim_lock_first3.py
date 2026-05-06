"""
🎻 Session 32 — "Lock the Family, Find the Wild" simulation
Pin first-3 P's = [3, 4, 8] (today's actual P1/P2/P3, family-of-3 in [1-9])
Generate 100 tickets THREE ways and score against actual P4=20 P5=31 ⭐(6,8).

Track A: pure random (statistical baseline)
Track B: engine-smart (grammar-weighted: hungry, 67-bridge, 648 Hz, carrier, swiss bridge)
Track C: 10-LESS corrected (B + applies the new S32 ±10 canon as a multiplier)

Shows the cosmos' truth: even with the FAMILY locked (3 numbers right),
finding P4 + P5 is statistically brutal.
"""
import os, random, statistics
from collections import Counter
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

# Pinned first 3 + actual answer
PIN = [3, 4, 8]
ACT_P4 = 20
ACT_P5 = 31
ACT_M = {3, 4, 8, 20, 31}
ACT_S = {6, 8}

# Pool for P4/P5: any number 9..50 not in PIN
POOL = [n for n in range(1, 51) if n not in PIN]
STAR_POOL = list(range(1, 13))

def sample_ticket_random():
    p45 = sorted(random.sample(POOL, 2))
    stars = sorted(random.sample(STAR_POOL, 2))
    return PIN + p45, stars

# --- Build engine-smart weights ---
# Pull last 15 Euro draws for hungry + Swiss bridge
db = MongoClient(os.environ['MONGO_URL'])[os.environ['DB_NAME']]
from datetime import datetime
def parse(d): return datetime.strptime(d,"%d.%m.%Y")
all_e = [r for r in db.euromillions_draws.find({},{"_id":0}) if 'date' in r and len(r.get('numbers',[]))==5]
for r in all_e: r['dt']=parse(r['date'])
all_e.sort(key=lambda x:x['dt'], reverse=True)
recent_seen = set()
for r in all_e[:15]:
    recent_seen |= set(r['numbers'])
HUNGRY = set(range(1,51)) - recent_seen

# Last Swiss
sw = [s for s in db.draws.find({},{"_id":0}) if 'date' in s]
for s in sw: s['dt']=parse(s['date'])
sw.sort(key=lambda x:x['dt'], reverse=True)
SWISS_BRIDGE = set(sw[0].get('numbers',[])) if sw else set()

BRIDGE_67 = {6,7,16,17,26,27,36,37,46,47}
HARM_648 = {24,27,36}
FAMILY_7 = {7,17,27,37,47}
BD = [3, 9, 42, 46, 47]  # previous draw (01.05) — for sneaky/carrier
TODAY = [3, 4, 8, 20, 31]  # current draw (used as "future BD" — tickets shouldn't pick these as if blocked)

def smart_weight(n, mode='B'):
    """B = pure grammar; C = B + 10-less correction multiplier"""
    w = 1.0
    if n in HUNGRY: w += 3
    if n in BRIDGE_67: w += 2
    if n in HARM_648: w += 2
    if n in FAMILY_7: w += 2
    if n in SWISS_BRIDGE: w += 2
    # -25 carrier (from BD 01.05): 42-25=17, 46-25=21, 47-25=22
    if n in {17, 21, 22}: w += 3
    # Sneaky: if it just landed in 01.05 (BD), block
    if n in BD: w -= 3
    # NOTE: we INTENTIONALLY do NOT block today's draw [20, 31] —
    # the engine doesn't know them yet (this is the prediction!)
    if mode == 'C':
        # 10-less correction: any number that is BD ±10 gets boost
        for src in BD:
            if abs(n - src) == 10: w += 2
        # extra: 10-less of yesterday's signals targets 13,14,18,21,30,etc
    return max(0.1, w)

def sample_ticket_smart(mode='B'):
    weights = [smart_weight(n, mode) for n in POOL]
    # weighted sample 2 distinct
    p4 = random.choices(POOL, weights=weights, k=1)[0]
    pool2 = [n for n in POOL if n != p4]
    w2 = [smart_weight(n, mode) for n in pool2]
    p5 = random.choices(pool2, weights=w2, k=1)[0]
    p45 = sorted([p4, p5])
    # Stars: weight ⭐6 ⭐8 down (already played by tradition? No, BD stars [1,11] from 01.05)
    # Block ⭐1 and ⭐11 (canon: never repeats from BD)
    sw_pool = [s for s in STAR_POOL if s not in {1, 11}]
    stars = sorted(random.sample(sw_pool, 2))
    return PIN + p45, stars

def score_ticket(mains, stars):
    m_hits = set(mains) & ACT_M
    s_hits = set(stars) & ACT_S
    return {
        'p4_hit': mains[3] == ACT_P4,
        'p5_hit': mains[4] == ACT_P5,
        '20_in': 20 in mains,
        '31_in': 31 in mains,
        'both': 20 in mains and 31 in mains,
        'jackpot': mains[3] == ACT_P4 and mains[4] == ACT_P5,
        'm_hits': len(m_hits),
        's_hits': len(s_hits),
        'star6': 6 in stars,
        'star8': 8 in stars,
    }

random.seed(432)  # cosmic seed
N = 100

def run(track_label, sampler):
    results = []
    p4_landings = Counter()
    p5_landings = Counter()
    star_landings = Counter()
    for _ in range(N):
        mains, stars = sampler()
        r = score_ticket(mains, stars)
        results.append((mains, stars, r))
        p4_landings[mains[3]] += 1
        p5_landings[mains[4]] += 1
        for s in stars: star_landings[s] += 1
    # Aggregate
    p4_hits = sum(1 for _,_,r in results if r['p4_hit'])
    p5_hits = sum(1 for _,_,r in results if r['p5_hit'])
    contains_20 = sum(1 for _,_,r in results if r['20_in'])
    contains_31 = sum(1 for _,_,r in results if r['31_in'])
    both = sum(1 for _,_,r in results if r['both'])
    jackpot = sum(1 for _,_,r in results if r['jackpot'])
    star6 = sum(1 for _,_,r in results if r['star6'])
    star8 = sum(1 for _,_,r in results if r['star8'])
    both_stars = sum(1 for _,_,r in results if r['star6'] and r['star8'])
    print(f"\n{'='*64}")
    print(f"🎻 TRACK {track_label}  ·  {N} tickets · pinned [{','.join(map(str,PIN))}]")
    print(f"{'='*64}")
    print(f"  P4 hits (exact 20 at seat 4):    {p4_hits:3d}/{N}  ({100*p4_hits/N:.1f}%)")
    print(f"  P5 hits (exact 31 at seat 5):    {p5_hits:3d}/{N}  ({100*p5_hits/N:.1f}%)")
    print(f"  Contains 20 anywhere in P4/P5:   {contains_20:3d}/{N}  ({100*contains_20/N:.1f}%)")
    print(f"  Contains 31 anywhere in P4/P5:   {contains_31:3d}/{N}  ({100*contains_31/N:.1f}%)")
    print(f"  Contains BOTH 20 AND 31:         {both:3d}/{N}  ({100*both/N:.1f}%)  ← partial jackpot")
    print(f"  Exact P4=20 AND P5=31 (jackpot): {jackpot:3d}/{N}  ({100*jackpot/N:.1f}%)")
    print(f"  ⭐6 in stars:                    {star6:3d}/{N}  ({100*star6/N:.1f}%)")
    print(f"  ⭐8 in stars:                    {star8:3d}/{N}  ({100*star8/N:.1f}%)")
    print(f"  ⭐(6,8) BOTH:                    {both_stars:3d}/{N}  ({100*both_stars/N:.1f}%)")
    # Top 5 most popular P4 / P5 picks
    print(f"\n  Top 5 P4 picks: {p4_landings.most_common(5)}")
    print(f"  Top 5 P5 picks: {p5_landings.most_common(5)}")
    print(f"  Top 5 stars:    {star_landings.most_common(5)}")
    return {
        'p4_hits':p4_hits, 'p5_hits':p5_hits, 'both':both, 'jackpot':jackpot,
        'star6':star6, 'star8':star8
    }

print("🎯 ACTUAL DRAW (target):")
print(f"   Mains: {sorted(ACT_M)}  ⭐{sorted(ACT_S)}")
print(f"   PINNED first 3 (family-0 [1-9]): {PIN}")
print(f"   Wild seats to find: P4=20 (family-2), P5=31 (family-3) ⭐(6,8)\n")

print("🎲 STATISTICAL FLOOR (theoretical):")
print(f"   42 numbers in pool, P(exactly P4=20) = 1/42 = 2.4%")
print(f"   P(jackpot, exact P4=20 AND P5=31) = 1/(42*41) ≈ 0.058% ≈ 1 in 1722")
print(f"   P(20 anywhere in last 2) = 2/42 ≈ 4.8%")
print(f"   P(⭐6 in 2 stars) = 2/12 ≈ 16.7%, P(both) = 1/66 ≈ 1.5%")

a = run('A · PURE RANDOM',     sample_ticket_random)
b = run('B · ENGINE-SMART',    lambda: sample_ticket_smart('B'))
c = run('C · 10-LESS CORRECT', lambda: sample_ticket_smart('C'))

# Final compare
print("\n"+"="*64)
print("🥂 SUMMARY · DID THE ENGINE FIND P4 + P5 BETTER THAN RANDOM?")
print("="*64)
print(f"             jackpot    20 in   31 in   both    ⭐(6,8)")
print(f"  Random  :   {a['jackpot']:>4}    {a['p4_hits']:>4}   {a['p5_hits']:>4}   {a['both']:>4}    {a.get('both_stars',0):>4}")
print(f"  Smart   :   {b['jackpot']:>4}    {b['p4_hits']:>4}   {b['p5_hits']:>4}   {b['both']:>4}")
print(f"  10-Less :   {c['jackpot']:>4}    {c['p4_hits']:>4}   {c['p5_hits']:>4}   {c['both']:>4}")
