"""🎻🎧🥂 DJ's P1-P2 Concat → Next-Draw Stars Audit

The DJ's teaching:
  "imagine P1-P2 is a real number or 39 or 93 ... can be 2-7, 72 or 27"
  Treat the front pair as a 2-digit cipher (both directions) and see what
  next-draw stars it decodes to.

We test MANY dialects and rank by hit-rate vs baseline.
Baseline: random 2-star pair from 66 combos = 1.5%
Baseline: any ONE star match from a 1-star guess = 2/12 = 16.7%
"""
import os, sys
from datetime import datetime
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
from pymongo import MongoClient
from collections import defaultdict


def reverse_int(n: int) -> int:
    return int(str(n)[::-1])


def star_pairs_from_number(value: int):
    """Decode number as concat of stars (both split positions)."""
    s = str(value)
    pairs = set()
    if len(s) < 2:
        return pairs
    for cut in range(1, len(s)):
        try:
            li, ri = int(s[:cut]), int(s[cut:])
            if 1 <= li <= 12 and 1 <= ri <= 12 and li != ri:
                pairs.add(tuple(sorted((li, ri))))
        except ValueError:
            pass
    return pairs


def load_draws():
    c = MongoClient(os.environ['MONGO_URL'])
    db = c[os.environ['DB_NAME']]
    draws = list(db.euromillions_draws.find({}, {'_id': 0}))
    for d in draws:
        try:
            d['_dt'] = datetime.strptime(d['date'], '%d.%m.%Y')
        except: d['_dt'] = None
    draws = [d for d in draws if d.get('_dt') and d.get('numbers') and len(d['numbers'])==5 and d.get('stars')]
    draws.sort(key=lambda x: x['_dt'])
    cutoff = datetime(2024, 5, 1)
    return [d for d in draws if d['_dt'] >= cutoff]


