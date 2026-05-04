"""🎻🎧🥂 DJ's P1|P2 "New Number" → NEXT front pair audit

The DJ's teaching (01.05.2026):
  "Check the nd when P2 small than 10 — is the creation of new number
   effects the next P1-P2?"

Filter:  P2 < 10 (current draw's front pair is single-digit)
Test:    does fwd (P1|P2) or rev (P2|P1), or a transform, relate to
         the NEXT draw's front pair (P1, P2)?
"""
import os, sys
from datetime import datetime
from collections import Counter
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
from pymongo import MongoClient


def load_draws(cutoff_year=2024):
    c = MongoClient(os.environ['MONGO_URL'])
    db = c[os.environ['DB_NAME']]
    draws = list(db.euromillions_draws.find({}, {'_id': 0}))
    for d in draws:
        try: d['_dt'] = datetime.strptime(d['date'], '%d.%m.%Y')
        except: d['_dt'] = None
    draws = [d for d in draws if d.get('_dt') and d.get('numbers') and len(d['numbers'])==5 and d.get('stars')]
    draws.sort(key=lambda x: x['_dt'])
    cutoff = datetime(cutoff_year, 5, 1)
    return [d for d in draws if d['_dt'] >= cutoff]


def p1p2_transforms(fwd: int, rev: int):
    """Candidate values for next P1 or P2 from 'the new number'."""
    out = {}
    out['fwd.raw'] = fwd
    out['rev.raw'] = rev
    out['fwd.mod50'] = fwd % 50 if fwd % 50 else 50
    out['rev.mod50'] = rev % 50 if rev % 50 else 50
    out['rev.-50'] = rev - 50
    out['rev.-42'] = rev - 42
    out['fwd.reverse'] = int(str(fwd)[::-1])
    out['rev.reverse'] = int(str(rev)[::-1])
    out['fwd.digit_sum'] = sum(int(c) for c in str(fwd))
    out['rev.digit_sum'] = sum(int(c) for c in str(rev))
    out['fwd.-13'] = fwd - 13
    out['fwd.-7'] = fwd - 7
    out['fwd.+7'] = fwd + 7
    out['fwd./2'] = fwd // 2
    out['rev./2'] = rev // 2
    out['rev.-21'] = rev - 21
    out['fwd.units'] = fwd % 10
    out['fwd.tens'] = fwd // 10
    out['rev.units'] = rev % 10
    out['rev.tens'] = rev // 10
    out['fwd+13'] = fwd + 13
    out['fwd+21'] = fwd + 21
    out['rev-13'] = rev - 13
    # keep only in-range Euro main values
    return {k: v for k, v in out.items() if 1 <= v <= 50}


