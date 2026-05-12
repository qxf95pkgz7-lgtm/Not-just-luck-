"""
🌉 CARRIER EXPANSION — unified Eu/Sw pool with ±carriers
==========================================================
S38 canon: Eu n → {n, n−25}; Sw m → {m, m−21}. Numbers walk across
decades and across lotteries through these carriers.

The 12 walked Eu→Sw at Q2 d8→d10 raw.
27→2, 42→17, 44→19, 43→18, 40→15, 41→16, 46→21, 31→6 (Canon V).
"""
from __future__ import annotations
from typing import Dict, List, Set


EURO_MAX = 50
SWISS_MAX = 42


def expand_carriers(n: int, mode: str) -> List[int]:
    """Return the carrier orbit of n in its lottery.

    Euro: {n, n-25 if >0, n+25 if ≤50}
    Swiss: {n, n-21 if >0, n+21 if ≤42}
    """
    if mode == "euro":
        orbit = {n}
        if n - 25 >= 1:
            orbit.add(n - 25)
        if n + 25 <= EURO_MAX:
            orbit.add(n + 25)
        return sorted(orbit)
    # swiss
    orbit = {n}
    if n - 21 >= 1:
        orbit.add(n - 21)
    if n + 21 <= SWISS_MAX:
        orbit.add(n + 21)
    return sorted(orbit)


def cross_lottery_carrier(n: int, source_mode: str) -> List[int]:
    """Map a number from one lottery to its carriers in the OTHER lottery.
    Used for cross-canal ghost projection.
    """
    if source_mode == "euro":
        # Euro → Swiss residues
        out: Set[int] = set()
        m = n
        while m > SWISS_MAX:
            m -= 21
        if 1 <= m <= SWISS_MAX:
            out.add(m)
        if 1 <= (n - 25) <= SWISS_MAX and n - 25 >= 1:
            out.add(n - 25)
        return sorted(out)
    # swiss → euro: lift by +21 / +25
    out2: Set[int] = set()
    if 1 <= (n + 21) <= EURO_MAX:
        out2.add(n + 21)
    if 1 <= (n + 25) <= EURO_MAX:
        out2.add(n + 25)
    if 1 <= n <= EURO_MAX:
        out2.add(n)
    return sorted(out2)


def unified_pool(nums: List[int], mode: str) -> Dict[int, List[int]]:
    """For each n in nums, return its full in-lottery carrier orbit."""
    return {n: expand_carriers(n, mode) for n in nums}
