"""
🌊 SINKING VOICE — P5→P4→P3→P2 sinking arcs across recent d
==========================================================
The mirror image of climbing_voice. A sinking number drifts from a front
position toward the back across d's. When a sinking voice locks at P5,
expect a SINK ARRIVAL (e.g. Q2d6 → Q2d7 P1=26 confirmed S34).
"""
from __future__ import annotations
from typing import Dict, List


def detect_sinking_voices(recent_draws: List[Dict], lookback: int = 6) -> Dict:
    """Scan the last `lookback` draws. Mark numbers whose position drifts to a
    HIGHER index across consecutive d's. A "lock at P5" = sinking arrival.
    """
    window = recent_draws[-lookback:] if len(recent_draws) > lookback else recent_draws
    arcs: List[Dict] = []
    locked_at_back: List[int] = []

    for i in range(len(window) - 1):
        a, b = window[i], window[i + 1]
        a_pos = {n: idx for idx, n in enumerate(a["p"])}
        b_pos = {n: idx for idx, n in enumerate(b["p"])}
        for n, ai in a_pos.items():
            if n in b_pos and b_pos[n] > ai:
                rise = b_pos[n] - ai
                arcs.append({
                    "n": n,
                    "from_d": a["date"],
                    "from_pos": f"P{ai+1}",
                    "to_d": b["date"],
                    "to_pos": f"P{b_pos[n]+1}",
                    "rise": rise,
                })
                # If the sink reaches the last position of b → arrival fires
                if b_pos[n] == len(b["p"]) - 1:
                    locked_at_back.append(n)

    sink_numbers = sorted({a["n"] for a in arcs})
    return {
        "arcs": arcs,
        "sinking_numbers": sink_numbers,
        "locked_at_back": sorted(set(locked_at_back)),
        "lookback_d": len(window),
        "rule": "Numbers drift backward across d. Lock at P5/P6 = sinking arrival; expect P1 echo next d.",
    }