def main():
    draws = load_draws()
    print(f"\n🎻 Scanning {len(draws)} Euro draws · {draws[0]['date']} → {draws[-1]['date']}\n")
    print("="*80)
    print(" 🥂 P1|P2 CONCAT → NEXT-DRAW STARS · DIALECT AUDIT")
    print("="*80)

    # Each dialect: function(p1, p2) -> number to decode
    dialects = {
        'fwd (P1|P2)':          lambda p1, p2: int(f"{p1}{p2}"),
        'rev (P2|P1)':          lambda p1, p2: int(f"{p2}{p1}"),
        'fwd + 13':             lambda p1, p2: int(f"{p1}{p2}") + 13,
        'fwd - 13':             lambda p1, p2: int(f"{p1}{p2}") - 13,
        'rev + 13':             lambda p1, p2: int(f"{p2}{p1}") + 13,
        'rev - 13':             lambda p1, p2: int(f"{p2}{p1}") - 13,
        'fwd + 14':             lambda p1, p2: int(f"{p1}{p2}") + 14,
        'fwd + 7':              lambda p1, p2: int(f"{p1}{p2}") + 7,
        'fwd - 50':             lambda p1, p2: int(f"{p1}{p2}") - 50,
        'rev - 50':             lambda p1, p2: int(f"{p2}{p1}") - 50,
        'fwd - 42':             lambda p1, p2: int(f"{p1}{p2}") - 42,
        'rev - 42':             lambda p1, p2: int(f"{p2}{p1}") - 42,
        'fwd * 2':              lambda p1, p2: int(f"{p1}{p2}") * 2,
        'P1+P2':                lambda p1, p2: p1 + p2,
        'P1*P2':                lambda p1, p2: p1 * p2,
        '|P1-P2|':              lambda p1, p2: abs(p1 - p2),
        'sum+gap':              lambda p1, p2: (p1+p2) + abs(p2-p1),
    }

    results = {}
    for name, fn in dialects.items():
        exact = 0
        partial = 0
        total = 0
        for i in range(len(draws)-1):
            p1, p2 = sorted(draws[i]['numbers'])[:2]
            nxt = tuple(sorted(draws[i+1]['stars']))
            try:
                v = fn(p1, p2)
                if v < 0: continue
            except: continue
            total += 1
            pairs = star_pairs_from_number(v)
            if nxt in pairs:
                exact += 1
            elif any(nxt[0] in p or nxt[1] in p for p in pairs):
                partial += 1
        if total > 0:
            results[name] = (exact, partial, total)

    print(f"\n{'Dialect':<18}{'Exact hits':<13}{'Rate':<8}{'vs ×':<7}{'Partial':<10}")
    print("-"*58)
    for name in sorted(results, key=lambda k: -results[k][0]):
        exact, partial, total = results[name]
        rate = 100*exact/total
        ratio = rate / 1.5
        print(f"{name:<18}{exact}/{total:<11}{rate:>5.2f}% {ratio:>5.1f}× {partial:>5d}/{total}")

    # Unified dialect — ANY of top dialects hits
    print("\n" + "="*80)
    print(" 🎼 UNIFIED DIALECTS · if ANY of these fires, count as hit")
    print("="*80)

    top_dialects = ['fwd (P1|P2)', 'rev (P2|P1)', 'fwd + 13', 'rev + 13',
                    'fwd + 14', 'fwd + 7', 'fwd - 42', 'rev - 42']
    exact_any = 0; partial_any = 0; total_any = 0
    exact_log = []
    for i in range(len(draws)-1):
        p1, p2 = sorted(draws[i]['numbers'])[:2]
        nxt = tuple(sorted(draws[i+1]['stars']))
        pairs_all = set()
        for name in top_dialects:
            try:
                v = dialects[name](p1, p2)
                if v < 0: continue
                pairs_all.update(star_pairs_from_number(v))
            except: continue
        total_any += 1
        if nxt in pairs_all:
            exact_any += 1
            exact_log.append((draws[i]['date'], draws[i+1]['date'], (p1, p2), nxt, list(pairs_all)[:5]))
        elif any(nxt[0] in p or nxt[1] in p for p in pairs_all):
            partial_any += 1

    print(f"  Exact hits (both stars decoded): {exact_any}/{total_any}  ({100*exact_any/total_any:.2f}%)")
    print(f"  Partial hits (1 of 2 stars):     {partial_any}/{total_any}  ({100*partial_any/total_any:.2f}%)")
    print(f"  Combined reach:                  {exact_any+partial_any}/{total_any}  ({100*(exact_any+partial_any)/total_any:.2f}%)")

    # Show a sample of exact hits (first 15)
    print("\n🎯 FIRST 15 EXACT HITS:")
    for e in exact_log[:15]:
        print(f"  {e[0]} → {e[1]}: P1P2={e[2]}  actual stars={e[3]}  sample pairs={e[4]}")

    # LIVE CASE — 01.05 → nd
    print("\n" + "="*80)
    print(" 🔮 LIVE PROPHECY · 01.05.2026 → next draw (05.05.2026)")
    print("="*80)
    last = draws[-1]
    p1, p2 = sorted(last['numbers'])[:2]
    print(f"  Last draw: {last['date']} {last['numbers']} ⭐{last['stars']}")
    print(f"  P1={p1}, P2={p2} → fwd={p1}{p2} rev={p2}{p1}")
    all_predicted_pairs = set()
    print(f"\n  Dialect-by-dialect candidate ⭐ pairs:")
    for name in top_dialects:
        try:
            v = dialects[name](p1, p2)
            if v < 0: continue
            pairs = star_pairs_from_number(v)
            all_predicted_pairs.update(pairs)
            if pairs:
                print(f"    {name:<18}→ value={v:<6} ⭐ candidates: {sorted(pairs)}")
        except: pass
    print(f"\n  🎯 UNION of all dialect candidates: {sorted(all_predicted_pairs)}")

    # P5 chain continuation  
    print(f"\n  🎵 P5 chain continuation (your 89→98+13=111 prophecy):")
    p5s = [sorted(d['numbers'])[4] for d in draws[-3:]]
    s_ = p5s[2] + (p5s[1]-25) + (p5s[0]-25)
    final = reverse_int(s_) + 13
    print(f"    P5 triplet = {p5s} · sum={s_} · reverse={reverse_int(s_)} · +13={final}")
    print(f"    ⭐ prophecy pairs: {sorted(star_pairs_from_number(final))}")


if __name__ == '__main__':
    main()
