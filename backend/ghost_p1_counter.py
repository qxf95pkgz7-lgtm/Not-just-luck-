"""
👻 GHOST P1 COUNTER — `ghost_p1_counter.py`
==========================================
Per-weekday-stream P1 ghost ledger with cumulative debt scoring.

DJ canon (Session 33):
  • "P1-2 first d and 2 d later come p1-4 then it's a ghost" (3 was skipped → 3 = ghost)
  • "When p1-10 instead of 5" → 5,6,7,8,9 all become ghosts (the gap)
  • Older ghosts weigh more than fresh ones (cumulative debt)
  • Swiss-circle projection: if next P1=X, back-closer hint = circle(X) or circle(pair-twin)

Output schema:
  {
    "weekday": "Wed" | "Sat" | "Tue" | "Fri",
    "quarter": 2,
    "year": 2026,
    "played_p1_sequence": [(date, p1), ...],
    "played_p1_set": [1, 2, 4],
    "ghost_p1_ranked": [{"n": 5, "age_d": 5, "score": 12, "reason": "..."}],
    "snap_back_chain": [{"d_position": 4, "p1": 10, "ghosts_introduced": [5,6,7,8,9]}],
    "deepest_ghost": {"n": 5, "age_d": 5},
  }
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from year_d_ledger import (
    EURO_MAINS_MAX,
    SWISS_MAINS_MAX,
    current_quarter_stream,
    ghost_set,
    load_draws,
    parse_dt,
    position_sequence,
    quarter_of,
    split_by_weekday,
)

# Reasonable upper bound on what P1 actually ever lands at (for ghost candidate space).
# Historically Swiss P1 rarely exceeds 16, Euro P1 rarely exceeds 25.
P1_GHOST_CEILING_SWISS = 20
P1_GHOST_CEILING_EURO = 25


def _detect_snap_back_chain(p1_sequence: List[tuple]) -> List[Dict]:
    """A 'snap-back' chain happens when P1 jumps abruptly LOW → HIGH or HIGH → LOW,
    leaving every integer between the prior and current P1 as a fresh ghost.

    Example (Swiss Wed-d Q2 2026):
      d1 P1=2, d3 P1=4 → ghosts={3}  (gap=2)
      d4 P1=10 → ghosts={5,6,7,8,9}  (gap=6 from prev P1=4)
    """
    chain = []
    prev_p1 = None
    for i, (date, p1) in enumerate(p1_sequence, start=1):
        if prev_p1 is not None:
            gap = p1 - prev_p1
            if abs(gap) >= 2:
                lo, hi = sorted([prev_p1, p1])
                introduced = list(range(lo + 1, hi))
                if introduced:
                    chain.append({
                        "d_position": i,
                        "date": date,
                        "p1": p1,
                        "prev_p1": prev_p1,
                        "gap": gap,
                        "ghosts_introduced": introduced,
                    })
        prev_p1 = p1
    return chain


def compute_ghost_p1(
    p1_sequence: List[tuple],
    weekday: str,
    quarter: int,
    year: int,
    mode: str,
) -> Dict:
    """Given the chronological P1 sequence of a single weekday-stream within
    a quarter, compute the ghost ledger.

    p1_sequence: [(date_str, p1_value), ...] in chronological order (oldest first).
    """
    ceiling = P1_GHOST_CEILING_SWISS if mode == "swiss" else P1_GHOST_CEILING_EURO
    played = [p for _, p in p1_sequence]
    played_set = sorted(set(played))
    raw_ghosts = [n for n in range(1, ceiling + 1) if n not in set(played)]

    # Age each ghost by the FIRST d-position where it could have landed but didn't.
    # An n becomes a ghost the first d-position where the cumulative played P1 set
    # implies "n should have appeared by now". Conservative: we age every ghost from
    # the first d-position whose P1 was >= n (the first time the sequence reached n's level).
    ghost_ages: Dict[int, int] = {}
    for d_pos, (_, p1) in enumerate(p1_sequence, start=1):
        for n in raw_ghosts:
            if n not in ghost_ages and p1 >= n:
                ghost_ages[n] = len(p1_sequence) - d_pos + 1
                # age = how many draws ago this ghost first became 'owed'

    # Ghost score: age (older = louder) + bonus for snap-back gap
    snap_back = _detect_snap_back_chain(p1_sequence)
    snap_back_introduced: Dict[int, int] = {}
    for sb in snap_back:
        for n in sb["ghosts_introduced"]:
            snap_back_introduced[n] = sb["d_position"]

    ranked = []
    for n in raw_ghosts:
        age = ghost_ages.get(n, 0)
        if age == 0 and n not in snap_back_introduced:
            # Hasn't been "owed" yet — outside the played range with no snap-back debt
            continue
        reasons = []
        score = 0
        if age > 0:
            score += age * 2
            reasons.append(f"age-{age}")
        if n in snap_back_introduced:
            score += 5
            reasons.append(f"snap-back-d{snap_back_introduced[n]}")
        ranked.append({"n": n, "age_d": age, "score": score, "reason": " | ".join(reasons)})

    ranked.sort(key=lambda x: (-x["score"], x["n"]))
    deepest = ranked[0] if ranked else None

    return {
        "weekday": weekday,
        "quarter": quarter,
        "year": year,
        "mode": mode,
        "played_p1_sequence": [{"date": d, "p1": p} for d, p in p1_sequence],
        "played_p1_set": played_set,
        "ghost_p1_ranked": ranked,
        "snap_back_chain": snap_back,
        "deepest_ghost": deepest,
        "ghost_ceiling": ceiling,
    }


async def build_p1_ghost_ledger(target_date: str, mode: str) -> Dict:
    """Master entry point.
    Returns weekday-split ghost ledger for the target's current quarter.

    For the target weekday's stream — full ghost analysis.
    For the OTHER weekday — same analysis (so we keep the canon: Wed/Sat separate).
    """
    target_dt = parse_dt(target_date)
    if not target_dt:
        return {"error": "invalid date"}
    target_q = quarter_of(target_dt, mode)
    target_y = target_dt.year
    target_wd = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}[target_dt.weekday()]

    draws = await load_draws(mode)
    streams = split_by_weekday(draws, mode)

    out: Dict = {
        "target_date": target_date,
        "target_weekday": target_wd,
        "target_quarter": target_q,
        "target_year": target_y,
        "mode": mode,
        "streams": {},
    }

    for wd, ws_draws in streams.items():
        stream = current_quarter_stream(target_dt, wd, draws, mode)
        if not stream:
            out["streams"][wd] = {"empty": True, "weekday": wd}
            continue
        p1_seq = [(d["date"], d["p"][0]) for d in stream]
        ledger = compute_ghost_p1(p1_seq, wd, target_q, target_y, mode)
        out["streams"][wd] = ledger

    out["target_stream"] = out["streams"].get(target_wd, {})
    return out


if __name__ == "__main__":
    import asyncio
    import json

    res = asyncio.run(build_p1_ghost_ledger("06.05.2026", "swiss"))
    print(json.dumps(res, indent=2, default=str))
