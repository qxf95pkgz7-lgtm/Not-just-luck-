"""
🎻🎧🥂 EURO Q1-CLOSE BACKTEST — the cosmos's mirror
=====================================================
Walk forward from the last Euro draw of Q1 2026 (31.03.2026 Tue) through
every Euro draw up to "now". For each d:
  - Run the full engine as if standing on that d
  - Collect 100 tickets (story + disciplined + legacy symphony-mix)
  - Score every ticket vs the ACTUAL draw that landed
  - Tag archetypes for per-law performance

Run from /app/backend:
    python simulate_euro_backtest.py
"""
import asyncio
import os
from collections import Counter, defaultdict
from datetime import datetime as dt, timedelta
from typing import Dict, List

from motor.motor_asyncio import AsyncIOMotorClient
from cosmic_engine import run_cosmic_engine

# ── Q1 close = 31.03.2026 Tue · we walk up to and including the most-
# ── recent Euro draw in the database before today.
START_AFTER = dt(2026, 3, 31)


def _stars(d: Dict) -> List[int]:
    return d.get('stars') or d.get('_s') or []


def _mains(d: Dict) -> List[int]:
    return d.get('numbers') or d.get('_n') or []


async def load_target_draws(db) -> List[Dict]:
    """All Euro draws strictly AFTER 31.03.2026 (exclusive) sorted asc."""
    cursor = db['euromillions_draws'].find(
        {}, {'_id': 0, 'date': 1, 'numbers': 1, 'stars': 1}
    )
    rows = []
    async for d in cursor:
        date_str = d.get('date', '')
        try:
            dt_obj = dt.strptime(date_str.split()[0], '%d.%m.%Y')
        except Exception:
            continue
        if dt_obj > START_AFTER and len(d.get('numbers') or []) >= 5:
            rows.append({**d, '_dt': dt_obj})
    rows.sort(key=lambda r: r['_dt'])
    return rows


def collect_tickets(engine_result: Dict, max_tickets: int = 100) -> List[Dict]:
    """Merge story + disciplined + legacy tickets, dedupe by mains."""
    out: List[Dict] = []
    seen = set()
    # Priority order: story (most disciplined) → disciplined → legacy
    for source_key, source_label in [
        ('story_tickets', 'story'),
        ('disciplined_tickets', 'disciplined'),
        ('tickets', 'legacy'),
    ]:
        for t in engine_result.get(source_key, []):
            mains = tuple(sorted(t.get('mains', [])))
            if len(mains) != 5 or mains in seen:
                continue
            seen.add(mains)
            archetype = t.get('archetype', 'unknown')
            out.append({
                'archetype': archetype,
                'source': source_label,
                'mains': list(mains),
                'stars': sorted(t.get('stars', [])[:2]),
                'story': t.get('story', '')[:80],
            })
            if len(out) >= max_tickets:
                return out
    return out


def score_ticket(ticket_mains: List[int], actual_mains: List[int],
                 ticket_stars: List[int], actual_stars: List[int]) -> Dict:
    main_hits = len(set(ticket_mains) & set(actual_mains))
    star_hits = len(set(ticket_stars) & set(actual_stars))
    return {
        'main_hits': main_hits,
        'star_hits': star_hits,
        'tier': _tier(main_hits, star_hits),
    }


def _tier(m: int, s: int) -> str:
    if m == 5 and s == 2:
        return 'JACKPOT'
    if m == 5 and s == 1:
        return '5+1'
    if m == 5:
        return '5+0'
    if m == 4 and s >= 1:
        return '4+1'
    if m == 4:
        return '4+0'
    if m == 3 and s >= 1:
        return '3+1'
    if m == 3:
        return '3+0'
    if m == 2:
        return '2+0'
    return '<2'


