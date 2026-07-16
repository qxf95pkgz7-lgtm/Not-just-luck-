"""
🎼 CANON 37 — DRAW INDEX DECODER (Mr. E's brain)

Given a target draw index (yearly count, e.g. #57 for Fri 17.07.2026),
decode how the universe encodes that index into the 5 sorted mains via:
  - 1P: single position (direct or Circle-lifted)
  - 2P: pair sum (any subset Circle-lifted)
  - 3P: triple sum (any subset Circle-lifted)

For FUTURE draws (no numbers yet), enumerate all candidate numbers derived
from the RC0 cosmic pool (RC0 = the anchor draw 32 draws prior, or user-set)
and rank candidate pairs/triples summing to the target.

For PAST draws, show which encodings actually fired + RC0 pool overlap.

Circle carrier for Euro = +25 (Swiss = +21). Wrap into [1, N] where N = 50
for Euro mains, 42 for Swiss mains.
"""

from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase


CARRIER = {"euro": 25, "swiss": 21}
POOL_MAX = {"euro": 50, "swiss": 42}
COLLECTION = {"euro": "euromillions_draws", "swiss": "draws"}
Q_PER_YEAR = {"euro": 27, "swiss": 26}  # approx draws per quarter


def wrap(n: int, hi: int) -> int:
    while n > hi:
        n -= hi
    while n < 1:
        n += hi
    return n


def circle(n: int, mode: str) -> int:
    return wrap(n + CARRIER[mode], POOL_MAX[mode])


def flip_wrap(n: int, mode: str) -> int:
    """Flip digits then wrap into range."""
    r = int(str(n).zfill(2)[::-1])
    return wrap(r, POOL_MAX[mode]) if r > 0 else n


def find_encodings(mains: List[int], target: int, mode: str) -> Dict[str, List[str]]:
    """Enumerate all 1P/2P/3P encodings of `target` from sorted mains."""
    C = lambda n: circle(n, mode)
    out = {"1P": [], "2P": [], "3P": []}
    positions = [(f"P{i+1}", mains[i]) for i in range(len(mains))]

    # 1P
    for k, v in positions:
        if v == target:
            out["1P"].append(f"{k}={v}")
        if C(v) == target:
            out["1P"].append(f"C({k})={v}→{C(v)}")

    # 2P
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            k1, v1 = positions[i]
            k2, v2 = positions[j]
            for c1 in (False, True):
                for c2 in (False, True):
                    a = C(v1) if c1 else v1
                    b = C(v2) if c2 else v2
                    if a + b == target:
                        l1 = f"C({k1})" if c1 else k1
                        l2 = f"C({k2})" if c2 else k2
                        out["2P"].append(f"{l1}({a})+{l2}({b})")

    # 3P
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            for k in range(j + 1, len(positions)):
                k1, v1 = positions[i]
                k2, v2 = positions[j]
                k3, v3 = positions[k]
                for c1 in (False, True):
                    for c2 in (False, True):
                        for c3 in (False, True):
                            a = C(v1) if c1 else v1
                            b = C(v2) if c2 else v2
                            c = C(v3) if c3 else v3
                            if a + b + c == target:
                                l1 = f"C({k1})" if c1 else k1
                                l2 = f"C({k2})" if c2 else k2
                                l3 = f"C({k3})" if c3 else k3
                                out["3P"].append(f"{l1}+{l2}+{l3}={a}+{b}+{c}")
    return out


def rc0_cosmic_pool(rc0_mains: List[int], mode: str, draws_between: int = 32) -> Dict[int, List[str]]:
    """Build the full cosmic pool from RC0 mains through all carriers.
    Returns dict: {number → [carrier tags]}.
    """
    C = lambda n: circle(n, mode)
    W = lambda n: wrap(n, POOL_MAX[mode])
    F = lambda n: flip_wrap(n, mode)
    pool: Dict[int, List[str]] = {}

    def add(n: int, tag: str):
        n = W(n)
        pool.setdefault(n, []).append(tag)

    for n in rc0_mains:
        add(n, "RC0")
        add(C(n), "C25")
        add(W(n + draws_between), f"+{draws_between}")
        add(W(n - draws_between), f"-{draws_between}")
        add(W(n + 13), "+13")
        add(W(POOL_MAX[mode] + 1 - n), "Comp")
        add(W(C(n) + draws_between), f"C25+{draws_between}")
        add(F(n), "Flip")
        add(C(F(n)), "Flip→C25")
    return pool


