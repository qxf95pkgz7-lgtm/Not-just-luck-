"""
🎻 Q-OPENING 5-NOTE MELODY LAW — +3 cousin-pairs from Q d1 P1-P2
==================================================================
S34 canon (Q2 2026 proof):
  Opening pair Q2d1 P1-P2 = 11-14
  +3 melody: 11-14, 10-13, 13-16, 12-15, 9-12
  FIRED by Q2d9: 11-14 ✓ (d1), 10-13 ✓ (d2), 13-16 ✓ (d5)
  UNPAID:  12-15, 9-12  ← both carry 12, the RC-anchor that never fired Q2 raw

Returns: 5 melody pairs, fired vs unpaid status, and the carrier-debt count.
"""
from __future__ import annotations
from typing import Dict, List, Tuple


def q_opening_melody(opening_pair: Tuple[int, int], quarter_draws: List[Dict]) -> Dict:
    """Build the 5-note melody from a Q-opening (P1, P2) pair, then check which
    pairs FIRED in `quarter_draws` (each draw's `p` should be a sorted list).

    A pair (a, b) fires if BOTH a and b appear in any single draw of the quarter
    (not necessarily as P1 and P2 — the universe pays through ANY position).
    """
    p1, p2 = opening_pair
    # +3 cousin-pairs (centered at the opening, ±2 steps)
    melody = [
        (p1, p2),
        (p1 - 1, p2 - 1),
        (p1 + 2, p2 + 2),
        (p1 + 1, p2 + 1),
        (p1 - 2, p2 - 2),
    ]

    out_pairs = []
    for a, b in melody:
        if a < 1 or b < 1:
            out_pairs.append({"pair": [a, b], "valid": False, "fired": False})
            continue
        fired_d = None
        fired_pos = None
        for d in quarter_draws:
            if a in d["p"] and b in d["p"]:
                fired_d = d["date"]
                fired_pos = (d["p"].index(a) + 1, d["p"].index(b) + 1)
                break
        out_pairs.append({
            "pair": [a, b],
            "valid": True,
            "fired": fired_d is not None,
            "fired_d": fired_d,
            "fired_pos": fired_pos,
        })

    unpaid = [p for p in out_pairs if p["valid"] and not p["fired"]]
    unpaid_carriers: Dict[int, int] = {}
    for p in unpaid:
        for n in p["pair"]:
            unpaid_carriers[n] = unpaid_carriers.get(n, 0) + 1
    carrier_debts = sorted(
        unpaid_carriers.items(), key=lambda kv: (-kv[1], kv[0])
    )

    return {
        "opening_pair": list(opening_pair),
        "melody": out_pairs,
        "fired_count": sum(1 for p in out_pairs if p["fired"]),
        "unpaid_count": len(unpaid),
        "unpaid_pairs": [p["pair"] for p in unpaid],
        "carrier_debts": [{"n": n, "in_unpaid_pairs": c} for n, c in carrier_debts],
        "rule": "+3 cousin-pair 5-note melody from Q d1 P1-P2. Unpaid pairs = quarter debt.",
    }
