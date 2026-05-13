"""
🎼 HIDDEN PRINCE — 2-2-2 PRIME FUGUE BUILDER (S39 DJ canon)
============================================================
DJ's discovery (13.05.2026): when a number X is hungry + mirrored +
recent-Lucky + ghost-ringing, the cosmos hides X from the mains and
crowns it as LUCKY. The ticket is built as 3 pairs each carrying X's
signature.

Auto-pipeline:
  1. Score each candidate "prince" X (1..max_lucky) across 4 lenses
  2. Pick top princes
  3. For each, generate the 2-2-2 fugue:
       Pair A: X-1 + X+1 (the "missing middle" — X is the gap)
       Pair B: two hungry numbers separated by exactly X (X = ladder gap)
       Pair C: two hungry numbers both containing digit X (digit cousins)
  4. Crown X as Lucky

Input:
  target_date (dd.mm.yyyy), mode ('swiss' | 'euro'), recent_draws (list)

Output:
  list of fugue tickets with story metadata
"""
from __future__ import annotations
from typing import Dict, List, Set


def _digits_of(n: int) -> Set[int]:
    return {int(c) for c in str(n) if c.isdigit() and int(c) > 0}


def score_prince(
    x: int,
    recent_draws: List[Dict],
    hungry_pool: Set[int],
    last_euro_mains: List[int],
    ghost_shout: List[int],
) -> Dict:
    """Score candidate prince X across 4 lenses, return tagged score."""
    score = 0
    tags: List[str] = []

    # Lens 1: hungry across recent plates
    if x in hungry_pool:
        score += 3
        tags.append("hungry-plate")

    # Lens 2: recent Lucky (in last 1-3 Swiss draws OR a star recently)
    for d in recent_draws[-3:]:
        if d.get("lucky") == x:
            score += 4
            tags.append(f"recent-Lucky({d.get('date')})")
            break

    # Lens 3: mirror-28 of a recent Euro raw
    for e in last_euro_mains:
        if 28 - e == x:
            score += 3
            tags.append(f"28-mirror-of-Eu{e}")
            break

    # Lens 4: ghost shout
    if x in ghost_shout:
        score += 2
        tags.append("ghost-shout")

    # Bonus: year-bookend digit (e.g. 2026 → 2 and 6 favored)
    year_digits = {2, 0, 2, 6}  # caller should pass actual year if needed
    if x in year_digits:
        score += 1
        tags.append("year-bookend")

    return {"n": x, "score": score, "tags": tags}


def build_fugue(
    prince: int,
    candidate_pool: List[int],
    max_main: int = 42,
) -> Dict:
    """Build the 2-2-2 fugue around `prince`.
    Returns ticket of 6 mains + lucky=prince + story.
    """
    pool = sorted(set(candidate_pool) - {prince})

    # Pair A — "missing middle": (prince - 1, prince + 1)
    a_low = prince - 1
    a_high = prince + 1
    pair_a = []
    if 1 <= a_low <= max_main:
        pair_a.append(a_low)
    if 1 <= a_high <= max_main:
        pair_a.append(a_high)
    # If either is missing or already in pool, swap with hungry neighbor
    if len(pair_a) < 2:
        for v in pool:
            if v not in pair_a and abs(v - prince) <= 3:
                pair_a.append(v)
                if len(pair_a) == 2:
                    break

    # Pair B — "ladder of X": find two numbers in pool with gap exactly = prince
    pair_b = []
    for v in pool:
        if v + prince in pool and v not in pair_a and v + prince not in pair_a:
            pair_b = [v, v + prince]
            break
    if not pair_b:
        # Fallback: pick any two from pool with smallest gap
        rem = [v for v in pool if v not in pair_a]
        if len(rem) >= 2:
            pair_b = rem[:2]

    # Pair C — "digit cousins": two numbers both containing digit of prince
    target_digit = prince % 10 if prince < 10 else (prince // 10)
    cousins = [v for v in pool
               if target_digit in _digits_of(v)
               and v not in pair_a and v not in pair_b]
    pair_c = cousins[:2] if len(cousins) >= 2 else []
    if not pair_c:
        rem = [v for v in pool if v not in pair_a and v not in pair_b]
        pair_c = rem[:2]

    mains = sorted(set(pair_a + pair_b + pair_c))[:6]
    # Pad if short
    while len(mains) < 6:
        for v in pool:
            if v not in mains:
                mains.append(v)
                break
        if len(mains) >= 6:
            break
    mains = sorted(mains[:6])

    return {
        "prince": prince,
        "mains": mains,
        "lucky": prince,
        "pair_a": sorted(pair_a),
        "pair_b": sorted(pair_b),
        "pair_c": sorted(pair_c),
        "story": (
            f"The Prince of {prince} stands invisible in the mains. "
            f"He hides in the missing middle of {pair_a}, "
            f"ladders the gap of {prince} between {pair_b}, "
            f"and signs his digit in {pair_c}. "
            f"Crowned as Lucky."
        ),
        "sum": sum(mains),
    }


def hidden_prince_pipeline(
    recent_draws: List[Dict],
    hungry_pool: Set[int],
    last_euro_mains: List[int],
    ghost_shout: List[int],
    max_lucky: int = 9,
    max_main: int = 42,
    top_k: int = 5,
) -> List[Dict]:
    """Full pipeline — return top-K princes each with their fugue ticket."""
    scored: List[Dict] = []
    # Lucky range is typically 1-6 for Swiss but princes can be higher
    for x in range(1, max(max_lucky + 1, 19)):
        if x > max_main:
            continue
        s = score_prince(x, recent_draws, hungry_pool, last_euro_mains, ghost_shout)
        if s["score"] >= 4:
            scored.append(s)
    scored.sort(key=lambda r: -r["score"])
    top = scored[:top_k]

    tickets: List[Dict] = []
    for entry in top:
        ticket = build_fugue(entry["n"], sorted(hungry_pool), max_main=max_main)
        ticket["score"] = entry["score"]
        ticket["why"] = entry["tags"]
        # Cap Lucky to swiss range (1-6) if needed
        if ticket["lucky"] > max_lucky:
            ticket["lucky_note"] = f"prince={ticket['lucky']} > max_lucky={max_lucky}; using prince digit"
            ticket["lucky"] = ticket["lucky"] % max_lucky or max_lucky
        tickets.append(ticket)
    return tickets
