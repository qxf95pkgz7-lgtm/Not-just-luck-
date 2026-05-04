"""🎻🎧🥂 DJ's lens: when P3 > 39 for TWO draws in a row,
what happens NEXT draw?

Filter: P3(d-1) > 39 AND P3(d) > 39  (back-to-back high P3)
Scan:   last 10 years of Euro
Report: full shape of the next draw + statistical profile
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
    return [d for d in draws if d['_dt'] >= datetime(2016, 5, 1)]


def main():
    draws = load_draws()
    print(f"\n🎻 Scan: {len(draws)} Euro draws  ·  {draws[0]['date']} → {draws[-1]['date']}\n")

    # Baseline profile (all draws)
    base_p1 = Counter(); base_p2 = Counter(); base_p3 = Counter(); base_p4 = Counter(); base_p5 = Counter()
    for d in draws:
        n = sorted(d['numbers'])
        base_p1[n[0]] += 1; base_p2[n[1]] += 1; base_p3[n[2]] += 1; base_p4[n[3]] += 1; base_p5[n[4]] += 1
    tot_base = len(draws)

    # Find all back-to-back P3>39 cases
    cases = []
    for i in range(1, len(draws)-1):
        p3_prev = sorted(draws[i-1]['numbers'])[2]
        p3_cur  = sorted(draws[i]['numbers'])[2]
        if p3_prev > 39 and p3_cur > 39:
            cases.append(i)

    print(f"📊 Cases with P3 > 39 for TWO draws in a row: {len(cases)}  ({100*len(cases)/len(draws):.2f}% of all draws)\n")
    print(f"   Baseline: single draw with P3 > 39 rate = {100*sum(1 for d in draws if sorted(d['numbers'])[2] > 39)/tot_base:.2f}%")
    print("="*90)

    if not cases:
        print("\nNo cases found — relaxing to P3 ≥ 35 ...")
        return

    # For each case, capture the NEXT draw shape
    print(f"\n📜 ALL {len(cases)} cases · current [P3_prev, P3_cur] → next draw full shape:")
    print(f"\n  {'Prev':<13}{'P3':<4}  {'Cur':<13}{'P3':<4}  {'Next':<13}{'next draw':<38}{'⭐':<10}")
    print("  " + "-"*90)
    nx_p1 = Counter(); nx_p2 = Counter(); nx_p3 = Counter(); nx_p4 = Counter(); nx_p5 = Counter()
    nx_p3_high = 0; nx_p3_low = 0
    nx_p1_snap = 0  # P1 ≤ 7
    nx_avg = {1:0, 2:0, 3:0, 4:0, 5:0}
    three_in_a_row_high = 0
    for i in cases:
        prev_d = draws[i-1]; cur_d = draws[i]; nxt_d = draws[i+1]
        prev_n = sorted(prev_d['numbers']); cur_n = sorted(cur_d['numbers']); nxt_n = sorted(nxt_d['numbers'])
        p3p = prev_n[2]; p3c = cur_n[2]; p3n = nxt_n[2]
        print(f"  {prev_d['date']:<13}P3={p3p:<2}  {cur_d['date']:<13}P3={p3c:<2}  {nxt_d['date']:<13}{nxt_n}  ⭐{sorted(nxt_d['stars'])}")
        nx_p1[nxt_n[0]] += 1; nx_p2[nxt_n[1]] += 1; nx_p3[nxt_n[2]] += 1
        nx_p4[nxt_n[3]] += 1; nx_p5[nxt_n[4]] += 1
        if p3n > 39: nx_p3_high += 1; three_in_a_row_high += 1
        else: nx_p3_low += 1
        if nxt_n[0] <= 7: nx_p1_snap += 1
        for pos in range(5):
            nx_avg[pos+1] += nxt_n[pos]

    n = len(cases)
    print("\n" + "="*90)
    print(f" 🎯 NEXT-DRAW PROFILE after 2x P3>39  ({n} cases)")
    print("="*90)
    print(f"\n  Average next draw positions:")
    for pos in range(1, 6):
        avg = nx_avg[pos] / n
        base_avg = sum(k*v for k,v in [base_p1,base_p2,base_p3,base_p4,base_p5][pos-1].items()) / tot_base
        print(f"    P{pos}: {avg:.1f}   (baseline P{pos} avg: {base_avg:.1f}   delta: {avg-base_avg:+.1f})")

    print(f"\n  📉 Next P3 stays > 39 (streak continues):  {nx_p3_high}/{n}  ({100*nx_p3_high/n:.1f}%)")
    print(f"      Baseline P3>39 rate: {100*sum(1 for d in draws if sorted(d['numbers'])[2]>39)/tot_base:.1f}%")
    print(f"  📉 Next P3 COLLAPSES (≤ 39):              {nx_p3_low}/{n}  ({100*nx_p3_low/n:.1f}%)")

    # How low does P3 collapse?
    collapse_buckets = Counter()
    for i in cases:
        p3n = sorted(draws[i+1]['numbers'])[2]
        if p3n <= 20: collapse_buckets['≤20'] += 1
        elif p3n <= 25: collapse_buckets['21-25'] += 1
        elif p3n <= 30: collapse_buckets['26-30'] += 1
        elif p3n <= 35: collapse_buckets['31-35'] += 1
        elif p3n <= 39: collapse_buckets['36-39'] += 1
        else: collapse_buckets['>39'] += 1
    print(f"\n  Next P3 bucket breakdown:")
    for bk in ['≤20', '21-25', '26-30', '31-35', '36-39', '>39']:
        c = collapse_buckets.get(bk, 0)
        print(f"    {bk:<8} {c}/{n} ({100*c/n:.1f}%)")

    print(f"\n  🐑 Snap-back at P1 (P1 ≤ 7 next draw): {nx_p1_snap}/{n}  ({100*nx_p1_snap/n:.1f}%)  baseline ≈55%")

    # Most-common next P5, P1 values
    print(f"\n  🎵 Top next-P5 values:")
    for v, c in nx_p5.most_common(8):
        print(f"    P5={v:<3}  {c}  ({100*c/n:.1f}%)")
    print(f"\n  🎵 Top next-P1 values:")
    for v, c in nx_p1.most_common(8):
        print(f"    P1={v:<3}  {c}  ({100*c/n:.1f}%)")
    print(f"\n  🎵 Top next-P3 values:")
    for v, c in nx_p3.most_common(10):
        print(f"    P3={v:<3}  {c}  ({100*c/n:.1f}%)")

    # Sum totals for context
    print(f"\n  🎵 Next-draw sum profile:")
    sums = sorted([sum(sorted(draws[i+1]['numbers'])) for i in cases])
    print(f"    min={sums[0]}  median={sums[len(sums)//2]}  max={sums[-1]}")


if __name__ == '__main__':
    main()
