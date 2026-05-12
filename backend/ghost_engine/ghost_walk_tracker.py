"""
🚶 GHOST WALK TRACKER — +1 forward walk with neighbor / digit / carrier probes
==============================================================================
S38 canon: a born ghost walks +1 per subsequent draw. At each step we also
probe its ±1 mirror-neighbor, digit-swap form, and carrier-form (Eu n−25 /
Sw m−21). The collection of these probes = the ghost's "hot zone" at age k.
"""
from __future__ import annotations
from typing import Dict, List, Set

from .carrier_expansion import expand_carriers


def _digit_swap(n: int) -> int:
    """Return the digit-swap (mirror-wrap) form. 12→21, 41→14, 34→43, single
    digit unchanged."""
    s = str(n)
    if len(s) == 1:
        return n
    return int(s[::-1])


def _hot_zone(n: int, age: int, mode: str, max_n: int) -> Set[int]:
    """Compute the ghost's hot zone at given age."""
    hot: Set[int] = set()
    # +age forward walk
    walked = n + age
    if 1 <= walked <= max_n:
        hot.add(walked)
    # raw
    if 1 <= n <= max_n:
        hot.add(n)
    # ±1 mirror-neighbor of raw + walked
    for base in {n, walked}:
        for delta in (-1, +1):
            v = base + delta
            if 1 <= v <= max_n:
                hot.add(v)
    # digit-swap
    swap = _digit_swap(n)
    if 1 <= swap <= max_n:
        hot.add(swap)
    # carrier-form
    for c in expand_carriers(n, mode):
        hot.add(c)
    return hot


def walk_ghosts_forward(ghost_birth: Dict, target_age: int, mode: str) -> Dict:
    """Project a ghost's hot zone at `target_age` draws since birth.

    ghost_birth: {"n", "born_date", "born_idx", ...}
    Returns: {"n", "age", "walked": n+age, "hot_zone": sorted list, "carriers": list,
              "neighbors": [n-1, n+1], "digit_swap": ...}
    """
    n = ghost_birth["n"]
    max_n = 50 if mode == "euro" else 42
    walked = n + target_age
    walked = walked if 1 <= walked <= max_n else None
    return {
        "n": n,
        "age": target_age,
        "walked": walked,
        "hot_zone": sorted(_hot_zone(n, target_age, mode, max_n)),
        "carriers": expand_carriers(n, mode),
        "neighbors": [v for v in (n - 1, n + 1) if 1 <= v <= max_n],
        "digit_swap": _digit_swap(n) if _digit_swap(n) != n else None,
    }
