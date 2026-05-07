"""
🪜 CLIMBING VOICE — P4→P3→P2→P1 arcs across recent d
====================================================
DJ canon (S34): A "climbing voice" is a number that drifts from a back
position in d_n to a front position in d_(n+k). They drop by RC-offsets
{3, 6, 12} (= RC-S2, envelope, RC-anchor in Q2 2026).

Lens output: numbers currently mid-climb + projected next P1/P2 candidates.
"""
from __future__ import annotations
from typing import Dict, List


def detect_climbing_voices(recent_draws: List[Dict], lookback: int = 6) -> Dict:
    """Scan the last `lookback` draws (chronological ascending). For every number
    appearing in two consecutive draws at a strictly LOWER position, mark it as
    climbing. Drops of {3, 6, 12} from RC offsets are flagged as canonical.
    """
    window = recent_draws[-lookback:] if len(recent_draws) > lookback else recent_draws
    arcs: List[Dict] = []
    canonical_drops = {3, 6, 12}
    next_p1_candidates: List[int] = []
    next_p2_candidates: List[int] = []

    for i in range(len(window) - 1):
        a, b = window[i], window[i + 1]
        a_pos = {n: idx for idx, n in enumerate(a["p"])}
        b_pos = {n: idx for idx, n in enumerate(b["p"])}
        for n, ai in a_pos.items():
            if n in b_pos and b_pos[n] < ai:
                drop = ai - b_pos[n]
                arcs.append({
                    "n": n,
                    "from_d": a["date"],
                    "from_pos": f"P{ai+1}",
                    "to_d": b["date"],
                    "to_pos": f"P{b_pos[n]+1}",
                    "drop": drop,
                    "canonical": drop in canonical_drops,
                })
                # If the climb reaches P2 or P1 → project the next-step candidate
                if b_pos[n] == 1:  # currently at P2
                    next_p1_candidates.append(n)
                elif b_pos[n] == 0:  # already P1; track as held
                    next_p1_candidates.append(n)

    # Long-arc projection: a number that climbed once may climb again next d
    arc_numbers = sorted({a["n"] for a in arcs if a["canonical"]})
    return {
        "arcs": arcs,
        "canonical_climbers": arc_numbers,
        "projected_next_p1": sorted(set(next_p1_candidates)),
        "projected_next_p2": sorted(set(next_p2_candidates)),
        "lookback_d": len(window),
        "rule": "Numbers drift forward across consecutive d. Drops of {3,6,12} = RC-canonical.",
    }
