"""
🎻 Range Break GRAMMAR Audit — Session 31 deep dive
Not just counts — read the STRUCTURE of each break:
  - What did the PREVIOUS draw (BD) look like before the break?
  - Day-of-week: Tue vs Fri break-fingerprints
  - Carrier digits: when P3=34 (high-break), 34 mod 25 = 9; what's hidden?
  - Co-occurrence: which seat-pairs break together?
  - The RESET law: what does the draw AFTER a heavy-break draw look like?
  - Date-sum bias of break events
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from collections import Counter, defaultdict

load_dotenv('/app/backend/.env')
db = MongoClient(os.environ['MONGO_URL'])[os.environ['DB_NAME']]
RANGES = {1:(1,9),2:(10,19),3:(20,29),4:(30,39),5:(40,50)}
WD = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']

def parse(d): return datetime.strptime(d,"%d.%m.%Y")
def in_range(s,v): lo,hi=RANGES[s]; return lo<=v<=hi
def break_dir(s,v):
    lo,hi=RANGES[s]
    if v<lo: return 'low'
    if v>hi: return 'high'
    return None
def date_sum(dt):
    s=str(dt.day)+str(dt.month)+str(dt.year)
    return sum(int(c) for c in s)
def carrier(v):
    """Decode hidden digit: mod-50 wrap, mirror, digit-sum"""
    return {
        'val': v,
        'modwrap': v%50 if v>50 else None,
        'reverse': int(str(v)[::-1].lstrip('0') or '0'),
        'rev_modwrap': (int(str(v)[::-1].lstrip('0') or '0'))%50,
        'digsum': sum(int(c) for c in str(v)),
        'minus25': v-25 if v>25 else None,
        'mirror42': 42-v if 0<v<42 else None,
    }

def main():
    rows = list(db.euromillions_draws.find({}, {'_id':0}))
    rows = [r for r in rows if 'date' in r and len(r.get('numbers',[]))==5]
    for r in rows: r['dt']=parse(r['date'])
    rows.sort(key=lambda x:x['dt'])
    sub = [r for r in rows if r['dt'].year==2026]
    print(f"📅 Audit window: 2026 ({len(sub)} draws)\n")

    # 1) Day-of-week break fingerprint
    print("🎯 BREAKS BY DAY-OF-WEEK (Tue vs Fri):")
    by_dow = defaultdict(lambda: {'n':0, 'breaks':Counter(), 'dirs':Counter()})
    for r in sub:
        dow = WD[r['dt'].weekday()]
        by_dow[dow]['n'] += 1
        nums=sorted(r['numbers'])
        for s,v in zip([1,2,3,4,5],nums):
            d=break_dir(s,v)
            if d:
                by_dow[dow]['breaks'][s]+=1
                by_dow[dow]['dirs'][(s,d)]+=1
    for dow in ['Tue','Fri']:
        d=by_dow[dow]
        print(f"  {dow} ({d['n']} draws):")
        for s in [1,2,3,4,5]:
            b=d['breaks'][s]
            hi=d['dirs'][(s,'high')]
            lo=d['dirs'][(s,'low')]
            print(f"    P{s}: {b:2d} breaks ({hi}H/{lo}L)")
    print()

    # 2) Co-occurrence matrix: when seat X breaks, which others break?
    print("🪞 CO-BREAK MATRIX (P=row breaks → P=col break frequency):")
    co = defaultdict(lambda: defaultdict(int))
    seat_total = Counter()
    for r in sub:
        nums=sorted(r['numbers'])
        breaks={s for s,v in zip([1,2,3,4,5],nums) if break_dir(s,v)}
        for s in breaks:
            seat_total[s]+=1
            for s2 in breaks:
                if s!=s2: co[s][s2]+=1
    print("       P1   P2   P3   P4   P5")
    for s in [1,2,3,4,5]:
        row=f"  P{s}: "
        for s2 in [1,2,3,4,5]:
            if s==s2: row+=f" -- "
            else:
                tot=seat_total[s]
                pct=100*co[s][s2]/tot if tot else 0
                row+=f" {pct:4.0f}%"
            row+=" "
        print(row)
    print()

    # 3) What does the BD (Before Draw) look like before a heavy-break (3+) draw?
    print("📜 BD BEFORE HEAVY-BREAK DRAWS (≥3 seats out of range):")
    for i,r in enumerate(sub):
        nums=sorted(r['numbers'])
        nbr=sum(1 for s,v in zip([1,2,3,4,5],nums) if break_dir(s,v))
        if nbr>=3 and i>0:
            bd=sub[i-1]
            bd_nums=sorted(bd['numbers'])
            bd_breaks=sum(1 for s,v in zip([1,2,3,4,5],bd_nums) if break_dir(s,v))
            print(f"  {r['date']} ({WD[r['dt'].weekday()]}) draw={nums} ⭐{r.get('stars',[])} ({nbr} breaks)")
            print(f"    BD {bd['date']}: {bd_nums} ⭐{bd.get('stars',[])} ({bd_breaks} breaks)")
    print()

    # 4) Carrier-digit signature for HIGH-BREAK numbers
    print("💎 CARRIER GRAMMAR — high-break values mod-50 / minus-25:")
    print("  (high-break = number sits one decade above its seat)")
    for r in sub:
        nums=sorted(r['numbers'])
        for s,v in zip([1,2,3,4,5],nums):
            if break_dir(s,v)=='high' and v>=20:
                m25 = v-25 if v>25 else None
                rev = int(str(v)[::-1].lstrip('0') or '0')
                msg=f"  {r['date']} P{s}={v}"
                if m25: msg+=f"  −25→{m25}"
                if rev!=v: msg+=f"  rev→{rev}"
                if v>50: msg+=f"  mod50→{v%50}"
                print(msg)
    print()

    # 5) Reset law: draw AFTER a heavy-break
    print("🔄 RESET PATTERN — draw AFTER 3+ break events:")
    for i,r in enumerate(sub[:-1]):
        nums=sorted(r['numbers'])
        nbr=sum(1 for s,v in zip([1,2,3,4,5],nums) if break_dir(s,v))
        if nbr>=3:
            nx=sub[i+1]
            nx_nums=sorted(nx['numbers'])
            nx_breaks=sum(1 for s,v in zip([1,2,3,4,5],nx_nums) if break_dir(s,v))
            print(f"  {r['date']} ({nbr} breaks) → next {nx['date']}: {nx_nums} ({nx_breaks} breaks)")
    print()

    # 6) Date-sum bias
    print("📐 DATE-SUM BIAS for break events:")
    ds_break = defaultdict(list)
    for r in sub:
        ds = date_sum(r['dt'])
        nums=sorted(r['numbers'])
        nbr=sum(1 for s,v in zip([1,2,3,4,5],nums) if break_dir(s,v))
        ds_break[ds].append(nbr)
    for ds in sorted(ds_break):
        vals = ds_break[ds]
        avg = sum(vals)/len(vals)
        print(f"  date-sum {ds:2d}: {len(vals)} draws, avg breaks/draw = {avg:.1f}")
    print()

    # 7) Tonight signal: 05.05.2026 = Tue, date-sum = 5+5+2+0+2+6=20
    target = parse("05.05.2026")
    ds_today = date_sum(target)
    dow_today = WD[target.weekday()]
    print(f"🎯 TONIGHT 05.05.2026 — {dow_today}, date-sum={ds_today}")
    print(f"   Tue avg breaks: {sum(b['n'] for b in by_dow.values() if b)}")
    tue_total = by_dow['Tue']['n']
    tue_breaks = sum(by_dow['Tue']['breaks'].values())
    print(f"   Tue: {tue_total} draws, {tue_breaks} total breaks → {tue_breaks/tue_total:.1f} breaks/draw avg")
    if ds_today in ds_break:
        vals=ds_break[ds_today]
        print(f"   date-sum {ds_today}: {len(vals)} prev draws, avg {sum(vals)/len(vals):.1f} breaks/draw")
    bd = sub[-1]
    bd_nums = sorted(bd['numbers'])
    bd_breaks = sum(1 for s,v in zip([1,2,3,4,5],bd_nums) if break_dir(s,v))
    print(f"   BD (01.05): {bd_nums} ⭐{bd.get('stars')} → {bd_breaks} breaks")
    print(f"   BD break shape: P2=9 low, P3=42 high, P4=46 high")

if __name__=='__main__':
    main()
