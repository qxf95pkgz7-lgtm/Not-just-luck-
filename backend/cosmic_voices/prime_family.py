"""
🧬 PRIME FAMILY LENS — `cosmic_voices/prime_family.py` (Lens #14)
==================================================================
DJ canon (Session 36, post-draw 08.05.2026):

> "The 37 came bring his 17 and uncle 2"

Tonight's draw [2, 17, 19, 34, 37] = 4 primes (2, 17, 19, 37) + 1 glue (34 = 2×17).
The cosmos plays prime-clusters with PRODUCT-GLUE: when 2 primes from the
draw multiply into a number ≤ 50, that product is the 5th main.

Detected patterns:
  • prime_density(BD) ≥ 3  → ND likely prime-laden too
  • product_glue: any 2 primes A,B in BD with A·B ≤ 50 → A·B is candidate ND
  • prime_neighbor: cousin primes ±2 of recent draws

Euro primes ≤ 50:
  {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47}
"""
from __future__ import annotations
from itertools import combinations
from typing import Dict, List

PRIMES_EURO = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47}


def is_prime(n: int) -> bool:
    return n in PRIMES_EURO


def prime_family_scan(recent_draws: List[Dict], main_max: int = 50) -> Dict:
    """Scan recent draws for prime-density patterns and project ND candidates.

    Looks at the BD (last draw) and last 3 for trends.
    """
    if not recent_draws:
        return {"available": False, "reason": "no recent draws"}

    window = recent_draws[-3:]
    series = []
    for d in window:
        primes_in_draw = [n for n in d["p"] if n in PRIMES_EURO]
        non_primes = [n for n in d["p"] if n not in PRIMES_EURO]
        # Check for product-glue: did any 2 primes multiply to give a non-prime in same draw?
        glues = []
        for a, b in combinations(primes_in_draw, 2):
            prod = a * b
            if prod in non_primes:
                glues.append({"primes": [a, b], "product_glue": prod})
        series.append({
            "date": d["date"],
            "mains": d["p"],
            "primes": primes_in_draw,
            "prime_count": len(primes_in_draw),
            "product_glues": glues,
            "prime_density_pct": round(100 * len(primes_in_draw) / max(1, len(d["p"])), 1),
        })

    # ── Project ND prime candidates from BD primes
    bd = window[-1]
    bd_primes = [n for n in bd["p"] if n in PRIMES_EURO]
    candidates: Dict[int, List[str]] = {}

    # Strategy 1: ±2 cousin primes of BD primes
    for p in bd_primes:
        for delta in (2, -2, 4, -4):
            cand = p + delta
            if 1 <= cand <= main_max and cand in PRIMES_EURO:
                candidates.setdefault(cand, []).append(f"cousin-prime-of-{p}")

    # Strategy 2: product glues in ND space — if BD has 2 primes A,B with A·B ≤ 50,
    # then A·B is a forced glue ND candidate
    for a, b in combinations(bd_primes, 2):
        prod = a * b
        if 1 <= prod <= main_max and prod not in PRIMES_EURO:
            candidates.setdefault(prod, []).append(f"product-glue-{a}×{b}")

    # Strategy 3: all primes ≤ main_max are seeded as fallback when BD is prime-heavy
    if len(bd_primes) >= 3:
        for p in PRIMES_EURO:
            if p not in bd["p"]:
                candidates.setdefault(p, []).append("prime-density-streak")

    boost_candidates = [
        {"n": n, "tags": tags} for n, tags in sorted(candidates.items())
    ]

    return {
        "available": True,
        "scan_window": series,
        "bd_primes": bd_primes,
        "bd_prime_count": len(bd_primes),
        "bd_density_alarm": len(bd_primes) >= 3,
        "boost_candidates": boost_candidates,
        "rule": ("Prime Family Law — if BD has ≥3 primes, ND likely prime-laden. "
                  "Product-glue: any 2 primes A·B≤50 in BD → A·B is forced "
                  "non-prime candidate (5th main). Cousin-primes ±2 of BD primes "
                  "carry forward."),
        "primes_table": sorted(PRIMES_EURO),
    }
