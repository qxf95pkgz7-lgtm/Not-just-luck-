"""
🎼 QUARTER SHAPE SIGNATURE — d1-d3 chord-shape detector
========================================================
S38 canon: each quarter sings its own internal chord-shape.
  • Q1 Swiss 2026 → `P1+P5=P6` was the dominant chord
  • Q2 Swiss 2026 → `P1+P2=P5/P4`

Scan d1-dN of a quarter's draws and find which equation holds in the most
draws → that's the QUARTER SHAPE. Used as a forward filter — future draws
in the same quarter are biased to honour the shape.
"""
from __future__ import annotations
from itertools import combinations
from typing import Dict, List


def _collect_equations(p: List[int]) -> List[str]:
    """All Pa+Pb=Pc equations holding inside a draw, returned as
    canonical 'P{a}+P{b}=P{c}' strings (1-indexed)."""
    eqs: List[str] = []
    idx_of = {v: i for i, v in enumerate(p)}
    for i, j in combinations(range(len(p)), 2):
        s = p[i] + p[j]
        if s in idx_of:
            k = idx_of[s]
            if k > j:
                eqs.append(f"P{i+1}+P{j+1}=P{k+1}")
    return eqs


def detect_quarter_shape(quarter_draws: List[Dict]) -> Dict:
    """Detect the dominant equation across draws of a quarter.

    Returns:
      {chord, count, total_draws, hit_rate, ranked: [(chord, count)...]}
    """
    counts: Dict[str, int] = {}
    for d in quarter_draws:
        for eq in _collect_equations(d.get("p") or []):
            counts[eq] = counts.get(eq, 0) + 1
    if not counts:
        return {
            "chord": None,
            "count": 0,
            "total_draws": len(quarter_draws),
            "hit_rate": 0.0,
            "ranked": [],
        }
    ranked = sorted(counts.items(), key=lambda x: -x[1])
    top = ranked[0]
    return {
        "chord": top[0],
        "count": top[1],
        "total_draws": len(quarter_draws),
        "hit_rate": round(top[1] / max(len(quarter_draws), 1), 3),
        "ranked": ranked[:6],
    }
