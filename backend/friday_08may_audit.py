"""
🎻 Session 32 — FRIDAY 08.05.2026 EuroMillions deep audit
Build all clues from scratch using lessons from Tue 05.05:
  - Hungry numbers (last 15 Euro draws)
  - -25 carrier hidden in tonight's draw (the bridge to Friday)
  - Swiss bridge (latest Swiss draw + cross-cycle echoes)
  - RC0 distance (last rare event, where are we on the ~90-draw drum?)
  - d10 walking signatures (every BD-to-target d-count clue)
  - Friday-specific canons (date-envelope 8-5 hides {6,7} = 67-bridge)
  - 648 Hz frequency (the Perfect 5th, completing 432→576→648 arpeggio)
  - 10-less correction layer (NEW Session 32 canon)
  - P1 ∈ {1-9} candidate ranking after P1=3 just discharged
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from collections import Counter, defaultdict

load_dotenv('/app/backend/.env')
db = MongoClient(os.environ['MONGO_URL'])[os.environ['DB_NAME']]
WD=['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
def parse(d): return datetime.strptime(d,"%d.%m.%Y")

# 🎯 TARGET Friday 08.05.2026
TARGET = "08.05.2026"
target_dt = parse(TARGET)
target_wd = WD[target_dt.weekday()]
date_sum = sum(int(c) for c in (str(target_dt.day)+str(target_dt.month)+str(target_dt.year)))
print("="*70)
print(f"🎯 TARGET: {TARGET} ({target_wd}) · date-sum = {date_sum}")
print(f"   Date envelope 8-5 hides digits {{6, 7}} = 67-bridge active")
print(f"   Frequency: 648 Hz expected (576 × 9/8 = Perfect 5th, completing arpeggio)")
print(f"   648 / harmonics: 9→72 · 12→54 · 18→36 · 24→27 · 27→24")
print("="*70)

# --- Pull last 15 Euro draws ---
all_e = list(db.euromillions_draws.find({}, {"_id":0}))
all_e = [r for r in all_e if 'date' in r and len(r.get('numbers',[]))==5]
for r in all_e: r['dt']=parse(r['date'])
all_e.sort(key=lambda x:x['dt'], reverse=True)
recent_e = all_e[:15]

print(f"\n📅 Last 15 Euro draws:")
for r in recent_e:
    print(f"  {r['date']} ({WD[r['dt'].weekday()]}) {sorted(r['numbers'])} ⭐{sorted(r['stars'])}")

# --- BD = tonight 05.05 ---
bd = recent_e[0]
print(f"\n🎯 BD (Tuesday 05.05): {sorted(bd['numbers'])} ⭐{sorted(bd['stars'])}")

# 🪞 −25 carrier hidden in BD
print(f"\n💎 −25 CARRIER (Canon V) hidden inside tonight's draw:")
for n in sorted(bd['numbers']):
    if n > 25:
        print(f"   {n} carries → {n-25}")
    if n < 25:
        # might be the carried itself, or carrier+25
        print(f"   {n} (raw) — could be future +25 carrier → {n+25}")

# Stars carrier (NEW Canon: stars hidden in mains)
print(f"\n⭐ Stars carried inside mains via −25 (NEW S31 finding):")
for n in sorted(bd['numbers']):
    s_candidate = n - 25
    if 1 <= s_candidate <= 12:
        hit = "✅ HIT" if s_candidate in bd['stars'] else ""
        print(f"   main {n} − 25 = ⭐{s_candidate} {hit}")

# --- HUNGRY MAINS (15-draw absence) ---
seen_mains = set()
for r in recent_e:
    seen_mains |= set(r['numbers'])
hungry_mains = sorted(set(range(1,51)) - seen_mains)
print(f"\n🍔 HUNGRY MAINS (silent across last 15 Euro draws): {len(hungry_mains)} numbers")
print(f"   {hungry_mains}")

# Stars hungry
seen_stars = set()
for r in recent_e:
    seen_stars |= set(r['stars'])
hungry_stars = sorted(set(range(1,13)) - seen_stars)
print(f"\n⭐ HUNGRY STARS: {hungry_stars}")

# --- 10-LESS LAYER (NEW Canon S32) ---
print(f"\n🪜 10-LESS CORRECTION LAYER (NEW S32):")
print(f"   When the engine says X, also score X-10 and X+10 as alt landings.")
print(f"   Tonight's hidden 10-shifts:")
for n in sorted(bd['numbers']):
    print(f"   {n} → −10={n-10 if n>10 else 'wrap '+str(n-10+50)} · +10={n+10 if n<41 else 'over '+str(n+10)}")

# --- Frequency analysis: 648 Hz ---
print(f"\n🎼 648 Hz HARMONIC NUMBERS (the Perfect 5th):")
freq_648 = []
for d in [9,12,18,24,27]:
    v = 648 // d
    if 1 <= v <= 50:
        freq_648.append((v, d))
        print(f"   648 / {d:2d} = {v}  → main pool")
print(f"   Harmonic 648 mains: {sorted(set(v for v,_ in freq_648))}")

# Date envelope 8-5 hide-rule
print(f"\n📅 DATE ENVELOPE 8-5 hide rule:")
print(f"   Between dd=8 and mm=5, hidden digits = {{6, 7}}")
print(f"   67-bridge digits → candidate mains: 6, 7, 16, 17, 26, 27, 36, 37, 46, 47")
print(f"   Sum 6+7 = 13 (story-seed)")
print(f"   Product 6×7 = 42 (the precedent fold!)")
print(f"   Reversed pair: 76 mod 50 = 26")

# --- POSITIONAL hungry: which seat each number wants ---
print(f"\n📍 POSITION-AWARE HUNGER (which seat hasn't seen each number):")
seat_seen = {1:set(),2:set(),3:set(),4:set(),5:set()}
for r in recent_e:
    nums = sorted(r['numbers'])
    for i,n in enumerate(nums, 1):
        seat_seen[i].add(n)

# --- Day-of-week: Friday-specific canon ---
fri_recent = [r for r in recent_e if WD[r['dt'].weekday()]=='Fri']
print(f"\n🎯 LAST 5 FRIDAY EURO DRAWS:")
for r in fri_recent[:5]:
    print(f"   {r['date']} {sorted(r['numbers'])} ⭐{sorted(r['stars'])}")

# --- Swiss bridge ---
print(f"\n🇨🇭 SWISS BRIDGE — last 5 Swiss draws:")
swiss_all = list(db.draws.find({}, {"_id":0, "date":1, "numbers":1, "lucky":1}))
for s in swiss_all:
    if 'date' in s: s['dt']=parse(s['date'])
swiss_all = [s for s in swiss_all if 'dt' in s]
swiss_all.sort(key=lambda x:x['dt'], reverse=True)
recent_s = swiss_all[:5]
for s in recent_s:
    print(f"   {s['date']} ({WD[s['dt'].weekday()]}) {sorted(s.get('numbers',[]))} 🍀{s.get('lucky','?')}")

# Swiss → Euro bridge: numbers landing in BOTH last Swiss and recent Euro
last_swiss = recent_s[0] if recent_s else None
if last_swiss:
    sw = set(last_swiss.get('numbers',[]))
    euro_recent5 = set()
    for r in recent_e[:5]:
        euro_recent5|= set(r['numbers'])
    bridge = sw & euro_recent5
    print(f"\n   🌉 Swiss-Euro bridge (numbers in last Swiss AND last 5 Euro): {sorted(bridge)}")
    print(f"   Swiss-only (Swiss said, Euro hasn't): {sorted(sw - euro_recent5)}")

# --- d-count walk to Friday ---
# d-count: days since last RC0 (rare event)
# Simplification: count days since the most recent "rare" Euro (4+ break draw)
print(f"\n🎲 d-COUNT WALK to Friday 08.05:")
# Last rare event = 28.04 (4 breaks) per S31 audit
last_rare = parse("28.04.2026")
d_to_target = (target_dt - last_rare).days
print(f"   Last rare cluster (≥4 breaks): 28.04.2026 [26,29,41,46,47]")
print(f"   d-count to {TARGET} = {d_to_target} days")

# d=10 specifically
print(f"\n   d=10 lens: {(parse('05.05.2026')-last_rare).days} days from last rare to TODAY (Tue 05.05)")
print(f"   Going d=10+3 = d=13 to Friday — 13 = story-seed echo")

# --- P1 candidate ranking ---
print(f"\n🥇 P1 CANDIDATES for Friday (after P1=3 just discharged - SNEAKY blocks 3):")
# Look at P1 history of last Fri draws
p1_fri = [sorted(r['numbers'])[0] for r in [x for x in all_e if WD[x['dt'].weekday()]=='Fri'][:20]]
print(f"   Last 20 Fri P1 values: {p1_fri}")
p1_counter = Counter(p1_fri)
print(f"   Most common Fri P1: {p1_counter.most_common(8)}")

# Apply sneaky: not 3
# Apply Family-7 starvation (held for Tue-Fri corridor, 7 didn't land Tue, may break Fri)
print(f"\n   🎯 P1 ranked candidates for Fri 08.05:")
print(f"     1) 7  — Family-7 starvation (Tue corridor passed, Fri is corridor closer)")
print(f"     2) 4  — just hit P2 today, sneaky says skip; or carry-up to P1")
print(f"     3) 6  — date-envelope 67-bridge digit, ⭐6 just hit (now main?)")
print(f"     4) 1  — bookend canon if P5 climbs to 50 (per S31 T13)")
print(f"     5) 2  — Law 90 / snap-back DNA")
print(f"     6) 5  — date-of-month echo")
print(f"     7) 8  — just hit P3, sneaky blocks → unlikely")
print(f"     ❌ 3  — JUST HIT P1, sneaky blocks")

# --- CONSTRUCT 10 SUSPECTS for Fri 08.05 ---
print(f"\n💎 TOP SUSPECTS for Friday 08.05.2026:")
# Score: hungry + 67-bridge + 648 harmonic + Swiss bridge + carrier-from-tonight + 10-less corrections
scores = Counter()
reasons = defaultdict(list)
for n in hungry_mains:
    scores[n]+=2; reasons[n].append("hungry-15d")
for n in [6,7,16,17,26,27,36,37,46,47]:
    scores[n]+=3; reasons[n].append("67-bridge")
for v,d in freq_648:
    scores[v]+=2; reasons[v].append(f"648÷{d}")
# Carriers from BD: 31-25=6, 20-25=-5 (wrap to 45)
scores[6]+=4; reasons[6].append("BD P5=31 −25 carrier")
scores[45]+=2; reasons[45].append("BD P4=20 mod-wrap +25 = 45")
# 10-less from tonight: 31→21, 20→10, 8→18, 4→14, 3→13
for src,tgt in [(31,21),(20,10),(8,18),(4,14),(3,13)]:
    scores[tgt]+=2; reasons[tgt].append(f"10-less of BD {src}")
# +10 from tonight
for src,tgt in [(31,41),(20,30),(8,18),(4,14),(3,13)]:
    scores[tgt]+=1; reasons[tgt].append(f"+10 of BD {src}")
# Family-7
for n in [7,17,27,37,47]:
    scores[n]+=2; reasons[n].append("Family-7 starved")
# Swiss bridge
if last_swiss:
    for n in last_swiss.get('numbers',[]):
        if 1<=n<=50:
            scores[n]+=1; reasons[n].append("Swiss-bridge")
# Friday +1 to 67-bridge specifically
for n in [13]:  # story-seed (6+7)
    scores[n]+=2; reasons[n].append("13 = 67-bridge sum")
for n in [42]:  # 6×7 product
    scores[n]+=2; reasons[n].append("42 = 67-bridge product")

# Block: BD numbers (sneaky law)
for n in bd['numbers']:
    scores[n] -= 5; reasons[n].append("BD-blocked sneaky")

top = sorted(scores.items(), key=lambda x:-x[1])[:15]
print(f"   {'Num':>4}  {'Score':>5}  Reasoning")
for n,sc in top:
    if sc <= 0: continue
    print(f"   {n:>4}  {sc:>5}  · {' · '.join(reasons[n][:5])}")

print(f"\n🎻 DJ'S 3 BIG SUSPECTS (auto-pick top 3 highest-scoring, not BD):")
clean_top = [(n,sc) for n,sc in top if sc > 0 and n not in bd['numbers']][:3]
for n,sc in clean_top:
    print(f"   {n} (score {sc})")