def rank_future_candidates(rc0_pool: Dict[int, List[str]], target: int, mode: str) -> Dict[str, Any]:
    """For a future draw, enumerate candidate pairs/triples from pool summing to target."""
    C = lambda n: circle(n, mode)
    pool_nums = sorted(rc0_pool.keys())

    def source_score(n: int) -> int:
        """Higher = more cosmically pure (more carriers point at n)."""
        return len(rc0_pool.get(n, []))

    # Direct pairs
    pair_direct = []
    for i, a in enumerate(pool_nums):
        for b in pool_nums[i + 1:]:
            if a + b == target:
                pair_direct.append({
                    "a": a, "b": b,
                    "a_src": rc0_pool[a], "b_src": rc0_pool[b],
                    "purity": source_score(a) + source_score(b),
                })
    pair_direct.sort(key=lambda x: -x["purity"])

    # Circle-lifted pairs (one lifted)
    pair_circle = []
    for i, a in enumerate(pool_nums):
        for b in pool_nums:
            if a == b: continue
            if C(a) + b == target and (a, b) not in {(p["a"], p["b"]) for p in pair_direct}:
                pair_circle.append({
                    "a_raw": a, "a_lifted": C(a), "b": b,
                    "a_src": rc0_pool[a], "b_src": rc0_pool[b],
                    "formula": f"C({a})={C(a)}+{b}={target}",
                    "purity": source_score(a) + source_score(b),
                })
    pair_circle.sort(key=lambda x: -x["purity"])

    # Direct triples
    triple_direct = []
    for i, a in enumerate(pool_nums):
        for j, b in enumerate(pool_nums[i + 1:], start=i + 1):
            for c in pool_nums[j + 1:]:
                if a + b + c == target:
                    triple_direct.append({
                        "a": a, "b": b, "c": c,
                        "a_src": rc0_pool[a], "b_src": rc0_pool[b], "c_src": rc0_pool[c],
                        "purity": source_score(a) + source_score(b) + source_score(c),
                    })
    triple_direct.sort(key=lambda x: -x["purity"])

    return {
        "pool_size": len(pool_nums),
        "pool": pool_nums,
        "pair_direct": pair_direct[:15],
        "pair_circle": pair_circle[:15],
        "triple_direct": triple_direct[:15],
    }


def suggest_ticket(rc0_pool: Dict[int, List[str]], target: int, mode: str) -> List[int]:
    """Auto-assemble a 5-number sorted ticket from the top RC0-purity candidates
    that includes at least one 2P or 3P pair/triple summing to target."""
    C = lambda n: circle(n, mode)
    pool_nums = sorted(rc0_pool.keys(), key=lambda n: (-len(rc0_pool[n]), n))
    # find any direct pair summing to target
    for a in pool_nums:
        for b in pool_nums:
            if a >= b: continue
            if a + b == target:
                # anchor pair found; fill with 3 more high-purity numbers
                anchor = {a, b}
                fillers = [n for n in pool_nums if n not in anchor][:3]
                return sorted(list(anchor) + fillers)
    # fallback: top-5 by purity
    return sorted(pool_nums[:5])


async def decode_target(
    db: AsyncIOMotorDatabase,
    mode: str,
    target_index: int,
    year: int,
    rc0_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Master entry — decode/forecast a target draw index within a year.

    If the draw exists (past), show actual mains + all encodings + RC0 overlap.
    If future, show RC0 pool + candidate pairs/triples + suggested ticket.
    """
    coll = COLLECTION[mode]
    # Get RC0 mains
    if rc0_date is None:
        # Default RC0 = draw #24 of Euro 2026 (24.03.2026)
        rc0_date = "24.03.2026" if mode == "euro" else None
    rc0_doc = await db[coll].find_one({"date": rc0_date}) if rc0_date else None
    rc0_mains = sorted(rc0_doc["numbers"]) if rc0_doc else []

    # Get all draws of the target year
    year_draws = await db[coll].find({"date": {"$regex": f"\\.{year}$"}}).to_list(500)

    def key(d): return tuple(map(int, d["date"].split(".")[::-1]))  # (yyyy, mm, dd)
    year_draws.sort(key=key)

    result: Dict[str, Any] = {
        "mode": mode,
        "target_index": target_index,
        "year": year,
        "rc0_date": rc0_date,
        "rc0_mains": rc0_mains,
    }

    if 1 <= target_index <= len(year_draws):
        target_doc = year_draws[target_index - 1]
        target_mains = sorted(target_doc["numbers"])
        rc0_pool = rc0_cosmic_pool(rc0_mains, mode) if rc0_mains else {}
        rc0_overlap = [n for n in target_mains if n in rc0_pool]
        encodings = find_encodings(target_mains, target_index, mode)
        result.update({
            "status": "past",
            "date": target_doc["date"],
            "mains": target_mains,
            "stars": target_doc.get("stars", []),
            "encodings": encodings,
            "rc0_overlap": rc0_overlap,
            "rc0_overlap_count": len(rc0_overlap),
            "rc0_overlap_sources": {n: rc0_pool.get(n, []) for n in rc0_overlap},
        })
    else:
        # Future draw — forecast
        rc0_pool = rc0_cosmic_pool(rc0_mains, mode) if rc0_mains else {}
        forecast = rank_future_candidates(rc0_pool, target_index, mode)
        suggested = suggest_ticket(rc0_pool, target_index, mode)
        result.update({
            "status": "future",
            "date": year_draws[-1]["date"] if year_draws else None,
            "note": f"Draw #{target_index} not yet in DB. Forecasting from RC0.",
            "forecast": forecast,
            "suggested_ticket": suggested,
            "rc0_pool_full": {int(k): v for k, v in rc0_pool.items()},
        })

    return result
