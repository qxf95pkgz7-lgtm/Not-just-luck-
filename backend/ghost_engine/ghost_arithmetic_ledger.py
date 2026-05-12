"""
👻 GHOST ARITHMETIC LEDGER — `?+Pa=Pb` door extractor
======================================================
S38 canon: every draw advertises arithmetic doors. For each ordered position
pair (Pa, Pb) with a < b, the door says "?+Pa=Pb" → expected = Pb − Pa.

If `expected` is a valid number AND is NOT in the actual draw → it's a
GHOST. The cosmos opened the door but nobody walked through.

Returns per-draw list of ghost births with their source doors.
"""
from __future__ import annotations
from itertools import combinations
from typing import Dict, List


def extract_ghosts_for_draw(draw: Dict, max_n: int) -> List[Dict]:
    """Return ghost births for one draw.

    draw: {"date", "dt", "p": [P1, ..., Pk], ...}
    A ghost = expected door value not present in `p`.

    Each ghost: {"n", "door": "P{a}+?=P{b}", "src": [Pa, Pb], "diff": Pb-Pa,
                  "type": "diff" | "sum"}
    """
    p = draw.get("p") or []
    if len(p) < 2:
        return []
    in_draw = set(p)
    ghosts: List[Dict] = []
    seen_n = set()
    # Diff doors: ? + Pa = Pb → ? = Pb - Pa
    for i, j in combinations(range(len(p)), 2):
        a, b = p[i], p[j]
        diff = b - a
        if 1 <= diff <= max_n and diff not in in_draw and diff not in seen_n:
            ghosts.append({
                "n": diff,
                "door": f"P{i+1}+?=P{j+1}",
                "src": [a, b],
                "diff": diff,
                "type": "diff",
            })
            seen_n.add(diff)
    # Sum doors: Pa + Pb = ? → ? = Pa + Pb (only the missing chain term as ghost)
    for i, j in combinations(range(len(p)), 2):
        a, b = p[i], p[j]
        s = a + b
        if 1 <= s <= max_n and s not in in_draw and s not in seen_n:
            ghosts.append({
                "n": s,
                "door": f"P{i+1}+P{j+1}=?",
                "src": [a, b],
                "diff": s,
                "type": "sum",
            })
            seen_n.add(s)
    return ghosts


def build_arithmetic_ledger(draws: List[Dict], mode: str) -> List[Dict]:
    """Build the full ghost-birth ledger across an ordered list of draws.

    Returns list of {date, dt, ghosts: [...], chain_terms: {pairs_diff, pairs_sum}}
    """
    max_n = 50 if mode == "euro" else 42
    out: List[Dict] = []
    for d in draws:
        ghosts = extract_ghosts_for_draw(d, max_n)
        out.append({
            "date": d.get("date"),
            "dt": d.get("dt"),
            "p": d.get("p"),
            "ghosts": ghosts,
            "ghost_count": len(ghosts),
            "ghost_ns": sorted({g["n"] for g in ghosts}),
        })
    return out
