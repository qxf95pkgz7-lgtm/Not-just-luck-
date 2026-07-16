"""
🎫 KOMBO TRACKER — Two historical-match tools for the DJ.

Kombo #1 — VIRGIN CHECK: given a set of mains, tell the DJ if this exact
combination has EVER played, and if so, on which date(s).

Kombo #2 — POSITION MATCH FINDER: given position-specific values
(e.g. P3=21, P5=47), return every historical draw whose sorted mains
match those exact positions.

Both work for Swiss (6 mains) and Euro (5 mains).
"""

from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase


def _collection_for(mode: str) -> str:
    m = (mode or "").lower()
    if m == "swiss":
        return "draws"
    if m == "euro":
        return "euromillions_draws"
    raise ValueError(f"Unknown mode '{mode}' — expected 'swiss' or 'euro'")


def _expected_size(mode: str) -> int:
    return 6 if mode.lower() == "swiss" else 5


async def virgin_check(
    db: AsyncIOMotorDatabase,
    mode: str,
    nums: List[int],
) -> Dict[str, Any]:
    """Kombo #1 — check if the exact sorted set of mains ever played.

    Returns:
        {
            "mode": "swiss"|"euro",
            "nums": [sorted mains],
            "expected_size": 5|6,
            "is_virgin": bool,        # True = never played
            "play_count": int,        # 0 = virgin, N = played N times
            "matches": [
                {"date": "dd.mm.yyyy", "numbers": [...], "lucky_number": 1, "replay_number": 3}
                or {"date": "dd.mm.yyyy", "numbers": [...], "stars": [1, 5]}
            ]
        }
    """
    coll = _collection_for(mode)
    size = _expected_size(mode)
    sorted_nums = sorted(int(n) for n in nums)

    if len(sorted_nums) != size:
        raise ValueError(
            f"{mode} needs exactly {size} mains, got {len(sorted_nums)}"
        )

    # Exact-set match (order-invariant, but our stored numbers are already sorted)
    query = {"numbers": sorted_nums}
    projection = {"_id": 0, "date": 1, "numbers": 1}
    if mode.lower() == "swiss":
        projection["lucky_number"] = 1
        projection["replay_number"] = 1
    else:
        projection["stars"] = 1

    cursor = db[coll].find(query, projection).batch_size(200)
    matches = await cursor.to_list(length=500)

    return {
        "mode": mode.lower(),
        "nums": sorted_nums,
        "expected_size": size,
        "is_virgin": len(matches) == 0,
        "play_count": len(matches),
        "matches": matches,
    }


async def position_match(
    db: AsyncIOMotorDatabase,
    mode: str,
    positions: Dict[int, int],
) -> Dict[str, Any]:
    """Kombo #2 — find historical draws matching position-specific values.

    positions maps 1-based position index -> value.
    e.g. {3: 21, 5: 47} means "P3 must be 21 AND P5 must be 47".

    Position is defined by sorted-ascending mains (P1 = smallest).

    Args:
        positions: dict of {pos_index (1-based): value}. At least 1 entry.
                   pos_index must be in [1, expected_size] for the mode.

    Returns:
        {
            "mode": "swiss"|"euro",
            "positions": {"P1": val, ...},   # normalized human-readable
            "match_count": int,
            "matches": [
                {"date": "dd.mm.yyyy", "numbers": [...], "lucky_number": ..., ...}
            ]
        }
    """
    coll = _collection_for(mode)
    size = _expected_size(mode)

    if not positions:
        raise ValueError("At least one position must be specified")

    for p in positions.keys():
        if p < 1 or p > size:
            raise ValueError(
                f"{mode} positions must be in 1..{size}, got P{p}"
            )

    # Since `numbers` is stored sorted, position P_k = numbers[k-1] (0-indexed).
    # We can construct a Mongo query using dot-notation on numbers.<index>.
    query: Dict[str, Any] = {}
    normalized: Dict[str, int] = {}
    for p, v in positions.items():
        p_idx = int(p) - 1
        val = int(v)
        query[f"numbers.{p_idx}"] = val
        normalized[f"P{p}"] = val

    projection = {"_id": 0, "date": 1, "numbers": 1}
    if mode.lower() == "swiss":
        projection["lucky_number"] = 1
        projection["replay_number"] = 1
    else:
        projection["stars"] = 1

    cursor = db[coll].find(query, projection).batch_size(200)
    raw_matches = await cursor.to_list(length=2000)

    # Sort matches by date descending (newest first) — parse dd.mm.yyyy properly
    def _sort_key(m: Dict[str, Any]):
        try:
            dd, mm, yyyy = m["date"].split(".")
            return (int(yyyy), int(mm), int(dd))
        except Exception:
            return (0, 0, 0)

    raw_matches.sort(key=_sort_key, reverse=True)

    return {
        "mode": mode.lower(),
        "positions": normalized,
        "match_count": len(raw_matches),
        "matches": raw_matches,
    }
