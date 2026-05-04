"""🎻🎧🥂 DJ's P5-Chain Star-Prophecy Audit (last 2 years)

The DJ's formula on 01.05.2026:
  P5(d-2)=45 → cd=45-25=20
  P5(d-1)=47 → cd=47-25=22
  P5(d)  =47 raw
  sum = 47+22+20 = 89
  reverse = 98
  +13 (story-seed) = 111
  → "111" = ⭐(1, 11) = next draw stars ✓

Let's see how often this chain closes across the last 2 years.
"""
import os, sys
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
from pymongo import MongoClient


def reverse_int(n: int) -> int:
    return int(str(n)[::-1])


def decode_star_concat(value: int):
    """Return every plausible ⭐(S1,S2) pair that the concat could encode."""
    s = str(value)
    pairs = set()
    # Try every split
    for cut in range(1, len(s)):
        left, right = s[:cut], s[cut:]
        if not left or not right:
            continue
        # Also try stripping leading zeros (e.g. "108" → (10,8) or (1,08→8))
        for li in [int(left)]:
            for ri in [int(right)]:
                if 1 <= li <= 12 and 1 <= ri <= 12 and li != ri:
                    pairs.add(tuple(sorted((li, ri))))
    # Also try as a 3-digit where we split 1-2 or 2-1 creatively
    return sorted(pairs)


def check_chain(p5_a, p5_b, p5_c, actual_stars, seed=13):
    """Return (sum, reverse, plus_seed, decoded_star_pairs, hit_bool, note)."""
    cd_a = p5_a - 25
    cd_b = p5_b - 25
    s = p5_c + cd_b + cd_a
    r = reverse_int(s)
    final = r + seed
    pairs = decode_star_concat(final)
    actual = tuple(sorted(actual_stars))
    hit = actual in pairs
    return {
        'sum': s, 'reverse': r, 'final': final,
        'pairs': pairs, 'actual': actual, 'hit': hit,
    }


