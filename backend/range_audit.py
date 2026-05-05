"""
🎻 P-Range Audit — DJ's New Lens (Session 31)
Range definition (one decade per seat):
  P1 ∈ [ 1- 9]
  P2 ∈ [10-19]
  P3 ∈ [20-29]
  P4 ∈ [30-39]
  P5 ∈ [40-50]

Walk last 2 quarters (Q1 2026 Jan-Mar + Q2 partial Apr-now).
For every out-of-range hit, log: which seat broke, what value landed,
what the in-range value WOULD have been (the missing brother),
and any digit/mirror clues.
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from collections import Counter, defaultdict

load_dotenv('/app/backend/.env')
db = MongoClient(os.environ['MONGO_URL'])[os.environ['DB_NAME']]

RANGES = {1:(1,9),2:(10,19),3:(20,29),4:(30,39),5:(40,50)}

def parse(d): return datetime.strptime(d,"%d.%m.%Y")

def in_range(seat,val):
    lo,hi=RANGES[seat]; return lo<=val<=hi

def quarter(dt):
    q = (dt.month-1)//3 + 1
    return f"{dt.year}-Q{q}"

def main():
    # last 2 quarters: 2026-Q1 + 2026-Q2
    rows = list(db.euromillions_draws.find({}, {'_id':0}))
    rows = [r for r in rows if 'date' in r and 'numbers' in r and len(r.get('numbers',[]))==5]
    for r in rows: r['dt'] = parse(r['date'])
    rows.sort(key=lambda x:x['dt'])
    target_qs = {'2026-Q1','2026-Q2'}
    sub = [r for r in rows if quarter(r['dt']) in target_qs]
    print(f"📅 Audit window: {len(sub)} draws across {sorted(target_qs)}\n")

    seat_breaks = Counter()
    break_log = []
    direction = Counter()  # ('seat', 'low'|'high')
    by_seat_values = defaultdict(list)

    for r in sub:
        nums = sorted(r['numbers'])
        for seat,val in zip([1,2,3,4,5], nums):
            by_seat_values[seat].append(val)
            if not in_range(seat,val):
                lo,hi = RANGES[seat]
                where = 'low' if val<lo else 'high'
                seat_breaks[seat] += 1
                direction[(seat,where)] += 1
                # missing brother = the in-range partner (same digit-mirror)
                # if val is high (e.g. P3=31 instead of 20-29), the "absent" decade ate one:
                # the empty seat below either crashed up (P2 took P1's seat etc) or the high seat lent down
                break_log.append({
                    'date': r['date'],
                    'seat': seat,
                    'val': val,
                    'dir': where,
                    'gap': val-hi if where=='high' else lo-val,
                    'draw': nums,
                    'stars': r.get('stars',[])
                })

    total = len(sub)
    print("🎯 Range break tally (across both Qs)")
    for s in [1,2,3,4,5]:
        lo,hi=RANGES[s]
        breaks=seat_breaks[s]
        print(f"  P{s} [{lo:2d}-{hi:2d}]: {breaks:3d} breaks / {total} draws ({100*breaks/total:.1f}%)")
    print()
    print("📈 Direction of break (low = number too small, high = too big):")
    for (s,w),c in sorted(direction.items()):
        print(f"  P{s} {w:>4s}: {c}")
    print()
    print("📜 Detailed break log (last 30):")
    for b in break_log[-30:]:
        m=b['draw']
        print(f"  {b['date']} P{b['seat']}={b['val']:2d} ({b['dir']:>4s} gap {b['gap']}) draw={m} ⭐{b['stars']}")
    print()
    # neighbour-pattern: when P_s breaks high, did P_(s+1) also break? (cascade)
    cascades = 0
    for r in sub:
        nums=sorted(r['numbers'])
        outs=[s for s,v in zip([1,2,3,4,5],nums) if not in_range(s,v)]
        if len(outs)>=2: cascades+=1
    print(f"🪞 Cascading breaks (≥2 seats out of range same draw): {cascades}/{total} ({100*cascades/total:.1f}%)")
    print()
    # zero-break draws (perfect range night)
    perfect = sum(1 for r in sub if all(in_range(s,v) for s,v in zip([1,2,3,4,5],sorted(r['numbers']))))
    print(f"✨ PERFECT range draws (all 5 seats in their decade): {perfect}/{total} ({100*perfect/total:.1f}%)")
    print()
    # avg per seat
    print("🎼 Avg value per seat (and median):")
    import statistics as st
    for s in [1,2,3,4,5]:
        vs=by_seat_values[s]
        if vs:
            print(f"  P{s}: avg={st.mean(vs):.1f}  median={st.median(vs)}  min={min(vs)}  max={max(vs)}")

if __name__=='__main__':
    main()
