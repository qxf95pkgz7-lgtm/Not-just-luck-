"""
🦶 STANCE TRACKER — compress-front / flip-up / sinking
=======================================================
S34 canon (Q2 2026 walk):
  d1 [11,14,19,36,49] → compress-front + stretch-back (BAIT stance)
  d3 [1,2,4,28,44]    → MAX compress (TRAP stance)
  d4 [22,23,28,41,47] → 🚨 FLIP UP (over-determined, P1 jumped to 22)
  d6 [25,26,30,40,45] → 5-of-5 over-determined; sinking-voice lock
  d7 [26,29,41,46,47] → sinking arrives (P1=26 = sinking arrival)
  d8 [3,9,42,46,47]   → 🚨 PAYMENT
  d9 [3,4,8,20,31]    → 🚨 CLOSER

Stance heuristic for a single draw:
  • front_span = P3 - P1
  • back_span  = P5 - P3 (Euro) / P6 - P3 (Swiss)
  • If front_span <= 4 AND back_span >= 18: COMPRESS-FRONT-STRETCH-BACK (bait)
  • If front_span <= 3 AND P1 <= 4: MAX-COMPRESS (trap)
  • If P1 > 18: FLIP-UP (over-determined)
  • If P5/P6 > 44 and saturation ≥ 3: SINKING-LOCK
  • Otherwise: NEUTRAL
"""
from __future__ import annotations
from typing import Dict, List


def _classify_stance(p: List[int], mode: str) -> str:
    if not p or len(p) < 5:
        return "—"
    p1 = p[0]
    p3 = p[2]
    p_last = p[-1]
    front_span = p3 - p1
    back_span = p_last - p3
    if p1 > 18:
        return "FLIP-UP"
    if front_span <= 3 and p1 <= 4:
        return "MAX-COMPRESS (trap)"
    if front_span <= 4 and back_span >= 18:
        return "COMPRESS-FRONT-STRETCH-BACK (bait)"
    if p_last >= 44:
        return "SINKING-LOCK"
    return "NEUTRAL"


def stance_tracker(recent_draws: List[Dict], mode: str, lookback: int = 8) -> Dict:
    """Assign a stance to each of the last `lookback` draws + project the next
    expected stance based on the rotation pattern (BAIT → TRAP → FLIP → ...).
    """
    window = recent_draws[-lookback:] if len(recent_draws) > lookback else recent_draws
    history = []
    for d in window:
        history.append({
            "date": d["date"],
            "mains": d["p"],
            "stance": _classify_stance(d["p"], mode),
        })

    # Simple projection: count flip-up density to anticipate post-flip release
    flip_count = sum(1 for h in history if h["stance"] == "FLIP-UP")
    compress_count = sum(1 for h in history if "COMPRESS" in h["stance"])
    last_stance = history[-1]["stance"] if history else "—"

    # Heuristic next-stance projection
    proj = "NEUTRAL"
    if last_stance == "FLIP-UP":
        proj = "PAYMENT (low P1, ghost-cashing)"
    elif "COMPRESS" in last_stance:
        proj = "FLIP-UP (over-determined release)"
    elif last_stance == "SINKING-LOCK":
        proj = "SINKING-ARRIVAL (P1 echoes the sink)"

    return {
        "history": history,
        "current_stance": last_stance,
        "flip_up_count": flip_count,
        "compress_count": compress_count,
        "projected_next_stance": proj,
        "rule": "Stance rotation: BAIT → TRAP → FLIP → PAYMENT → CLOSER. After flip = ghost-cashing.",
    }