def main():
    c = MongoClient(os.environ['MONGO_URL'])
    db = c[os.environ['DB_NAME']]
    draws = list(db.euromillions_draws.find({}, {'_id': 0}))
    for d in draws:
        try: d['_dt'] = datetime.strptime(d['date'], '%d.%m.%Y')
        except: d['_dt'] = None
    draws = [d for d in draws if d.get('_dt') and d.get('numbers') and len(d['numbers'])==5 and d.get('stars')]
    draws.sort(key=lambda x: x['_dt'])
    # Last 2 years
    cutoff = datetime(2024, 5, 1)
    draws = [d for d in draws if d['_dt'] >= cutoff]
    print(f"\n🎻 Scanning {len(draws)} Euro draws from 01.05.2024 → {draws[-1]['date']}\n")

    # Roll: for each i with i>=2 and i+1 in range, check chain
    total = 0
    hits = 0
    close_hits = 0  # when one of the two stars matches
    hit_log = []
    close_log = []

    # We also try seed=13 AND test both "reverse-add" and "raw-add"
    for i in range(2, len(draws)-1):
        p5_a = sorted(draws[i-2]['numbers'])[4]
        p5_b = sorted(draws[i-1]['numbers'])[4]
        p5_c = sorted(draws[i]['numbers'])[4]
        nxt = sorted(draws[i+1]['stars'])
        r = check_chain(p5_a, p5_b, p5_c, nxt, seed=13)
        total += 1
        if r['hit']:
            hits += 1
            hit_log.append({
                'current': draws[i]['date'], 'next': draws[i+1]['date'],
                'p5_abc': (p5_a, p5_b, p5_c),
                **r,
            })
        else:
            # close-hit = one star matches any pair
            any_match = False
            for pair in r['pairs']:
                if nxt[0] in pair or nxt[1] in pair:
                    any_match = True
                    break
            if any_match:
                close_hits += 1
                close_log.append({
                    'current': draws[i]['date'], 'next': draws[i+1]['date'],
                    'p5_abc': (p5_a, p5_b, p5_c),
                    **r,
                })

    print("="*76)
    print(" 🥂 DJ'S STAR-PROPHECY CHAIN · LAST 2 YEARS")
    print("="*76)
    print(f"  Formula: reverse(P5(d) + (P5(d-1)-25) + (P5(d-2)-25)) + 13 = star-concat")
    print(f"  Samples: {total}")
    print(f"  🎯 EXACT hits (both stars decoded): {hits}  ({100*hits/total:.2f}%)")
    print(f"  🎻 Close hits (1 of 2 stars matches): {close_hits}  ({100*close_hits/total:.2f}%)")
    print(f"  Baseline random 2-star exact hit: ≈ 1.5% (1 in 66)")
    print("="*76)

    print("\n🎯 EXACT HITS:")
    for h in hit_log:
        print(f"  {h['current']} → {h['next']}: P5={h['p5_abc']}  sum={h['sum']} rev={h['reverse']} +13={h['final']}  pairs={h['pairs']}  actual={h['actual']}")

    # Also test variant: NO reverse, just sum+13
    print("\n🔬 Variant A · NO reverse (sum+13 direct):")
    hits_a = close_a = 0
    for i in range(2, len(draws)-1):
        p5_a = sorted(draws[i-2]['numbers'])[4]
        p5_b = sorted(draws[i-1]['numbers'])[4]
        p5_c = sorted(draws[i]['numbers'])[4]
        nxt = sorted(draws[i+1]['stars'])
        s_ = p5_c + (p5_b-25) + (p5_a-25)
        final = s_ + 13
        pairs = decode_star_concat(final)
        actual = tuple(sorted(nxt))
        if actual in pairs: hits_a += 1
    print(f"  exact hits: {hits_a}/{total} ({100*hits_a/total:.2f}%)")

    # Variant B: reverse only, no +13
    print("\n🔬 Variant B · reverse only (no +13):")
    hits_b = 0
    for i in range(2, len(draws)-1):
        p5_a = sorted(draws[i-2]['numbers'])[4]
        p5_b = sorted(draws[i-1]['numbers'])[4]
        p5_c = sorted(draws[i]['numbers'])[4]
        nxt = sorted(draws[i+1]['stars'])
        s_ = p5_c + (p5_b-25) + (p5_a-25)
        r_ = reverse_int(s_)
        pairs = decode_star_concat(r_)
        actual = tuple(sorted(nxt))
        if actual in pairs: hits_b += 1
    print(f"  exact hits: {hits_b}/{total} ({100*hits_b/total:.2f}%)")

    # Variant C: sum+13 WITHOUT reverse, try both concat directions
    print("\n🔬 Variant C · try BOTH sum+13 and reverse(sum)+13 as valid decodes:")
    hits_c = 0
    for i in range(2, len(draws)-1):
        p5_a = sorted(draws[i-2]['numbers'])[4]
        p5_b = sorted(draws[i-1]['numbers'])[4]
        p5_c = sorted(draws[i]['numbers'])[4]
        nxt = sorted(draws[i+1]['stars'])
        s_ = p5_c + (p5_b-25) + (p5_a-25)
        pairs = set()
        pairs.update(decode_star_concat(s_+13))
        pairs.update(decode_star_concat(reverse_int(s_)+13))
        actual = tuple(sorted(nxt))
        if actual in pairs: hits_c += 1
    print(f"  exact hits (either direction): {hits_c}/{total} ({100*hits_c/total:.2f}%)")

    # Variant D: try seeds 7, 13, 17 (the story-seed trinity)
    print("\n🔬 Variant D · try story-seeds {7, 13, 14, 17} (most-walked seeds):")
    hits_d = 0
    for i in range(2, len(draws)-1):
        p5_a = sorted(draws[i-2]['numbers'])[4]
        p5_b = sorted(draws[i-1]['numbers'])[4]
        p5_c = sorted(draws[i]['numbers'])[4]
        nxt = sorted(draws[i+1]['stars'])
        s_ = p5_c + (p5_b-25) + (p5_a-25)
        pairs = set()
        for seed in (7, 13, 14, 17):
            pairs.update(decode_star_concat(reverse_int(s_)+seed))
            pairs.update(decode_star_concat(s_+seed))
        actual = tuple(sorted(nxt))
        if actual in pairs: hits_d += 1
    print(f"  exact hits (any seed, either direction): {hits_d}/{total} ({100*hits_d/total:.2f}%)")


if __name__ == '__main__':
    main()