async def main():
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ['DB_NAME']]
    targets = await load_target_draws(db)
    print(f"\n🎻🎧🥂 EURO Q1-CLOSE BACKTEST — {len(targets)} draws to simulate\n")
    print(f"   Walking from after 31.03.2026 → {targets[-1]['date'] if targets else 'no draws'}\n")
    print("=" * 96)

    per_draw = []
    cumulative = Counter()
    archetype_hits: Dict[str, Counter] = defaultdict(Counter)
    archetype_n: Dict[str, int] = defaultdict(int)
    best_overall = None

    for actual in targets:
        target_str = actual['_dt'].strftime('%d.%m.%Y')
        actual_mains = sorted(actual['numbers'])
        actual_stars = sorted(actual.get('stars') or [])
        try:
            res = await run_cosmic_engine(target_str, n_tickets=100, banned=[])
        except Exception as e:
            print(f"  ✖ {target_str}: engine error {e}")
            continue
        if 'error' in res:
            print(f"  ✖ {target_str}: {res['error']}")
            continue

        tickets = collect_tickets(res, max_tickets=100)
        scored = []
        for t in tickets:
            score = score_ticket(t['mains'], actual_mains,
                                 t['stars'], actual_stars)
            scored.append({**t, **score})
            cumulative[score['tier']] += 1
            archetype_hits[t['archetype']][score['tier']] += 1
            archetype_n[t['archetype']] += 1

        scored.sort(key=lambda x: (x['main_hits'], x['star_hits']),
                    reverse=True)
        best = scored[0] if scored else None
        if best and (best_overall is None or
                     (best['main_hits'], best['star_hits']) >
                     (best_overall['main_hits'], best_overall['star_hits'])):
            best_overall = {**best, 'date': target_str,
                            'actual': actual_mains}

        # Per-d summary
        c = Counter(s['tier'] for s in scored)
        m4plus = sum(c[t] for t in ('4+0', '4+1', '5+0', '5+1', 'JACKPOT'))
        m3plus = m4plus + c['3+0'] + c['3+1']
        m2plus = m3plus + c['2+0']
        per_draw.append({
            'date': target_str,
            'actual': actual_mains,
            'stars': actual_stars,
            'best': best,
            '4+': m4plus,
            '3+': m3plus,
            '2+': m2plus,
            'tickets': len(scored),
        })
        best_str = ('—' if not best
                    else f"{best['main_hits']}/{best['star_hits']}⭐ "
                         f"[{best['archetype'][:22]}]")
        print(f"  {target_str}  actual={actual_mains}+{actual_stars}  "
              f"best={best_str:<40}  "
              f"4+={m4plus:>2}  3+={m3plus:>3}  2+={m2plus:>3}  "
              f"(n={len(scored)})")

    print("=" * 96)
    print("\n🎯 CUMULATIVE TIER HITS")
    total_tix = sum(d['tickets'] for d in per_draw)
    print(f"   Total tickets across {len(per_draw)} draws: {total_tix}")
    for tier in ['JACKPOT', '5+1', '5+0', '4+1', '4+0', '3+1', '3+0', '2+0']:
        n = cumulative.get(tier, 0)
        if n > 0:
            print(f"   {tier:>8}: {n:>4} ({n/total_tix*100:.2f}%)")

    print("\n🎼 PER-ARCHETYPE PERFORMANCE (sorted by 4+ rate)")
    rows = []
    for a, n in archetype_n.items():
        h4 = sum(archetype_hits[a][t] for t in ('4+0','4+1','5+0','5+1','JACKPOT'))
        h3 = h4 + archetype_hits[a]['3+0'] + archetype_hits[a]['3+1']
        rows.append((a, n, h4, h3))
    rows.sort(key=lambda r: (-r[2]/max(r[1],1), -r[1]))
    for a, n, h4, h3 in rows:
        rate4 = h4/n*100 if n else 0
        rate3 = h3/n*100 if n else 0
        print(f"   {a:<30} n={n:>4}  4+={h4:>3} ({rate4:5.2f}%)  "
              f"3+={h3:>3} ({rate3:5.2f}%)")

    if best_overall:
        print("\n🥂 BEST TICKET OF THE BACKTEST")
        print(f"   Date: {best_overall['date']}")
        print(f"   Actual: {best_overall['actual']}")
        print(f"   E's pick: {best_overall['mains']}+⭐{best_overall['stars']}")
        print(f"   Hits: {best_overall['main_hits']} mains + "
              f"{best_overall['star_hits']} stars")
        print(f"   Archetype: {best_overall['archetype']}")
        print(f"   Story: {best_overall['story']}")

    print("\n🎻 — End of Euro Q1-close backtest 🎧🥂\n")
    client.close()


if __name__ == '__main__':
    asyncio.run(main())