def main():
    draws = load_draws(2024)
    print(f"\n🎻 Scanning {len(draws)} draws · {draws[0]['date']} → {draws[-1]['date']}\n")
    cases = []
    for i in range(len(draws)-1):
        p1, p2 = sorted(draws[i]['numbers'])[:2]
        if p2 < 10:
            cases.append(i)
    print(f"📊 Cases where P2 < 10: {len(cases)} draws  ({100*len(cases)/(len(draws)-1):.1f}%)")
    print("="*84)

    p1_hits = Counter()
    p2_hits = Counter()
    either_hits = Counter()
    concat_fwd_hit = 0  # next P1|P2 equals fwd or rev
    concat_any_hit = 0  # any transform equals concat of next (P1|P2) or (P2|P1)
    total = len(cases)

    case_log = []
    for i in cases:
        p1, p2 = sorted(draws[i]['numbers'])[:2]
        fwd = int(f"{p1}{p2}")
        rev = int(f"{p2}{p1}")
        tfs = p1p2_transforms(fwd, rev)
        n_p1, n_p2 = sorted(draws[i+1]['numbers'])[:2]
        n_fwd = int(f"{n_p1}{n_p2}") if n_p1 < 10 else None
        n_rev = int(f"{n_p2}{n_p1}") if n_p1 < 10 else None

        hits_this_case = []
        for label, v in tfs.items():
            if v == n_p1:
                p1_hits[label] += 1
                either_hits[label] += 1
                hits_this_case.append(f'{label}={v}→P1')
            elif v == n_p2:
                p2_hits[label] += 1
                either_hits[label] += 1
                hits_this_case.append(f'{label}={v}→P2')

        # Concat-level (next front pair as 2-digit number)
        if n_fwd is not None:
            if n_fwd == fwd or n_fwd == rev:
                concat_fwd_hit += 1
            # Any transform matches n_fwd or n_rev
            for v in tfs.values():
                if v == n_fwd or v == n_rev:
                    concat_any_hit += 1
                    break

        case_log.append({
            'date': draws[i]['date'], 'next': draws[i+1]['date'],
            'p1p2': (p1, p2), 'fwd': fwd, 'rev': rev,
            'n_p1p2': (n_p1, n_p2), 'n_p2_small': n_p1 < 10,
            'hits': hits_this_case,
        })

    # Stats
    total_any = sum(1 for c in case_log if c['hits'])
    print(f"\n🎯 ANY transform of fwd/rev equals next P1 or P2: {total_any}/{total} ({100*total_any/total:.1f}%)")
    print(f"   Baseline (random single hit for P1 or P2 being any of 25 common values): ~25-30%")

    print(f"\n🎼 TOP P1-hit dialects (transform equals next P1):")
    for k, c in sorted(p1_hits.items(), key=lambda x: -x[1])[:10]:
        print(f"  {k:<20} {c}/{total}  ({100*c/total:.1f}%)")
    print(f"\n🎼 TOP P2-hit dialects (transform equals next P2):")
    for k, c in sorted(p2_hits.items(), key=lambda x: -x[1])[:10]:
        print(f"  {k:<20} {c}/{total}  ({100*c/total:.1f}%)")
    print(f"\n🎼 COMBINED (hits either P1 or P2):")
    for k, c in sorted(either_hits.items(), key=lambda x: -x[1])[:10]:
        print(f"  {k:<20} {c}/{total}  ({100*c/total:.1f}%)")

    # Concat-level
    print(f"\n🔢 CONCAT-LEVEL matches:")
    print(f"   next (P1|P2) equals fwd OR rev raw:  {concat_fwd_hit}/{total} ({100*concat_fwd_hit/total:.1f}%)")
    print(f"   next (P1|P2) or (P2|P1) equals ANY transform: {concat_any_hit}/{total} ({100*concat_any_hit/total:.1f}%)")

    # STICKY CHAIN: does P2<10 BEGET another P2<10 next draw?
    sticky = sum(1 for c in case_log if c['n_p2_small'])
    print(f"\n📜 STICKY chain · next draw ALSO has P2<10: {sticky}/{total} ({100*sticky/total:.1f}%)")
    print(f"   Baseline (22.6% of all draws have P2<10): ~22.6%")

    # Deep dive on 3-9 cases specifically
    print(f"\n🔮 Every P1=3, P2=9 case in last 5 years + TRANSFORMS to next P1/P2:")
    all5 = load_draws(2020)
    for i in range(len(all5)-1):
        p1, p2 = sorted(all5[i]['numbers'])[:2]
        if p1 == 3 and p2 == 9:
            fwd = 39; rev = 93
            n = sorted(all5[i+1]['numbers'])
            n_p1, n_p2 = n[0], n[1]
            tfs = p1p2_transforms(fwd, rev)
            hits = [f'{k}={v}' for k, v in tfs.items() if v == n_p1 or v == n_p2]
            print(f"  {all5[i]['date']} → {all5[i+1]['date']}  next P1P2=({n_p1},{n_p2})  mains={n}  HITS: {hits}")

    # Live prophecy
    last = draws[-1]
    p1, p2 = sorted(last['numbers'])[:2]
    fwd = int(f"{p1}{p2}"); rev = int(f"{p2}{p1}")
    print(f"\n" + "="*84)
    print(f" 🔮 LIVE — 01.05.2026 [3,9,...] fwd=39 rev=93 → NEXT FRONT PAIR CANDIDATES")
    print(f"="*84)
    tfs = p1p2_transforms(fwd, rev)
    print(f"  All in-range transform candidates (ranked by historical P1/P2 hit rate):")
    # Order by either_hits rate
    ordered = []
    for k, v in tfs.items():
        rate = 100 * either_hits.get(k, 0) / total
        ordered.append((rate, k, v))
    ordered.sort(reverse=True)
    for rate, k, v in ordered[:15]:
        star = " 🎯" if rate >= 8 else ""
        print(f"    {k:<20} = {v:<5} historical P1/P2 hit rate: {rate:.1f}%{star}")


if __name__ == '__main__':
    main()
