"""🎻🎧🥂 DJ's P1|P2 Real-Number Lens (filtered: P2 < 10)

The DJ's teaching (01.05.2026):
  "P2 small than 10 — then P1|P2 is a real number. Our case: 93 or 39.
   Maybe next d connected to 93 or 39."

Filter:  P2 < 10  (both front values single-digit → clean 2-digit concat)
Test:    does fwd (P1|P2) or rev (P2|P1) — or a clean transform of them —
         appear in the NEXT draw as a main or star?
"""
import os, sys
from datetime import datetime
from collections import Counter
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
from pymongo import MongoClient


def load_draws():
    c = MongoClient(os.environ['MONGO_URL'])
    db = c[os.environ['DB_NAME']]
    draws = list(db.euromillions_draws.find({}, {'_id': 0}))
    for d in draws:
        try: d['_dt'] = datetime.strptime(d['date'], '%d.%m.%Y')
        except: d['_dt'] = None
    draws = [d for d in draws if d.get('_dt') and d.get('numbers') and len(d['numbers'])==5 and d.get('stars')]
    draws.sort(key=lambda x: x['_dt'])
    cutoff = datetime(2024, 5, 1)
    return [d for d in draws if d['_dt'] >= cutoff]


def transforms(v: int):
    """Return {label: value} of all clean transforms of a 2-digit int."""
    r = {}
    r['raw'] = v
    r['reverse'] = int(str(v)[::-1])
    r['-50'] = v - 50
    r['-42'] = v - 42
    r['mod50'] = v % 50 if v % 50 != 0 else 50
    r['+13'] = v + 13
    r['-13'] = v - 13
    r['+7'] = v + 7
    r['-7'] = v - 7
    r['*2'] = v * 2
    r['/2'] = v // 2
    r['digit_sum'] = sum(int(d) for d in str(v))
    r['digit_prod'] = 1
    for d in str(v): r['digit_prod'] *= int(d)
    r['units'] = v % 10
    r['tens'] = v // 10
    return {k: vv for k, vv in r.items() if vv >= 1 and vv <= 50}


