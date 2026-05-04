"""🎻🎧🥂 Deeper audit:
  (b) When P2<10 AND next P2<10 (chain holds) — which transform fires loudest?
  (c) Mirror: when P2>=10 (large front), does next P2>=10 too?
"""
import os, sys
from datetime import datetime
from collections import Counter
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
from pymongo import MongoClient


def load_draws(year_cutoff=2024):
    c = MongoClient(os.environ['MONGO_URL'])
    db = c[os.environ['DB_NAME']]
    draws = list(db.euromillions_draws.find({}, {'_id': 0}))
    for d in draws:
        try: d['_dt'] = datetime.strptime(d['date'], '%d.%m.%Y')
        except: d['_dt'] = None
    draws = [d for d in draws if d.get('_dt') and d.get('numbers') and len(d['numbers'])==5 and d.get('stars')]
    draws.sort(key=lambda x: x['_dt'])
    return [d for d in draws if d['_dt'] >= datetime(year_cutoff, 5, 1)]


def p1p2_transforms(fwd, rev):
    out = {
        'fwd.raw': fwd, 'rev.raw': rev,
        'fwd.units': fwd % 10, 'fwd.tens': fwd // 10,
        'rev.units': rev % 10, 'rev.tens': rev // 10,
        'fwd.digit_sum': sum(int(c) for c in str(fwd)),
        'fwd.-13': fwd - 13, 'fwd.+13': fwd + 13, 'fwd.-7': fwd - 7, 'fwd.+7': fwd + 7,
        'fwd./2': fwd // 2, 'rev./2': rev // 2,
        'rev.-50': rev - 50, 'rev.-42': rev - 42, 'rev.-21': rev - 21,
        'rev.mod50': rev % 50 if rev % 50 else 50,
        'fwd.mod50': fwd % 50 if fwd % 50 else 50,
    }
    return {k: v for k, v in out.items() if 1 <= v <= 50}


def main():
    draws = load_draws(2024)
    print(f"\n🎻 Scan {len(draws)} draws · {draws[0]['date']} → {draws[-1]['date']}\n")

    # ========== (c) MIRROR LAW: P2>=10 chain ==========
    large_chain = 0; large_total = 0
    small_chain = 0; small_total = 0
    mid_chain = 0; mid_total = 0  # P2 in [10, 14]
    tall_chain = 0; tall_total = 0  # P2 >= 15
    for i in range(len(draws)-1):
        _, p2 = sorted(draws[i]['numbers'])[:2]
        _, n_p2 = sorted(draws[i+1]['numbers'])[:2]
        if p2 < 10:
            small_total += 1
            if n_p2 < 10: small_chain += 1
        else:
            large_total += 1
            if n_p2 >= 10: large_chain += 1
        if 10 <= p2 <= 14:
            mid_total += 1
            if 10 <= n_p2 <= 14: mid_chain += 1
        if p2 >= 15:
            tall_total += 1
            if n_p2 >= 15: tall_chain += 1
    print("="*82)
    print(" 🔁 (c) THE CHAIN / MIRROR LAW — does the front-pair size stick?")
    print("="*82)
    print(f"  small chain (P2<10 → next P2<10):       {small_chain}/{small_total}  ({100*small_chain/small_total:.1f}%)  baseline 22.6%")
    print(f"  large chain (P2≥10 → next P2≥10):       {large_chain}/{large_total}  ({100*large_chain/large_total:.1f}%)  baseline 77.4%")
    print(f"  mid chain   (P2∈[10,14] → next same):   {mid_chain}/{mid_total}  ({100*mid_chain/mid_total:.1f}%)")
    print(f"  tall chain  (P2≥15 → next P2≥15):       {tall_chain}/{tall_total}  ({100*tall_chain/tall_total:.1f}%)")

    # ========== (b) Chain-held cases — what transform fires? ==========
    cases = []
    for i in range(len(draws)-1):
        p1, p2 = sorted(draws[i]['numbers'])[:2]
        n_p1, n_p2 = sorted(draws[i+1]['numbers'])[:2]
        if p2 < 10 and n_p2 < 10:
            cases.append((i, p1, p2, n_p1, n_p2))
    total = len(cases)
    print("\n" + "="*82)
    print(f" 🎯 (b) CHAIN-HELD CASES — P2<10 AND next P2<10 ({total} cases)")
    print(f"    Which transform of fwd/rev fires strongest at next P1 or P2?")
    print("="*82)

    p1_hits = Counter(); p2_hits = Counter(); both_hits = Counter(); ever_hits = 0
    chain_log = []
    for (i, p1, p2, n_p1, n_p2) in cases:
        fwd = int(f"{p1}{p2}"); rev = int(f"{p2}{p1}")
        tfs = p1p2_transforms(fwd, rev)
        case_hits = []
        for k, v in tfs.items():
            if v == n_p1:
                p1_hits[k] += 1; both_hits[k] += 1
                case_hits.append(f'{k}={v}→P1')
            elif v == n_p2:
                p2_hits[k] += 1; both_hits[k] += 1
                case_hits.append(f'{k}={v}→P2')
        if case_hits:
            ever_hits += 1
        chain_log.append({'date': draws[i]['date'], 'next': draws[i+1]['date'],
                           'cur': (p1, p2), 'nxt': (n_p1, n_p2), 'hits': case_hits})

    print(f"\n  📊 Ever-any-hit rate in chain cases: {ever_hits}/{total} ({100*ever_hits/total:.1f}%)")
    print(f"\n  🎼 TOP dialects (hit next P1 or P2) when chain holds:")
    for k, c in sorted(both_hits.items(), key=lambda x: -x[1])[:10]:
        print(f"    {k:<20} {c}/{total}  ({100*c/total:.1f}%)")

    print(f"\n  🎼 TOP P1-hit dialects in chain:")
    for k, c in sorted(p1_hits.items(), key=lambda x: -x[1])[:6]:
        print(f"    {k:<20} {c}/{total}  ({100*c/total:.1f}%)")
    print(f"\n  🎼 TOP P2-hit dialects in chain:")
    for k, c in sorted(p2_hits.items(), key=lambda x: -x[1])[:6]:
        print(f"    {k:<20} {c}/{total}  ({100*c/total:.1f}%)")

    # Show all chain cases
    print(f"\n  📜 ALL {total} chain cases (current [P1,P2] → next [P1,P2]):")
    for e in chain_log[:40]:
        hh = ' | '.join(e['hits']) if e['hits'] else '∅'
        print(f"    {e['date']} {e['cur']} → {e['next']} {e['nxt']}   {hh}")

    # ========== EXACT FRONT-PAIR REPEAT / OSCILLATE ==========
    exact_repeat = 0
    swap = 0  # next P1==cur P2, next P2==cur P1
    within1 = 0
    for (i, p1, p2, n_p1, n_p2) in cases:
        if (n_p1, n_p2) == (p1, p2): exact_repeat += 1
        if (n_p1, n_p2) == (p2, p1): swap += 1
        if abs(n_p1-p1) <= 1 and abs(n_p2-p2) <= 1: within1 += 1
    print(f"\n  🎵 Chain fine-grain:")
    print(f"    exact front-pair repeat: {exact_repeat}/{total}")
    print(f"    front-pair swap (mirror): {swap}/{total}")
    print(f"    next front within ±1 of current: {within1}/{total}  ({100*within1/total:.1f}%)")


if __name__ == '__main__':
    main()
