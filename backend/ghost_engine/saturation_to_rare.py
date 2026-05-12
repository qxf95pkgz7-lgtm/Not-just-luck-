"""
🌌 SATURATION → FAMILY-RARE CASCADE PREDICTOR
================================================
S38 canon: when a number hits ≥5 times in 9 draws, it "dethrones" into a
decade-cluster — the family decade of that number becomes the next rare
landing zone (Q1 2026: 20 sat → 5-in-30s → HUGE 6-in-30s on 07.02.2026).
"""
from __future__ import annotations
from collections import Counter
from typing import Dict, List


def _decade_of(n: int) -> str:
    if n <= 9:
        return "1-9"
    if n <= 19:
        return "10-19"
    if n <= 29:
        return "20-29"
    if n <= 39:
        return "30-39"
    if n <= 49:
        return "40-49"
    return "50"


def saturation_watch(draws: List[Dict], window: int = 9, threshold: int = 5) -> Dict:
    """Scan the last `window` draws. Any number with count ≥ threshold flags
    its decade as the next family-rare suspect.

    Returns:
      {
        "saturated": [{n, count, decade}],
        "suspect_decades": [decade names with saturation pressure],
        "decade_density": {decade: total_count_in_window},
        "next_family_rare_zone": leader decade
      }
    """
    win = draws[-window:] if len(draws) > window else draws
    counter: Counter = Counter()
    decade_density: Counter = Counter()
    for d in win:
        for n in (d.get("p") or []):
            counter[n] += 1
            decade_density[_decade_of(n)] += 1
    saturated = [
        {"n": n, "count": c, "decade": _decade_of(n)}
        for n, c in counter.most_common() if c >= threshold
    ]
    suspect_decades: List[str] = []
    for s in saturated:
        if s["decade"] not in suspect_decades:
            suspect_decades.append(s["decade"])
    next_zone = None
    if decade_density:
        next_zone = decade_density.most_common(1)[0][0]
    return {
        "window_size": len(win),
        "threshold": threshold,
        "saturated": saturated,
        "suspect_decades": suspect_decades,
        "decade_density": dict(decade_density),
        "next_family_rare_zone": next_zone,
    }