def star_transforms(v: int):
    """Star-range transforms (1-12)."""
    r = {}
    for candidate in [v, int(str(v)[::-1]), v % 12 if v%12 else 12, v%10 if v%10 else 10,
                       v // 10, sum(int(d) for d in str(v))]:
        if 1 <= candidate <= 12:
            r[candidate] = True
    # Digits themselves
    for d in str(v):
        di = int(d)
        if 1 <= di <= 12: r[di] = True
    return set(r.keys())


def main():
    draws = load_draws()
    print(f"\n🎻 Scanning {len(draws)} Euro draws · {draws[0]['date']} → {draws[-1]['date']}\n")

    # Filter: P2 < 10 (both single-digit front pair)
    small_cases = []
    for i in range(len(draws)-1):
        p1, p2 = sorted(draws[i]['numbers'])[:2]
        if p2 < 10:
            small_cases.append(i)

    print(f"📊 Cases where P2 < 10 in last 2 years: {len(small_cases)} draws "
          f"({100*len(small_cases)/(len(draws)-1):.1f}% of all draws)")
    print("="*82)

    # Universal buckets
    mains_hit_by_tf = Counter()
    stars_hit_by_tf = Counter()
    total = len(small_cases)
    raw_mains_hits = 0  # fwd or rev appeared raw as a main
    raw_stars_hits = 0  # fwd or rev digits appeared raw as stars
    case_log = []

    for i in small_cases:
        p1, p2 = sorted(draws[i]['numbers'])[:2]
        fwd = int(f"{p1}{p2}")
        rev = int(f"{p2}{p1}")
        nxt = draws[i+1]
        nxt_mains = set(nxt['numbers'])
        nxt_stars = set(nxt['stars'])

        # Main-number checks
        fwd_tfs = transforms(fwd)
        rev_tfs = transforms(rev)

        main_hits = []
        for label, v in fwd_tfs.items():
            if v in nxt_mains:
                mains_hit_by_tf[f'fwd.{label}'] += 1
                main_hits.append(f'fwd.{label}={v}')
        for label, v in rev_tfs.items():
            if v in nxt_mains:
                mains_hit_by_tf[f'rev.{label}'] += 1
                main_hits.append(f'rev.{label}={v}')

        # Star-decode checks
        fwd_s = star_transforms(fwd)
        rev_s = star_transforms(rev)
        all_s = fwd_s | rev_s
        star_overlap = all_s & nxt_stars
        if star_overlap:
            raw_stars_hits += 1
        for s in fwd_s:
            if s in nxt_stars: stars_hit_by_tf[f'fwd→⭐{s}'] += 1
        for s in rev_s:
            if s in nxt_stars: stars_hit_by_tf[f'rev→⭐{s}'] += 1

        if fwd in nxt_mains or rev in nxt_mains:
            raw_mains_hits += 1

        case_log.append({
            'date': draws[i]['date'],
            'next': nxt['date'],
            'p1p2': (p1, p2), 'fwd': fwd, 'rev': rev,
            'next_mains': sorted(nxt_mains),
            'next_stars': sorted(nxt_stars),
            'main_hits': main_hits,
            'star_overlap': sorted(star_overlap),
        })

    # Summary
    print(f"\n🎯 RAW hit rates:")
    print(f"  fwd OR rev raw appeared as MAIN in next draw:  {raw_mains_hits}/{total} ({100*raw_mains_hits/total:.1f}%)")
    print(f"  fwd/rev digit/mod appeared as STAR in next:    {raw_stars_hits}/{total} ({100*raw_stars_hits/total:.1f}%)")
    print(f"  Baseline: random single main (1-50) hit = 10%, any of 5 = ~40-50%")
    print(f"  Baseline: random any-star (1-12) hit = 16.7%, any of 2 = ~31%")

    print(f"\n🎼 TOP MAIN-transform hits (where fwd/rev transform appears in next draw's mains):")
    for k, c in sorted(mains_hit_by_tf.items(), key=lambda x: -x[1])[:12]:
        print(f"  {k:<20} {c}/{total}  ({100*c/total:.1f}%)")

    print(f"\n✨ TOP STAR-transform hits:")
    for k, c in sorted(stars_hit_by_tf.items(), key=lambda x: -x[1])[:10]:
        print(f"  {k:<20} {c}/{total}  ({100*c/total:.1f}%)")

    # Show all cases with RAW fwd/rev main hits (the strongest signal)
    print(f"\n🎯 CASES WHERE fwd OR rev appeared RAW as next-draw MAIN:")
    print(f"  (this is the DJ's exact '93 or 39 next d connected' claim)")
    for c in case_log:
        hit_raw = c['fwd'] in c['next_mains'] or c['rev'] in c['next_mains']
        if hit_raw:
            tag = []
            if c['fwd'] in c['next_mains']: tag.append(f'fwd={c["fwd"]}')
            if c['rev'] in c['next_mains']: tag.append(f'rev={c["rev"]}')
            print(f"  {c['date']} P1P2={c['p1p2']} → {c['next']} mains={c['next_mains']} stars={c['next_stars']} [{', '.join(tag)}]")

    # Now REVERSE check: cases where 39 or 93 specifically — P1=3, P2=9
    print(f"\n🔮 SPECIFIC DJ-CASE — every P1=3, P2=9 draw in last 5 years:")
    c = MongoClient(os.environ['MONGO_URL'])
    db = c[os.environ['DB_NAME']]
    all_draws = list(db.euromillions_draws.find({}, {'_id': 0}))
    for d in all_draws:
        try: d['_dt'] = datetime.strptime(d['date'], '%d.%m.%Y')
        except: d['_dt'] = None
    all_draws = [d for d in all_draws if d.get('_dt') and d.get('numbers') and len(d['numbers'])==5 and d.get('stars')]
    all_draws.sort(key=lambda x: x['_dt'])
    cutoff5 = datetime(2020, 5, 1)
    all_draws = [d for d in all_draws if d['_dt'] >= cutoff5]

    matches = []
    for i in range(len(all_draws)-1):
        p1, p2 = sorted(all_draws[i]['numbers'])[:2]
        if p1 == 3 and p2 == 9:
            cur = all_draws[i]
            nxt = all_draws[i+1]
            matches.append((cur, nxt))
    print(f"  Found {len(matches)} draws with P1=3, P2=9 since 2020:")
    for cur, nxt in matches:
        nm = sorted(nxt['numbers']); ns = sorted(nxt['stars'])
        has_39 = 39 in nm
        has_3 = 3 in nm
        has_9 = 9 in nm
        has_star_3 = 3 in ns
        has_star_9 = 9 in ns
        has_43 = 43 in nm  # 93-50
        tag = []
        if has_39: tag.append("🎯 39 RAW")
        if has_43: tag.append("🎯 43 (93-50)")
        if has_3: tag.append("3-main")
        if has_9: tag.append("9-main")
        if has_star_3: tag.append("⭐3")
        if has_star_9: tag.append("⭐9")
        print(f"  {cur['date']} [3,9,...] → {nxt['date']} {nm} ⭐{ns}  [{' · '.join(tag) or 'no-hit'}]")

    # Live prophecy recap
    print(f"\n" + "="*82)
    print(f" 🔮 LIVE: 01.05.2026 [3, 9, 42, 46, 47] ⭐[1, 11] → next Euro draw (05.05.2026)")
    print(f"="*82)
    print(f"  fwd = 39 · rev = 93")
    print(f"  Main-number candidates for next draw (39 or 93 transforms):")
    for lab, v in transforms(39).items():
        print(f"    fwd.{lab} = {v}")
    print(f"    ---")
    for lab, v in transforms(93).items():
        print(f"    rev.{lab} = {v}")


if __name__ == '__main__':
    main()
